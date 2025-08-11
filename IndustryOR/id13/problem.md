Tom and Jerry just bought a farm in Sunshine Valley, and they are considering using it to plant corn, wheat, soybeans, and sorghum. The profit per acre for planting corn is $1500, the profit per acre for planting wheat is $1200, the profit per acre for planting soybeans is $1800, and the profit per acre for planting sorghum is $1600. To maximize their profit, how many acres of land should they allocate to each crop? Tom and Jerry’s farm has a total area of 100 acres.

The land area used for planting corn must be at least twice the land area used for planting wheat.

The land area used for planting soybeans must be at least half the land area used for planting sorghum.

The land area used for planting wheat must be three times the land area used for planting sorghum.

# 问题

## 问题描述
农场主需要在总面积为100英亩的土地上，规划种植玉米、小麦、大豆和高粱四种作物的面积。目标是最大化农场的总利润，同时必须满足一系列关于不同作物种植面积比例的约束条件。

## 问题分析
这是一个典型的**线性规划 (Linear Programming, LP)** 问题，属于运筹学中经典的**资源分配问题 (Resource Allocation Problem)**。该问题的核心是在满足多种资源和比例约束的条件下，确定一组连续变量（各种作物的种植面积）的最优值，以实现线性目标函数（总利润）的最大化。

## 核心假设
1.  **确定性模型 (Deterministic Model):** 模型中的所有参数，如单位利润和总土地面积，均为已知且恒定的常数。不考虑市场价格波动或作物产量的随机性。
2.  **单周期静态模型 (Single-Period Static Model):** 模型仅为单个种植季进行优化，不考虑作物轮作、土壤肥力变化等跨周期的动态因素。
3.  **利润线性与资源同质 (Linearity and Homogeneity):** 每种作物的总利润与种植面积严格成正比。100英亩的土地是同质的，可无差别地用于种植任何作物。
4.  **面积可分 (Divisibility):** 土地面积可以被任意分割，即种植面积是连续的非负实数。
5.  **资源无限 (Unlimited Ancillary Resources):** 除了土地资源外，其他所需资源（如水、劳动力、种子、化肥等）均被视为无限供给，不构成约束。

## 数据定义
此问题中包含两类核心数据：作物的属性和农场的总面积。

*   **集合 (Sets)**
    *   $C$: 所有可选作物的集合, $C = \{1, 2, 3, 4\}$，分别代表玉米、小麦、大豆、高粱。

*   **参数 (Parameters)**
    *   $p_c$: 种植作物 $c$ 的单位面积利润 (单位: 美元/英亩)。
    *   $A_{total}$: 农场的总可用面积 (单位: 英亩)。

具体数值如下：
| 索引 $c$ | 作物名称 | 单位利润 $p_c$ ($/英亩) |
| :--- | :--- | :--- |
| 1 | 玉米 (Corn) | 1500 |
| 2 | 小麦 (Wheat) | 1200 |
| 3 | 大豆 (Soybeans) | 1800 |
| 4 | 高粱 (Sorghum) | 1600 |
| | **总面积** | $A_{total} = 100$ |

# 数学形式

## 变量定义
为了表示分配给每种作物的土地面积，我们定义如下的决策变量。这些变量是**连续变量 (Continuous Variables)**。
*   $x_c$: 分配给种植作物 $c$ 的土地面积 (单位: 英亩)。
    *   $x_1$: 种植玉米的面积。
    *   $x_2$: 种植小麦的面积。
    *   $x_3$: 种植大豆的面积。
    *   $x_4$: 种植高粱的面积。

## 目标函数
我们的目标是最大化所有作物产生的总利润。
*   **最大化总利润:** $\max \sum_{c \in C} p_c \cdot x_c$
    *   即: $\max (1500 \cdot x_1 + 1200 \cdot x_2 + 1800 \cdot x_3 + 1600 \cdot x_4)$

## 约束条件
模型必须满足以下约束：
1.  **总面积约束 (Total Acreage Constraint):**
    *   **说明:** 所有作物占用的总面积不能超过农场的总可用面积。采用小于等于约束 `(≤)` 是为了构建一个更具普适性的模型，它允许在特定比例约束下将部分土地休耕作为最优选择。
    *   **公式:** $\sum_{c \in C} x_c \le A_{total}$
        *   即: $x_1 + x_2 + x_3 + x_4 \le 100$

2.  **玉米-小麦比例约束 (Corn-to-Wheat Ratio Constraint):**
    *   **说明:** 用于种植玉米的土地面积必须至少是种植小麦面积的两倍。
    *   **公式:** $x_1 - 2x_2 \ge 0$

3.  **大豆-高粱比例约束 (Soybean-to-Sorghum Ratio Constraint):**
    *   **说明:** 用于种植大豆的土地面积必须至少是种植高粱面积的一半。
    *   **公式:** $x_3 - 0.5x_4 \ge 0$

4.  **小麦-高粱比例约束 (Wheat-to-Sorghum Ratio Constraint):**
    *   **说明:** 用于种植小麦的土地面积必须精确等于种植高粱面积的三倍。
    *   **公式:** $x_2 - 3x_4 = 0$

5.  **非负约束 (Non-negativity Constraint):**
    *   **说明:** 分配给任何一种作物的土地面积都不能是负数。
    *   **公式:** $x_c \ge 0, \forall c \in C$
        *   即: $x_1, x_2, x_3, x_4 \ge 0$