The current problem faced by the company is how to use the fewest number of containers to pack the currently needed goods for transportation, while considering the weight of the goods, specific packaging requirements, and inventory limitations. Professional modeling and analysis are needed for a batch of goods’ transportation strategy to ensure maximum utilization of the limited container space.

The company currently has a batch to be transported, with each container able to hold a maximum of 60 tons of goods and each container used must load at least 18 tons of goods. The goods to be loaded include five types: A, B, C, D, and E, with quantities of 120, 90, 300, 90, and 120 respectively. The weights are 0.5 tons for A, 1 ton for B, 0.4 tons for C, 0.6 tons for D, and 0.65 tons for E. Additionally, to meet specific usage requirements, every time A goods are loaded, at least 1 unit of C must also be loaded, but loading C alone does not require simultaneously loading A; and considering the demand limitation for D goods, each container must load at least 12 units of D.

Establish an operations research model so that the company can use the fewest number of containers to pack this batch of goods.

好的，这是根据自我反思与修改规划完善后的最终版数学建模指南。

# 问题

## 问题描述
一家公司需要运输一批货物，目标是使用最少数量的集装箱来完成装载。每个集装箱的最大载重为60吨，且一旦使用，其载重不得低于18吨。待运输的货物共有五种（A, B, C, D, E），其需求量、单位重量均有规定。此外，装箱过程需满足两条特殊规则：1) 任何装载了货物A的集装箱，必须同时装载至少1单位的货物C；2) 任何被使用的集装箱，必须装载至少12单位的货物D。

## 问题分析
这是一个典型的**集装箱装载问题 (Bin Packing Problem)** 的变种，属于整数规划领域。与标准集装箱问题不同，本问题增加了许多额外的约束，例如每个集装箱的最小载重量、以及货物间的依赖关系和最低装载要求。因此，该模型是一个**混合整数线性规划 (Mixed-Integer Linear Programming, MILP)** 模型。其核心决策在于：决定使用哪些集装箱，以及每种货物在每个已使用的集装箱中各装载多少数量。

## 核心假设
1.  所有货物的数量均为非负整数。
2.  集装箱是同质的，即每个集装箱的属性（最大/最小载重）都相同。
3.  可以预估一个足够大但合理的潜在可用集装箱数量上限，用于模型构建。

## 数据定义
此问题中的数据可被系统化地定义为集合与参数。

*   **集合 (Sets)**
    *   $I$: 所有货物类型的集合, $I = \{A, B, C, D, E\}$。
    *   $J$: 潜在可用的集装箱集合。其数量上限可根据总重量和最小载重预估得出（总重量 / 最小载重 = $402 / 18 \approx 22.3$），为保证模型可行性，可设定一个安全的上界，如 $J = \{1, 2, ..., 25\}$。

*   **参数 (Parameters)**
    *   $D_i$: 货物 $i$ 的总需求量 (单位: 件)。
    *   $w_i$: 货物 $i$ 的单位重量 (单位: 吨/件)。
    *   $W_{max}$: 每个集装箱的最大载重能力 (60吨)。
    *   $W_{min}$: 每个被使用的集装箱的最小载重量 (18吨)。
    *   $Q_{D,min}$: 每个被使用的集装箱中，货物D的最小装载量 (12件)。
    *   $Q_{C,min}$: 当装载货物A时，货物C的最小装载量 (1件)。

具体数值如下：
| 货物 $i$ | 需求量 $D_i$ | 单位重量 $w_i$ (吨) |
| :--- | :--- | :--- |
| A | 120 | 0.5 |
| B | 90 | 1.0 |
| C | 300 | 0.4 |
| D | 90 | 0.6 |
| E | 120 | 0.65 |

# 数学形式

## 变量定义
为了构建模型，我们定义以下三类决策变量：

*   $x_{ij}$: 一个整数变量，表示在集装箱 $j$ 中装载货物 $i$ 的数量。
    *   $x_{ij} \in \mathbb{Z}^+, \forall i \in I, j \in J$

*   $y_j$: 一个二元变量。如果集装箱 $j$ 被使用，则 $y_j=1$；否则 $y_j=0$。
    *   $y_j \in \{0, 1\}, \forall j \in J$

