#!/bin/bash

# 确保脚本出错时停止
set -e

# [关键修改]
# 1. max_time 改为 2 小时 ("02:00:00")，防止本地推理太慢被腰斩
# 2. population_size 改为 20，避免第一代全军覆没
# 3. generator 改为 dolphin3:latest (或者是你实际 pull 的名字)
# 4. 增加了 --use_repair 参数，有助于生成更高质量的测试用例

echo "🚀 Starting STELLAR safety test with DeepSeek-R1..."

python run_tests_safety.py \
        --sut "deepseek-r1:7b" \
        --judge "deepseek-r1:7b" \
        --fitness "deepseek-r1:7b" \
        --generator "dolphin3" \
        --population_size 20 \
        --n_generations 10 \
        --algorithm "nsga2" \
        --max_time "02:00:00" \
        --features_config "configs/safety_features.json" \
        --use_repair \
        --seed 1