In network communication services, bandwidth plays an important role. Below is a bandwidth communication table between several communication nodes, showing the bandwidth between any two nodes. If two nodes cannot be directly connected, the corresponding bandwidth is $0$. It is required to establish a link between node $A$ and node $E$ that must pass through service node $C$ (without loops). The bandwidth of this link is defined as the minimum bandwidth value on the link. Please propose a reasonable link arrangement to maximize the bandwidth of this link and find out the maximum bandwidth.

\begin{table}[h]
\centering
\begin{tabular}{|c|c|c|c|c|c|}
\hline
& A & B & C & D & E \\
\hline
A & 0 & 90 & 85 & 0 & 65 \\
\hline
B & 95 & 0 & 70 & 65 & 34 \\
\hline
C & 60 & 0 & 0 & 88 & 80 \\
\hline
D & 67 & 30 & 25 & 0 & 84 \\
\hline
E & 0 & 51 & 0 & 56 & 0 \\
\hline
\end{tabular}
\end{table}

# 问题

## 问题描述
在一个由多个通信节点组成的网络中，给定任意两个节点间的有向带宽值。要求规划一条从起始节点 $A$ 到终点节点 $E$ 的通信链路，该链路必须经过一个特定的服务节点 $C$，并且不能包含回路（即为一条简单路径）。链路的整体带宽被定义为该链路上所有路段带宽的最小值。目标是找出一条满足条件的链路，使其整体带宽最大化，并确定这个最大的带宽值。

## 问题分析
此问题是一个**最大瓶颈路径问题 (Maximum Bottleneck Path Problem)**。其核心目标是最大化路径上权重最小的边的权重。

由于路径被强制要求通过节点 $C$，最清晰且健壮的建模策略是将问题**分解为两个独立的、连续的子问题**：
1.  **子问题一:** 寻找一条从 $A$ 到 $C$ 的最大瓶颈路径。
2.  **子问题二:** 寻找一条从 $C$ 到 $E$ 的最大瓶颈路径，其约束条件是不能使用子问题一中已经用过的中间节点，以确保最终合成的路径是一条无环的简单路径。

最终的整体瓶颈带宽将是这两个子问题求得的瓶颈带宽中的较小值。每个子问题都可以被精确地构建为一个**混合整数线性规划 (Mixed-Integer Linear Programming, MILP)** 模型。

## 核心假设
1.  **有向连接:** 节点间的带宽是单向的，即从 $i \to j$ 的连接不意味着存在 $j \to i$ 的连接。
2.  **带宽非负:** 所有带宽值均为非负数。带宽为 $0$ 表示两个节点间不存在直接的通信链路。
3.  **路径简单性:** 最终的 $A \to C \to E$ 链路是一条简单路径，即除了起始节点 $A$、中转节点 $C$ 和终止节点 $E$ 外，路径不会重复访问任何节点。

## 数据定义
问题中的数据可以被组织成节点集合和节点间的带宽参数。

*   **集合 (Sets)**
    *   $N$: 所有通信节点的集合。$N = \{A, B, C, D, E\}$。

*   **参数 (Parameters)**
    *   $c_{ij}$: 从节点 $i$ 到节点 $j$ 的直接链路的带宽值, 其中 $i, j \in N$。如果不存在直接链路，则 $c_{ij} = 0$。

# 数学形式

该问题通过一个两阶段的流程来求解。

---

### **阶段一: 求解 A 到 C 的最大瓶颈路径**

首先，我们构建模型来寻找从节点 $A$ 到节点 $C$ 的最大瓶颈路径。

#### **变量定义**
*   $x_{ij}$: 一个二元变量。如果选择从节点 $i$ 到节点 $j$ 的链路作为 $A \to C$ 路径的一部分，则 $x_{ij}=1$；否则 $x_{ij}=0$。
*   $b_{AC}$: 一个非负连续变量，代表 $A \to C$ 路径的瓶颈带宽。
*   $u_i$: 一个辅助连续变量，用于消除子环路（MTZ约束），表示节点 $i$ 在路径中的顺序。

#### **目标函数**
*   **最大化 A-C 瓶颈带宽:** $\max b_{AC}$

#### **约束条件**
1.  **流量守恒约束 (Flow Conservation):**
    *   **说明:** 定义路径的起点和终点，并确保路径的连续性。
    *   **公式:**
        *   $\sum_{j \in N, j \neq A} x_{Aj} - \sum_{j \in N, j \neq A} x_{jA} = 1$ (节点A净流出为1)
        *   $\sum_{j \in N, j \neq C} x_{jC} - \sum_{j \in N, j \neq C} x_{Cj} = -1$ (节点C净流入为1)
        *   $\sum_{j \in N, j \neq k} x_{kj} - \sum_{j \in N, j \neq k} x_{jk} = 0, \forall k \in N \setminus \{A, C\}$ (其他节点流量守恒)
        *   $\sum_{j \in N, j \neq k} x_{jk} \le 1, \forall k \in N \setminus \{A\}$ (每个节点最多进入一次)

