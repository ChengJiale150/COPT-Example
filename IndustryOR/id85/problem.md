A company is producing two products (X and Y). The resources required for the production of X and Y are divided into two parts: machine time for automated processing and craftsman time for manual finishing. The table below shows the number of minutes required for each product:

| Item | Machine Time (minutes) | Craftsman Time (minutes) |
| :---: | :---: | :---: |
| X | 13 | 20 |
| Y | 19 | 29 |

The company has 40 hours of machine time available in the next working week, but only 35 hours of craftsman time. The cost of machine time is £10 per hour, and the cost of craftsman time is £2 per hour. Idle time for machines and craftsmen incurs no cost. For each product produced (all products produced will be sold), the revenue for product X is £20, and the revenue for product Y is £30. The company has a specific contract that requires 10 units of product X to be produced for a customer each week. Formulate a model for this problem.

# 问题

## 问题描述
一家公司生产两种产品（X和Y）。生产过程需要消耗两种资源：用于自动化处理的机器时间和用于手工精加工的工匠时间。每单位产品所需的资源时间（分钟）如下表所示。在下一个工作周，公司有40小时的可用机器时间和35小时的可用工匠时间。机器时间成本为每小时10英镑，工匠时间成本为每小时2英镑，闲置时间不产生费用。所有生产出的产品都将被售出，产品X的收入为每件20英镑，产品Y的收入为每件30英镑。此外，公司有一份合同，要求每周必须为一位客户生产10个单位的产品X。需要为此问题建立一个数学模型，以确定两种产品的最优生产数量。

## 问题分析
这是一个典型的**产品组合优化 (Product Mix Optimization)** 问题。其核心目标是在满足多种资源（机器时间、工匠时间）和最低生产需求（合同要求）的约束下，决定每种产品的生产数量，以实现公司总利润的最大化。由于产品生产数量在现实中通常是不可分割的单位，我们采用**整数线性规划 (Integer Linear Programming, ILP)** 来确保决策变量为整数，这比允许小数产量的线性规划更贴近实际情况。

## 核心假设
1.  **整数生产**: 产品的生产数量必须为非负整数。不能生产小数个产品。
2.  **成本归因**: 生产成本仅与实际使用的资源时间相关。机器或工匠的闲置时间不产生任何成本。
3.  **确定性**: 所有参数，包括资源消耗时间、可用资源总量、成本和收入，都是已知且恒定的。
4.  **销售保证**: 所有生产出来的产品都会被成功售出，实现其对应的收入。
5.  **线性关系假设**: 假设单位产品的资源消耗、成本和收入是恒定的，总消耗/收益与产量成正比。模型未考虑规模经济或边际效益递减。
6.  **无转换成本假设**: 假设在生产不同产品之间切换时，不存在额外的准备时间（Setup Time）或成本。

## 数据定义
为保证模型的数学正确性，所有输入参数的单位都进行了统一。时间单位统一为**分钟**，成本单位统一为**英镑/分钟**。所有后续计算均基于此统一标准。

*   **集合 (Sets)**
    *   $P$: 所有产品的集合, $P = \{X, Y\}$。

*   **参数 (Parameters)**
    *   $R_p$: 生产并销售一单位产品 $p$ 所获得的收入 (£)。
    *   $T_{p,r}$: 生产一单位产品 $p$ 所需的资源 $r$ 的时间 (分钟)。其中资源 $r \in \{\text{machine}, \text{craftsman}\}$。
    *   $A_r$: 资源 $r$ 的总可用时间 (分钟)。
    *   $C_r$: 资源 $r$ 每分钟的使用成本 (£/分钟)。
    *   $D_X$: 产品X的合同要求的最低周产量。

具体数值如下：
| 参数 | 描述 | 产品 X | 产品 Y |
| :--- | :--- | :--- | :--- |
| $R_p$ | 收入 (£/单位) | 20 | 30 |
| $T_{p, \text{machine}}$ | 机器时间 (分钟/单位) | 13 | 19 |
| $T_{p, \text{craftsman}}$ | 工匠时间 (分钟/单位) | 20 | 29 |

| 参数 | 描述 | 资源: 机器 | 资源: 工匠 |
| :--- | :--- | :--- | :--- |
| $A_r$ | 总可用时间 (分钟) | $40 \text{h} \times 60 = 2400$ | $35 \text{h} \times 60 = 2100$ |
| $C_r$ | 成本 (£/分钟) | $10 / 60 = 1/6$ | $2 / 60 = 1/30$ |

| 参数 | 描述 | 数值 |
| :--- | :--- | :--- |
| $D_X$ | 产品X最低产量 | 10 |


# 数学形式

## 变量定义
我们定义以下决策变量来表示两种产品的生产数量：
*   $x_p$: 在下一周计划生产的产品 $p$ 的数量, 其中 $p \in P$。
    *   $x_X$: 计划生产的产品X的数量。
    *   $x_Y$: 计划生产的产品Y的数量。

## 目标函数
我们的目标是最大化公司的总利润。从业务逻辑上，总利润等于总收入减去总生产成本。
*   **最大化总利润 (业务逻辑形式):**
    $\max \left( \sum_{p \in P} R_p \cdot x_p \right) - \left( \sum_{p \in P} (T_{p, \text{machine}} \cdot C_{\text{machine}} + T_{p, \text{craftsman}} \cdot C_{\text{craftsman}}) \cdot x_p \right)$

## 约束条件
生产计划必须满足以下所有限制：
1.  **机器时间约束 (Machine Time Constraint):**
    *   **说明:** 用于生产所有产品的总机器时间不能超过可用的机器时间总量。
    *   **公式:** $\sum_{p \in P} T_{p, \text{machine}} \cdot x_p \le A_{\text{machine}}$
    *   **具体形式:** $13 x_X + 19 x_Y \le 2400$

2.  **工匠时间约束 (Craftsman Time Constraint):**
    *   **说明:** 用于生产所有产品的总工匠时间不能超过可用的工匠时间总量。
    *   **公式:** $\sum_{p \in P} T_{p, \text{craftsman}} \cdot x_p \le A_{\text{craftsman}}$
    *   **具体形式:** $20 x_X + 29 x_Y \le 2100$

3.  **合同要求约束 (Contractual Obligation Constraint):**
    *   **说明:** 产品X的产量必须至少满足合同规定的数量。
    *   **公式:** $x_X \ge D_X$
    *   **具体形式:** $x_X \ge 10$

4.  **变量类型约束 (Variable Type Constraint):**
    *   **说明:** 生产数量必须是非负整数。
    *   **公式:** $x_p \ge 0 \text{ and } x_p \in \mathbb{Z}, \forall p \in P$
    *   **具体形式:** $x_X, x_Y \ge 0 \text{ and are integers}$