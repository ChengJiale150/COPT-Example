Mary is planning her dinner tonight. Every 100 grams of okra contains 3.2 grams of fiber, every 100 grams of carrots contains 2.7 grams of fiber, every 100 grams of celery contains 1.6 grams of fiber, and every 100 grams of cabbage contains 2 grams of fiber. How many grams of each type of food should Mary buy to maximize her fiber intake?

She is considering choosing one among salmon, beef, and pork as a protein source.

She also considers choosing at least two kinds of vegetables among okra, carrots, celery, and cabbage.

The price of salmon is $4 per 100 grams, beef is $3.6 per 100 grams, pork is $1.8 per 100 grams. The price of okra is $2.6 per 100 grams, carrots are $1.2 per 100 grams, celery is $1.6 per 100 grams, and cabbage is $2.3 per 100 grams. Mary has a budget of $15 for this meal.

The total food intake should be 600 grams.

好的，这是根据修改规划生成的最终版数学建模指南。

# 问题

## 问题描述

### 背景
一位名叫Mary的女士计划准备一顿晚餐。

### 目标
在满足一系列条件下，最大化总膳食纤维摄入量。

### 规则与限制
1.  **总预算:** 所有食物的总花费不得超过$15。
2.  **总重量:** 所有食物的总重量必须恰好为600克。
3.  **蛋白质选择:** 必须从三文鱼、牛肉、猪肉中**选择且仅选择一种**作为蛋白质来源。
4.  **蔬菜选择:** 必须从秋葵、胡萝卜、芹菜、卷心菜中**至少选择两种**作为蔬菜来源。

## 问题分析
这是一个典型的**混合整数线性规划 (Mixed-Integer Linear Programming, MILP)** 问题。

*   **线性规划 (Linear Programming)**: 目标函数（最大化纤维）和所有约束（预算、重量）都是决策变量的线性组合。
*   **混合整数 (Mixed-Integer)**: 问题中包含两种类型的决策变量：
    1.  **连续变量**: 每种食物的购买量（例如，可以购买150.5克胡萝卜）。
    2.  **二元变量**: 是否选择某种食物（例如，选择三文鱼而不选择牛肉或猪肉）。

问题的核心是在满足多种逻辑和物理约束的条件下，对一组连续和离散的决策进行优化，以达到最大化目标。

## 核心假设
1.  **纤维来源**: 只有蔬菜（秋葵、胡萝卜、芹菜、卷心菜）含有膳食纤维，蛋白质类食物（三文鱼、牛肉、猪肉）的纤维含量为0。这是根据问题描述中未提供蛋白质纤维含量而做出的合理推断。
2.  **数量连续性**: 每种食物的购买量可以是任意非负实数，不存在最小包装单位的限制。
3.  **数据确定性**: 所有价格和纤维含量均为已知且恒定的常数。

## 数据定义
为了构建模型，我们将问题中的信息结构化为集合和参数。为了方便计算，所有食物的数量单位定义为“100克”，价格和纤维含量也相应地以此为基准。

*   **集合 (Sets)**
    *   $P$: 蛋白质类食物的集合, $P = \{\text{三文鱼}, \text{牛肉}, \text{猪肉}\}$。
    *   $V$: 蔬菜类食物的集合, $V = \{\text{秋葵}, \text{胡萝卜}, \text{芹菜}, \text{卷心菜}\}$。
    *   $F$: 所有食物的集合, $F = P \cup V$。

*   **参数 (Parameters)**
    *   $c_i$: 食物 $i$ 的价格 (单位: 美元 / 100克)。
    *   $f_i$: 食物 $i$ 的纤维含量 (单位: 克 / 100克)。
    *   $B_{max}$: 晚餐的总预算上限 (单位: 美元)。
    *   $W_{total}$: 晚餐的总重量要求 (单位: 克)。