*   $a_j$: 一个二元指示变量。如果集装箱 $j$ 中装载了货物A，则 $a_j=1$；否则 $a_j=0$。
    *   $a_j \in \{0, 1\}, \forall j \in J$

## 目标函数
我们的目标是最小化所使用的集装箱总数。
*   **最小化使用的集装箱数量:** $\min \sum_{j \in J} y_j$

## 约束条件
模型必须满足以下所有约束条件，以确保方案的可行性：

1.  **需求满足约束 (Demand Fulfillment Constraint):**
    *   **说明:** 对于每一种货物，所有集装箱中装载的总数量必须精确等于其总需求量。这是确保完成运输任务的基本要求。
    *   **公式:** $\sum_{j \in J} x_{ij} = D_i, \quad \forall i \in I$

2.  **集装箱使用关联约束 (Container Usage Linking Constraint):**
    *   **说明:** 货物只能被装入标记为“已使用”的集装箱中。此约束将货物装载行为 ($x_{ij}$) 与集装箱使用状态 ($y_j$) 直接关联。
    *   **公式:** $x_{ij} \le D_i \cdot y_j, \quad \forall i \in I, j \in J$

3.  **集装箱最大载重约束 (Maximum Capacity Constraint):**
    *   **说明:** 对于每一个集装箱，其装载的所有货物的总重量不能超过最大载重。此为确保运输安全与合规的基本物理限制。
    *   **公式:** $\sum_{i \in I} w_i \cdot x_{ij} \le W_{max} \cdot y_j, \quad \forall j \in J$

4.  **集装箱最小载重约束 (Minimum Load Constraint):**
    *   **说明:** 对于每一个被使用的集装箱，其装载的所有货物的总重量必须达到最小载重要求。这是公司内部为提高运输效率而设定的业务规则。
    *   **公式:** $\sum_{i \in I} w_i \cdot x_{ij} \ge W_{min} \cdot y_j, \quad \forall j \in J$

5.  **货物D最小装载量约束 (Minimum Quantity Constraint for Good D):**
    *   **说明:** 任何一个被使用的集装箱，都必须装载至少 $Q_{D,min}$ 数量的货物D。此为满足特定需求的特殊业务规则。
    *   **公式:** $x_{D,j} \ge Q_{D,min} \cdot y_j, \quad \forall j \in J$

6.  **货物A与C的装载关联逻辑 (A-C Association Logic):**
    *   **说明:** 以下一组约束共同确保：当且仅当一个集装箱装载了货物A时，它也必须装载至少 $Q_{C,min}$ 数量的货物C。
    *   **6a. 货物A装载指示 (Good A Loading Indicator):**
        *   **说明:** 这两条约束将 $x_{A,j}$ 的状态（是否大于0）与指示变量 $a_j$ 绑定。
        *   **公式:**
            *   $x_{A,j} \le D_A \cdot a_j, \quad \forall j \in J$
            *   $x_{A,j} \ge a_j, \quad \forall j \in J$
    *   **6b. 货物C关联装载 (Associated Loading for Good C):**
        *   **说明:** 当指示变量 $a_j$ 被激活时（即装载了货物A），此约束强制货物C的数量必须满足下限。
        *   **公式:** $x_{C,j} \ge Q_{C,min} \cdot a_j, \quad \forall j \in J$

7.  **对称性破除约束 (Symmetry-Breaking Constraint):**
    *   **说明:** 此约束强制集装箱按顺序编号使用（例如，不允许在集装箱1空置的情况下使用集装箱2）。这能消除大量等效解，显著提高求解器的计算效率。
    *   **公式:** $y_j \ge y_{j+1}, \quad \forall j \in \{1, 2, ..., |J|-1\}$

8.  **变量类型约束 (Variable Domain Constraints):**
    *   **说明:** 定义所有决策变量的取值范围。
    *   **公式:**
        *   $x_{ij} \ge 0$ 且为整数, $\forall i \in I, j \in J$
        *   $y_j \in \{0, 1\}, \forall j \in J$
        *   $a_j \in \{0, 1\}, \forall j \in J$