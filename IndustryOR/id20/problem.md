Bright Future Toys wants to build and sell robots, model cars, building blocks, and dolls. The profit for each robot sold is $15, for each model car sold is $8, for each set of building blocks sold is $12, and for each doll sold is $5. How many types of toys should Bright Future Toys manufacture to maximize profit?
There are 1200 units of plastic available. Each robot requires 30 units of plastic, each model car requires 10 units of plastic, each set of building blocks requires 20 units of plastic, and each doll requires 15 units of plastic.

There are 800 units of electronic components available. Each robot requires 8 units of electronic components, each model car requires 5 units of electronic components, each set of building blocks requires 3 units of electronic components, and each doll requires 2 units of electronic components.

If Bright Future Toys manufactures robots, they will not manufacture dolls.

However, if they manufacture model cars, they will also manufacture building blocks.

The number of dolls manufactured cannot exceed the number of model cars manufactured.

# 问题

## 问题描述
一家名为“光明未来”的玩具公司计划生产和销售四种玩具：机器人、模型车、积木和娃娃。每种玩具的单位利润、所需资源（塑料和电子元件）以及总资源可用量均已给定。公司的目标是在满足一系列生产约束条件的前提下，决定每种玩具的生产数量，以实现总利润的最大化。

## 问题分析
这是一个典型的**混合整数线性规划 (Mixed-Integer Linear Programming, MILP)** 问题。该问题的核心是在多种有限资源（塑料、电子元件）的约束下，确定一组整数决策变量（各种玩具的生产数量），以最大化一个线性目标函数（总利润）。此问题还包含了一些特殊的逻辑约束，例如互斥生产（生产机器人则不生产娃娃）和条件生产（生产模型车则必须生产积木），这些逻辑约束需要通过引入二元变量来精确建模。

## 核心假设
1.  **整数产量**: 玩具的生产数量必须为非负整数。不能生产小数个玩具。
2.  **资源线性消耗**: 每种资源的消耗量与玩具的生产数量成正比。
3.  **利润确定性**: 每种玩具的单位利润是固定且已知的。
4.  **资源可分**: 资源（塑料、电子元件）可以被任意分割使用。
5.  **产销合一**: 所有生产出的玩具都能被成功售出并实现其利润。
6.  **无固定成本**: 假设生产任何一种玩具（无论数量多少）都不需要支付额外的一次性固定成本或生产线启动成本。所有成本已线性地包含在单位利润的计算中。

## 数据定义
此问题中的数据可分为玩具属性、资源总量和逻辑规则。

*   **集合 (Sets)**
    *   $T$: 所有玩具类型的集合, $T = \{1, 2, 3, 4\}$，分别代表机器人、模型车、积木、娃娃。

*   **参数 (Parameters)**
    *   $p_i$: 玩具 $i$ 的单位利润。
    *   $a_{i, \text{plastic}}$: 生产一个单位的玩具 $i$ 所需的塑料数量。
    *   $a_{i, \text{elec}}$: 生产一个单位的玩具 $i$ 所需的电子元件数量。
    *   $C_{\text{plastic}}$: 可用的塑料总量。
    *   $C_{\text{elec}}$: 可用的电子元件总量。
    *   $M_i$: 玩具 $i$ 在资源限制下的理论最大产量，用于构建稳健的逻辑约束。$M_i = \min \left( \lfloor \frac{C_{\text{plastic}}}{a_{i, \text{plastic}}} \rfloor, \lfloor \frac{C_{\text{elec}}}{a_{i, \text{elec}}} \rfloor \right)$。

具体数值如下：
| 索引 $i$ | 玩具类型 | 利润 $p_i$ ($) | 塑料消耗 $a_{i, \text{plastic}}$ | 电子元件消耗 $a_{i, \text{elec}}$ | 理论最大产量 $M_i$ |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 机器人 | 15 | 30 | 8 | $\min(\lfloor\frac{1200}{30}\rfloor, \lfloor\frac{800}{8}\rfloor) = 40$ |
| 2 | 模型车 | 8 | 10 | 5 | $\min(\lfloor\frac{1200}{10}\rfloor, \lfloor\frac{800}{5}\rfloor) = 120$ |
| 3 | 积木 | 12 | 20 | 3 | $\min(\lfloor\frac{1200}{20}\rfloor, \lfloor\frac{800}{3}\rfloor) = 60$ |
| 4 | 娃娃 | 5 | 15 | 2 | $\min(\lfloor\frac{1200}{15}\rfloor, \lfloor\frac{800}{2}\rfloor) = 80$ |
| | **资源总量** | | $C_{\text{plastic}} = 1200$ | $C_{\text{elec}} = 800$ | |

