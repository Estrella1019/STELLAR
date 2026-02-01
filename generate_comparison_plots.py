#!/usr/bin/env python3
"""
生成 STELLAR 论文风格的对比图表
包含 TSR (Test Success Rate), Time, Critical Ratio 等关键指标
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import json
from datetime import datetime

# 设置中文字体和样式
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300
sns.set_style("whitegrid")
sns.set_palette("husl")

class ExperimentAnalyzer:
    """实验结果分析器"""

    def __init__(self, results_base_path="results"):
        self.results_base = Path(results_base_path)
        self.experiments = {
            "RANDOM": None,
            "T-wise": None,
            "STELLAR": None
        }

    def find_latest_results(self):
        """查找最新的实验结果"""
        print("📁 搜索实验结果...")

        # 查找所有结果目录
        all_dirs = list(self.results_base.glob("**/summary_results.csv"))

        if not all_dirs:
            print("❌ 未找到任何实验结果")
            return False

        # 按实验类型分组 - 使用完整路径判断
        for result_file in all_dirs:
            result_dir = result_file.parent
            full_path = str(result_dir)

            # 判断实验类型 - 优先检查父目录名
            exp_type = None

            # 检查路径中是否包含 random/twise/stellar 文件夹
            if "/random/" in full_path:
                exp_type = "RANDOM"
            elif "/twise/" in full_path:
                exp_type = "T-wise"
            elif "/stellar/" in full_path:
                exp_type = "STELLAR"
            # 如果路径中没有明确文件夹，检查算法类型
            elif "NSGA" in full_path or "nsga" in full_path.lower():
                exp_type = "STELLAR"
            elif "GS" in full_path or "_gs_" in full_path.lower():
                exp_type = "T-wise"
            elif "RS" in full_path or "_rs_" in full_path.lower():
                # 确保不是 NSGA-II 的 RS 子文件夹
                if "NSGA" not in full_path and "nsga" not in full_path.lower():
                    exp_type = "RANDOM"

            if exp_type is None:
                continue

            # 保存最新的结果（如果已有结果，比较时间戳选择最新的）
            if self.experiments[exp_type] is None:
                self.experiments[exp_type] = result_dir
                print(f"  ✅ 找到 {exp_type}: {result_dir.relative_to(self.results_base)}")
            else:
                # 比较时间戳，选择最新的
                current_time = result_dir.name  # 使用目录名作为时间戳
                existing_time = self.experiments[exp_type].name
                if current_time > existing_time:
                    self.experiments[exp_type] = result_dir
                    print(f"  ✅ 更新 {exp_type}: {result_dir.relative_to(self.results_base)}")

        return any(v is not None for v in self.experiments.values())

    def load_experiment_data(self, exp_type):
        """加载单个实验的数据"""
        result_dir = self.experiments[exp_type]
        if result_dir is None:
            return None

        data = {
            "type": exp_type,
            "dir": result_dir,
            "summary": None,
            "failures": None,
            "metrics": {}
        }

        # 读取 summary_results.csv
        summary_file = result_dir / "summary_results.csv"
        if summary_file.exists():
            data["summary"] = pd.read_csv(summary_file)

        # 读取 failures_over_time.csv
        failures_file = result_dir / "failures_over_time.csv"
        if failures_file.exists():
            data["failures"] = pd.read_csv(failures_file)

        # 读取 calculation_properties.csv
        calc_file = result_dir / "calculation_properties.csv"
        if calc_file.exists():
            calc_df = pd.read_csv(calc_file)
            for _, row in calc_df.iterrows():
                data["metrics"][row.iloc[0]] = row.iloc[1]

        # 计算关键指标
        self._calculate_metrics(data)

        return data

    def _calculate_metrics(self, data):
        """计算关键指标"""
        metrics = data["metrics"]
        summary = data["summary"]
        failures = data["failures"]

        # TSR (Test Success Rate) = 失败测试数 / 总测试数
        if failures is not None and len(failures) > 0:
            total_failures = failures["FailuresFound"].iloc[-1]
            metrics["total_failures"] = int(total_failures)

            # 首个失败发现时间
            first_failure_idx = failures[failures["FailuresFound"] > 0].index[0] if any(failures["FailuresFound"] > 0) else -1
            if first_failure_idx >= 0:
                metrics["first_failure_time"] = float(failures.loc[first_failure_idx, "Time_s"])
            else:
                metrics["first_failure_time"] = 0
        else:
            metrics["total_failures"] = 0
            metrics["first_failure_time"] = 0

        # 从 summary 中提取
        if summary is not None and len(summary) > 0:
            last_row = summary.iloc[-1]

            # 总测试数
            if "n_evaluations" in summary.columns:
                metrics["total_tests"] = int(last_row["n_evaluations"])
            elif "evaluated_individuals" in summary.columns:
                metrics["total_tests"] = int(last_row["evaluated_individuals"])
            else:
                metrics["total_tests"] = 100  # 默认值

            # 执行时间
            if "exec_time" in summary.columns:
                metrics["execution_time"] = float(last_row["exec_time"])
            else:
                metrics["execution_time"] = 0

            # 去重后的失败数
            if "Number Critical Scenarios (duplicate free)" in summary.columns:
                metrics["unique_failures"] = int(last_row["Number Critical Scenarios (duplicate free)"])
            else:
                metrics["unique_failures"] = metrics["total_failures"]

            # 平均适应度和最佳适应度
            if "avg_fitness" in summary.columns:
                metrics["avg_fitness"] = float(last_row["avg_fitness"])
            else:
                metrics["avg_fitness"] = 0

            if "best_fitness" in summary.columns:
                metrics["best_fitness"] = float(last_row["best_fitness"])
            else:
                metrics["best_fitness"] = 0

        # 计算 TSR (Critical Ratio)
        if metrics["total_tests"] > 0:
            metrics["tsr"] = (metrics["total_failures"] / metrics["total_tests"]) * 100
        else:
            metrics["tsr"] = 0

        # 计算效率指标
        if metrics.get("execution_time", 0) > 0:
            metrics["failures_per_second"] = metrics["total_failures"] / metrics["execution_time"]
            metrics["failures_per_minute"] = metrics["total_failures"] / (metrics["execution_time"] / 60)
            metrics["tests_per_minute"] = metrics["total_tests"] / (metrics["execution_time"] / 60)
        else:
            metrics["failures_per_second"] = 0
            metrics["failures_per_minute"] = 0
            metrics["tests_per_minute"] = 0

        # 失败发现多样性 (去重率)
        if metrics["total_failures"] > 0:
            metrics["diversity_ratio"] = (metrics["unique_failures"] / metrics["total_failures"]) * 100
        else:
            metrics["diversity_ratio"] = 0

        # 失败发现成功率
        if metrics["total_tests"] > 0:
            metrics["failure_detection_rate"] = (metrics["total_failures"] / metrics["total_tests"]) * 100
        else:
            metrics["failure_detection_rate"] = 0

    def generate_comparison_plots(self, output_dir="comparison_results"):
        """生成对比图表"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)

        # 加载所有实验数据
        exp_data = {}
        for exp_type in ["RANDOM", "T-wise", "STELLAR"]:
            data = self.load_experiment_data(exp_type)
            if data:
                exp_data[exp_type] = data
                print(f"\n✅ {exp_type} 数据:")
                print(f"   总测试: {data['metrics']['total_tests']}")
                print(f"   失败数: {data['metrics']['total_failures']}")
                print(f"   去重失败: {data['metrics'].get('unique_failures', 'N/A')}")
                print(f"   TSR: {data['metrics']['tsr']:.2f}%")
                print(f"   时间: {data['metrics']['execution_time']:.1f}s ({data['metrics']['execution_time']/60:.1f}分钟)")
                print(f"   首次失败时间: {data['metrics'].get('first_failure_time', 'N/A'):.1f}s")
                print(f"   效率: {data['metrics']['failures_per_minute']:.2f} failures/min")
                print(f"   多样性: {data['metrics'].get('diversity_ratio', 'N/A'):.1f}%")

        if not exp_data:
            print("❌ 没有可用的实验数据")
            return

        # 生成各种图表
        self._plot_tsr_comparison(exp_data, output_path)
        self._plot_time_comparison(exp_data, output_path)
        self._plot_failures_over_time(exp_data, output_path)
        self._plot_efficiency(exp_data, output_path)
        self._plot_comprehensive_comparison(exp_data, output_path)

        # 生成报告
        self._generate_report(exp_data, output_path)

        print(f"\n✅ 所有图表已生成到: {output_path}")

    def _plot_tsr_comparison(self, exp_data, output_path):
        """图1: TSR (Test Success Rate / Critical Ratio) 对比"""
        fig, ax = plt.subplots(figsize=(10, 6))

        methods = list(exp_data.keys())
        tsrs = [exp_data[m]["metrics"]["tsr"] for m in methods]
        colors = ["#3498db", "#e74c3c", "#2ecc71"]

        bars = ax.bar(methods, tsrs, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontsize=14, fontweight='bold')

        ax.set_ylabel('TSR (Test Success Rate) %', fontsize=13, fontweight='bold')
        ax.set_title('Test Success Rate (TSR) Comparison\n攻击成功率对比',
                    fontsize=15, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_ylim(0, max(tsrs) * 1.2)

        plt.tight_layout()
        plt.savefig(output_path / "1_tsr_comparison.png", dpi=300, bbox_inches='tight')
        print(f"  ✅ TSR 对比图")
        plt.close()

    def _plot_time_comparison(self, exp_data, output_path):
        """图2: 执行时间对比"""
        fig, ax = plt.subplots(figsize=(10, 6))

        methods = list(exp_data.keys())
        times = [exp_data[m]["metrics"]["execution_time"] / 60 for m in methods]  # 转换为分钟
        colors = ["#3498db", "#e74c3c", "#2ecc71"]

        bars = ax.bar(methods, times, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}m',
                   ha='center', va='bottom', fontsize=14, fontweight='bold')

        ax.set_ylabel('Execution Time (minutes)', fontsize=13, fontweight='bold')
        ax.set_title('Execution Time Comparison\n执行时间对比',
                    fontsize=15, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        plt.tight_layout()
        plt.savefig(output_path / "2_time_comparison.png", dpi=300, bbox_inches='tight')
        print(f"  ✅ 时间对比图")
        plt.close()

    def _plot_failures_over_time(self, exp_data, output_path):
        """图3: 失败发现曲线（论文图2风格）"""
        fig, ax = plt.subplots(figsize=(12, 7))

        colors = {"RANDOM": "#3498db", "T-wise": "#e74c3c", "STELLAR": "#2ecc71"}
        markers = {"RANDOM": "o", "T-wise": "s", "STELLAR": "^"}

        for method, data in exp_data.items():
            if data["failures"] is not None:
                df = data["failures"]
                time_minutes = df["Time_s"] / 60
                failures = df["FailuresFound"]

                ax.plot(time_minutes, failures,
                       label=method,
                       color=colors[method],
                       marker=markers[method],
                       linewidth=2.5,
                       markersize=8,
                       alpha=0.9)

        ax.set_xlabel('Time (minutes)', fontsize=13, fontweight='bold')
        ax.set_ylabel('Number of Failures Found', fontsize=13, fontweight='bold')
        ax.set_title('Failures Discovered Over Time\n失败发现曲线 (论文图2风格)',
                    fontsize=15, fontweight='bold', pad=20)
        ax.legend(fontsize=12, framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')

        plt.tight_layout()
        plt.savefig(output_path / "3_failures_over_time.png", dpi=300, bbox_inches='tight')
        print(f"  ✅ 失败曲线图（论文风格）")
        plt.close()

    def _plot_efficiency(self, exp_data, output_path):
        """图4: 效率对比（失败数/分钟）"""
        fig, ax = plt.subplots(figsize=(10, 6))

        methods = list(exp_data.keys())
        efficiencies = []
        for m in methods:
            time_min = exp_data[m]["metrics"]["execution_time"] / 60
            failures = exp_data[m]["metrics"]["total_failures"]
            eff = failures / time_min if time_min > 0 else 0
            efficiencies.append(eff)

        colors = ["#3498db", "#e74c3c", "#2ecc71"]
        bars = ax.bar(methods, efficiencies, color=colors, alpha=0.8,
                     edgecolor='black', linewidth=1.5)

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}',
                   ha='center', va='bottom', fontsize=14, fontweight='bold')

        ax.set_ylabel('Failures per Minute', fontsize=13, fontweight='bold')
        ax.set_title('Efficiency Comparison\n效率对比 (失败数/分钟)',
                    fontsize=15, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        plt.tight_layout()
        plt.savefig(output_path / "4_efficiency_comparison.png", dpi=300, bbox_inches='tight')
        print(f"  ✅ 效率对比图")
        plt.close()

    def _plot_comprehensive_comparison(self, exp_data, output_path):
        """图5: 综合对比（多指标雷达图）"""
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

        # 准备数据
        categories = ['TSR\n(%)', 'Total\nFailures', 'Efficiency\n(F/min)',
                     'Speed\n(1/time)']
        N = len(categories)

        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]

        colors = {"RANDOM": "#3498db", "T-wise": "#e74c3c", "STELLAR": "#2ecc71"}

        for method, data in exp_data.items():
            metrics = data["metrics"]

            # 归一化数据到 0-100
            tsr_norm = metrics["tsr"]
            failures_norm = (metrics["total_failures"] / max(
                [d["metrics"]["total_failures"] for d in exp_data.values()])) * 100

            time_min = metrics["execution_time"] / 60
            efficiency_norm = ((metrics["total_failures"] / time_min) / max(
                [d["metrics"]["total_failures"] / (d["metrics"]["execution_time"] / 60)
                 for d in exp_data.values()])) * 100 if time_min > 0 else 0

            speed_norm = (1 / (metrics["execution_time"] / 60) / max(
                [1 / (d["metrics"]["execution_time"] / 60)
                 for d in exp_data.values()])) * 100 if time_min > 0 else 0

            values = [tsr_norm, failures_norm, efficiency_norm, speed_norm]
            values += values[:1]

            ax.plot(angles, values, 'o-', linewidth=2.5,
                   label=method, color=colors[method], markersize=8)
            ax.fill(angles, values, alpha=0.15, color=colors[method])

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=11, fontweight='bold')
        ax.set_ylim(0, 100)
        ax.set_title('Comprehensive Performance Comparison\n综合性能对比',
                    fontsize=15, fontweight='bold', pad=30)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path / "5_comprehensive_radar.png", dpi=300, bbox_inches='tight')
        print(f"  ✅ 综合对比雷达图")
        plt.close()

    def _generate_report(self, exp_data, output_path):
        """生成文本报告"""
        report = []
        report.append("=" * 120)
        report.append("STELLAR 实验对比报告 (Extended Metrics)")
        report.append("=" * 120)
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # 表格对比 - 扩展版
        report.append("📊 关键指标对比 (Key Metrics Comparison):")
        report.append("-" * 120)

        # 表头
        header = f"{'方法':<12} {'总测试':<10} {'失败数':<10} {'去重失败':<10} {'TSR(%)':<10} " \
                 f"{'时间(分)':<10} {'效率(F/m)':<12} {'测试/分':<10}"
        report.append(header)
        report.append("-" * 120)

        # 数据行
        for method, data in exp_data.items():
            m = data["metrics"]
            time_min = m["execution_time"] / 60 if m["execution_time"] > 0 else 0.01

            row = f"{method:<12} {m['total_tests']:<10} {m['total_failures']:<10} " \
                  f"{m.get('unique_failures', m['total_failures']):<10} {m['tsr']:<10.2f} " \
                  f"{time_min:<10.1f} {m['failures_per_minute']:<12.2f} " \
                  f"{m['tests_per_minute']:<10.1f}"
            report.append(row)

        report.append("-" * 120)
        report.append("")

        # 详细指标表格
        report.append("📈 详细性能指标 (Detailed Performance Metrics):")
        report.append("-" * 120)

        header2 = f"{'方法':<12} {'首次失败(s)':<15} {'多样性(%)':<12} {'检测率(%)':<12} " \
                  f"{'平均适应度':<15} {'最佳适应度':<15}"
        report.append(header2)
        report.append("-" * 120)

        for method, data in exp_data.items():
            m = data["metrics"]

            row = f"{method:<12} {m.get('first_failure_time', 0):<15.1f} " \
                  f"{m.get('diversity_ratio', 0):<12.1f} {m.get('failure_detection_rate', 0):<12.2f} " \
                  f"{m.get('avg_fitness', 0):<15.3f} {m.get('best_fitness', 0):<15.3f}"
            report.append(row)

        report.append("-" * 120)
        report.append("")

        # 改进倍数分析
        report.append("🎯 改进分析 (Improvement Analysis):")
        report.append("-" * 120)

        if "STELLAR" in exp_data and "RANDOM" in exp_data:
            stellar_failures = exp_data["STELLAR"]["metrics"]["total_failures"]
            random_failures = exp_data["RANDOM"]["metrics"]["total_failures"]
            stellar_tsr = exp_data["STELLAR"]["metrics"]["tsr"]
            random_tsr = exp_data["RANDOM"]["metrics"]["tsr"]

            if random_failures > 0:
                improvement_failures = stellar_failures / random_failures
                improvement_tsr = stellar_tsr / random_tsr if random_tsr > 0 else 0

                report.append(f"STELLAR vs RANDOM:")
                report.append(f"  - 失败数改进: {improvement_failures:.2f}x ({random_failures} → {stellar_failures})")
                report.append(f"  - TSR改进: {improvement_tsr:.2f}x ({random_tsr:.2f}% → {stellar_tsr:.2f}%)")

                # 首次失败时间对比
                stellar_first = exp_data["STELLAR"]["metrics"].get("first_failure_time", 0)
                random_first = exp_data["RANDOM"]["metrics"].get("first_failure_time", 0)
                if random_first > 0 and stellar_first > 0:
                    speedup = random_first / stellar_first
                    report.append(f"  - 首次发现加速: {speedup:.2f}x ({random_first:.1f}s → {stellar_first:.1f}s)")

            if "T-wise" in exp_data:
                twise_failures = exp_data["T-wise"]["metrics"]["total_failures"]
                twise_tsr = exp_data["T-wise"]["metrics"]["tsr"]

                if twise_failures > 0:
                    improvement_twise = stellar_failures / twise_failures
                    improvement_tsr_twise = stellar_tsr / twise_tsr if twise_tsr > 0 else 0

                    report.append(f"\nSTELLAR vs T-wise:")
                    report.append(f"  - 失败数改进: {improvement_twise:.2f}x ({twise_failures} → {stellar_failures})")
                    report.append(f"  - TSR改进: {improvement_tsr_twise:.2f}x ({twise_tsr:.2f}% → {stellar_tsr:.2f}%)")

        report.append("")
        report.append("=" * 120)

        # 指标说明
        report.append("\n📖 指标说明 (Metrics Description):")
        report.append("-" * 120)
        report.append("TSR (Test Success Rate): 攻击成功率，失败数占总测试数的百分比")
        report.append("去重失败: 去除重复后的独特失败场景数量")
        report.append("效率 (F/m): 每分钟发现的失败数，越高越好")
        report.append("测试/分: 每分钟执行的测试数量")
        report.append("首次失败: 发现第一个失败所需的时间(秒)，越小越好")
        report.append("多样性: 去重失败占总失败的比例，越高表示失败样本越多样化")
        report.append("检测率: 成功检测到失败的测试占比")
        report.append("=" * 120)

        report_text = "\n".join(report)
        print("\n" + report_text)

        with open(output_path / "comparison_report.txt", "w", encoding="utf-8") as f:
            f.write(report_text)

        print(f"  ✅ 对比报告")


if __name__ == "__main__":
    print("=" * 80)
    print("🎨 STELLAR 实验对比图表生成器")
    print("=" * 80)

    analyzer = ExperimentAnalyzer()

    if analyzer.find_latest_results():
        print("\n📊 生成对比图表...")
        analyzer.generate_comparison_plots()

        print("\n" + "=" * 80)
        print("✅ 完成！生成的图表:")
        print("   1. 1_tsr_comparison.png - TSR 对比")
        print("   2. 2_time_comparison.png - 时间对比")
        print("   3. 3_failures_over_time.png - 失败曲线（论文风格）")
        print("   4. 4_efficiency_comparison.png - 效率对比")
        print("   5. 5_comprehensive_radar.png - 综合雷达图")
        print("   6. comparison_report.txt - 文本报告")
        print("=" * 80)
    else:
        print("❌ 未找到实验结果")
        print("请先运行实验:")
        print("  ./run_all_experiments.sh")
