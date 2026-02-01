#!/bin/bash
# 一键运行快速测试（10分钟）
# 验证配置是否正常工作

cd /Users/panjiaying/Documents/Projects/STELLAR

echo "🧪 运行快速测试（10分钟）..."
echo "================================"

python run_tests_safety.py \
    --sut "dolphin3" \
    --judge "qwen2.5:7b" \
    --fitness "qwen2.5:7b" \
    --generator "dolphin3" \
    --population_size 100 \
    --algorithm rs \
    --max_time "00:10:00" \
    --seed 1 \
    --no_wandb

echo ""
echo "✅ 测试完成！"
echo "查看结果："
echo "  tail results/*/failures_over_time.csv"