# 数学形式

## 变量定义
为了构建模型，我们需要定义两类决策变量：

*   **生产数量变量 (Integer Variables):**
    *   $x_i$: 计划生产的玩具 $i$ 的数量。这是一个非负整数。
    *   $x_i \in \mathbb{Z}^+, \forall i \in T$

*   **生产决策变量 (Binary Variables):**
    *   $y_i$: 一个关键的二元决策变量，用于**指示**是否要生产玩具 $i$。如果决定生产 ($x_i > 0$)，则 $y_i=1$；否则 $y_i=0$。该变量是实现复杂逻辑约束（如“如果...则...”或“不能同时...”）的**核心工具**，作为连接商业规则与生产数量的“开关”。
    *   $y_i \in \{0, 1\}, \forall i \in T$

## 目标函数
目标是最大化所有售出玩具的总利润。

*   **最大化总利润:** $\max \sum_{i \in T} p_i \cdot x_i$

## 约束条件
模型必须满足以下所有约束条件：

1.  **塑料资源约束 (Plastic Resource Constraint):**
    *   **说明:** 所有玩具消耗的塑料总量不能超过可用的塑料总量。
    *   **公式:** $\sum_{i \in T} a_{i, \text{plastic}} \cdot x_i \le C_{\text{plastic}}$

2.  **电子元件资源约束 (Electronic Component Constraint):**
    *   **说明:** 所有玩具消耗的电子元件总量不能超过可用的电子元件总量。
    *   **公式:** $\sum_{i \in T} a_{i, \text{elec}} \cdot x_i \le C_{\text{elec}}$

3.  **互斥生产约束 (Mutually Exclusive Production Constraint):**
    *   **说明:** 如果生产机器人 ($y_1=1$)，则不能生产娃娃 ($y_4=0$)。此约束确保两者不能同时被选择生产。
    *   **公式:** $y_1 + y_4 \le 1$

4.  **条件生产约束 (Conditional Production Constraint):**
    *   **说明:** 如果生产模型车 ($y_2=1$)，则必须生产积木 ($y_3=1$)。
    *   **公式:** $y_2 \le y_3$

5.  **生产数量关系约束 (Production Quantity Relation Constraint):**
    *   **说明:** 生产的娃娃数量不能超过生产的模型车数量。
    *   **公式:** $x_4 \le x_2$

6.  **变量连接约束 (Linking Constraints):**
    *   **说明:** 这组约束将生产数量变量 ($x_i$) 与生产决策变量 ($y_i$) 紧密地关联起来，建立起“当且仅当决定生产时，产量才为正”的逻辑。
    *   **公式 (上界):** $x_i \le M_i \cdot y_i, \forall i \in T$
        *   此公式规定，如果未决定生产玩具 $i$ ($y_i=0$)，则其产量 $x_i$ 必须为0。如果决定生产 ($y_i=1$)，则其产量 $x_i$ 不能超过理论最大值 $M_i$。使用计算出的紧凑值 $M_i$ 而非任意大数，可以提高模型的数值稳定性和求解效率。
    *   **公式 (下界):** $x_i \ge y_i, \forall i \in T$
        *   此公式规定，如果决定生产玩具 $i$ ($y_i=1$)，则其产量 $x_i$ 必须至少为1（因为 $x_i$ 是整数），从而避免了 $y_i=1$ 但 $x_i=0$ 的无意义解。

7.  **变量类型约束 (Variable Type Constraints):**
    *   **说明:** 定义每个变量的取值范围。
    *   **公式:**
        *   $x_i \in \mathbb{Z}^+, \forall i \in T$ (生产数量为非负整数)
        *   $y_i \in \{0, 1\}, \forall i \in T$ (生产决策为二元变量)