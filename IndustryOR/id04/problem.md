A farmer needs to decide how many cows, sheep, and chickens to raise in order to achieve maximum profit. The farmer can sell cows, sheep, and chickens for $500, $200, and $8 each, respectively. The feed costs for each cow, sheep, and chicken are $100, $80, and $5, respectively. The profit is the difference between the selling price and the feed cost. Each cow, sheep, and chicken produces 10, 5, and 3 units of manure per day, respectively. Due to the limited time the farm staff has for cleaning the farm each day, they can handle up to 800 units of manure. Additionally, because of the limited farm size, the farmer can raise at most 50 chickens. Furthermore, the farmer must have at least 10 cows to meet customer demand. The farmer must also raise at least 20 sheep. Finally, the total number of animals cannot exceed 100.

# 问题

## 问题描述
一位农场主需要决定饲养牛、羊、鸡的数量，以实现利润最大化。每种动物的售价、饲料成本、以及产生的利润（售价-成本）均不相同。农场的运营受到多项条件的限制：首先，每日处理的动物粪便总量有上限；其次，由于场地有限，鸡的饲养数量有上限；再次，为了满足客户需求，牛和羊的饲养数量有下限；最后，农场可容纳的动物总数也存在上限。

## 问题分析
这是一个典型的**整数线性规划 (Integer Linear Programming, ILP)** 问题。其核心是在满足一系列线性约束条件（资源限制、最小需求、容量限制等）下，通过调整一组整数决策变量（各种动物的数量），来最大化一个线性的目标函数（总利润）。

该模型是对现实问题的简化，例如，它使用“动物总数上限”作为“农场大小有限”的代理指标，并使用“粪便处理上限”作为劳动力或设备资源的代理指标。

## 核心假设
1.  **线性关系假设:** 每种动物的利润、粪便产量与饲养数量成正比，不存在规模效应或边际效益递减。
2.  **参数确定性假设:** 所有参数（价格、成本、粪便产量等）都是确定且已知的常数。
3.  **变量整数假设:** 所有动物的数量必须为非负整数。
4.  **无资本限制假设:** 农场主拥有充足的初始资金购买任意组合的动物，不存在预算约束。
5.  **静态模型假设:** 这是一个单周期静态模型，不考虑动物生长周期、多阶段现金流等动态因素。

## 数据定义
此问题中的数据可分为动物的属性参数和农场的限制参数。

*   **集合 (Sets)**
    *   $A$: 所有可饲养动物类型的索引集合, $A = \{1, 2, 3\}$。
        *   索引 1: 牛
        *   索引 2: 羊
        *   索引 3: 鸡

*   **基础参数 (Base Parameters)**
    *   $s_i$: 动物 $i$ 的售价 (单位: 美元)。
    *   $c_i$: 动物 $i$ 的饲料成本 (单位: 美元)。
    *   $m_i$: 一只动物 $i$ 每日产生的粪便量 (单位: unit)。
    *   $L_{i}^{min}$: 动物 $i$ 的最小饲养数量。
    *   $L_{i}^{max}$: 动物 $i$ 的最大饲养数量。
    *   $M_{max}$: 农场每日可处理的最大粪便总量 (单位: unit)。
    *   $N_{max}$: 农场可饲养的动物总数上限。

*   **导出参数 (Derived Parameters)**
    *   $p_i$: 饲养一只动物 $i$ 所能获得的利润 (单位: 美元)，其计算公式为 $p_i = s_i - c_i$。

具体数值如下：
| 索引 $i$ | 动物类型 | 售价 $s_i$ ($) | 成本 $c_i$ ($) | **利润 $p_i$ ($)** | 每日粪便产量 $m_i$ (unit) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 牛 | 500 | 100 | **400** | 10 |
| 2 | 羊 | 200 | 80 | **120** | 5 |
| 3 | 鸡 | 8 | 5 | **3** | 3 |

农场限制参数：
| 限制类型 | 符号 | 数值 |
| :--- | :--- | :--- |
| 最大粪便处理量 | $M_{max}$ | 800 |
| 最小养牛数 | $L_{1}^{min}$ | 10 |
| 最小养羊数 | $L_{2}^{min}$ | 20 |
| 最大养鸡数 | $L_{3}^{max}$ | 50 |
| 动物总数上限 | $N_{max}$ | 100 |

# 数学形式

## 变量定义
为了表示每种动物的饲养数量，我们定义如下的整数决策变量：
*   $x_i$: 计划饲养的动物 $i$ 的数量, 其中 $i \in A$。
    *   $x_i \in \mathbb{Z}_{\ge 0}, \forall i \in A$

## 目标函数
我们的目标是最大化农场的总利润。
*   **最大化总利润:** $\max \sum_{i \in A} p_i \cdot x_i$
    *   **具体形式:** $\max (400 \cdot x_1 + 120 \cdot x_2 + 3 \cdot x_3)$

## 约束条件
模型必须满足以下所有约束条件：
1.  **粪便处理能力约束 (Manure Handling Constraint):**
    *   **说明:** 所有动物产生的每日粪便总量不能超过农场的最大处理能力。
    *   **公式:** $\sum_{i \in A} m_i \cdot x_i \le M_{max}$
    *   **具体形式:** $10 \cdot x_1 + 5 \cdot x_2 + 3 \cdot x_3 \le 800$

2.  **动物总数约束 (Total Animal Constraint):**
    *   **说明:** 饲养的动物总数不能超过农场的最大容量。
    *   **公式:** $\sum_{i \in A} x_i \le N_{max}$
    *   **具体形式:** $x_1 + x_2 + x_3 \le 100$

3.  **最小饲养数量约束 (Minimum Requirement Constraints):**
    *   **说明:** 特定动物的饲养数量必须达到其最低要求。
    *   **公式:** $x_i \ge L_{i}^{min}$ for specified $i$.
    *   **具体形式:**
        *   $x_1 \ge 10$
        *   $x_2 \ge 20$

4.  **最大饲养数量约束 (Maximum Capacity Constraint):**
    *   **说明:** 特定动物的饲养数量不能超过其最大容量限制。
    *   **公式:** $x_i \le L_{i}^{max}$ for specified $i$.
    *   **具体形式:** $x_3 \le 50$

5.  **变量类型约束 (Variable Type Constraint):**
    *   **说明:** 所有决策变量必须为非负整数。
    *   **公式:** $x_i \in \mathbb{Z}_{\ge 0}, \forall i \in A$
    *   **具体形式:** $x_1, x_2, x_3$ 必须为非负整数。