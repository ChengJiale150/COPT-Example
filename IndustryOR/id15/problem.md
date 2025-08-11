A certain factory needs to use a special tool over $n$ planning stages. At stage $j$, $r_j$ specialized tools are needed. At the end of this stage, all tools used within this stage must be sent for repair before they can be reused. There are two repair methods: one is slow repair, which is cheaper (costs $b$ per tool) but takes longer ($p$ stages to return); the other is fast repair, which costs $c$ per tool $(c > b)$ and is faster, requiring only $q$ stages to return $(q < p)$. If the repaired tools cannot meet the needs, new ones must be purchased, with a cost of $a$ per new tool $(a > c)$. This special tool will no longer be used after $n$ stages. Determine an optimal plan for purchasing and repairing the tools to minimize the cost spent on tools during the planning period.\n\nn = 10 # number of stages\nr = [3, 5, 2, 4, 6, 5, 4, 3, 2, 1] # tool requirements per stage, indexing starts at 1\na = 10 # cost of buying a new tool\nb = 1 # cost of slow repair\nc = 3 # cost of fast repair\np = 3 # slow repair duration\nq = 1 # fast repair duration

好的，遵照您的指示，这是基于自我反思与修改规划后，生成的最终版数学建模指南。

# 问题

## 问题描述
某工厂在一个包含 $n$ 个阶段的规划期内需要使用一种特殊工具。在第 $j$ 阶段，需要 $r_j$ 个该种工具。在每个阶段结束后，所有在该阶段内使用过的工具都必须送去维修才能再次使用。维修方式有两种：慢速维修，成本为每个 $b$，耗时 $p$ 个阶段；快速维修，成本为每个 $c$（$c>b$），耗时 $q$ 个阶段（$q<p$）。如果维修返回的工具无法满足需求，则必须购买新工具，单价为 $a$（$a>c$）。该工具在 $n$ 个阶段后不再使用。问题要求制定一个最优的工具采购与维修计划，以最小化整个规划期内花费在工具上的总成本。

## 问题分析
这是一个典型的**多阶段库存管理**与**动态规划**问题。其核心是在一个有限的时间跨度内，通过一系列决策（采购、快修、慢修）来满足每个阶段的动态需求，同时最小化总成本。

该问题可以被精确地构建为一个**整数线性规划 (Integer Linear Programming, ILP)** 模型。我们采用**工具流守恒 (Tool Flow Conservation)** 的思想进行建模，即在每个阶段，确保可用的工具流入量（新购+返修）恰好等于该阶段的需求量（即流出量）。这种方法通过平衡流量来满足需求，比直接追踪系统中每个工具的状态更为简洁高效。

## 核心假设
1.  **初始状态:** 在第1阶段开始之前，工厂没有任何可用的工具库存。
    *   **对模型的影响:** 这意味着在规划初期，工具的供应完全依赖于新购。在数学上，这通过设定在早期阶段（如 $j-p \le 0$）返修量为零来实现。
2.  **即时决策与交付:** 在每个阶段开始时做出的采购决策，其购买的工具可以立即用于该阶段。
    *   **对模型的影响:** 这使得在阶段 $j$ 购买的工具 $x_j$ 可以直接计入该阶段的供应。
3.  **强制维修:** 在一个阶段使用过的所有工具（数量为 $r_j$）必须在该阶段结束时全部送去维修，不能留存或闲置。
    *   **对模型的影响:** 这是模型的一个核心约束，直接体现为“送去快修和慢修的工具总数等于当期使用量”。
4.  **维修周期确定:** 送去维修的工具，其返回时间是固定的。在第 $j$ 阶段末送去慢修/快修的工具，将在第 $j+p$ / $j+q$ 阶段初变为可用状态。
    *   **对模型的影响:** 这决定了供需平衡约束中返修工具的时间下标关系。
5.  **生命周期结束:** 在第 $n$ 阶段结束后，工具的生命周期结束，其残值为零。
    *   **对模型的影响:** 目标函数只计算规划期内的成本，不考虑期末工具的任何剩余价值。这可能导致在期末做出仅为满足“强制维修”规则的最低成本决策。

## 数据定义
此问题中的数据主要包括规划期信息、各阶段需求以及成本和时间参数。

