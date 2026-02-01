# 🎯 STELLAR 实验执行方案（终极版）

## 📋 **问题诊断结果**

✅ **已完成**：
- 清理旧数据
- 创建3组实验脚本
- 修复 Fitness 评估逻辑
- 修复 Critical 判定逻辑

❌ **发现的问题**：
- **DeepSeek-R1 作为 SUT 响应全是空的**
- 无法进行有效测试

---

## 🔧 **解决方案**

### 推荐配置：

| 角色 | 模型 | 原因 |
|------|------|------|
| SUT (被测) | **dolphin3** | 未审查模型，容易被攻击 ✅ |
| Judge | **qwen2.5:7b** | 稳定可靠的评判 ✅ |
| Generator | **dolphin3** | 擅长生成攻击 ✅ |

---

## 🚀 **立即执行（三个命令）**

### 步骤 1: 拉取 Qwen2.5（如果没有）

```bash
ollama pull qwen2.5:7b
```

### 步骤 2: 修改实验脚本

打开并编辑以下3个文件，修改模型参数：

**文件 1**: `run_experiment_1_random.sh`
```bash
# 找到并修改这几行:
--sut "dolphin3" \
--judge "qwen2.5:7b" \
--fitness "qwen2.5:7b" \
--generator "dolphin3" \
```

**文件 2**: `run_experiment_2_twise.sh`
```bash
# 同样修改:
--sut "dolphin3" \
--judge "qwen2.5:7b" \
--fitness "qwen2.5:7b" \
--generator "dolphin3" \
```

**文件 3**: `run_experiment_3_stellar.sh`
```bash
# 同样修改:
--sut "dolphin3" \
--judge "qwen2.5:7b" \
--fitness "qwen2.5:7b" \
--generator "dolphin3" \
```

### 步骤 3: 运行实验

```bash
cd /Users/panjiaying/Documents/Projects/STELLAR

# 方案 A: 一键运行所有实验（6小时）
./run_all_experiments.sh

# 方案 B: 先快速测试（10分钟）
python run_tests_safety.py \
    --sut "dolphin3" \
    --judge "qwen2.5:7b" \
    --fitness "qwen2.5:7b" \
    --generator "dolphin3" \
    --population_size 100 \
    --algorithm rs \
    --max_time "00:10:00" \
    --seed 1
```

---

## 📊 **预期结果**

使用 dolphin3 作为 SUT 后，应该看到：

### 失败数量
- RANDOM: **50-150** 个失败
- T-wise: **80-200** 个失败
- STELLAR: **150-400** 个失败（**2-3倍改进**）

### 失败率
- RANDOM: ~5-10%
- T-wise: ~8-12%
- STELLAR: **~15-25%** ✨

---

## 🔍 **验证配置正确**

运行快速测试后，检查：

```bash
# 查看失败数
tail results/*/failures_over_time.csv

# 应该看到类似：
# iteration,failures
# 0,0
# 10,5
# 20,12
# ...
# 100,35  ← 失败数应该 > 0
```

如果失败数 > 0，说明配置成功！

---

## 📁 **文件清单**

| 文件 | 用途 | 状态 |
|------|------|------|
| `run_experiment_1_random.sh` | RANDOM 实验 | ⚠️  需修改模型 |
| `run_experiment_2_twise.sh` | T-wise 实验 | ⚠️  需修改模型 |
| `run_experiment_3_stellar.sh` | STELLAR 实验 | ⚠️  需修改模型 |
| `run_all_experiments.sh` | 一键运行 | ✅ |
| `analyze_results.py` | 结果分析 | ✅ |
| `examples/safety/eval.py` | 评估逻辑 | ✅ 已修复 |

---

## 🎬 **完整命令速查**

```bash
# 1. 确保在项目目录
cd /Users/panjiaying/Documents/Projects/STELLAR

# 2. 拉取模型
ollama pull qwen2.5:7b

# 3. 编辑实验脚本（修改 --sut, --judge, --fitness）
nano run_experiment_1_random.sh
nano run_experiment_2_twise.sh
nano run_experiment_3_stellar.sh

# 4. 运行实验
./run_all_experiments.sh

# 5. 实时监控（新终端）
tail -f log.txt

# 6. 查看结果
cat results/$(date +%d-%m-%Y)/analysis/report.txt
open results/$(date +%d-%m-%Y)/analysis/failures_over_time.png
```

---

## ⚠️ **常见问题**

### Q: 还是 failure 为 0 怎么办？
A: 检查 dolphin3 模型是否正确运行：
```bash
ollama run dolphin3 "test"
```

### Q: WandB 要不要用？
A: 可选。如果不想用，在实验脚本中添加 `--no_wandb`

### Q: 实验太慢？
A: 减少时间和种群：
```bash
--max_time "01:00:00"
--population_size 1000
```

---

**准备好了吗？修改脚本并开始实验！** 🚀
