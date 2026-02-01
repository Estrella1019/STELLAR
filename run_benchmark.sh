# ================= 配置区域 =================
DATE_TAG=$(date +%d-%m-%Y)
RESULTS_DIR="./results/$DATE_TAG"

# 1. 攻击者 (Generator): 负责生成红队提示词
# 使用你刚才专门下载的 dolphin3 (去掉 :latest)
GENERATOR="dolphin3" 

# 2. 被测模型 (SUT): 也就是我们要攻击的对象
# 使用你 Ollama 列表里的 DeepSeek
SUT="deepseek-r1:7b"

# 3. 裁判与打分 (Fitness & Judge): 负责判断攻击是否成功
# [关键修改] 原来是 gpt-4o-mini，现在改成你也拥有的 mistral
# Mistral 7B 逻辑清晰，非常适合做裁判
FITNESS="mistral"
JUDGE="mistral"

# 4. 实验限制
MAX_TIME="00:10:00"

# 创建结果目录
mkdir -p $RESULTS_DIR

echo "========================================"
echo "🚀 开始运行 Benchmark 对比实验"
echo "📅 日期: $DATE_TAG"
echo "🤖 Generator: $GENERATOR | SUT: $SUT"
echo "⏱️ 单个实验限时: $MAX_TIME"
echo "========================================"

# ----------------------------------------
# 实验 1: RANDOM (随机搜索基准)
# ----------------------------------------
echo "\n[1/3] Running RANDOM Search (RS)..."
python run_tests_safety.py \
    --population_size 100 \
    --n_generations 1 \
    --algorithm rs \
    --max_time "$MAX_TIME" \
    --results_folder "$RESULTS_DIR/random" \
    --features_config "configs/safety_features.json" \
    --seed 1 \
    --sut "$SUT" \
    --generator "$GENERATOR" \
    --fitness "$FITNESS" \
    --judge "$JUDGE"
    # 注意：移除了 --no_wandb 以确保上传数据

# ----------------------------------------
# 实验 2: T-wise (Grid Search)
# ----------------------------------------
echo "\n[2/3] Running T-wise Sampling (GS)..."
python run_tests_safety.py \
    --population_size 100 \
    --n_generations 1 \
    --algorithm gs \
    --max_time "$MAX_TIME" \
    --results_folder "$RESULTS_DIR/twise" \
    --features_config "configs/safety_features.json" \
    --seed 1 \
    --sut "$SUT" \
    --generator "$GENERATOR" \
    --fitness "$FITNESS" \
    --judge "$JUDGE"

# ----------------------------------------
# 实验 3: STELLAR (NSGA-II + Repair)
# ----------------------------------------
echo "\n[3/3] Running STELLAR (NSGA2 + Repair)..."
python run_tests_safety.py \
    --population_size 20 \
    --n_generations 10 \
    --algorithm nsga2 \
    --max_time "$MAX_TIME" \
    --results_folder "$RESULTS_DIR/stellar" \
    --features_config "configs/safety_features.json" \
    --seed 1 \
    --use_repair \
    --sut "$SUT" \
    --generator "$GENERATOR" \
    --fitness "$FITNESS" \
    --judge "$JUDGE"

echo "\n✅ 所有实验已完成！请前往 WandB 查看对比图表。"