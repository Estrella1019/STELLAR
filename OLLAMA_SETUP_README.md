# STELLAR + Ollama 本地运行配置指南

## ✅ 已完成的修改

根据你的 Ollama 模型列表，STELLAR 已经配置为使用以下本地模型：

### 1. 环境变量配置 (`.env`)
```bash
# Ollama 地址
OPENAI_BASE_URL=http://localhost:11434/v1

# Judge 模型 (用于评估测试结果)
JUDGE_MODEL=deepseek-r1:7b

# Generator 模型 (用于生成攻击提示词)
GENERATOR_MODEL=dolphin3:latest

# SUT 被测系统模型
LLM_TYPE=deepseek-r1:7b
DEPLOYMENT_NAME=deepseek-r1:7b
LLM_OLLAMA=deepseek-r1:7b
```

### 2. 模型定义 (`llm/llms.py`)
已添加本地模型到 `LLMType` 枚举：
- `DEEPSEEK_R1 = "deepseek-r1:7b"`
- `DOLPHIN3 = "dolphin3"`
- `DOLPHIN_LLAMA3 = "dolphin-llama3"`
- `LLAMA3_1 = "llama3.1"`

所有这些模型已加入 `LOCAL_MODELS` 集合，确保走 Ollama 调用路径。

### 3. Ollama 调用函数 (`llm/call_ollama.py`)
使用 `ollama.chat()` API 进行本地推理，支持：
- 温度控制
- Token 限制
- Top-p 采样
- 重复惩罚

### 4. Judge 评估增强 (`examples/safety/eval.py`)
- **问题**: DeepSeek-R1 会输出 `<think>...</think>` 思考过程
- **解决**: 添加 `clean_deepseek_output()` 函数清洗输出
- **增强**: 支持多种评分格式 (0-1 浮点数、1-10 整数评分)
- **兜底**: 解析失败时返回 0.5 而不是 1.0，避免误判

### 5. 运行脚本 (`run_safety_local.sh`)
配置参数：
```bash
--sut "deepseek-r1:7b"          # 被测系统
--judge "deepseek-r1:7b"        # 评判模型
--fitness "deepseek-r1:7b"      # 适应度计算
--generator "dolphin3"          # 测试生成
--population_size 20            # 种群大小
--max_time "02:00:00"           # 2小时超时
--algorithm "nsga2"             # 遗传算法
--use_repair                    # 启用修复算子
```

---

## 🔧 需要手动检查的配置

### 1. 确认 Ollama 服务运行
```bash
# 检查 Ollama 是否运行
curl http://localhost:11434/api/tags

# 如果没有运行，启动它
ollama serve
```

### 2. 验证模型可用性
```bash
# 确认 deepseek-r1:7b 已下载
ollama list | grep deepseek-r1

# 确认 dolphin3 已下载
ollama list | grep dolphin3

# 如果缺失，拉取模型
ollama pull deepseek-r1:7b
ollama pull dolphin3:latest
```

### 3. 测试模型调用
```bash
cd /Users/panjiaying/Documents/Projects/STELLAR
python -c "
from llm.llms import pass_llm, LLMType
result = pass_llm('Hello', llm_type=LLMType.DEEPSEEK_R1)
print(result)
"
```

---

## 🚀 运行实验

### Safety 测试 (论文中的 SafeQA)
```bash
cd /Users/panjiaying/Documents/Projects/STELLAR
chmod +x run_safety_local.sh
./run_safety_local.sh
```

### Navigation 测试 (论文中的 NaviQA)
```bash
# 需要先修改 run_tests_navi.py (参考 run_tests_safety.py 的修改)
python run_tests_navi.py \
    --sut "deepseek-r1:7b" \
    --judge "deepseek-r1:7b" \
    --fitness "deepseek-r1:7b" \
    --generator "dolphin3" \
    --population_size 20 \
    --algorithm "nsga2d"
```

---

## 📊 查看结果

结果会保存在 `results/` 目录下，关键文件：
- `failures_over_time.csv` - 失败测试用例随时间变化
- `archive.csv` - 所有测试用例归档
- `critical_cases.csv` - 被判定为 critical 的失败案例

---

## ⚠️ 常见问题

### 问题 1: `KeyError: 'dolphin3'` 或模型未找到
**原因**: 模型名称不匹配
**解决**:
```bash
# 查看 Ollama 中的实际模型名
ollama list

# 修改 .env 中的 GENERATOR_MODEL 为实际名称
# 例如: GENERATOR_MODEL=dolphin3:latest
```

### 问题 2: Judge 一直返回 0.5 (解析失败)
**原因**: DeepSeek-R1 输出格式不符合预期
**解决**:
1. 检查 `examples/safety/eval.py` 中的 `clean_deepseek_output()` 函数
2. 临时启用 debug 输出查看原始响应:
```python
# 在 eval.py 的 eval() 函数中添加
print(f"DEBUG Raw Response: {response}")
print(f"DEBUG Clean Response: {clean_response}")
```

### 问题 3: Ollama 内存不足
**解决**:
```bash
# 使用更小的模型
ollama pull qwen2.5:7b
# 修改 .env 为 LLM_TYPE=qwen2.5:7b
```

### 问题 4: 生成速度太慢
**解决**:
1. 减少 `--population_size` 到 10
2. 减少 `--max_time` 到 "01:00:00"
3. 使用更快的模型如 `llama3.2:3b`

---

## 📝 模型选择建议

根据论文要求和你的硬件配置：

| 角色 | 推荐模型 | 原因 |
|-----|---------|------|
| **Generator** | `dolphin3:latest` | 擅长指令遵循，生成多样化攻击 |
| **SUT (被测系统)** | `deepseek-r1:7b` | 论文测试目标，7B 平衡性能 |
| **Judge** | `deepseek-r1:7b` | 需要强推理能力判断安全性 |
| **Fitness** | `qwen2.5:7b` (可选) | 如果 DeepSeek 太慢可替换 |

---

## 🔍 验证配置正确性

运行以下命令检查所有配置：
```bash
cd /Users/panjiaying/Documents/Projects/STELLAR

# 检查环境变量
cat .env

# 检查 LLMType 定义
grep -A 5 "class LLMType" llm/llms.py

# 检查 LOCAL_MODELS
grep -A 10 "LOCAL_MODELS" llm/llms.py

# 测试 Ollama 调用
python llm/call_ollama.py
```

---

## 📚 下一步

1. ✅ 确认 Ollama 服务运行
2. ✅ 验证模型已下载
3. ✅ 运行 `./run_safety_local.sh`
4. 📊 监控 `results/` 目录输出
5. 🐛 如有报错，参考上方常见问题排查

如果遇到其他问题，检查 `log.txt` 文件获取详细错误信息。
