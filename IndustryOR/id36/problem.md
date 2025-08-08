The Vehicle Routing Problem (VRP) was first proposed by Dantzig and Ramser in 1959. It is a classic combinatorial optimization problem. The basic VRP can be described as follows: in a certain area, there is a number of customers and a distribution center or depot. Customers are generally located at different positions, and each has a specific demand for goods. The distribution center needs to dispatch a fleet of vehicles and design appropriate delivery routes to fulfill the demands of all customers. The objective of VRP is to optimize a certain benefit metric while satisfying all customer demands. The benefit metric is usually presented as an objective function, which varies according to the company's requirements. Common objective functions include minimizing the total distance traveled by vehicles, minimizing the total delivery time, or minimizing the number of vehicles used. In addition to satisfying customer demands, VRP often needs to consider various other constraints, leading to several variants. For example, if the vehicle's load cannot exceed its maximum capacity, the problem becomes the Capacitated Vehicle Routing Problem (CVRP). If each customer's delivery must be made within a specific time frame, the problem becomes the Vehicle Routing Problem with Time Windows (VRPTW).

The Vehicle Routing Problem with Time Windows (VRPTW) is a classic variant of the VRP. There are many real-world applications of VRPTW, as customer locations often have service time windows. For instance, some logistics centers need to stock parcels during off-peak hours, and large supermarkets need to replenish goods outside of business hours. Real-time delivery services like food delivery also require strict delivery time windows. Time windows can be categorized as hard or soft. A Hard Time Window (HTW) means that a vehicle must arrive at the delivery point within or before the time window; late arrivals are not permitted. If a vehicle arrives early, it must wait until the time window opens to begin service. This is common in scenarios like supermarket restocking and logistics center inbound operations. A Soft Time Window (STW) means that a vehicle is not strictly required to arrive within the time window, but it is encouraged to do so. A penalty is incurred for early or late arrivals. This is applicable in scenarios such as meal delivery, school bus services, and industrial deliveries.

The Vehicle Routing Problem with Hard Time Windows (VRPHTW) can be described as follows: within a region, there is a set of customer locations and a central depot. Vehicles must start from the depot and return to the depot, following continuous paths. Each customer must be served by exactly one vehicle, and vehicles have a limited capacity. Each customer has a specific service time window, and service is only accepted within this window. A vehicle can arrive at a customer location early and wait for the time window to open, or it can arrive within the time window to provide service. Service can only begin within the time window, and the service duration is known. The distribution center must arrange an optimal delivery plan to both complete the delivery tasks and minimize travel costs. Because VRPHTW does not allow for delays, it, like the VRP, primarily emphasizes the minimization of travel costs along the routes.

Now we consider a major enterprise logistics provider, 'Global Logistics', is responsible for providing precise material delivery services for multiple high-end office buildings and shops in a city's central business district (CBD). Due to traffic control in the CBD and the specific receiving requirements of the customers, the delivery task is highly challenging.

**Specific Requirements:**

1. **Delivery Task**: There are 20 customers requiring delivery service on the day, and the demands of all customers must be met.
2. **Vehicle Constraints**: The company can use at most 5 trucks, and the capacity of each truck is 200 units.
3. **Capacity Constraint**: The total demand of all customers on a single route must not exceed the truck's maximum capacity (200 units).
4. **Time Window Constraint**: Each customer has a strict 'hard time window.' Service must begin within this specified time window. Early arrivals must wait, and late arrivals are not permitted.
5. **Service Time**: Due to the complex handover procedures at customer sites, a fixed service time of 90 minutes is required for unloading, handover, and paperwork at each customer location.
6. **Optimization Objective**: While satisfying all constraints, the company's objective is to **minimize the total distance traveled by all vehicles** to reduce operational costs.

**Data Details:**

* **Central Depot (Depot 0)**:
* Coordinates: (40, 50)
* Operating Time Window: [0, 1236] (minutes)
* **Customer Locations (Customers 1-20)**: The coordinates, demand, service time window, and service duration for each customer are shown in the table below.

