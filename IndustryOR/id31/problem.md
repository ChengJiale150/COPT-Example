A factory produces three types of products: I, II, and III. Each product must undergo two processing stages, A and B. The factory has two types of equipment to complete stage A (A1, A2) and three types of equipment to complete stage B (B1, B2, B3).

The production rules are as follows:
- Product I can be processed on any type of A equipment (A1 or A2) and any type of B equipment (B1, B2, or B3).
- Product II can be processed on any type of A equipment (A1 or A2), but for stage B, it can only be processed on B1 equipment.
- Product III can only be processed on A2 equipment for stage A and B2 equipment for stage B.

The detailed data for processing time per piece, costs, sales price, and machine availability is provided in the table below. The objective is to determine the optimal production plan to maximize the factory's total profit.

Data Table
| Equipment | Product I | Product II | Product III | Effective Machine Hours | Processing Cost per Machine Hour (Yuan/hour) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| A1 | 5 | 10 | - | 6000 | 0.05 |
| A2 | 7 | 9 | 12 | 10000 | 0.03 |
| B1 | 6 | 8 | - | 4000 | 0.06 |
| B2 | 4 | - | 11 | 7000 | 0.11 |
| B3 | 7 | - | - | 4000 | 0.05 |
| Raw Material Cost (Yuan/piece) | 0.25 | 0.35 | 0.5 | - | - |
| Unit Price (Yuan/piece) | 1.25 | 2 | 2.8 | - | - |


# 问题

## 问题描述
一家工厂生产三种产品（I, II, III），每种产品需经过A、B两个加工阶段。工厂拥有两类A阶段设备（A1, A2）和三类B阶段设备（B1, B2, B3）。不同产品在不同设备上的加工路径受到限制，具体规则如下：
*   产品I：可在任意A类设备（A1或A2）和任意B类设备（B1, B2或B3）上加工。
*   产品II：可在任意A类设备（A1或A2）上加工，但B阶段仅可在B1设备上加工。
*   产品III：A阶段仅可在A2设备上加工，B阶段仅可在B2设备上加工。

问题提供了各产品在各设备上的单位加工时间、设备小时成本、设备可用总工时、产品单位原料成本及销售单价。目标是制定一个生产计划，以确定各种产品的生产数量，从而最大化工厂的总利润。

## 问题分析
这是一个典型的**线性规划 (Linear Programming, LP)** 问题。其核心是在满足多种资源（各类型设备的可用工时）和复杂工艺路径约束的条件下，通过决策不同产品在不同工艺路线上的生产数量，来优化一个线性的目标函数（总利润）。如果要求产品数量必须为整数，则该问题将转变为一个**整数线性规划 (Integer Linear Programming, ILP)** 问题。

本模型采用**基于路径的变量**，即每个决策变量代表一条从始至终的完整生产路径的产量。这种定义方式天然地保证了对于每一单位产品，其在A阶段的加工与B阶段的加工是成对出现的，因此无需额外设立**流守恒约束**，从而简化了模型结构。

## 核心假设
1.  **连续生产**: 产品的生产数量可以是小数（非整数），即允许生产半成品或将产品数量视为一个时期内的平均生产率。
2.  **确定性环境**: 所有参数，如加工时间、成本、售价和设备可用工时，都是已知且恒定的。
3.  **市场需求无限**: 假设所有生产出的产品都能以固定价格售出，不考虑市场容量或价格随销量变化的弹性。
4.  **资源线性消耗**: 资源的消耗（如机器工时）与产品产量成正比，不存在因生产规模变化导致的效率增减。
5.  **忽略设备转换成本与时间**: 假设在同一台设备上切换生产不同产品时，不存在任何准备、清洁或调试所需的时间和成本。

## 数据定义
为了构建模型，我们将问题中的信息系统化地定义为集合与参数。