具体数值如下：
| 食物 $i$ | 集合 | 价格 $c_i$ ($/100g) | 纤维 $f_i$ (g/100g) |
| :--- | :--- | :--- | :--- |
| 三文鱼 | $P$ | 4.0 | 0 |
| 牛肉 | $P$ | 3.6 | 0 |
| 猪肉 | $P$ | 1.8 | 0 |
| 秋葵 | $V$ | 2.6 | 3.2 |
| 胡萝卜 | $V$ | 1.2 | 2.7 |
| 芹菜 | $V$ | 1.6 | 1.6 |
| 卷心菜 | $V$ | 2.3 | 2.0 |
| | | | |
| **总预算** | $B_{max}$ | 15 | |
| **总重量** | $W_{total}$ | 600 | |

# 数学形式

## 变量定义
为了对问题进行建模，我们定义两类决策变量：

*   **连续变量 (Continuous Variables)**
    *   $x_i$: 购买食物 $i$ 的数量，单位为“100克”。例如，$x_{\text{胡萝卜}}=1.5$ 表示购买150克胡萝卜。
        *   $x_i \ge 0, \forall i \in F$

*   **二元变量 (Binary Variables)**
    *   $y_i$: 一个二元变量，用于表示是否选择食物 $i$。如果选择食物 $i$，则 $y_i=1$；否则 $y_i=0$。
        *   $y_i \in \{0, 1\}, \forall i \in F$

## 目标函数
目标是最大化总膳食纤维摄入量。只有蔬菜含有纤维。

*   **最大化总纤维:** $\max \sum_{i \in V} f_i \cdot x_i$

## 约束条件
模型必须满足以下所有限制条件：

1.  **总预算约束 (Budget Constraint):**
    *   **说明:** 所有购买食物的总花费不能超过预算上限 $B_{max}$。
    *   **公式:** $\sum_{i \in F} c_i \cdot x_i \le B_{max}$

2.  **总重量约束 (Total Weight Constraint):**
    *   **说明:** 所有购买食物的总重量必须恰好等于 $W_{total}$。由于变量 $x_i$ 的单位是100克，因此需要进行单位换算。
    *   **公式:** $100 \cdot \sum_{i \in F} x_i = W_{total}$
    *   **简化形式:** $\sum_{i \in F} x_i = \frac{W_{total}}{100} = 6$

3.  **蛋白质选择约束 (Protein Selection Constraint):**
    *   **说明:** 必须从蛋白质集合 $P$ 中选择且仅选择一种。
    *   **公式:** $\sum_{i \in P} y_i = 1$

4.  **蔬菜选择约束 (Vegetable Selection Constraint):**
    *   **说明:** 必须从蔬菜集合 $V$ 中至少选择两种。
    *   **公式:** $\sum_{i \in V} y_i \ge 2$

5.  **采购量与选择决策的联动约束 (Linking Constraints for Purchase and Selection):**
    *   **说明:** 这组约束确保了“选择”($y_i$)与“购买”($x_i$)两个变量之间的逻辑一致性。它强制实现了“当且仅当”的关系：当一种食物被选择时，其购买量必须大于零；当一种食物未被选择时，其购买量必须为零。
    *   **公式:**
        1.  $x_i \le M \cdot y_i, \forall i \in F$
        2.  $x_i \ge \epsilon \cdot y_i, \forall i \in F$
    *   **参数解释:**
        *   $M$ 是一个足够大的正数 (Big-M)。在此问题中，总购买量为6个单位（600克），因此任何单一食物的购买量 $x_i$ 不会超过6。我们可以设定 $M=6$。
        *   $\epsilon$ 是一个极小的正数（例如 $\epsilon=0.001$），代表有意义的最小购买量，以避免购买量为零的无效选择。

6.  **变量域约束 (Variable Domain Constraints):**
    *   **说明:** 定义每个变量的取值范围。
    *   **公式:**
        *   $x_i \ge 0, \forall i \in F$
        *   $y_i \in \{0, 1\}, \forall i \in F$