#!/bin/bash
#  修复版实验配置
# 使用 dolphin3 作为 SUT（更容易被攻击）
# 使用 qwen2.5 作为 Judge（更稳定）

set -e

DATE=$(date +%d-%m-%Y)

echo "🚀 实验 1: RANDOM Search (修复版)"
echo "================================"
echo "SUT: dolphin3 (被测系统)"
echo "Judge: qwen2.5 (评判)"
echo "Generator: dolphin3 (生成器)"
echo ""

python run_tests_safety.py \
    --sut "dolphin3" \
    --judge "qwen2.5:7b" \
    --fitness "qwen2.5:7b" \
    --generator "dolphin3" \
    --population_size 2000 \
    --n_generations 1 \
    --algorithm rs \
    --max_time "02:00:00" \
    --results_folder "./results/${DATE}/random" \
    --features_config "configs/safety_features.json" \
    --seed 1 \
    --no_wandb

echo "✅ 实验 1 完成！"
