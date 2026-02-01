#!/bin/bash
set -e

# 实验1: RANDOM (随机搜索)
# 对应论文中的基线方法

DATE=$(date +%d-%m-%Y)

echo "🎲 开始实验 1: RANDOM Search"
echo "================================"

python run_tests_safety.py \
    --sut "dolphin3" \
    --judge "qwen2.5:7b" \
    --fitness "qwen2.5:7b" \
    --generator "dolphin3" \
    --population_size 2000 \
    --n_generations 1 \
    --algorithm rs \
    --max_time "00:20:00" \
    --results_folder "./results/${DATE}/random" \
    --features_config "configs/safety_features.json" \
    --seed 1

echo "✅ 实验 1 完成！结果保存在 results/${DATE}/random/"
