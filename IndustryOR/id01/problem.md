A factory produces two types of food, I and II, and currently has 50 skilled workers. It is known that one skilled worker can produce $10 \ \mathrm{kg} / \ \mathrm{h}$ of food I or $6 \ \mathrm{kg} / \ \mathrm{h}$ of food II. According to contract bookings, the weekly demand for these two foods will rise sharply, as shown in Table 1-11. Therefore, the factory has decided to train 50 new workers by the end of the 8th week. It is known that a worker works $40 \ \mathrm{h}$ per week, and a skilled worker can train up to three new workers in two weeks (during the training period, both the skilled worker and the trainees do not participate in production). The weekly wage of a skilled worker is 360 yuan, the weekly wage of a trainee during the training period is 120 yuan, and after training, the wage is 240 yuan per week, with the same production efficiency as skilled workers. During the transition period of training, many skilled workers are willing to work overtime, and the factory has decided to arrange some workers to work $60 \ \mathrm{h}$ per week, with a weekly wage of 540 yuan. If the booked food cannot be delivered on time, the compensation fee for each week of delay per $ \ \mathrm{kg}$ is 0.5 yuan for food I and 0.6 yuan for food II. Under these conditions, how should the factory make comprehensive arrangements to minimize the total cost?

Table 1-11

| Week | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|------|---|---|---|---|---|---|---|---|
| I    | 10000 | 10000  | 12000  | 12000  | 16000  | 16000  | 20000  | 20000  |
| II   | 6000 | 7200 | 8400 | 10800 | 10800 | 12000  | 12000  | 12000  |

# 问题

## 问题描述
一家工厂在未来8周内需要满足两种食品（I和II）的合同需求。工厂现有50名熟练工人，并计划在第8周结束前完成对50名新工人的培训。该问题的核心目标是，在满足一系列关于生产效率、工时、薪酬、培训规则和延期交付罚款的条件下，制定一个最优的周度劳动力分配、生产和培训计划，以最小化未来8周的总成本。总成本包括所有工人的工资以及因未能按时交付而产生的罚款。

## 问题分析
这是一个典型的**多周期混合整数线性规划 (Multi-period Mixed-Integer Linear Programming, MILP)** 问题。
*   **多周期 (Multi-period):** 决策是在一个连续的时间跨度（8周）内做出的，并且本周的决策（如开始培训）会影响未来几周的状态（如可用工人数）。
*   **混合整数 (Mixed-Integer):** 问题中包含整数决策变量（如分配的工人数）和连续决策变量（如生产数量、延期交付量）。
*   **线性规划 (Linear Programming):** 目标函数（总成本）和所有约束条件都是决策变量的线性函数。

该模型需要整合劳动力规划、培训调度和生产库存管理三个子问题。

## 核心假设
1.  **培训师资格唯一性:** 只有最初的50名熟练工具备培训新工人的资格，新培训完成的工人不能立即成为培训师。
2.  **培训师工作状态:** 担任培训任务的熟练工按标准工时计薪（每周40小时），不参与加班或生产。
3.  **培训效率的动态解释:** “一名熟练工可在两周内培训三名新工”被解读为一个动态比例约束。即在任意一周 $t$，在岗培训师的数量必须足够支持该周所有在训学员（包括本周新开始的和上周开始的），其比例关系在约束中体现。
4.  **工人不可分割:** 分配到各项任务的工人数必须为整数。
5.  **培训完成时限:** 所有50名新工人的培训必须在第7周（包含第7周）或之前开始，以确保在第8周结束时完成培训。
6.  **初始状态:** 在第1周开始前，没有任何库存或缺货。

## 数据定义
此问题中的数据可被系统化地定义为集合与参数。

*   **集合与索引 (Sets & Indices)**
    *   $T$: 规划周期的集合, $T = \{1, 2, ..., 8\}$。索引 $t \in T$ 代表规划周期中的某一周。
    *   $I$: 食品类型的集合, $I = \{1, 2\}$。索引 $i \in I$ 代表食品的某个品类。

