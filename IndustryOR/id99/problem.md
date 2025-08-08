An electronic system is composed of 3 types of components. The system operates normally if all three components function properly. By installing one or more spare parts for any of the components, the reliability of the components can be improved. The system's operational reliability is the product of the reliabilities of each component, and the reliability of each component is a function of the number of spare parts installed. The first half of the table below shows the function relationship between the number of spare parts and the reliability of a specific component. The prices and weights of the 3 types of components are shown in rows 8 to 9 of the table. Given that the total budget for all spare parts is limited to 150 yuan, and the weight limit is 20 kg, how should spare parts be installed to maximize the system's operational reliability?

\begin{table}[h]
\centering
\begin{tabular}{|c|c|c|c|}
\hline
\textbf{Component Number} & \textbf{1} & \textbf{2} & \textbf{3} \\ \hline
\textbf{Number of Spares} & & & \\ \hline
0 & 0.5 & 0.6 & 0.7 \\ \hline
1 & 0.6 & 0.75 & 0.9 \\ \hline
2 & 0.7 & 0.95 & 1.0 \\ \hline
3 & 0.8 & 1.0 & 1.0 \\ \hline
4 & 0.9 & 1.0 & 1.0 \\ \hline
5 & 1.0 & 1.0 & 1.0 \\ \hline
\textbf{Unit Price (yuan)} & 20 & 30 & 40 \\ \hline
\textbf{Unit Weight (kg)} & 2 & 4 & 6 \\ \hline
\end{tabular}
\caption{Spare Component Data Table}
\end{table}

# 问题

## 问题描述
一个电子系统由三种不同类型的组件构成，系统正常运行的前提是所有三种组件都能正常工作。通过为任一组件安装一个或多个备件，可以提高该组件的可靠性。系统的总运行可靠性是各组件可靠性的乘积，而每个组件的可靠性是其所安装备件数量的函数。现有预算上限为150元，总重量限制为20公斤，需要确定为每种组件安装多少备件，才能使整个系统的运行可靠性达到最大。

## 问题分析
此问题本质上是一个在多重资源（预算、重量）约束下的最优分配问题。其最直观的数学形式是一个**非线性整数规划 (Non-Linear Integer Programming, NLIP)**。这是因为目标函数是各个组件可靠性的乘积，呈现非线性特征，而决策变量（备件数量）必须为整数。

直接求解非线性乘积形式的目标函数通常计算成本高昂且复杂。为了构建一个更高效、更易于求解的模型，我们采用**对数变换**这一关键技巧。由于对数函数是单调递增的，最大化一个正数的乘积（$\max \prod R_i$）等价于最大化其对数的和（$\max \sum \log(R_i)$）。

通过此变换，我们将原始的非线性目标函数成功转化为线性形式，从而将整个问题重构为一个标准的**0-1整数线性规划 (0-1 Integer Linear Programming)** 问题。这种模型可以被成熟的商业或开源优化求解器高效、可靠地求解。

## 核心假设
1.  **系统可靠性模型**: 系统的可靠性是各组件可靠性的直接乘积，这意味着各组件的失效是相互独立的事件。
2.  **增量成本与重量假设**: 预算和重量的计算仅针对新增加的**备件**，不包括系统中已存在的基础组件（即备件数量为0时对应的组件）。因此，为组件 $i$ 安装 $j$ 个备件的成本为 $c_i \cdot j$，重量为 $w_i \cdot j$。
3.  **数据范围假设**: 每种组件可安装的备件数量上限为5个，这是基于所提供数据表的范围得出的结论。模型不考虑超过5个备件的可能性。
4.  **可靠性正值假设**: 所有组件在任何备件配置下的可靠性 $R_{ij}$ 均为严格正数。这是对数变换方法能够成立的必要数学前提。

## 数据定义
此问题中的数据可以被结构化为集合与参数。

*   **集合 (Sets)**
    *   $I$: 组件类型的集合, $I = \{1, 2, 3\}$。
    *   $J$: 可选的备件数量的集合, $J = \{0, 1, 2, 3, 4, 5\}$。

*   **参数 (Parameters)**
    *   $R_{ij}$: 组件 $i$ 在安装 $j$ 个备件时的可靠性。
    *   $c_i$: 组件 $i$ 的单位备件价格 (单位: 元)。
    *   $w_i$: 组件 $i$ 的单位备件重量 (单位: 公斤)。
    *   $C_{max}$: 最大预算限制, $C_{max} = 150$ 元。
    *   $W_{max}$: 最大重量限制, $W_{max} = 20$ 公斤。

具体数值如下表所示：

| 参数 | 组件 1 ($i=1$) | 组件 2 ($i=2$) | 组件 3 ($i=3$) |
| :--- | :--- | :--- | :--- |
| **可靠性 $R_{ij}$** | | | |
| $j=0$ | 0.5 | 0.6 | 0.7 |
| $j=1$ | 0.6 | 0.75 | 0.9 |
| $j=2$ | 0.7 | 0.95 | 1.0 |
| $j=3$ | 0.8 | 1.0 | 1.0 |
| $j=4$ | 0.9 | 1.0 | 1.0 |
| $j=5$ | 1.0 | 1.0 | 1.0 |
| **价格 $c_i$ (元)** | 20 | 30 | 40 |
| **重量 $w_i$ (公斤)** | 2 | 4 | 6 |

# 数学形式

## 变量定义
为了将离散选择线性化，我们定义如下的二元决策变量：
*   $x_{ij}$: 一个二元变量。如果为组件 $i$ 选择安装 $j$ 个备件，则 $x_{ij}=1$；否则 $x_{ij}=0$。
    *   $x_{ij} \in \{0, 1\}, \forall i \in I, j \in J$

我们没有直接使用整数变量“备件数量”，而是采用了一组二元变量 $x_{ij}$。这种方法将一个离散的多值选择（为组件 $i$ 选择安装多少备件）转化为一组互斥的二元选择（是否为组件 $i$ 选择方案 $j$），从而保持了模型的完全线性，这对于高效求解至关重要。

## 目标函数
*   **最大化总可靠性的对数:** $\max \sum_{i \in I} \sum_{j \in J} \log(R_{ij}) \cdot x_{ij}$
    *   **说明:** 这个线性化的目标函数与原始的非线性目标在最优点上是等价的，但其结构使得问题能被标准的混合整数线性规划（MILP）求解器高效求解。

## 约束条件
模型必须满足以下约束：

1.  **唯一选择约束 (Unique Choice Constraint):**
    *   **说明:** 对于每一种组件，必须且只能选择一个备件方案（包括选择0个备件）。
    *   **公式:** $\sum_{j \in J} x_{ij} = 1, \forall i \in I$

2.  **预算约束 (Budget Constraint):**
    *   **说明:** 所有已安装备件的总成本不能超过预算上限。
    *   **公式:** $\sum_{i \in I} \sum_{j \in J} (c_i \cdot j) \cdot x_{ij} \le C_{max}$

3.  **重量约束 (Weight Constraint):**
    *   **说明:** 所有已安装备件的总重量不能超过重量上限。
    *   **公式:** $\sum_{i \in I} \sum_{j \in J} (w_i \cdot j) \cdot x_{ij} \le W_{max}$

4.  **变量类型约束 (Variable Type Constraint):**
    *   **说明:** 决策变量为二元变量，只能取0或1。
    *   **公式:** $x_{ij} \in \{0, 1\}, \forall i \in I, \forall j \in J$