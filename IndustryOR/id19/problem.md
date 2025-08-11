A furniture store can choose to order chairs from three different manufacturers: A, B, and C. The cost of ordering each chair from manufacturer A is $50, from manufacturer B is $45, and from manufacturer C is $40. The store needs to minimize the total cost of the order.

Additionally, each order from manufacturer A will include 15 chairs, while each order from manufacturers B and C will include 10 chairs. The number of orders must be an integer. The store needs to order at least 100 chairs.

Each order from manufacturer A will include 15 chairs, while each order from manufacturers B and C will include 10 chairs. The store needs to order at most 500 chairs.

If the store decides to order chairs from manufacturer A, it must also order at least 10 chairs from manufacturer B.

Furthermore, if the store decides to order chairs from manufacturer B, it must also order chairs from manufacturer C.

# 问题

## 问题描述
一家家具店需要向三家制造商（A、B、C）订购椅子，目标是最小化总采购成本。每家制造商的单位椅子成本和单次订货的椅子数量均不相同。具体来说，制造商A的椅子单价为$50，每次订货包含15把；制造商B的单价为$45，每次订货包含10把；制造商C的单价为$40，每次订货包含10把。

此外，订单需要满足以下条件：
1.  向每家制造商的订货次数必须是整数。
2.  订购的椅子总数必须至少为100把，但不能超过500把。
3.  如果决定从制造商A订货，那么必须同时从制造商B订购至少10把椅子。
4.  如果决定从制造商B订货，那么也必须从制造商C订货。

## 问题分析
这是一个典型的**混合整数线性规划 (Mixed-Integer Linear Programming, MILP)** 问题。该问题的核心决策是确定向每家制造商的订货次数（整数变量）。目标函数是线性的（最小化总成本）。约束条件中包含了线性的数量限制，以及需要引入辅助二元变量来处理的逻辑条件（“如果...那么...”）。

## 核心假设
1.  所有成本和数量参数都是确定且已知的。
2.  每把椅子的成本是固定的，不随订购数量变化（无批量折扣）。
3.  “从某制造商订货”被定义为向该制造商的订货次数大于零（即 $x_m > 0$）。本模型通过引入二元变量 $y_m$ 来精确捕捉此状态。

## 数据定义
此问题中的数据可分为制造商的属性和订单的总体要求。

*   **集合 (Sets)**
    *   $M$: 所有可选制造商的集合, $M = \{A, B, C\}$。

*   **参数 (Parameters)**
    *   $c_m$: 从制造商 $m$ 购买的每把椅子的成本 (单位: $)。
    *   $q_m$: 从制造商 $m$ 每次订货所包含的椅子数量。
    *   $Q_{min}$: 要求订购的最小总椅子数。
    *   $Q_{max}$: 允许订购的最大总椅子数。
    *   $Q_{B,min}$: 如果从A订货，要求从B订购的最小椅子数。

具体数值如下：
| 制造商 $m$ | 成本 $c_m$ ($) | 每次订货数量 $q_m$ |
| :--- | :--- | :--- |
| A | 50 | 15 |
| B | 45 | 10 |
| C | 40 | 10 |
| **总体要求** | | |
| 最小总数 $Q_{min}$ | 100 | |
| 最大总数 $Q_{max}$ | 500 | |
| A->B最小订购数 $Q_{B,min}$ | 10 | |

# 数学形式

## 变量定义
为了构建模型，我们定义两类决策变量：

*   **整数变量 (Integer Variables)**
    *   $x_m$: 决定向制造商 $m$ 下订单的次数。这是一个非负整数。
        *   $x_m \in \mathbb{Z}_{\ge 0}, \forall m \in M$

*   **辅助二元变量 (Auxiliary Binary Variables)**
    *   $y_m$: 一个二元变量，用于指示是否从制造商 $m$ 订货。如果 $x_m > 0$，则 $y_m=1$；否则 $y_m=0$。
        *   $y_m \in \{0, 1\}, \forall m \in M$

## 目标函数
目标是最小化采购所有椅子的总成本。总成本是各制造商的（订货次数 × 每次订货数量 × 单位成本）之和。

*   **最小化总成本:** $\min \sum_{m \in M} c_m \cdot q_m \cdot x_m$

## 约束条件
模型必须满足以下所有限制：

1.  **总椅子数下限约束 (Total Quantity Lower Bound):**
    *   **说明:** 所有订购的椅子总数必须不小于100。
    *   **公式:** $\sum_{m \in M} q_m \cdot x_m \ge 100$

2.  **总椅子数上限约束 (Total Quantity Upper Bound):**
    *   **说明:** 所有订购的椅子总数必须不超过500。
    *   **公式:** $\sum_{m \in M} q_m \cdot x_m \le 500$

3.  **条件约束 (A → B):**
    *   **说明:** 如果从制造商A订货 ($y_A=1$)，则从制造商B的订货次数必须至少为1。由于从B每次订货10把，这等价于至少订购10把椅子。
    *   **公式:** $x_B \ge y_A$

4.  **条件约束 (B → C):**
    *   **说明:** 如果从制造商B订货 ($y_B=1$)，则必须也从制造商C订货 ($y_C=1$)。
    *   **公式:** $y_C \ge y_B$

5.  **变量链接约束 (Variable Linking Constraints):**
    *   **说明:** 这组约束确保整数变量 $x_m$ 和二元变量 $y_m$ 的逻辑关系正确。
        *   **公式 1:** $x_m \le K_m \cdot y_m, \forall m \in M$
            *   此约束强制：如果不从制造商 $m$ 订货 ($y_m=0$)，则其订货次数 $x_m$ 必须为0。其中 $K_m$ 是一个为每个制造商单独计算的有效上界，即 $K_m = \lfloor Q_{max} / q_m \rfloor$。具体为：$K_A=33, K_B=50, K_C=50$。
        *   **公式 2:** $x_m \ge y_m, \forall m \in M$
            *   此约束强制：如果决定从制造商 $m$ 订货 ($y_m=1$)，那么其实际订货次数 $x_m$ 必须至少为1。

6.  **变量类型约束 (Variable Type Constraints):**
    *   **说明:** 定义每个变量的取值范围。
    *   **公式:**
        *   $x_m \in \mathbb{Z}_{\ge 0}, \forall m \in M$ (订货次数为非负整数)
        *   $y_m \in \{0, 1\}, \forall m \in M$ (指示变量为二元变量)