*   **参数 (Parameters)**
    *   $D_{it}$: 第 $t$ 周对食品 $i$ 的需求量 (kg)。
    *   $P_i$: 每小时可生产食品 $i$ 的数量 (kg/h)。$P_1 = 10$, $P_2 = 6$。
    *   $W_0$: 初始熟练工人数, $W_0 = 50$。
    *   $N_{total}$: 计划培训的新工总人数, $N_{total} = 50$。
    *   $H_{norm}$: 标准周工作时长, $H_{norm} = 40$ h。
    *   $H_{ot}$: 加班周工作时长, $H_{ot} = 60$ h。
    *   $R_{train}$: 每名培训师最多可培训的新工人数, $R_{train} = 3$。
    *   $C_{S,norm}$: 熟练工人标准周薪, $C_{S,norm} = 360$ 元。
    *   $C_{N,norm}$: 新晋工人标准周薪, $C_{N,norm} = 240$ 元。
    *   $C_{ot}$: 加班周薪 (对所有工人), $C_{ot} = 540$ 元。
    *   $C_{T}$: 受训工人的周薪, $C_{T} = 120$ 元。
    *   $C_{P,i}$: 食品 $i$ 每公斤每周的延期交付罚款, $C_{P,1} = 0.5$, $C_{P,2} = 0.6$ 元/kg。

**需求数据表 ($D_{it}$):**
| 周 $t$ | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 食品I | 10000 | 10000 | 12000 | 12000 | 16000 | 16000 | 20000 | 20000 |
| 食品II | 6000 | 7200 | 8400 | 10800 | 10800 | 12000 | 12000 | 12000 |

# 数学形式

## 变量定义
| 符号 | 描述 | 类型 | 索引 |
| :--- | :--- | :--- | :--- |
| $W_{S,n,t}$ | 第 $t$ 周从事生产的**初始熟练工**（标准工时）人数 | 非负整数 | $t \in T$ |
| $W_{S,o,t}$ | 第 $t$ 周从事生产的**初始熟练工**（加班）人数 | 非负整数 | $t \in T$ |
| $W_{S,tr,t}$ | 第 $t$ 周从事**培训**的**初始熟练工**人数 | 非负整数 | $t \in T$ |
| $W_{N,n,t}$ | 第 $t$ 周从事生产的**新晋熟练工**（标准工时）人数 | 非负整数 | $t \in T$ |
| $W_{N,o,t}$ | 第 $t$ 周从事生产的**新晋熟练工**（加班）人数 | 非负整数 | $t \in T$ |
| $N_{start,t}$ | 第 $t$ 周**开始**接受培训的新工人数 | 非负整数 | $t \in T$ |
| $X_{it}$ | 第 $t$ 周食品 $i$ 的总产量 | 连续非负 | $i \in I, t \in T$ |
| $Inv_{it}$ | 第 $t$ 周结束时食品 $i$ 的库存量 | 连续非负 | $i \in I, t \in T$ |
| $B_{it}$ | 第 $t$ 周结束时食品 $i$ 的缺货量（延期交付量） | 连续非负 | $i \in I, t \in T$ |

## 目标函数
我们的目标是最小化8周内的总成本，包括所有工人的工资和延期交付的罚款。
*   **最小化总成本:**
    $\min \sum_{t=1}^{8} \left( (W_{S,n,t} + W_{S,tr,t}) \cdot C_{S,norm} + W_{S,o,t} \cdot C_{ot} + W_{N,n,t} \cdot C_{N,norm} + W_{N,o,t} \cdot C_{ot} + (N_{start,t} + N_{start,t-1}) \cdot C_{T} + \sum_{i \in I} B_{it} \cdot C_{P,i} \right)$
    *   **说明:** 总成本由以下几部分构成：
        *   **初始熟练工薪酬:** $(W_{S,n,t} + W_{S,tr,t}) \cdot C_{S,norm} + W_{S,o,t} \cdot C_{ot}$
        *   **新晋熟练工薪酬:** $W_{N,n,t} \cdot C_{N,norm} + W_{N,o,t} \cdot C_{ot}$
        *   **受训工人薪酬:** $(N_{start,t} + N_{start,t-1}) \cdot C_{T}$。在第 $t$ 周，处于培训状态的工人包括本周开始的 $N_{start,t}$ 人（第一周培训）和上周开始的 $N_{start,t-1}$ 人（第二周培训）。约定 $N_{start,0}=0$。
        *   **延期交付罚款:** $\sum_{i \in I} B_{it} \cdot C_{P,i}$

