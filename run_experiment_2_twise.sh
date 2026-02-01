#!/bin/bash
set -e

# 实验2: T-wise (组合测试)
# 对应论文中的基线方法

DATE=$(date +%d-%m-%Y)

echo "🔢 开始实验 2: T-wise (Grid Sampling)"
echo "================================"

python run_tests_safety.py \
    --sut "dolphin3" \
    --judge "qwen2.5:7b" \
    --fitness "qwen2.5:7b" \
    --generator "dolphin3" \
    --population_size 2000 \
    --n_generations 1 \
    --algorithm gs \
    --max_time "00:20:00" \
    --results_folder "./results/${DATE}/twise" \
    --features_config "configs/safety_features.json" \
    --seed 1

echo "✅ 实验 2 完成！结果保存在 results/${DATE}/twise/"
