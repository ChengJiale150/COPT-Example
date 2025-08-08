A factory produces three types of products: I, II, and III. Each product needs to go through two processing procedures, A and B. The factory has two pieces of equipment that can complete process A, denoted as A1 and A2; it has three pieces of equipment that complete process B, denoted as B1, B2, and B3. Product I can be processed on any equipment for A and B; Product II can be processed on any A equipment but only on B1 for process B; Product III can only be processed on A2 and B2. Given the unit processing time on various machines, raw material costs, product sale prices, effective machine hours, and the costs of operating the machines at full capacity as shown in Table 1-4, the task is to arrange the optimal production plan to maximize the factory's profit.

Table 1-4
| Equipment | Product I | Product II | Product III | Effective Machine Hours | Operating Costs at Full Capacity (Yuan) |
|------------|-----------|------------|-------------|--------------------------|------------------------------------------|
| A1 | 5 | 10 | | 6000 | 300 |
| A2 | 7 | 9 | 12 | 10000 | 321 |
| B1 | 6 | 8 | | 4000 | 250 |
| B2 | 4 | | 11 | 7000 | 783 |
| B3 | 7 | | | 4000 | 200 |
| Raw Material Cost (Yuan/Unit) | 0.25 | 0.35 | 0.50 | | |
| Unit Price (Yuan/Unit) | 1.25 | 2.00 | 2.80 | | |


# 问题

## 问题描述
一家工厂生产 I、II、III 三种产品。每种产品均需经过 A、B 两道工序。工厂拥有可完成A工序的设备A1、A2两台，以及可完成B工序的设备B1、B2、B3三台。
不同产品对设备的使用存在限制：
*   产品I：可在任意A、B设备上加工。
*   产品II：可在任意A设备上加工，但B工序只能在设备B1上完成。
*   产品III：A工序只能在设备A2上完成，B工序只能在设备B2上完成。

给定各产品在不同设备上的单位加工时间、原材料成本、产品售价、设备有效工作台时以及设备满负荷运行成本，目标是制定一个最优的生产计划，以实现工厂利润的最大化。

## 问题分析
这是一个典型的**生产规划问题**，属于资源优化配置的范畴。由于决策变量中既包含连续的生产数量，又包含用于表示设备是否启用的0-1变量，因此该问题应被建模为**混合整数线性规划 (Mixed-Integer Linear Programming, MILP)**。

模型的目标是最大化总利润，总利润等于总销售收入减去总原材料成本和总设备运行成本。约束条件主要包括各台设备的有效工时限制，以及将生产活动与设备启用状态相关联的逻辑约束。

## 核心假设
1.  **生产数量连续性**: 产品的生产数量可以是任意非负实数。
2.  **设备运行成本**: 表中所给的“满负荷运行成本”被理解为一种**固定成本**。即，只要一台设备被用于生产（无论生产时间长短），该成本就会产生；若设备完全不使用，则不产生此项成本。此假设基于问题未提供单位时间可变运行成本的数据。
3.  **线性关系**: 产品的加工时间、成本和收入与生产数量成正比，不存在规模效应或因转换产品产生的额外设置时间。
4.  **市场与供应**: 假设工厂生产出的所有产品都能售出（市场需求无限），且所需原材料的供应也是无限的。
5.  **数据确定性**: 所有给定的参数（如加工时间、成本、价格、设备时长）都是确定且已知的。

## 数据定义
为了构建模型，我们将问题中的信息系统化地定义为集合与参数。

*   **集合 (Sets)**
    *   $P$: 所有产品的集合, $P = \{I, II, III\}$。
    *   $M_A$: A工序的设备集合, $M_A = \{A1, A2\}$。
    *   $M_B$: B工序的设备集合, $M_B = \{B1, B2, B3\}$。
    *   $M$: 所有设备的集合, $M = M_A \cup M_B$。
    *   $R$: 所有**有效生产路径**的集合，每个元素是一个三元组 $(p, a, b)$，表示产品 $p$ 可以通过设备 $a$ 和设备 $b$ 的组合进行生产。根据问题描述，该集合包含以下9个元素：
        $R = \{ (I, A1, B1), (I, A1, B2), (I, A1, B3),$
        $(I, A2, B1), (I, A2, B2), (I, A2, B3),$
        $(II, A1, B1), (II, A2, B1),$
        $(III, A2, B2) \}$

