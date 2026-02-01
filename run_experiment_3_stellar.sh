#!/bin/bash
set -e

# 实验3: STELLAR (本文方法)
# 使用遗传算法优化测试生成

DATE=$(date +%d-%m-%Y)

echo "🌟 开始实验 3: STELLAR (NSGA-II)"
echo "================================"

python run_tests_safety.py \
    --sut "dolphin3" \
    --judge "qwen2.5:7b" \
    --fitness "qwen2.5:7b" \
    --generator "dolphin3" \
    --population_size 20 \
    --n_generations 100 \
    --algorithm nsga2 \
    --max_time "00:20:00" \
    --results_folder "./results/${DATE}/stellar" \
    --features_config "configs/safety_features.json" \
    --seed 1 \
    --use_repair

echo "✅ 实验 3 完成！结果保存在 results/${DATE}/stellar/"
