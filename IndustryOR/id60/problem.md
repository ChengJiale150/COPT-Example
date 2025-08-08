A traveling salesman must visit 7 customers at 7 different locations, with the (symmetric) distance matrix as follows:

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | - | 86 | 49 | 57 | 31 | 69 | 50 |
| 2 | | - | 68 | 79 | 93 | 24 | 5 |
| 3 | | | - | 16 | 7 | 72 | 67 |
| 4 | | | | - | 90 | 69 | 1 |
| 5 | | | | | - | 86 | 59 |
| 6 | | | | | | - | 81 |

Formulate a mathematical program to determine the visiting order starting and ending at location 1 to minimize the travel distance, and solve it using COPTPY.

# 问题

## 问题描述
一名旅行商需要从1号地点出发，访问其余6个不同的客户地点（共7个地点），最后返回1号地点。给定一个对称的距离矩阵，目标是规划一条访问顺序，使得总旅行距离最短。在此过程中，每个客户地点必须且只能被访问一次。

## 问题分析
这是一个经典的**对称旅行商问题 (Symmetric Traveling Salesman Problem, STSP)**，是组合优化领域中最著名的问题之一，属于NP-hard问题。其目标是在一个图中寻找一条经过所有节点一次且仅一次的、总权重（距离）最小的哈密顿回路。

该问题可以被构建为一个**混合整数线性规划 (Mixed-Integer Linear Programming, MILP)** 模型。主流的建模方法有两种：
1.  **DFJ (Dantzig-Fulkerson-Johnson) 公式**: 通过添加割集约束来消除子回路。该方法理论上更紧凑，对于大规模问题求解效率更高，但其约束数量是指数级的，通常需要借助“延迟约束生成”等高级技巧来实现。
2.  **MTZ (Miller-Tucker-Zemlin) 公式**: 通过引入辅助的顺序变量来消除子回路。该方法的约束数量是多项式级的，模型结构简单，易于直接实现。

虽然本问题是对称的，但为了展示一种直观且易于实现的建模方式，我们将采用MTZ公式，该公式建立在一个有向图的表示之上。

## 核心假设
1.  **图的完备性:** 任意两个地点之间都存在路径，构成一个完全图。
2.  **距离对称性:** 从地点 $i$ 到地点 $j$ 的距离与从 $j$ 到 $i$ 的距离相等 ($c_{ij} = c_{ji}$)。
3.  **回路唯一性:** 必须形成一个包含所有地点的单一闭合回路，而非多个不相连的子回路。
4.  **访问唯一性:** 除起点和终点为同一地点外，路径中不重复访问任何地点。

## 数据定义
此问题中包含两类核心数据：地点的集合和地点间的距离。在建模前，需对原始数据进行预处理。

*   **数据预处理:**
    1.  将给定的上三角距离矩阵扩展为一个完整的、$n \times n$ 的对称方阵。
    2.  为防止模型选择无效的自环路径 (如 $i \to i$)，将对角线元素 $c_{ii}$ 的值设为一个足够大的数（理论上为无穷大）。

*   **集合 (Sets)**
    *   $V$: 所有地点的集合, $V = \{1, 2, 3, 4, 5, 6, 7\}$。
    *   $V'$: 除起始点外的所有客户地点的集合, $V' = V \setminus \{1\} = \{2, 3, 4, 5, 6, 7\}$。

*   **参数 (Parameters)**
    *   $c_{ij}$: 从地点 $i$ 到地点 $j$ 的旅行距离。
    *   $n$: 地点的总数, $n = |V| = 7$。

# 数学形式

## 变量定义
*   **路径选择变量 (Path Selection Variables):**
    *   $x_{ij}$: 一个二元变量。如果旅行商选择从地点 $i$ 直接前往地点 $j$，则 $x_{ij}=1$；否则 $x_{ij}=0$。
        *   $x_{ij} \in \{0, 1\}, \forall i, j \in V, i \neq j$

*   **辅助顺序变量 (Auxiliary Sequence Variables):**
    *   $u_i$: 一个连续或整数变量，用于表示客户地点 $i$ 在整个访问路径中的顺序。此变量仅对 $V'$ 中的客户地点定义。
        *   $u_i \ge 0, \forall i \in V'$

## 目标函数
我们的目标是最小化整个旅程的总旅行距离。
*   **最小化总距离:** $\min \sum_{i \in V} \sum_{j \in V, j \neq i} c_{ij} \cdot x_{ij}$

## 约束条件
模型必须满足以下约束：

1.  **出度约束 (Departure Constraint):**
    *   **说明:** 对于每一个地点，旅行商必须且只能离开一次。
    *   **公式:** $\sum_{j \in V, j \neq i} x_{ij} = 1, \quad \forall i \in V$

2.  **入度约束 (Arrival Constraint):**
    *   **说明:** 对于每一个地点，旅行商必须且只能到达一次。
    *   **公式:** $\sum_{i \in V, i \neq j} x_{ij} = 1, \quad \forall j \in V$

3.  **子回路消除约束 (Subtour Elimination Constraint - MTZ Formulation):**
    *   **说明:** 此组约束是MTZ模型的核心，用以保证所有选择的路径能连接成一个单一的、不间断的大回路。它通过建立路径选择变量 $x_{ij}$ 和顺序变量 $u_i, u_j$ 之间的逻辑关系来实现。
        *   **当 $x_{ij}=1$ 时** (即选择路径 $i \to j$): 约束变为 $u_i - u_j + n \le n-1$, 化简得 $u_j \ge u_i + 1$。这强制要求节点 $j$ 的访问次序（由 $u_j$ 表示）必须在节点 $i$ 的次序之后，从而在路径中建立了正确的先后关系。
        *   **当 $x_{ij}=0$ 时** (即不选择路径 $i \to j$): 约束变为 $u_i - u_j \le n-1$。考虑到 $u_i$ 和 $u_j$ 的取值范围，这是一个自然成立的冗余约束，不会对未选择的路径施加任何限制。
    *   **公式:** $u_i - u_j + n \cdot x_{ij} \le n-1, \quad \forall i, j \in V', i \neq j$

4.  **辅助变量边界约束 (Auxiliary Variable Bounds):**
    *   **说明:** 为确保MTZ约束的有效性，需要为辅助变量 $u_i$ 设置合理的取值范围。路径从起点1开始，因此客户地点的顺序在2到n之间。
    *   **公式:** $2 \le u_i \le n, \quad \forall i \in V'$

5.  **变量类型约束 (Variable Type Constraint):**
    *   **说明:** 路径选择变量 $x_{ij}$ 必须是二元的。
    *   **公式:** $x_{ij} \in \{0, 1\}, \quad \forall i, j \in V, i \neq j$