| Customer ID | Coordinates (X, Y) | Demand (units) | Time Window (minutes) | Service Duration (minutes) |
| :--- | :--- | :--- |:--- | :--- |
| 1 | (45, 68) | 10 | [912, 967] | 90 |
| 2 | (45, 70) | 30 | [825, 870] | 90 |
| 3 | (42, 66) | 10 | [65, 146] | 90 |
| 4 | (42, 68) | 10 | [727, 782] | 90 |
| 5 | (42, 65) | 10 | [15, 67] | 90 |
| 6 | (40, 69) | 20 | [621, 702] | 90 |
| 7 | (40, 66) | 20 | [170, 225] | 90 |
| 8 | (38, 68) | 20 | [255, 324] | 90 |
| 9 | (38, 70) | 10 | [534, 605] | 90 |
| 10 | (35, 66) | 10 | [357, 410] | 90 |
| 11 | (35, 69) | 10 | [448, 505] | 90 |
| 12 | (25, 85) | 20 | [652, 721] | 90 |
| 13 | (22, 75) | 30 | [30, 92] | 90 |
| 14 | (22, 85) | 10 | [567, 620] | 90 |
| 15 | (20, 80) | 40 | [384, 429] | 90 |
| 16 | (20, 85) | 40 | [475, 528] | 90 |
| 17 | (18, 75) | 20 | [99, 148] | 90 |
| 18 | (15, 75) | 20 | [179, 254] | 90 |
| 19 | (15, 80) | 10 | [278, 345] | 90 |
| 20 | (30, 50) | 10 | [10, 73] | 90 |

Now, please provide an operations research model for this VRPHTW.

# 问题

## 问题描述
一家名为“Global Logistics”的企业需要为城市中心商务区（CBD）的20个客户提供物资配送服务。该任务需要从一个中心仓库出发，使用一支最多由5辆卡车组成的车队。每辆卡车的最大载货量为200个单位。所有客户的需求都必须被满足，且每个客户都规定了服务必须在其中开始的严格“硬时间窗”。在每个客户点，都需要固定的90分钟服务时间。公司的优化目标是在满足所有约束条件的前提下，最小化整个车队行驶的总距离。

## 问题分析
这是一个典型的**带硬时间窗的车辆路径问题 (Vehicle Routing Problem with Hard Time Windows, VRPHTW)**。它属于NP-hard组合优化问题的范畴，是经典车辆路径问题（VRP）的一个重要变种。该问题的核心决策包括：
1.  **分配 (Assignment):** 哪个客户由哪辆车服务。
2.  **排序 (Sequencing):** 每辆车应按什么顺序访问其分配到的客户。
3.  **调度 (Scheduling):** 每辆车在每个客户点的具体到达和服务开始时间。

该问题可以被建模为一个**混合整数线性规划 (Mixed-Integer Linear Programming, MILP)** 模型。

## 核心假设
1.  **网络表示:** 所有地点（仓库和客户）可以被视为图上的节点。连接任意两个节点的路径是存在的，其成本（距离）是确定的。
2.  **距离与时间:** 为简化模型，我们假设车辆行驶时间在数值上等于其行驶距离，这等效于假设车辆的平均速度为1个距离单位/分钟。如果存在一个已知的平均速度 $v$，则行驶时间应计算为 $t_{ij} = d_{ij} / v$。
3.  **车辆同质性:** 所有卡车具有相同的容量和性能。
4.  **服务不可中断:** 一旦在客户点开始服务，服务过程不会中断，持续时间固定。
5.  **等待允许:** 车辆可以提前到达客户点，但必须等到时间窗开启才能开始服务。等待本身不产生额外成本。
6.  **确定性:** 所有数据，包括客户需求、位置、时间窗和服务时间，都是确定且已知的。

## 数据定义
我们将问题中的所有地点（仓库和客户）统一表示为节点集合。

*   **集合 (Sets)**
    *   $N$: 所有节点的集合。我们将仓库定义为节点0，客户定义为节点1到20。因此，$N = \{0, 1, 2, ..., 20\}$。
    *   $C$: 所有客户节点的集合，$C = N \setminus \{0\} = \{1, 2, ..., 20\}$。
    *   $K$: 可用车辆的集合，$K = \{1, 2, 3, 4, 5\}$。

*   **参数 (Parameters)**
    *   $q_i$: 客户 $i$ 的需求量 (单位: units), $\forall i \in C$。对于仓库，$q_0 = 0$。
    *   $Q$: 每辆车的最大容量 ($Q=200$)。
    *   $s_i$: 在客户 $i$ 点的固定服务时间 ($s_i=90$ 分钟), $\forall i \in C$。对于仓库，$s_0 = 0$。
    *   $[e_i, l_i]$: 节点 $i$ 的服务时间窗，其中 $e_i$ 是最早服务开始时间，$l_i$ 是最晚服务开始时间, $\forall i \in N$。
    *   $(X_i, Y_i)$: 节点 $i$ 的地理坐标, $\forall i \in N$。
    *   $d_{ij}$: 从节点 $i$ 到节点 $j$ 的欧几里得距离，计算公式为 $d_{ij} = \sqrt{(X_i - X_j)^2 + (Y_i - Y_j)^2}$, $\forall i, j \in N$。
    *   $t_{ij}$: 从节点 $i$ 到节点 $j$ 的行驶时间。根据核心假设2，我们令 $t_{ij} = d_{ij}$, $\forall i, j \in N$。
    *   $M$: 一个足够大的正数（Big M），用于线性化逻辑约束。在实践中，应为每个约束选择一个尽可能紧凑的M值以提高求解效率。例如，对于时间流约束，一个有效的M值可以是 $M_{ij} = l_i + s_i + t_{ij} - e_j$。

