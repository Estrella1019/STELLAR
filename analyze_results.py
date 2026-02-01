#!/usr/bin/env python3
"""
分析实验结果并生成对比图表
用于 WandB 和本地可视化
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
import sys
from datetime import datetime

# 设置中文字体（macOS）
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

def find_latest_results():
    """查找最新的实验结果目录"""
    results_dir = Path("results")
    if not results_dir.exists():
        print("❌ results 目录不存在")
        return None

    # 查找包含日期的子目录
    date_dirs = [d for d in results_dir.iterdir() if d.is_dir()]
    if not date_dirs:
        print("❌ 没有找到实验结果")
        return None

    # 返回最新的日期目录
    latest = max(date_dirs, key=lambda x: x.stat().st_mtime)
    print(f"📁 使用结果目录: {latest}")
    return latest

def load_experiment_data(exp_dir):
    """加载单个实验的数据"""
    failures_file = exp_dir / "failures_over_time.csv"
    archive_file = exp_dir / "archive.csv"

    data = {
        "name": exp_dir.name,
        "failures": None,
        "archive": None,
        "total_failures": 0,
        "total_tests": 0,
        "failure_rate": 0.0
    }

    if failures_file.exists():
        try:
            df = pd.read_csv(failures_file)
            data["failures"] = df
            # 获取最后一行的统计
            if len(df) > 0:
                data["total_failures"] = df.iloc[-1].get("failures", 0)
        except Exception as e:
            print(f"  ⚠️  读取 failures_over_time.csv 失败: {e}")

    if archive_file.exists():
        try:
            df = pd.read_csv(archive_file)
            data["archive"] = df
            data["total_tests"] = len(df)
            if data["total_tests"] > 0:
                data["failure_rate"] = data["total_failures"] / data["total_tests"]
        except Exception as e:
            print(f"  ⚠️  读取 archive.csv 失败: {e}")

    return data

def plot_comparison(random_data, twise_data, stellar_data, output_dir):
    """生成对比图表"""
    output_dir.mkdir(exist_ok=True, parents=True)

    # 图1: Failures Over Time (论文图2上)
    fig, ax = plt.subplots(figsize=(12, 6))

    experiments = [
        ("RANDOM", random_data, "blue"),
        ("T-wise", twise_data, "orange"),
        ("STELLAR", stellar_data, "green")
    ]

    for name, data, color in experiments:
        if data["failures"] is not None:
            df = data["failures"]
            # 假设有 time 和 failures 列
            if "failures" in df.columns:
                ax.plot(df.index, df["failures"], label=name, color=color, linewidth=2)

    ax.set_xlabel("测试执行数", fontsize=12)
    ax.set_ylabel("发现的失败数量", fontsize=12)
    ax.set_title("失败发现曲线对比 (Failures Over Time)", fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / "failures_over_time.png", dpi=300)
    print(f"  ✅ 生成图表: failures_over_time.png")
    plt.close()

    # 图2: 总失败数对比 (柱状图)
    fig, ax = plt.subplots(figsize=(10, 6))

    names = ["RANDOM", "T-wise", "STELLAR"]
    failures = [
        random_data["total_failures"],
        twise_data["total_failures"],
        stellar_data["total_failures"]
    ]
    colors = ["blue", "orange", "green"]

    bars = ax.bar(names, failures, color=colors, alpha=0.7, edgecolor='black')

    # 在柱子上显示数值
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax.set_ylabel("总失败数", fontsize=12)
    ax.set_title("三种方法的总失败发现量对比", fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / "total_failures.png", dpi=300)
    print(f"  ✅ 生成图表: total_failures.png")
    plt.close()

    # 图3: 失败率对比 (Failure Rate)
    fig, ax = plt.subplots(figsize=(10, 6))

    rates = [
        random_data["failure_rate"] * 100,
        twise_data["failure_rate"] * 100,
        stellar_data["failure_rate"] * 100
    ]

    bars = ax.bar(names, rates, color=colors, alpha=0.7, edgecolor='black')

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax.set_ylabel("失败率 (%)", fontsize=12)
    ax.set_title("三种方法的失败率对比", fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / "failure_rate.png", dpi=300)
    print(f"  ✅ 生成图表: failure_rate.png")
    plt.close()

def generate_report(random_data, twise_data, stellar_data, output_dir):
    """生成文本报告"""
    report = []
    report.append("=" * 60)
    report.append("STELLAR 实验结果报告")
    report.append("=" * 60)
    report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")

    experiments = [
        ("RANDOM Search", random_data),
        ("T-wise (Grid Sampling)", twise_data),
        ("STELLAR (NSGA-II)", stellar_data)
    ]

    for name, data in experiments:
        report.append(f"\n{name}:")
        report.append(f"  总测试数: {data['total_tests']}")
        report.append(f"  发现失败: {data['total_failures']}")
        report.append(f"  失败率: {data['failure_rate']*100:.2f}%")

    # 计算改进比例
    if random_data["total_failures"] > 0:
        improvement_vs_random = stellar_data["total_failures"] / random_data["total_failures"]
        report.append(f"\nSTELLAR vs RANDOM 改进: {improvement_vs_random:.2f}x")

    if twise_data["total_failures"] > 0:
        improvement_vs_twise = stellar_data["total_failures"] / twise_data["total_failures"]
        report.append(f"STELLAR vs T-wise 改进: {improvement_vs_twise:.2f}x")

    report.append("\n" + "=" * 60)

    report_text = "\n".join(report)
    print(report_text)

    # 保存报告
    with open(output_dir / "report.txt", "w", encoding="utf-8") as f:
        f.write(report_text)

    return report_text

def main():
    print("📊 分析实验结果")
    print("=" * 60)

    # 查找结果目录
    date_dir = find_latest_results()
    if not date_dir:
        sys.exit(1)

    # 查找三个实验目录
    random_dir = date_dir / "random"
    twise_dir = date_dir / "twise"
    stellar_dir = date_dir / "stellar"

    missing = []
    if not random_dir.exists():
        missing.append("random")
    if not twise_dir.exists():
        missing.append("twise")
    if not stellar_dir.exists():
        missing.append("stellar")

    if missing:
        print(f"❌ 缺少实验结果: {', '.join(missing)}")
        print("请先运行对应的实验脚本")
        sys.exit(1)

    # 加载数据
    print("\n📂 加载实验数据...")
    random_data = load_experiment_data(random_dir)
    print(f"  ✅ RANDOM: {random_data['total_failures']} failures")

    twise_data = load_experiment_data(twise_dir)
    print(f"  ✅ T-wise: {twise_data['total_failures']} failures")

    stellar_data = load_experiment_data(stellar_dir)
    print(f"  ✅ STELLAR: {stellar_data['total_failures']} failures")

    # 生成图表
    print("\n📈 生成对比图表...")
    output_dir = date_dir / "analysis"
    plot_comparison(random_data, twise_data, stellar_data, output_dir)

    # 生成报告
    print("\n📄 生成实验报告...")
    generate_report(random_data, twise_data, stellar_data, output_dir)

    print(f"\n✅ 分析完成！结果保存在: {output_dir}")
    print(f"\n查看图表:")
    print(f"  - failures_over_time.png")
    print(f"  - total_failures.png")
    print(f"  - failure_rate.png")
    print(f"  - report.txt")

if __name__ == "__main__":
    main()