## 约束条件
1.  **初始熟练工平衡约束 (Initial Skilled Worker Balance):**
    *   **说明:** 每周，所有初始熟练工必须被分配到生产（标准或加班）或培训岗位上。
    *   **公式:** $W_{S,n,t} + W_{S,o,t} + W_{S,tr,t} = W_0, \quad \forall t \in T$

2.  **新晋熟练工平衡约束 (Newly Skilled Worker Balance):**
    *   **说明:** 每周，所有已完成培训的新晋工人必须被分配到生产岗位（标准或加班）。可用的新晋工人数是之前所有完成两周培训周期的工人之和。
        **举例说明:** 在第3周 ($t=3$)，可用的新晋工人数为 $\sum_{k=1}^{1} N_{start,k} = N_{start,1}$，即仅为第1周开始培训的工人数，因为他们的两年培训期在第2周结束时正好完成。
    *   **公式:** $W_{N,n,t} + W_{N,o,t} = \sum_{k=1}^{t-2} N_{start,k}, \quad \forall t \in T$

3.  **总培训人数约束 (Total Trainees Constraint):**
    *   **说明:** 到第8周结束时，必须总共培训50名新工人。这意味着他们最晚必须在第7周开始培训。
    *   **公式:** $\sum_{t=1}^{7} N_{start,t} = N_{total}$

4.  **培训能力约束 (Training Capacity Constraint):**
    *   **说明:** 每周投入培训的熟练工人数必须足够支持当前所有在训的新工。在第 $t$ 周，在训学员总数为本周开始的 $N_{start,t}$ 人和上周开始的 $N_{start,t-1}$ 人。
    *   **公式:** $R_{train} \cdot W_{S,tr,t} \ge N_{start,t} + N_{start,t-1}, \quad \forall t \in T$

5.  **生产能力约束 (Production Capacity Constraint):**
    *   **说明:** 两种食品的总生产工时不能超过所有生产工人的总可用工时。
    *   **公式:** $\frac{X_{1t}}{P_1} + \frac{X_{2t}}{P_2} \le (W_{S,n,t} + W_{N,n,t}) \cdot H_{norm} + (W_{S,o,t} + W_{N,o,t}) \cdot H_{ot}, \quad \forall t \in T$

6.  **库存-缺货平衡约束 (Inventory-Backlog Balance):**
    *   **说明:** 上一周的净库存（库存减缺货）加上本周的产量，必须等于本周的需求加上本周的净库存。这是连接各个周期的核心约束。
    *   **公式:** $Inv_{i,t-1} - B_{i,t-1} + X_{it} = D_{it} + Inv_{it} - B_{it}, \quad \forall i \in I, \forall t \in T$
    *   (约定初始条件 $Inv_{i,0} = 0$ 和 $B_{i,0} = 0$)

7.  **变量类型与非负约束 (Variable Type and Non-negativity):**
    *   **说明:** 所有变量必须为非负，且劳动力分配变量必须为整数。
    *   **公式:**
        *   $W_{S,n,t}, W_{S,o,t}, W_{S,tr,t}, W_{N,n,t}, W_{N,o,t}, N_{start,t} \in \mathbb{Z}^+, \quad \forall t \in T$
        *   $X_{it}, Inv_{it}, B_{it} \ge 0, \quad \forall i \in I, \forall t \in T$