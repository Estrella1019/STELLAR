# llm/client.py

import os
import time
import traceback
import re
import json
import httpx
from openai import OpenAI, BadRequestError, APITimeoutError
from llm.llms import LLMType

from dotenv import load_dotenv
load_dotenv()

class OpenAIClient:
    total_token_usage = 0
    total_call_count = 0
    
    def __init__(self, model_enum: LLMType, api_key: str = None):
        # 1. 兼容性处理：无论传入的是 Enum 还是 字符串，都转为字符串
        raw_model_name = model_enum.value if hasattr(model_enum, 'value') else str(model_enum)
        self.model_name = raw_model_name

        # 2. 模型重定向 (从 .env 读取配置)
        judge_model = os.getenv("JUDGE_MODEL", "deepseek-r1:7b")
        generator_model = os.getenv("GENERATOR_MODEL", "dolphin3:latest")
        
        # 拦截 STELLAR 默认的 GPT 模型，转为本地模型
        if "gpt-4" in raw_model_name:
            if "mini" in raw_model_name:
                self.deployment_name = judge_model  # 判卷模型
            else:
                self.deployment_name = generator_model # 生成模型
            print(f"🔄 [Redirect] {raw_model_name} => {self.deployment_name}")
        else:
            self.deployment_name = raw_model_name
            print(f"👀 [Init] Client: {self.deployment_name}")

        # 3. 初始化客户端 (Ollama)
        # ⚠️ 设置 600秒 (10分钟) 超时，防止 R1 思考时间过长导致断开
        self.client = OpenAI(
            api_key="ollama",
            base_url=os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1"),
            timeout=httpx.Timeout(600.0, read=600.0, write=600.0, connect=10.0)
        )

        self.token_usage = 0
        self.call_counter = 0

    def _clean_deepseek_response(self, content):
        """
        [核心修复] 暴力提取 JSON。
        即使模型输出了 <think> 或 'Here is the json:', 也能提取出正确的 {...} 部分。
        """
        if not content:
            return ""
        
        # 1. 先去掉 <think> 标签
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
        
        # 2. 尝试寻找第一个 '{' 和最后一个 '}' 包裹的内容
        #    这能解决 "Sure! ```json { ... } ```" 这种格式问题
        match = re.search(r'(\{.*\})', content, re.DOTALL)
        if match:
            clean_json = match.group(1)
            return clean_json
            
        # 3. 如果找不到大括号，只能返回原始内容 (可能会导致外部解析失败)
        return content.strip()

    def call(self, 
             prompt: str, 
             max_tokens=4096, 
             temperature=0.6, 
             system_message=None, 
             context=None):
        
        if system_message is None:
            system_message = "You are a helpful assistant."

        try:        
            self.call_counter += 1
            OpenAIClient.total_call_count += 1

            start_time = time.time()
            formatted_system_msg = system_message.format(context) if context else system_message
            
            # DeepSeek R1 推荐用法：System Prompt 放入 user 消息前或 system 消息
            messages = [
                {"role": "system", "content": formatted_system_msg},
                {"role": "user", "content": prompt}
            ]

            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            end_time = time.time()

            used_tokens = 0
            if response.usage:
                used_tokens = response.usage.total_tokens
            self.token_usage += used_tokens
            OpenAIClient.total_token_usage += used_tokens

            raw_content = response.choices[0].message.content
            
            # [调用清洗函数]
            clean_content = self._clean_deepseek_response(raw_content)

            # [Debug] 如果返回为空，打印警告
            if not clean_content:
                print(f"⚠️ [Client] Empty response from {self.deployment_name}")

            return clean_content, used_tokens, end_time - start_time

        except APITimeoutError:
            print(f"❌ [Timeout] Model {self.deployment_name} did not reply in 600s.")
            return "", 0, -1
            
        except BadRequestError as e:
            print(f"❌ [BadRequest] {e}")
            return f"BADREQUEST_ERROR: {e}", 0, -1

        except Exception as e:
            print(f"❌ [Exception] {type(e).__name__}: {e}")
            traceback.print_exc()
            return "", 0, -1
    
    @classmethod
    def from_deployment_name(cls, deployment_name: str, api_key: str = None):
        class MockEnum:
            value = deployment_name
        return cls(MockEnum, api_key="ollama")