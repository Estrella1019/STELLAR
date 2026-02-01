import os
DEBUG = False
LLM_TYPE = "gpt-4o"
MAX_TOKENS = 300
# DEPLOYMENT_NAME = "gpt-35-turbo-1106"
DEPLOYMENT_NAME = "gpt-4o"
#DEPLOYMENT_NAME = "DeepSeek-R1-qcbar"
N_VALIDATORS = 1
# "gpt-35-turbo-1106"
# "gpt-4o"
# ==============================
# 修改：从 .env 读取本地 Ollama 模型配置
# ==============================

# 采样/生成 (Generator) -> 用 .env 里的 GENERATOR_MODEL (Dolphin3)
LLM_SAMPLING = os.getenv("GENERATOR_MODEL", "dolphin3:latest")
LLM_MUTATOR = os.getenv("GENERATOR_MODEL", "dolphin3:latest")
LLM_CROSSOVER = os.getenv("GENERATOR_MODEL", "dolphin3:latest")

# 评估/裁判 (Judge) -> 用 .env 里的 JUDGE_MODEL (Qwen2.5)
LLM_VALIDATOR = os.getenv("JUDGE_MODEL", "qwen2.5:7b")

# IPA (如果你不知道这是啥，也用生成器模型顶替)
LLM_IPA = os.getenv("GENERATOR_MODEL", "dolphin3:latest")
LLM_IPA = DEPLOYMENT_NAME#"gpt-4o"#"gpt-35-turbo-1106"

CONTEXT = {
    "location" : {
        "position" : "Amathountos Avenue 502, 4520, Limassol, Cyprus",
        "time" : "2025-03-19T09:00:00Z",
    }
}
###############

EXAMPLE = "I am hungry and like Pizza."
USER_PROFILE  = "The user is an IT employee and is lactose intolerant."