*   **集合 (Sets)**
    *   $J$: 所有规划阶段的集合, $J = \{1, 2, \dots, n\}$。

*   **参数 (Parameters)**
    *   $n$: 总规划阶段数。
    *   $r_j$: 阶段 $j$ 的工具需求量, $\forall j \in J$。
    *   $a$: 购买一个新工具的成本。
    *   $b$: 慢速维修一个工具的成本。
    *   $c$: 快速维修一个工具的成本。
    *   $p$: 慢速维修所需的时间（阶段数）。
    *   $q$: 快速维修所需的时间（阶段数）。

具体数值如下：
| 参数 | 描述 | 数值 |
| :--- | :--- | :--- |
| $n$ | 总阶段数 | 10 |
| $r_j$ | 各阶段需求 | $[3, 5, 2, 4, 6, 5, 4, 3, 2, 1]$ |
| $a$ | 新购成本 | 10 |
| $b$ | 慢修成本 | 1 |
| $c$ | 快修成本 | 3 |
| $p$ | 慢修周期 | 3 |
| $q$ | 快修周期 | 1 |

# 数学形式

## 变量定义
为了构建模型，我们定义以下三组决策变量，分别代表每个阶段的采购和维修决策：
*   $x_j$: 在阶段 $j$ 开始时新购买的工具数量, $\forall j \in J$。
*   $y_j$: 在阶段 $j$ 结束后送去**慢速维修**的工具数量, $\forall j \in J$。
*   $z_j$: 在阶段 $j$ 结束后送去**快速维修**的工具数量, $\forall j \in J$。

## 目标函数
我们的目标是最小化在整个规划期 $n$ 内的总成本，包括所有新购成本、慢速维修成本和快速维修成本。
*   **最小化总成本:**
    $\min \sum_{j=1}^{n} (a \cdot x_j + b \cdot y_j + c \cdot z_j)$

## 约束条件
模型必须满足以下三类约束条件，以确保其符合问题的物理和逻辑规则：

1.  **工具供应与需求平衡 (Tool Supply-Demand Balance):**
    *   **说明:** 在每个阶段 $j$，可用的工具总数必须恰好等于该阶段的需求 $r_j$。可用工具的来源包括三个部分：
        1.  $x_j$: 本阶段新购买的工具。
        2.  $y_{j-p}$: 在 $p$ 个阶段前（即第 $j-p$ 阶段末）送去慢修并于本阶段初返回的工具。
        3.  $z_{j-q}$: 在 $q$ 个阶段前（即第 $j-q$ 阶段末）送去快修并于本阶段初返回的工具。
        为了处理边界情况（即规划初期），我们定义当时间索引 $k \le 0$ 时，相应的维修返回量为0（即 $y_k=0, z_k=0$）。
    *   **公式:** $x_j + y_{j-p} + z_{j-q} = r_j, \quad \forall j \in J$
    *   **示例:** 以第 $j=4$ 阶段为例（$p=3, q=1$），该约束变为 $x_4 + y_{4-3} + z_{4-1} = r_4$，即 $x_4 + y_1 + z_3 = r_4$。这表示第4阶段的需求 $r_4$ 由该阶段新购的工具 $x_4$、第1阶段末送去慢修返回的工具 $y_1$、以及第3阶段末送去快修返回的工具 $z_3$ 共同满足。

2.  **工具维修分配 (Repair Allocation):**
    *   **说明:** 根据“强制维修”假设，在每个阶段 $j$ 结束时，所有在该阶段使用过的 $r_j$ 个工具都必须被分配去进行慢速或快速维修。
    *   **公式:** $y_j + z_j = r_j, \quad \forall j \in J$
    *   **模型洞察:** 此约束即使在规划期末（如第 $n$ 阶段）也必须满足。这意味着模型必须为在第 $n$ 阶段使用的 $r_n$ 个工具支付维修费，尽管它们无法在规划期内返回使用。此时，模型会选择成本更低的维修方式（通常是慢修）来满足此规则，这是完全符合逻辑的成本最小化行为。

3.  **变量非负与整数约束 (Non-negativity and Integer Constraint):**
    *   **说明:** 所有决策变量（购买或维修的工具数量）都必须是非负整数。
    *   **公式:** $x_j, y_j, z_j \in \mathbb{Z}_{\ge 0}, \quad \forall j \in J$