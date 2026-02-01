import os

DEBUG = False

LLM_TYPE = os.getenv("LLM_TYPE", "deepseek-chat")
MAX_TOKENS = 400

DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME", "deepseek-chat")
N_VALIDATORS = int(os.getenv("N_VALIDATORS", 1))

LLM_OLLAMA = os.getenv("LLM_OLLAMA", "deepseek-chat")
LLM_SAMPLING = os.getenv("LLM_SAMPLING", "deepseek-chat")
LLM_MUTATOR = os.getenv("LLM_MUTATOR", "deepseek-chat")
LLM_CROSSOVER = os.getenv("LLM_CROSSOVER", "deepseek-chat")
LLM_VALIDATOR = os.getenv("LLM_VALIDATOR", "deepseek-chat")
LLM_IPA = os.getenv("LLM_IPA", DEPLOYMENT_NAME)

CONTEXT = {
    "location": {
        "position": os.getenv("LOCATION_POSITION", "Amathountos Avenue 502, 4520, Limassol, Cyprus"),
        "time": os.getenv("LOCATION_TIME", "2025-03-19T09:00:00Z"),
    }
}
