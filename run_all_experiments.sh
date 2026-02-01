#!/bin/bash
# 一键运行所有三组实验
# 会按顺序运行 RANDOM -> T-wise -> STELLAR

set -e

DATE=$(date +%d-%m-%Y)

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║       STELLAR 完整实验流程 (论文复现)                         ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📅 实验日期: ${DATE}"
echo "📊 将运行 3 组实验: RANDOM, T-wise, STELLAR"
echo "⏱️  预计总时长: 6 小时 (每个实验 2 小时)"
echo ""

# 询问确认
read -p "是否继续？(y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 已取消"
    exit 1
fi

# 清理旧数据（可选）
read -p "是否清理旧实验数据？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  清理旧数据..."
    rm -rf results/* wandb/*
    echo "✅ 清理完成"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "实验 1/3: RANDOM Search"
echo "════════════════════════════════════════════════════════════════"
./run_experiment_1_random.sh

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "实验 2/3: T-wise (Grid Sampling)"
echo "════════════════════════════════════════════════════════════════"
./run_experiment_2_twise.sh

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "实验 3/3: STELLAR (NSGA-II)"
echo "════════════════════════════════════════════════════════════════"
./run_experiment_3_stellar.sh

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    🎉 所有实验完成！                           ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 开始分析结果..."
python analyze_results.py

echo ""
echo "✅ 完整实验流程结束"
echo "📁 结果位置: results/${DATE}/"
echo "📈 图表位置: results/${DATE}/analysis/"
echo "🌐 WandB: https://wandb.ai (查看项目: stellar-reproduction)"
