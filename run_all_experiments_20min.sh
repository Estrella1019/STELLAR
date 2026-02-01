#!/bin/bash
set -e

# ========================================
# STELLAR 三组实验 - 20分钟快速版本
# ========================================

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   🚀 STELLAR 三组实验 - 20分钟快速版本                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "实验配置:"
echo "  - 每个实验运行时间: 20分钟"
echo "  - 总预计时间: ~60分钟"
echo "  - SUT: dolphin3 (无审查模型)"
echo "  - Judge/Fitness: qwen2.5:7b (稳定评估)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 记录开始时间
START_TIME=$(date +%s)

# 实验1: RANDOM
echo ""
echo "🎲 [1/3] 开始实验: RANDOM Search (20分钟)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
./run_experiment_1_random.sh
echo "✅ RANDOM 完成！"

# 实验2: T-wise
echo ""
echo "🔢 [2/3] 开始实验: T-wise Grid Sampling (20分钟)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
./run_experiment_2_twise.sh
echo "✅ T-wise 完成！"

# 实验3: STELLAR
echo ""
echo "🌟 [3/3] 开始实验: STELLAR NSGA-II (20分钟)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
./run_experiment_3_stellar.sh
echo "✅ STELLAR 完成！"

# 生成对比图表
echo ""
echo "📊 生成对比图表..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python generate_comparison_plots.py

# 计算总用时
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   🎉 所有实验完成！                                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "⏱️  总用时: ${MINUTES}分${SECONDS}秒"
echo ""
echo "📁 结果位置:"
DATE=$(date +%d-%m-%Y)
echo "  - results/${DATE}/random/    (RANDOM 实验结果)"
echo "  - results/${DATE}/twise/     (T-wise 实验结果)"
echo "  - results/${DATE}/stellar/   (STELLAR 实验结果)"
echo "  - comparison_results/        (对比图表和报告)"
echo ""
echo "📊 生成的图表:"
echo "  1. 1_tsr_comparison.png      - TSR 攻击成功率对比"
echo "  2. 2_time_comparison.png     - 执行时间对比"
echo "  3. 3_failures_over_time.png  - 失败发现曲线"
echo "  4. 4_efficiency_comparison.png - 效率对比"
echo "  5. 5_comprehensive_radar.png - 综合性能雷达图"
echo "  6. comparison_report.txt     - 详细对比报告"
echo ""
echo "📈 查看报告:"
echo "  cat comparison_results/comparison_report.txt"
echo ""
echo "🖼️  查看图表:"
echo "  open comparison_results/*.png"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ 实验完成！现在可以查看对比结果了！"
