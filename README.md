# 生产规划与人员培训优化问题

本项目旨在解决一个复杂的多周期生产规划与人员培训问题。通过构建一个混合整数线性规划 (MILP) 模型，并使用 COPT 求解器，来找到在满足一系列约束条件下总成本最低的生产与培训方案。

## 项目结构与文件说明

```
.
├── output/                     # 输出目录，存放所有生成的结果文件
│   ├── detailed_results.json   # 详细的周度结果（JSON格式）
│   ├── production_planning.lp  # COPT生成的LP模型文件
│   ├── production_planning.sol # COPT生成的最优解文件
│   └── weekly_results.csv      # 简化的周度结果（CSV格式）
├── problem.md                  # 详细的问题描述、数学建模和假设
├── raw_problem.md              # 原始问题的简要描述
├── README.md                   # 本文件
├── result.txt                  # 最优目标函数值（总成本）
├── solve_production_planning.py # 核心求解脚本
├── validate_solution.py        # 解决方案验证脚本
└── verification_checklist.md   # 模型验证清单
```

### 文件说明

- **`raw_problem.md`**: 原始问题的简要描述(包含中文翻译版本)

- **`problem.md`**: 详细描述了问题的背景、核心假设、数学公式（包括变量、目标函数和约束条件）以及所有相关数据。这是理解本项目的起点。

- **`solve_production_planning.py`**: 这是项目的核心脚本。它使用 `coptpy` 库来：
    1.  定义所有参数和变量。
    2.  构建 `problem.md` 中描述的 MILP 模型。
    3.  调用 COPT 求解器来找到最优解。
    4.  将结果输出到 `output` 目录下的多个文件中，包括 `.lp`、`.sol`、`.json` 和 `.csv` 文件，并将最终的总成本写入 `result.txt`。

- **`validate_solution.py`**: 用于验证 `solve_production_planning.py` 生成的解是否有效。它会读取 `output/detailed_results.json` 文件，并逐一检查是否满足所有在 `problem.md` 中定义的约束条件，如劳动力守恒、培训目标和生产能力等。

- **`output/`**: 此目录存放所有由 `solve_production_planning.py` 生成的输出文件。
    - `detailed_results.json`: 包含了每一周的详细决策变量值，如各类工人的数量、产量和积压量。
    - `weekly_results.csv`: `detailed_results.json` 的简化版，更便于在电子表格软件中查看。
    - `production_planning.lp`: 描述了优化问题的标准 LP 文件格式，可用于其他求解器。
    - `production_planning.sol`: 包含模型的最优解。

- **`result.txt`**: 一个简单的文本文件，记录了求解成功后的最低总成本。

## 环境配置

本项目依赖 COPT 求解器及其 Python 接口 `coptpy`。请确保您已正确安装和配置 COPT。

```bash
pip install uv
uv sync
```

## 运行与验证

### 步骤 1: 求解问题

运行核心求解脚本来解决生产规划问题。该脚本将执行优化计算，并生成所有结果文件。

```bash
uv run solve_production_planning.py
```

执行后，您可以查看 `output/` 目录下的结果文件，以及 `result.txt` 中的最终成本。

### 步骤 2: 验证解决方案

为了确保解的正确性，运行验证脚本。该脚本将检查解是否违反了任何约束。

```bash
uv run validate_solution.py
```

如果所有约束都得到满足，脚本将输出确认信息。

## 问题描述

该项目解决的是一个动态规划问题，目标是为一家工厂在8周内最小化总成本。工厂需要平衡生产两种产品的需求、管理现有熟练工（常规工作与加班）、并培训新工人以满足未来的劳动力需求。成本包括工人工资和因未能按时交货而产生的罚款。详细的数学模型请参见 `problem.md`。