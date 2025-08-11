An Italian transportation company needs to move some empty containers from its 6 warehouses (located in Verona, Perugia, Rome, Pescara, Taranto, and Lamezia) to major national ports (Genoa, Venice, Ancona, Naples, Bari). The container inventory at the warehouses is as follows:

| | Empty Containers |
|:---:|:---:|
| Verona | 10 |
| Perugia | 12 |
| Rome | 20 |
| Pescara | 24 |
| Taranto | 18 |
| Lamezia | 40 |

The demand at the ports is as follows:

| | Container Demand |
|:---:|:---:|
| Genoa | 20 |
| Venice | 15 |
| Ancona | 25 |
| Naples | 33 |
| Bari | 21 |

The transport is carried out by a fleet of trucks. The cost to transport each container is proportional to the distance traveled by the trucks, with a rate of 30 euros per kilometer. Each truck can carry up to 2 containers. The distances are as follows:

| | Genoa | Venice | Ancona | Naples | Bari |
|:---:|:---:|:---:|:---:|:---:|:---:|
| Verona | $290 \mathrm{~km}$ | $115 \mathrm{~km}$ | $355 \mathrm{~km}$ | $715 \mathrm{~km}$ | $810 \mathrm{~km}$ |
| Perugia | $380 \mathrm{~km}$ | $340 \mathrm{~km}$ | $165 \mathrm{~km}$ | $380 \mathrm{~km}$ | $610 \mathrm{~km}$ |
| Rome | $505 \mathrm{~km}$ | $530 \mathrm{~km}$ | $285 \mathrm{~km}$ | $220 \mathrm{~km}$ | $450 \mathrm{~km}$ |
| Pescara | $655 \mathrm{~km}$ | $450 \mathrm{~km}$ | $155 \mathrm{~km}$ | $240 \mathrm{~km}$ | $315 \mathrm{~km}$ |
| Taranto | $1010 \mathrm{~km}$ | $840 \mathrm{~km}$ | $550 \mathrm{~km}$ | $305 \mathrm{~km}$ | $95 \mathrm{~km}$ |
| Lamezia | $1072 \mathrm{~km}$ | $1097 \mathrm{~km}$ | $747 \mathrm{~km}$ | $372 \mathrm{~km}$ | $333 \mathrm{~km}$ |

# 问题

## 问题描述
一家意大利运输公司计划将其位于6个仓库（维罗纳、佩鲁贾、罗马、佩斯卡拉、塔兰托、拉默齐亚）的空集装箱，调运至5个主要港口（热那亚、威尼斯、安科纳、那不勒斯、巴里）。每个仓库有一定数量的库存，每个港口有一定数量的需求。运输通过卡车队完成，每辆卡车最多可装载2个集装箱。运输成本与卡车行驶距离成正比，费率为每公里30欧元。目标是制定一个运输计划，在满足所有港口需求的前提下，最小化总运输成本。

## 问题分析
这是一个经典的**运输问题 (Transportation Problem)**的变体。其核心挑战在于非线性的成本结构：运输成本是所运集装箱数量的**阶梯函数 (Step Function)**，因为它取决于派遣的卡车数量（运1个或2个集装箱都需要派遣一辆卡车，成本相同）。为了解决这个问题，需要通过引入一个表示卡车数量的整数变量，将此问题**线性化**，最终构建为一个**混合整数线性规划 (Mixed-Integer Linear Programming, MILP)** 模型。

## 核心假设
1.  **供应充足**: 总供应量（124个集装箱）大于总需求量（114个集装箱），因此所有港口的需求都可以被满足。
2.  **成本结构**: 运输成本仅与派遣的卡车数量和行驶距离有关，而与卡车是否满载（即装载1个或2个集装箱）无关。
3.  **资源可用性**: 在每个仓库，可供调遣的卡车数量不受限制。
4.  **静态单周期模型**: 此模型为静态规划模型，不考虑运输时间、发货或到货的时间窗口限制。
5.  **路径直达**: 卡车从一个仓库直接驶向一个港口，不存在中途停靠。
6.  **整数变量**: 运输的集装箱数量和派遣的卡车数量都必须是整数。

## 数据定义
此问题中的数据可分为集合、供应与需求参数、以及成本相关参数。

*   **集合 (Sets)**
    *   $W$: 所有仓库（供应点）的集合。$W = \{\text{维罗纳, 佩鲁贾, 罗马, 佩斯卡拉, 塔兰托, 拉默齐亚}\}$
    *   $P$: 所有港口（需求点）的集合。$P = \{\text{热那亚, 威尼斯, 安科纳, 那不勒斯, 巴里}\}$

