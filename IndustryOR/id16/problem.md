A store plans to formulate the purchasing and sales plan for a certain product for the first quarter of next year. It is known that the warehouse capacity of the store can store up to 500 units of the product, and there are 200 units in stock at the end of this year. The store purchases goods once at the beginning of each month. The purchasing and selling prices of the product in each month are shown in Table 1.3.

Table 1.3

| Month | 1 | 2 | 3 |
| :---: | :---: | :---: | :---: |
| Purchasing Price (Yuan) | 8 | 6 | 9 |
| Selling Price (Yuan) | 9 | 8 | 10 |

Now, determine how many units should be purchased and sold each month to maximize the total profit, and express this problem as a linear programming model.

# 问题

## 问题描述
一家商店需要为其在明年第一季度的某商品制定采购与销售计划。已知该商店的仓库最大容量为500单位，且在今年年底（即明年第一季度初）的初始库存为200单位。商店在每个月的月初进行一次采购。该商品在各个月份的采购价格与销售价格如下表所示。目标是确定每个月应采购和销售多少单位的商品，以实现总利润的最大化。

| 月份 | 1月 | 2月 | 3月 |
| :---: | :---: | :---: | :---: |
| 采购价 (元/单位) | 8 | 6 | 9 |
| 销售价 (元/单位) | 9 | 8 | 10 |

## 问题分析
这是一个典型的 **多周期库存管理问题 (Multi-period Inventory Problem)**。该问题的核心是在满足仓储容量、库存平衡等一系列随时间动态变化的约束条件下，通过优化每个时间周期内的采购和销售决策，来最大化整个计划期内的总利润。此问题可以被构建为一个**线性规划 (Linear Programming, LP)** 模型。该模型不仅考虑了周期内的现金流，也计入了期末剩余库存的价值。

## 核心假设
1.  **需求无上限**: 在给定的销售价格下，市场可以吸收任意数量的商品。即，销售量仅受限于商店的库存，而非外部市场需求。
2.  **瞬时交易**: 采购在月初瞬间完成并入库，销售则在本月内完成。
3.  **期末库存价值**: 计划期结束时（三月末）剩余的库存具有价值，其价值按第三个月的采购成本计算。这是为了避免模型做出不切实际的期末清仓决策。
4.  **无持有成本与损耗**: 商品在存储过程中不产生额外的持有成本（如资金占用、仓储管理费）和物理损耗。
5.  **变量连续性**: 采购量和销售量可以是任意非负实数。若商品为不可分割的单位（如电视机），则模型应调整为**混合整数线性规划 (MILP)**，相关变量需取整数。

## 数据定义
此问题中的数据主要包括时间周期、价格信息、容量限制和初始状态。

*   **集合 (Sets)**
    *   $T$: 计划期内的月份集合, $T = \{1, 2, 3\}$，分别代表1月、2月、3月。

*   **参数 (Parameters)**
    *   $c_t$: 在月份 $t$ 的单位采购成本 (元/单位)。
    *   $p_t$: 在月份 $t$ 的单位销售价格 (元/单位)。
    *   $C_{max}$: 仓库的最大容量， $C_{max} = 500$ (单位)。
    *   $I_0$: 第0个月末（即1月初）的初始库存量， $I_0 = 200$ (单位)。

具体数值如下：
| 月份 $t$ | 采购价 $c_t$ | 销售价 $p_t$ |
| :---: | :---: | :---: |
| 1 | 8 | 9 |
| 2 | 6 | 8 |
| 3 | 9 | 10 |

# 数学形式

## 变量定义
为了描述每个月的决策和状态，我们定义以下三组变量：
*   $x_t$: 在月份 $t$ 初采购的商品数量 (单位)。
*   $y_t$: 在月份 $t$ 内销售的商品数量 (单位)。
*   $I_t$: 在月份 $t$ 末的库存数量 (单位)。

其中 $t \in T = \{1, 2, 3\}$。

## 目标函数
我们的目标是最大化三个月内的总利润，该利润由两部分构成：各月的运营利润（销售收入减采购成本）与计划期末剩余库存的残值。

*   **最大化总利润:** $\max \sum_{t \in T} (p_t \cdot y_t - c_t \cdot x_t) + c_3 \cdot I_3$

## 约束条件
模型必须满足以下几类约束条件，以确保计划的可行性：

1.  **库存平衡约束 (Inventory Balance Constraint):**
    *   **说明:** 每个月末的库存量，等于上月末的库存量加上本月采购量，再减去本月销售量。此约束是连接各个周期的核心，并结合库存非负约束，隐含了月销售量不能超过当月可供总量的限制。
    *   **公式:** $I_t = I_{t-1} + x_t - y_t, \quad \forall t \in T$
    *   (其中 $I_0$ 是一个已知的初始库存参数)

2.  **峰值库存容量约束 (Peak Inventory Capacity Constraint):**
    *   **说明:** 每个月初完成采购后，仓库内的总库存量（即上期末库存与本期采购量之和）代表了本月库存的峰值，该峰值不能超过仓库最大容量。
    *   **公式:** $I_{t-1} + x_t \le C_{max}, \quad \forall t \in T$

3.  **非负约束 (Non-negativity Constraint):**
    *   **说明:** 所有的采购量、销售量和库存量都必须是非负的。
    *   **公式:** $x_t \ge 0, \quad y_t \ge 0, \quad I_t \ge 0, \quad \forall t \in T$