*   **集合 (Sets)**
    *   $P$: 所有产品的集合, $P = \{I, II, III\}$。
    *   $M_A$: A阶段设备的集合, $M_A = \{A1, A2\}$。
    *   $M_B$: B阶段设备的集合, $M_B = \{B1, B2, B3\}$。
    *   $M$: 所有设备的集合, $M = M_A \cup M_B$。
    *   $R_{valid}$: 所有**可行工艺路径** $(p, a, b)$ 的三元组集合，其中 $p \in P, a \in M_A, b \in M_B$。根据问题描述：
        *   $R_{valid} = \{$
            $(I, A1, B1), (I, A1, B2), (I, A1, B3),$
            $(I, A2, B1), (I, A2, B2), (I, A2, B3),$
            $(II, A1, B1), (II, A2, B1),$
            $(III, A2, B2)$
        $\}$

*   **参数 (Parameters)**
    *   $S_p$: 产品 $p$ 的单位销售价格 (元/件)。
    *   $C_p^{raw}$: 产品 $p$ 的单位原材料成本 (元/件)。
    *   $T_{p,m}$: 产品 $p$ 在设备 $m$ 上的单位加工时间 (小时/件)。
    *   $H_m$: 设备 $m$ 在计划期内的总可用有效工时 (小时)。
    *   $C_m^{proc}$: 设备 $m$ 的单位小时加工成本 (元/小时)。

# 数学形式

## 变量定义
*   **决策变量**
    *   $x_{p,a,b}$: 决策变量，表示通过可行工艺路径 $(p, a, b) \in R_{valid}$ 生产的产品数量 (单位: 件)。

*   **聚合指标定义 (用于结果分析)**
    *   $X_p$: 产品 $p$ 的总生产数量。
        *   $X_p = \sum_{(p',a,b) \in R_{valid} \text{ s.t. } p'=p} x_{p,a,b}, \quad \forall p \in P$

## 目标函数
目标是最大化总利润。总利润 = 总销售收入 - 总原材料成本 - 总加工成本。

*   **单位路径利润 ($\pi_{p,a,b}$):**
    *   **说明:** 在路径 $(p, a, b)$ 上生产一件产品所能获得的利润。
    *   **公式:** $\pi_{p,a,b} = S_p - C_p^{raw} - (T_{p,a} \cdot C_a^{proc} + T_{p,b} \cdot C_b^{proc}), \quad \forall (p,a,b) \in R_{valid}$

*   **最大化总利润:**
    *   **说明:** 将所有可行路径上生产的产品的利润加总，得到总利润，并将其最大化。
    *   **公式:** $\max \sum_{(p,a,b) \in R_{valid}} \pi_{p,a,b} \cdot x_{p,a,b}$

## 约束条件
模型必须满足设备可用工时的限制。

1.  **A阶段设备工时约束 (Stage A Machine Capacity):**
    *   **说明:** 对于每一台A阶段设备，其被所有产品占用的总加工时间不能超过该设备的可用总工时。
    *   **公式:** $\sum_{(p,a',b) \in R_{valid} \text{ s.t. } a'=a} T_{p,a} \cdot x_{p,a,b} \le H_a, \quad \forall a \in M_A$

2.  **B阶段设备工时约束 (Stage B Machine Capacity):**
    *   **说明:** 对于每一台B阶段设备，其被所有产品占用的总加工时间不能超过该设备的可用总工时。
    *   **公式:** $\sum_{(p,a,b') \in R_{valid} \text{ s.t. } b'=b} T_{p,b} \cdot x_{p,a,b} \le H_b, \quad \forall b \in M_B$

3.  **变量非负约束 (Non-negativity Constraint):**
    *   **说明:** 所有路径的生产数量都不能是负数。
    *   **公式:** $x_{p,a,b} \ge 0, \quad \forall (p,a,b) \in R_{valid}$

4.  **整数约束 (Integer Constraint):**
    *   **说明:** 产品必须以完整单位生产，则决策变量必须为整数。
    *   **公式:** $x_{p,a,b} \in \mathbb{Z}^+, \quad \forall (p,a,b) \in R_{valid}$