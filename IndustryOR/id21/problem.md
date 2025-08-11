A restaurant needs to order dining tables from three different suppliers, A, B, and C. The cost of ordering each dining table from Supplier A is $120, from Supplier B is $110, and from Supplier C is $100. The restaurant needs to minimize the total cost of the order.

Additionally, each order from Supplier A will include 20 tables, while each order from Suppliers B and C will include 15 tables. The number of orders must be an integer. The restaurant needs to order at least 150 tables.

Each order from Supplier A will include 20 tables, and each order from Suppliers B and C will include 15 tables. The restaurant needs to order no more than 600 tables.

If the restaurant decides to order tables from Supplier A, it must also order at least 30 tables from Supplier B.

Additionally, if the restaurant decides to order tables from Supplier B, it must also order tables from Supplier C.

# 问题

## 问题描述
一家餐厅需要从A、B、C三家供应商处订购餐桌。餐厅的目标是最小化总订购成本。

具体信息如下：
1.  **成本**: 从供应商A订购每张餐桌的成本为$120，供应商B为$110，供应商C为$100。
2.  **订购单位**: 供应商A的订单必须以20张餐桌为一批次进行；供应商B和C的订单必须以15张餐桌为一批次进行。订购的批次数必须为整数。
3.  **数量限制**: 餐厅总共需要订购至少150张餐桌，但不能超过600张。
4.  **条件约束**:
    *   如果餐厅决定从供应商A订购（即订购批次数大于0），则必须同时从供应商B订购至少30张餐桌。
    *   如果餐厅决定从供应商B订购（即订购批次数大于0），则必须同时从供应商C订购（即订购批次数大于0）。

## 问题分析
这是一个典型的**混合整数线性规划 (Mixed-Integer Linear Programming, MILP)** 问题。该问题包含整数决策变量（各供应商的订购批次数）和二元决策变量（用于处理条件约束）。目标是最小化一个线性成本函数，同时满足一系列线性约束和逻辑约束。此问题的核心建模挑战在于如何将“如果...则...”形式的商业规则，转化为求解器可以理解的线性数学约束。通过引入辅助二元变量，我们成功地将这些逻辑条件线性化，从而构建了一个标准的MILP模型。

## 核心假设
1.  成本与订购数量成线性关系。
2.  订购批次数必须为非负整数。
3.  所有参数（成本、批次大小、需求量）都是确定且已知的。
4.  供应商的供应能力没有上限（除了问题中给出的总数上限）。

## 数据定义
此问题中的数据可分为供应商集合、成本与批次参数、以及需求限制。

*   **集合 (Sets)**
    *   $S$: 所有供应商的集合, $S = \{A, B, C\}$。

*   **参数 (Parameters)**
    *   $p_s$: 从供应商 $s$ 订购每张餐桌的成本 (单位: 美元)。
    *   $b_s$: 供应商 $s$ 的每批次订单包含的餐桌数量。
    *   $C_s$: 从供应商 $s$ 订购一个批次的成本，该参数为简化目标函数而预先计算。
    *   $T_{min}$: 餐厅需要订购的最小总餐桌数。
    *   $T_{max}$: 餐厅允许订购的最大总餐桌数。
    *   $T_{B,req}$: 当从A订购时，要求从B订购的最小餐桌数。

具体数值如下：
| 供应商 $s$ | 单价 $p_s$ ($) | 批次大小 $b_s$ | 批次成本 $C_s = p_s \cdot b_s$ ($) |
| :--- | :--- | :--- | :--- |
| A | 120 | 20 | 2400 |
| B | 110 | 15 | 1650 |
| C | 100 | 15 | 1500 |
| **需求限制** | | | |
| 最小总数 $T_{min}$ | 150 | | |
| 最大总数 $T_{max}$ | 600 | | |
| B的条件需求 $T_{B,req}$ | 30 | | |

# 数学形式

## 变量定义
为了对问题进行建模，我们定义以下决策变量：