2.  **瓶颈带宽定义约束 (Bottleneck Definition):**
    *   **说明:** 瓶颈带宽 $b_{AC}$ 不能超过路径上任何被选中链路的带宽。
    *   **公式:** $b_{AC} \le c_{ij} + M \cdot (1 - x_{ij}), \forall i, j \in N, i \neq j$
        *   注: $M$ 是一个足够大的正数，可取 $M = \max_{i,j} \{c_{ij}\}$。

3.  **子环路消除约束 (Subtour Elimination - MTZ):**
    *   **说明:** 确保所有被选中的链路形成一条从 $A$ 到 $C$ 的单一连通路径。
    *   **公式:** $u_i - u_j + 1 \le (|N|-1)(1-x_{ij}), \forall i, j \in N \setminus \{A\}, i \neq j$
    *   **公式:** $1 \le u_i \le |N|-1, \forall i \in N \setminus \{A\}$

4.  **变量类型约束 (Variable Type):**
    *   **公式:**
        *   $x_{ij} \in \{0, 1\}, \forall i, j \in N, i \neq j$
        *   $b_{AC} \ge 0$
        *   $u_i \ge 0, \forall i \in N \setminus \{A\}$

---

### **阶段二: 求解 C 到 E 的最大瓶颈路径**

在求解阶段一后，我们得到最优的 $A \to C$ 路径。设该路径所经过的节点集合为 $N_{AC}^*$。阶段二的目标是在剩余可用节点中寻找从 $C$ 到 $E$ 的最大瓶颈路径。

*   **定义可用节点集:** $N' = N \setminus (N_{AC}^* \setminus \{A, C\})$。这排除了在 $A \to C$ 路径中已经使用过的中间节点。

#### **变量定义**
*   $y_{ij}$: 一个二元变量。如果选择从节点 $i$ 到节点 $j$ 的链路作为 $C \to E$ 路径的一部分，则 $y_{ij}=1$；否则 $y_{ij}=0$。
*   $b_{CE}$: 一个非负连续变量，代表 $C \to E$ 路径的瓶颈带宽。
*   $v_i$: 一个辅助连续变量，用于消除子环路。

#### **目标函数**
*   **最大化 C-E 瓶颈带宽:** $\max b_{CE}$

#### **约束条件**
此模型的约束条件与阶段一类似，但作用于可用节点集 $N'$。

1.  **流量守恒约束 (Flow Conservation):**
    *   **公式:**
        *   $\sum_{j \in N', j \neq C} y_{Cj} - \sum_{j \in N', j \neq C} y_{jC} = 1$ (节点C净流出为1)
        *   $\sum_{j \in N', j \neq E} y_{jE} - \sum_{j \in N', j \neq E} y_{Ej} = -1$ (节点E净流入为1)
        *   $\sum_{j \in N', j \neq k} y_{kj} - \sum_{j \in N', j \neq k} y_{jk} = 0, \forall k \in N' \setminus \{C, E\}$
        *   $\sum_{j \in N', j \neq k} y_{jk} \le 1, \forall k \in N' \setminus \{C\}$

2.  **瓶颈带宽定义约束 (Bottleneck Definition):**
    *   **公式:** $b_{CE} \le c_{ij} + M \cdot (1 - y_{ij}), \forall i, j \in N', i \neq j$

3.  **子环路消除约束 (Subtour Elimination - MTZ):**
    *   **公式:** $v_i - v_j + 1 \le (|N'|-1)(1-y_{ij}), \forall i, j \in N' \setminus \{C\}, i \neq j$
    *   **公式:** $1 \le v_i \le |N'|-1, \forall i \in N' \setminus \{C\}$

4.  **变量类型约束 (Variable Type):**
    *   **公式:**
        *   $y_{ij} \in \{0, 1\}, \forall i, j \in N', i \neq j$
        *   $b_{CE} \ge 0$
        *   $v_i \ge 0, \forall i \in N' \setminus \{C\}$

---

### **最终解的合成**

1.  **最优路径:** 最终的路径由阶段一和阶段二的最优解组合而成。路径为 $\{ (i,j) | x_{ij}^*=1 \} \cup \{ (i,j) | y_{ij}^*=1 \}$。
2.  **最大带宽:** 最终链路的最大瓶颈带宽是两个子路径瓶颈带宽中的较小者。
    *   **公式:** $b_{max} = \min(b_{AC}^*, b_{CE}^*)$
    *   其中 $b_{AC}^*$ 和 $b_{CE}^*$ 分别是阶段一和阶段二模型求得的最优目标函数值。