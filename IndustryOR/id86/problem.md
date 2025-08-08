Healthy Pet Foods Company produces two types of dog food: Meaties and Yummies. Each pack of Meaties contains 2 pounds of grains and 3 pounds of meat; each pack of Yummies contains 3 pounds of grains and 1.5 pounds of meat. The company believes it can sell any quantity of dog food that it can produce. Meaties sell for $2.80 per pack, and Yummies sell for $2.00 per pack. The company's production is subject to several constraints. First, a maximum of 400,000 pounds of grains can be purchased each month at a price of $0.20 per pound of grains. A maximum of 300,000 pounds of meat can be purchased each month at a price of $0.50 per pound of meat. Additionally, a special machine is required to produce Meaties, with a monthly capacity of 90,000 packs. The variable costs for mixing and packaging dog food are $0.25 per pack (Meaties) and $0.20 per pack (Yummies). Detailed information is provided in Table B-1.

**Table B-1 Healthy Pet Foods Data**

| | Meaties | Yummies |
|--------------------|--------------|------------|
| Price per pack | $2.80 | $2.00 |
| Raw materials | | |
| - Grains | 2.0 lbs | 3.0 lbs |
| - Meat | 3.0 lbs | 1.5 lbs |
| Variable cost | $0.25/pack | $0.20/pack |
| Resources | | |
| Meaties capacity | 90,000 packs/month | |
| Monthly available grains | 400,000 lbs | |
| Monthly available meat | 300,000 lbs | |

Assume you are the manager of the dog food department at Healthy Pet Foods Company. Your salary is based on the department's profit, so you will try to maximize profit. How should you operate the department to maximize both the profit and your salary?


# 问题

## 问题描述
Healthy Pet Foods 公司生产两种狗粮产品：Meaties 和 Yummies。公司需要决定这两种产品的月度生产量，以实现部门利润的最大化。该决策受到多种资源的限制，包括两种主要原材料（谷物和肉类）的月度最大采购量，以及生产 Meaties 的专用机器的月度产能限制。问题提供了每种产品的售价、原材料消耗量、变动成本以及各项资源的总量和成本。

## 问题分析
这是一个典型的**产品组合优化问题 (Product Mix Problem)**。其核心是在一系列资源约束下，确定两种或多种产品的最优生产数量，以最大化总利润。由于目标函数（总利润）和所有约束条件（资源消耗）都是决策变量（产品数量）的线性函数，因此该问题可以被建模为一个**线性规划 (Linear Programming, LP)** 问题。

## 核心假设
1.  **市场需求假设**: 公司能够售出所有生产出的产品，即市场需求是无限的，生产即销售。
2.  **参数确定性**: 所有给定的参数（如价格、成本、资源可用量、原材料消耗率）在规划期（一个月）内是已知且恒定的。
3.  **线性关系**: 成本、收入和资源消耗与生产数量成正比，不存在规模经济或批量折扣。
4.  **决策变量连续性假设**: 假设产品生产量为连续变量。鉴于月产量较大，将非整数解四舍五入对总利润的影响可忽略不计，同时可使用更高效的线性规划求解器。
5.  **单周期静态模型**: 本模型为单周期（月度）静态模型，不考虑库存持有成本及跨周期影响。
6.  **资源同质性**: 每种原材料（谷物、肉类）都是同质的，没有质量差异。

## 数据定义
此问题中的数据可分为产品属性、原材料成本和资源限制。

*   **集合 (Sets)**
    *   $P$: 产品的集合, $P = \{M, Y\}$，其中 $M$ 代表 Meaties, $Y$ 代表 Yummies。

*   **参数 (Parameters)**

| 参数符号 | 含义 | Meaties ($p=M$) | Yummies ($p=Y$) |
| :--- | :--- | :--- | :--- |
| $s_p$ | 单位售价 ($/包) | $2.80 | $2.00 |
| $g_p$ | 单位谷物用量 (磅/包) | $2.0 | $3.0 |
| $m_p$ | 单位肉类用量 (磅/包) | $3.0 | $1.5 |
| $v_p$ | 单位变动成本 ($/包) | $0.25 | $0.20 |

| 参数符号 | 含义 | 数值 |
| :--- | :--- | :--- |
| $c_g$ | 谷物单位成本 ($/磅) | $0.20 |
| $c_m$ | 肉类单位成本 ($/磅) | $0.50 |
| $G_{max}$ | 月度谷物可用总量 (磅) | $400,000 |
| $M_{max}$ | 月度肉类可用总量 (磅) | $300,000 |
| $C_M$ | Meaties 月度最大产能 (包) | $90,000 |

# 数学形式

## 变量定义
我们定义以下决策变量来表示两种产品的月度生产量：
*   $x_M$: 每月生产 Meaties 的数量 (单位: 包)。
*   $x_Y$: 每月生产 Yummies 的数量 (单位: 包)。

## 目标函数
**最大化总利润:**
目标是最大化总收入与总成本（包括原材料成本和变动成本）之差。其通用形式为：
$\max \ Z = \text{总收入} - \text{总原料成本} - \text{总变动成本}$
$\max \ Z = \sum_{p \in P} s_p x_p - \sum_{p \in P} (g_p c_g + m_p c_m) x_p - \sum_{p \in P} v_p x_p$

为简化模型，我们首先计算每种产品的单位利润：
*   **Meaties 单位利润 ($profit_M$):**
    $profit_M = s_M - (g_M c_g + m_M c_m) - v_M = 2.80 - (2.0 \cdot 0.20 + 3.0 \cdot 0.50) - 0.25 = \$0.65$
*   **Yummies 单位利润 ($profit_Y$):**
    $profit_Y = s_Y - (g_Y c_g + m_Y c_m) - v_Y = 2.00 - (3.0 \cdot 0.20 + 1.5 \cdot 0.50) - 0.20 = \$0.45$

因此，目标函数可简化为最大化两种产品的总利润之和：
*   **公式:** $\max \ Z = 0.65 \cdot x_M + 0.45 \cdot x_Y$

## 约束条件
生产活动必须在以下限制条件内进行：

1.  **谷物资源约束 (Grains Constraint):**
    *   **说明:** 生产所有产品所消耗的谷物总量不能超过每月可采购的谷物上限。
    *   **公式:** $2.0 \cdot x_M + 3.0 \cdot x_Y \le 400,000$

2.  **肉类资源约束 (Meat Constraint):**
    *   **说明:** 生产所有产品所消耗的肉类总量不能超过每月可采购的肉类上限。
    *   **公式:** $3.0 \cdot x_M + 1.5 \cdot x_Y \le 300,000$

3.  **Meaties 产能约束 (Meaties Capacity Constraint):**
    *   **说明:** Meaties 的月度产量不能超过其专用机器的生产能力。
    *   **公式:** $x_M \le 90,000$

4.  **非负约束 (Non-negativity Constraint):**
    *   **说明:** 产品的生产数量不能为负数。这是一个隐含的物理约束。
    *   **公式:** $x_M \ge 0, x_Y \ge 0$