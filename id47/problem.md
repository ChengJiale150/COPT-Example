A certain farm has 100 hectares of land and 15,000 yuan in funds for production development. The labor force situation on the farm is 3,500 person-days in autumn and winter, and 4,000 person-days in spring and summer. If the labor force itself is not fully utilized, they can work externally, earning 2.1 yuan/person-day in spring and summer and 1.8 yuan/person-day in autumn and winter.

The farm cultivates three types of crops: soybeans, corn, and wheat, and also raises dairy cows and chickens. Crop cultivation requires no specialized investment, but raising animals involves an investment of 400 yuan per dairy cow and 3 yuan per chicken. Raising dairy cows requires allocating 1.5 hectares of land per cow to grow feed, and involves 100 person-days in autumn and winter, and 50 person-days in spring and summer per cow. The annual net income is 400 yuan per dairy cow. Raising chickens does not use land, requires 0.6 person-days in autumn and winter, and 0.3 person-days in spring and summer per chicken. Annual net income is 2 yuan per chicken. The current chicken coop can accommodate up to 3,000 chickens, and the cow barn can accommodate up to 32 dairy cows. The labor and income requirements for the three types of crops per year are shown in Table 1-9.

Table 1-9
| Item | Soybean | Corn | Wheat |
|----------------|---------|------|-------|
| Person-days (Autumn/Winter) | 20 | 35 | 10 |
| Person-days (Spring/Summer) | 50 | 75 | 40 |
| Annual Net Income (Yuan/hectare) | 175 | 300 | 120 |

Determine the farm's operating plan to maximize annual net income. Please note that Labor days are calculated in whole days, fractions are not allowed.

# 问题

## 问题描述
一个农场拥有100公顷土地、15000元生产资金，以及季节性劳动力资源（秋冬季3500人日，春夏季4000人日）。农场可以从事三类作物（大豆、玉米、小麦）的种植和两类动物（奶牛、鸡）的养殖。各项经营活动对资源的需求和产生的年净收益各不相同。具体来说，养殖奶牛需占用土地和投入资金，而种植作物仅需劳动力。养殖活动有圈舍容量限制。此外，若劳动力未被完全利用，可安排外出务工以增加收入，其报酬也因季节而异。问题要求确定一个最优的经营方案（即各种作物种植面积和动物养殖数量），以实现农场年净总收入的最大化。

## 问题分析
这是一个典型的**资源分配问题**，旨在有限的资源（土地、资金、劳动力）下，通过优化各项生产活动的规模来最大化总收益。由于决策变量中包含了连续变量（如作物种植面积）和整数变量（如动物养殖数量、外派劳动力天数），因此该问题属于**混合整数线性规划 (Mixed-Integer Linear Programming, MILP)** 问题。

## 核心假设
1.  **线性关系**: 所有活动的投入（资源消耗）和产出（净收入）与其规模成正比。例如，种植2公顷大豆的收入和劳动力需求是种植1公顷的两倍。
2.  **资源可分性**: 土地资源可以被无限分割（例如，可以种植10.5公顷玉米）。
3.  **确定性**: 模型中的所有参数（如价格、成本、劳动力需求、资源总量等）都是已知的、恒定的数值。
4.  **单一周期**: 模型考虑的是一个年度的经营计划，不涉及跨年度的库存或投资影响。
5.  **市场无限**: 农场生产的所有产品（包括外派劳动力）都能按给定的净收入率被市场完全吸收。
6.  **劳动力同质性**: 模型假设在同一季节（如“春夏季”）内的所有“人日”劳动力是无差别的，可以灵活分配给该季节的任何农活，不考虑特定技能要求。
7.  **资源静态假设**: 模型视土地、资金和劳动力为年度总量资源，不考虑年内的动态变化（如现金流、作物生长周期内的劳动力需求波动）。

## 数据定义
我们将问题中的所有已知数值信息系统化地定义为参数。

**资源总量 (Resource Endowments)**
| 符号 | 描述 | 数值 |
| :--- | :--- | :--- |
| $R_{land}$ | 可用土地总面积 | 100 (公顷) |
| $R_{capital}$ | 可用资金总额 | 15000 (元) |
| $R_{labor\_aw}$ | 秋冬可用劳动力 | 3500 (人日) |
| $R_{labor\_ss}$ | 春夏可用劳动力 | 4000 (人日) |

**生产活动参数 (Production Activities Parameters)**
*   **作物 (Crops)**
| 参数 | 描述 | 大豆 | 玉米 | 小麦 |
| :--- | :--- | :--- | :--- | :--- |
| $C_{aw,j}$ | 每公顷作物$j$的秋冬劳动力需求 | 20 | 35 | 10 |
| $C_{ss,j}$ | 每公顷作物$j$的春夏劳动力需求 | 50 | 75 | 40 |
| $I_{crop,j}$ | 每公顷作物$j$的年净收入 (元) | 175 | 300 | 120 |

