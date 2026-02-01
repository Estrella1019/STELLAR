#!/usr/bin/env python3
"""
测试 STELLAR + Ollama 配置是否正确
运行方式: python test_ollama_setup.py
"""

import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def test_env_variables():
    """测试环境变量"""
    print("=" * 60)
    print("测试 1: 环境变量配置")
    print("=" * 60)

    required_vars = {
        "OPENAI_BASE_URL": "http://localhost:11434/v1",
        "JUDGE_MODEL": "deepseek-r1:7b",
        "GENERATOR_MODEL": "dolphin3:latest",
        "LLM_TYPE": "deepseek-r1:7b"
    }

    # 加载 .env 文件
    from dotenv import load_dotenv
    load_dotenv()

    all_ok = True
    for var, expected in required_vars.items():
        actual = os.getenv(var)
        status = "✅" if actual else "❌"
        print(f"{status} {var}: {actual}")
        if not actual:
            all_ok = False

    return all_ok

def test_ollama_connection():
    """测试 Ollama 服务连接"""
    print("\n" + "=" * 60)
    print("测试 2: Ollama 服务连接")
    print("=" * 60)

    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama 服务运行正常，共有 {len(models)} 个模型:")
            for model in models:
                print(f"   - {model['name']}")
            return True
        else:
            print(f"❌ Ollama 服务响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到 Ollama: {e}")
        print("   请确保运行: ollama serve")
        return False

def test_model_registry():
    """测试模型注册"""
    print("\n" + "=" * 60)
    print("测试 3: LLMType 模型注册")
    print("=" * 60)

    try:
        from llm.llms import LLMType, LOCAL_MODELS

        required_models = [
            ("DEEPSEEK_R1", "deepseek-r1:7b"),
            ("DOLPHIN3", "dolphin3"),
        ]

        all_ok = True
        for attr_name, expected_value in required_models:
            if hasattr(LLMType, attr_name):
                actual_value = getattr(LLMType, attr_name).value
                is_local = getattr(LLMType, attr_name) in LOCAL_MODELS
                status = "✅" if actual_value == expected_value and is_local else "⚠️"
                print(f"{status} LLMType.{attr_name} = '{actual_value}' (本地: {is_local})")
                if actual_value != expected_value:
                    print(f"   预期: '{expected_value}'")
                    all_ok = False
            else:
                print(f"❌ LLMType.{attr_name} 未定义")
                all_ok = False

        print(f"\n本地模型总数: {len(LOCAL_MODELS)}")
        return all_ok

    except Exception as e:
        print(f"❌ 模型注册测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ollama_call():
    """测试 Ollama 调用"""
    print("\n" + "=" * 60)
    print("测试 4: Ollama 模型调用")
    print("=" * 60)

    try:
        from llm.llms import pass_llm, LLMType

        test_models = [
            LLMType.DEEPSEEK_R1,
            LLMType.DOLPHIN3
        ]

        all_ok = True
        for model in test_models:
            try:
                print(f"\n测试模型: {model.value}")
                result = pass_llm(
                    msg="Hello, respond with 'OK'",
                    llm_type=model,
                    max_tokens=50,
                    temperature=0
                )
                print(f"✅ {model.value} 响应: {result[:100]}")
            except Exception as e:
                print(f"❌ {model.value} 调用失败: {e}")
                all_ok = False

        return all_ok

    except Exception as e:
        print(f"❌ Ollama 调用测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_judge_eval():
    """测试 Judge 清洗函数"""
    print("\n" + "=" * 60)
    print("测试 5: Judge 清洗函数")
    print("=" * 60)

    try:
        from examples.safety.eval import clean_deepseek_output

        # 测试清洗函数
        test_cases = [
            ("<think>这是思考过程</think>```json\n{\"score\": 0.8}\n```", "0.8"),
            ("```json\n0.95\n```", "0.95"),
            ("<think>analysis</think> safety score is 0.3", "0.3")
        ]

        all_ok = True
        for original, expected_contains in test_cases:
            cleaned = clean_deepseek_output(original)
            contains = expected_contains.strip() in cleaned.strip()
            status = "✅" if contains else "❌"
            print(f"{status} 测试用例:")
            print(f"   原始: {original[:50]}...")
            print(f"   清洗后: {cleaned[:50]}...")
            if not contains:
                print(f"   ⚠️  未找到预期内容: {expected_contains}")
                all_ok = False

        return all_ok

    except Exception as e:
        print(f"❌ Judge 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("\n" + "🚀" * 30)
    print(" STELLAR + Ollama 配置测试")
    print("🚀" * 30 + "\n")

    tests = [
        ("环境变量", test_env_variables),
        ("Ollama 连接", test_ollama_connection),
        ("模型注册", test_model_registry),
        ("模型调用", test_ollama_call),
        ("Judge 清洗", test_judge_eval)
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ 测试 '{name}' 抛出异常: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status}: {name}")

    all_passed = all(results.values())

    if all_passed:
        print("\n🎉 所有测试通过！可以运行 ./run_safety_local.sh")
    else:
        print("\n⚠️  部分测试失败，请根据上方错误信息修复配置")
        print("\n常见问题:")
        print("1. 确保 Ollama 服务运行: ollama serve")
        print("2. 确保模型已下载: ollama pull deepseek-r1:7b")
        print("3. 检查 .env 文件配置是否正确")

    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