*   **参数 (Parameters)**
    *   $S_p$: 产品 $p$ 的单位售价 (元/件)。
    *   $C_p$: 产品 $p$ 的单位原材料成本 (元/件)。
    *   $T_{p,m}$: 产品 $p$ 在设备 $m$ 上的单位加工时间 (小时/件)。通过预定义集合 $R$，我们确保模型中只使用有意义的、有限的加工时间值。
    *   $H_m$: 设备 $m$ 的有效工作时长 (小时)。
    *   $F_m$: 设备 $m$ 的固定运行成本 (元)。

# 数学形式

## 变量定义
为了确定生产计划，我们定义以下两类决策变量：

*   $x_{p,a,b}$: 决策变量，表示通过路径 $(p, a, b) \in R$ 生产的产品 $p$ 的数量 (件)。
    *   $x_{p,a,b} \ge 0, \forall (p, a, b) \in R$

*   $y_m$: 二元决策变量，用于表示设备 $m$ 是否被启用。如果设备 $m$ 被用于生产，则 $y_m=1$；否则 $y_m=0$。
    *   $y_m \in \{0, 1\}, \forall m \in M$

## 辅助变量定义
为了提高模型解的可读性，我们定义以下辅助变量来表示各产品的总产量：

*   $X_p$: 辅助变量，表示产品 $p$ 的总生产数量 (件)。
    *   $X_p = \sum_{(a,b) | (p,a,b) \in R} x_{p,a,b}, \quad \forall p \in P$

## 目标函数
我们的目标是最大化总利润，即总收入减去总成本。

*   **最大化总利润:**
    $\max \left( \sum_{(p,a,b) \in R} (S_p - C_p) \cdot x_{p,a,b} - \sum_{m \in M} F_m \cdot y_m \right)$
    *   **说明:** 目标函数的第一部分计算了所有生产活动带来的总边际利润（售价减原料成本）。第二部分计算了所有被启用的设备产生的总固定运行成本。

## 约束条件
生产计划必须满足以下限制：

1.  **设备A工时约束 (Process A Capacity Constraints):**
    *   **说明:** 对于每一台A工序的设备，其总加工时间不能超过其有效工作时长。
    *   **公式:** $\sum_{(p,b) | (p,a,b) \in R} T_{p,a} \cdot x_{p,a,b} \le H_a, \quad \forall a \in M_A$

2.  **设备B工时约束 (Process B Capacity Constraints):**
    *   **说明:** 对于每一台B工序的设备，其总加工时间不能超过其有效工作时长。
    *   **公式:** $\sum_{(p,a) | (p,a,b) \in R} T_{p,b} \cdot x_{p,a,b} \le H_b, \quad \forall b \in M_B$

3.  **设备启用逻辑约束 (Machine Activation Constraints):**
    *   **说明:** 如果一台设备被用于生产，那么其对应的启用变量 $y_m$ 必须为1。这通过“大M方法”实现，其中 $K_m$ 是一个足够大但合理的常数。
    *   **公式 (设备A):** $\sum_{(p,b) | (p,a,b) \in R} x_{p,a,b} \le K_a \cdot y_a, \quad \forall a \in M_A$
    *   **公式 (设备B):** $\sum_{(p,a) | (p,a,b) \in R} x_{p,a,b} \le K_b \cdot y_b, \quad \forall b \in M_B$
    *   **注:** $K_m$ 是一个足够大的正数（Big-M）。为保证模型的数值稳定性，$K_m$ 可取为设备 $m$ 在其有效时长内能生产的最大产品数量，例如 $K_m = H_m / \min_{\{p | T_{p,m} > 0\}} \{T_{p,m}\}$。如果任何流经设备 $m$ 的产量 $x_{p,a,b}$ 大于0，则 $y_m$ 被强制为1，从而在目标函数中计入固定成本 $F_m$。

4.  **变量类型约束 (Variable Type Constraints):**
    *   **说明:** 生产数量必须为非负数，设备启用变量必须为0或1。
    *   **公式:**
        *   $x_{p,a,b} \ge 0, \quad \forall (p,a,b) \in R$
        *   $y_m \in \{0, 1\}, \quad \forall m \in M$