# 数学形式

## 变量定义
为了描述车辆的路径和时间安排，我们定义以下决策变量：

*   **路径变量 (Routing Variable):**
    *   $x_{ijk}$: 一个二元变量。如果车辆 $k$ 从节点 $i$ 直接行驶到节点 $j$，则 $x_{ijk}=1$；否则 $x_{ijk}=0$。
        *   $x_{ijk} \in \{0, 1\}, \forall i, j \in N, \forall k \in K$

*   **时间变量 (Timing Variable):**
    *   $B_i$: 一个连续变量，表示在节点 $i$ 的**服务开始时间**。车辆可以早于 $B_i$ 到达，但必须等待至 $B_i$ 时刻才能开始服务。
        *   $B_i \ge 0, \forall i \in N$

## 目标函数
我们的目标是最小化所有车辆行驶的总距离。

*   **最小化总行驶距离:**
    $\min \sum_{i \in N} \sum_{j \in N} \sum_{k \in K} d_{ij} \cdot x_{ijk}$

## 约束条件
模型必须满足以下一系列约束条件，以确保解决方案的可行性。

1.  **客户服务唯一性 (Customer Assignment):**
    *   **说明:** 每个客户必须被访问一次，且仅被一辆车访问。
    *   **公式:** $\sum_{k \in K} \sum_{i \in N} x_{ijk} = 1, \quad \forall j \in C$

2.  **车辆路径连续性 (Flow Conservation):**
    *   **说明:** 如果一辆车进入一个客户节点，它必须从该节点离开。这保证了路径的连续性。
    *   **公式:** $\sum_{i \in N} x_{ipk} - \sum_{j \in N} x_{pjk} = 0, \quad \forall p \in C, \forall k \in K$

3.  **车辆调度 (Vehicle Dispatch and Return):**
    *   **说明:** 每辆被使用的车都必须从仓库出发，并且最终必须返回仓库。
    *   **公式:** $\sum_{j \in C} x_{0jk} = \sum_{i \in C} x_{i0k}, \quad \forall k \in K$
    *   **说明:** 每辆车最多只能从仓库出发一次。
    *   **公式:** $\sum_{j \in C} x_{0jk} \le 1, \quad \forall k \in K$

4.  **车辆容量约束 (Capacity Constraint):**
    *   **说明:** 每条路径上所有客户的总需求量不能超过车辆的最大容量。其中，$\sum_{j \in N} x_{ijk}$ 作为指示器，判断车辆 $k$ 是否服务了客户 $i$。
    *   **公式:** $\sum_{i \in C} q_i \left( \sum_{j \in N} x_{ijk} \right) \le Q, \quad \forall k \in K$

5.  **时间窗约束 (Time Window Constraint):**
    *   **说明:** 在任何节点的服务开始时间都必须在其指定的时间窗内。
    *   **公式:** $e_i \le B_i \le l_i, \quad \forall i \in N$

6.  **时间流一致性与子路径消除 (Time Flow and Subtour Elimination):**
    *   **说明:** 如果车辆 $k$ 从节点 $i$ 前往节点 $j$，那么在 $j$ 的服务开始时间 $B_j$ 必须晚于或等于在 $i$ 的服务完成时间 ($B_i + s_i$) 加上从 $i$ 到 $j$ 的旅行时间 $t_{ij}$。此约束同时隐式地消除了不包含仓库的无效子路径。
    *   **公式:** $B_i + s_i + t_{ij} - M \cdot (1 - x_{ijk}) \le B_j, \quad \forall i \in N, \forall j \in C, i \neq j, \forall k \in K$

7.  **车辆返回时间约束 (Return to Depot Time Constraint):**
    *   **说明:** 车辆完成最后一个客户的服务并返回仓库的时间，不得晚于仓库的关闭时间 $l_0$。
    *   **公式:** $B_i + s_i + t_{i0} - M \cdot (1 - \sum_{k \in K} x_{i0k}) \le l_0, \quad \forall i \in C$

8.  **禁止自环 (Self-Loop Elimination):**
    *   **说明:** 禁止车辆从一个节点直接行驶回其自身。
    *   **公式:** $x_{iik} = 0, \quad \forall i \in N, \forall k \in K$

9.  **变量类型约束 (Variable Domain):**
    *   **说明:** 定义决策变量的取值范围。
    *   **公式:**
        *   $x_{ijk} \in \{0, 1\}, \quad \forall i, j \in N, \forall k \in K$
        *   $B_i \ge 0, \quad \forall i \in N$