*   **参数 (Parameters)**
    *   $S_i$: 仓库 $i$ 的空集装箱供应量 (单位: 个), $\forall i \in W$。
    *   $D_j$: 港口 $j$ 的空集装箱需求量 (单位: 个), $\forall j \in P$。
    *   $d_{ij}$: 从仓库 $i$ 到港口 $j$ 的距离 (单位: 公里), $\forall i \in W, j \in P$。
    *   $C$: 每辆卡车每公里的运输费率。$C = 30$ 欧元/公里。
    *   $K$: 每辆卡车的最大装载容量。$K = 2$ 个集装箱/卡车。

上述参数的具体数值分别对应下方的“供应数据”、“需求数据”和“距离数据”表格。

**供应数据:**
| 仓库 $i$ | 供应量 $S_i$ |
| :--- | :--- |
| 维罗纳 | 10 |
| 佩鲁贾 | 12 |
| 罗马 | 20 |
| 佩斯卡拉 | 24 |
| 塔兰托 | 18 |
| 拉默齐亚 | 40 |

**需求数据:**
| 港口 $j$ | 需求量 $D_j$ |
| :--- | :--- |
| 热那亚 | 20 |
| 威尼斯 | 15 |
| 安科纳 | 25 |
| 那不勒斯 | 33 |
| 巴里 | 21 |

**距离数据 $d_{ij}$ (km):**
| | 热那亚 | 威尼斯 | 安科纳 | 那不勒斯 | 巴里 |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 维罗纳 | 290 | 115 | 355 | 715 | 810 |
| 佩鲁贾 | 380 | 340 | 165 | 380 | 610 |
| 罗马 | 505 | 530 | 285 | 220 | 450 |
| 佩斯卡拉 | 655 | 450 | 155 | 240 | 315 |
| 塔兰托 | 1010 | 840 | 550 | 305 | 95 |
| 拉默齐亚 | 1072 | 1097 | 747 | 372 | 333 |

# 数学形式

## 变量定义
为了构建模型，我们需要定义两组决策变量：
*   $x_{ij}$: 从仓库 $i$ 运输到港口 $j$ 的**集装箱数量**。这是一个非负整数变量。
    *   $x_{ij} \in \mathbb{Z}^+ \cup \{0\}, \forall i \in W, \forall j \in P$
*   $t_{ij}$: 从仓库 $i$ 派遣到港口 $j$ 的**卡车数量**。这是一个非负整数变量。
    *   $t_{ij} \in \mathbb{Z}^+ \cup \{0\}, \forall i \in W, \forall j \in P$

**建模思路**: 变量 $x_{ij}$ 是我们关心的物理流动，但成本与它并非线性关系。因此，我们引入辅助变量 $t_{ij}$ 作为成本的直接计算载体，并通过约束将两者关联起来，从而实现模型的线性化。

## 目标函数
我们的目标是最小化总运输成本。总成本是所有路线上的卡车运输成本之和。
*   **最小化总成本:** $\min \sum_{i \in W} \sum_{j \in P} C \cdot d_{ij} \cdot t_{ij}$
    *   **说明:** 该公式计算了从每个仓库 $i$ 到每个港口 $j$ 的卡车数量 $t_{ij}$，乘以相应的距离 $d_{ij}$ 和单位成本 $C$，然后将所有路线的成本相加，得到总成本。

## 约束条件
模型的决策必须满足以下所有限制：

1.  **供应约束 (Supply Constraint):**
    *   **说明:** 对于每一个仓库，运出的集装箱总数不能超过其库存量。
    *   **公式:** $\sum_{j \in P} x_{ij} \le S_i, \quad \forall i \in W$

2.  **需求满足约束 (Demand Fulfillment Constraint):**
    *   **说明:** 对于每一个港口，收到的集装箱总数必须恰好等于其需求量。
    *   **公式:** $\sum_{i \in W} x_{ij} = D_j, \quad \forall j \in P$

3.  **卡车-集装箱关联约束 (Truck-Container Linking Constraint):**
    *   **说明:** 此线性约束将运输的集装箱数量与派遣的卡车数量关联起来。至关重要的是，当它与最小化目标函数相结合时，能够在线性框架内精确地模拟非线性的向上取整关系，即 $t_{ij} = \lceil x_{ij} / K \rceil$。为了最小化总成本，优化器将被迫为给定的 $x_{ij}$ 选择满足此不等式的最小整数 $t_{ij}$，从而避免派遣不必要的卡车。
    *   **公式:** $x_{ij} \le K \cdot t_{ij}, \quad \forall i \in W, \forall j \in P$

4.  **变量类型约束 (Variable Type Constraint):**
    *   **说明:** 运输的集装箱数量和派遣的卡车数量都必须是非负整数。
    *   **公式:** $x_{ij} \in \mathbb{Z}^+, t_{ij} \in \mathbb{Z}^+, \quad \forall i \in W, \forall j \in P$
    *   *注：$\mathbb{Z}^+$ 表示非负整数集合 $\{0, 1, 2, ...\}$。*