*   **整数变量 (Integer Variables)**
    *   $x_s$: 决定从供应商 $s$ 订购的批次数。这是一个非负整数。
        *   $x_s \in \mathbb{Z}_{\ge 0}, \forall s \in S$

*   **辅助二元变量 (Auxiliary Binary Variables)**
    *   $y_A$: 一个二元变量。如果从供应商A订购 ($x_A > 0$)，则 $y_A=1$；否则 $y_A=0$。
    *   $y_B$: 一个二元变量。如果从供应商B订购 ($x_B > 0$)，则 $y_B=1$；否则 $y_B=0$。
        *   $y_A, y_B \in \{0, 1\}$

## 目标函数
目标是最小化总的订购成本，即所有供应商的批次成本之和。
*   **最小化总成本:** $\min \sum_{s \in S} C_s \cdot x_s$
    *   即: $\min (2400 \cdot x_A + 1650 \cdot x_B + 1500 \cdot x_C)$

## 约束条件
模型必须满足以下所有约束条件。其中，条件约束通过“Big-M”方法实现，该方法利用一个足够大的常数$M$将二元变量的开关作用传递给整数变量，从而将逻辑条件转化为线性不等式。

1.  **最小总数量约束 (Minimum Total Quantity Constraint):**
    *   **说明:** 所有供应商提供的餐桌总数必须至少为150张。
    *   **公式:** $\sum_{s \in S} b_s \cdot x_s \ge T_{min}$
        *   即: $20x_A + 15x_B + 15x_C \ge 150$

2.  **最大总数量约束 (Maximum Total Quantity Constraint):**
    *   **说明:** 所有供应商提供的餐桌总数不能超过600张。
    *   **公式:** $\sum_{s \in S} b_s \cdot x_s \le T_{max}$
        *   即: $20x_A + 15x_B + 15x_C \le 600$

3.  **条件约束 1 (A $\rightarrow$ B):**
    *   **说明:** 如果从供应商A订购 ($x_A > 0$)，则从供应商B订购的批次数必须至少为2批（即$2 \times 15 = 30$张）。
    *   **公式:**
        *   $x_A \le 30 \cdot y_A$
        *   $x_B \ge 2 \cdot y_A$
    *   **解释:**
        *   第一条公式将 $x_A$ 和 $y_A$ 关联。如果 $x_A > 0$，则 $y_A$ 必须为1。这里的常数30是 $x_A$ 的一个有效上界（由最大总数约束 $20x_A \le 600$ 推得 $x_A \le 30$）。
        *   第二条公式执行逻辑。如果 $y_A=1$，约束变为 $x_B \ge 2$，确保从B订购至少2个批次。如果 $y_A=0$，约束变为 $x_B \ge 0$，不产生额外限制。

4.  **条件约束 2 (B $\rightarrow$ C):**
    *   **说明:** 如果从供应商B订购 ($x_B > 0$)，则必须从供应商C订购 ($x_C > 0$)。
    *   **公式:**
        *   $x_B \le 40 \cdot y_B$
        *   $x_C \ge y_B$
    *   **解释:**
        *   第一条公式关联 $x_B$ 和 $y_B$。如果 $x_B > 0$，则 $y_B$ 必须为1。这里的常数40是 $x_B$ 的一个有效上界（由最大总数约束 $15x_B \le 600$ 推得 $x_B \le 40$）。
        *   第二条公式执行逻辑。如果 $y_B=1$，约束变为 $x_C \ge 1$，确保至少从C订购一个批次。如果 $y_B=0$，约束变为 $x_C \ge 0$，不产生额外限制。

5.  **变量类型约束 (Variable Type Constraints):**
    *   **说明:** 订购的批次数必须为非负整数，辅助变量为二元变量。
    *   **公式:**
        *   $x_s \in \mathbb{Z}_{\ge 0}, \forall s \in S$
        *   $y_A, y_B \in \{0, 1\}$