*   **动物 (Animals)**
| 参数 | 描述 | 奶牛 | 鸡 |
| :--- | :--- | :--- | :--- |
| $L_{animal,k}$ | 每头/只动物$k$占用的土地 (公顷) | 1.5 | 0 |
| $K_{animal,k}$ | 每头/只动物$k$的资金投入 (元) | 400 | 3 |
| $A_{aw,k}$ | 每头/只动物$k$的秋冬劳动力需求 | 100 | 0.6 |
| $A_{ss,k}$ | 每头/只动物$k$的春夏劳动力需求 | 50 | 0.3 |
| $I_{animal,k}$ | 每头/只动物$k$的年净收入 (元) | 400 | 2 |
| $Cap_{animal,k}$ | 动物$k$的养殖容量上限 | 32 | 3000 |

**外派劳务参数 (External Labor Parameters)**
| 符号 | 描述 | 数值 |
| :--- | :--- | :--- |
| $I_{labor\_aw}$ | 秋冬外派劳动力收入率 (元/人日) | 1.8 |
| $I_{labor\_ss}$ | 春夏外派劳动力收入率 (元/人日) | 2.1 |

# 数学形式

## 变量定义
为了确定各项经营活动的规模，我们定义以下决策变量：

*   **作物种植面积 (连续变量):**
    *   $x_1$: 计划种植大豆的面积 (单位: 公顷)。
    *   $x_2$: 计划种植玉米的面积 (单位: 公顷)。
    *   $x_3$: 计划种植小麦的面积 (单位: 公顷)。

*   **动物养殖数量 (整数变量):**
    *   $y_1$: 计划养殖奶牛的数量 (单位: 头)。
    *   $y_2$: 计划养殖鸡的数量 (单位: 只)。

*   **外派剩余劳动力 (整数变量):**
    *   $L_{aw}$: 秋冬季节外派的剩余劳动力 (单位: 人日)。
    *   $L_{ss}$: 春夏季节外派的剩余劳动力 (单位: 人日)。

## 目标函数
我们的目标是最大化农场的年度总净收入，该收入由五部分构成：三种作物的收入、两种动物的收入以及两季外派劳动力的收入。

*   **最大化年净总收入:**
    $\max Z = (175 \cdot x_1 + 300 \cdot x_2 + 120 \cdot x_3) + (400 \cdot y_1 + 2 \cdot y_2) + (1.8 \cdot L_{aw} + 2.1 \cdot L_{ss})$

## 约束条件
所有决策必须在农场的资源和物理限制内进行：

1.  **土地资源约束 (Land Constraint):**
    *   **说明:** 所有作物种植面积与为奶牛预留的饲料地面积之和，不能超过农场可用的土地总面积。
    *   **公式:** $x_1 + x_2 + x_3 + 1.5 \cdot y_1 \le 100$

2.  **资金约束 (Capital Constraint):**
    *   **说明:** 养殖奶牛和鸡所需的总投资不能超过农场的可用资金总额。
    *   **公式:** $400 \cdot y_1 + 3 \cdot y_2 \le 15000$

3.  **秋冬劳动力平衡约束 (Autumn/Winter Labor Balance):**
    *   **说明:** 此约束采用**等式形式**，其精妙之处在于将劳动力消耗和剩余劳动力外派两个决策耦合在一起。左侧的生产活动消耗量与外派劳动力 $L_{aw}$ 之和必须等于右侧的劳动力总供给。这确保了资源不会被超额使用，同时 $L_{aw}$ 的值被精确定义为未被内部生产使用的劳动力数量。由于总劳动力供给 $R_{labor\_aw}$ 和外派劳动力 $L_{aw}$ 均为整数，此等式约束**隐含地保证了各项生产活动的总劳动力消耗也必然是一个整数**，完全符合‘劳动力按整日计算’的要求。
    *   **公式:** $(20 \cdot x_1 + 35 \cdot x_2 + 10 \cdot x_3) + (100 \cdot y_1 + 0.6 \cdot y_2) + L_{aw} = 3500$

4.  **春夏劳动力平衡约束 (Spring/Summer Labor Balance):**
    *   **说明:** 同样，用于各项生产活动的春夏劳动力与外派的春夏劳动力之和，必须等于农场拥有的春夏劳动力总量。
    *   **公式:** $(50 \cdot x_1 + 75 \cdot x_2 + 40 \cdot x_3) + (50 \cdot y_1 + 0.3 \cdot y_2) + L_{ss} = 4000$

5.  **养殖容量约束 (Capacity Constraints):**
    *   **说明:** 养殖的动物数量不能超过其圈舍的物理容量上限。
    *   **奶牛容量:** $y_1 \le 32$
    *   **鸡容量:** $y_2 \le 3000$

6.  **变量类型与非负性约束 (Variable Type and Non-negativity Constraints):**
    *   **说明:** 所有决策变量都不能为负数。其中，动物数量和外派劳动力天数必须为整数。
    *   **公式:**
        *   $x_1, x_2, x_3 \ge 0$
        *   $y_1, y_2 \ge 0$ 且为整数
        *   $L_{aw}, L_{ss} \ge 0$ 且为整数