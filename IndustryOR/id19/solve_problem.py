import coptpy as cp
from coptpy import COPT

try:
    # 1. 创建COPT求解环境
    env = cp.Envr()

    # 2. 创建优化模型
    model = env.createModel("furniture_store_optimization")

    # 3. 定义问题数据
    # 制造商集合
    manufacturers = ['A', 'B', 'C']
    
    # 每把椅子成本 ($)
    costs = {'A': 50, 'B': 45, 'C': 40}
    
    # 每次订货椅子数量
    quantities_per_order = {'A': 15, 'B': 10, 'C': 10}
    
    # 总椅子数约束
    min_chairs = 100
    max_chairs = 500
    
    # 如果从A订货，B的最小椅子数
    b_min_chairs = 10
    
    # 计算每个制造商的最大订货次数上界 K_m
    K = {}
    for m in manufacturers:
        K[m] = max_chairs // quantities_per_order[m]

    # 4. 添加决策变量
    # x_m: 向制造商 m 的订货次数 (整数变量)
    x = model.addVars(manufacturers, vtype=COPT.INTEGER, lb=0, nameprefix="x")
    
    # y_m: 是否从制造商 m 订货的二元变量
    y = model.addVars(manufacturers, vtype=COPT.BINARY, nameprefix="y")

    # 5. 添加约束条件
    
    # 约束1: 总椅子数下限约束
    model.addConstr(
        cp.quicksum(quantities_per_order[m] * x[m] for m in manufacturers) >= min_chairs,
        name="min_chairs_constraint"
    )
    
    # 约束2: 总椅子数上限约束
    model.addConstr(
        cp.quicksum(quantities_per_order[m] * x[m] for m in manufacturers) <= max_chairs,
        name="max_chairs_constraint"
    )
    
    # 约束3: 条件约束 (A → B): 如果从A订货，则从B至少订1次
    model.addConstr(x['B'] >= y['A'], name="A_implies_B")
    
    # 约束4: 条件约束 (B → C): 如果从B订货，则必须从C订货
    model.addConstr(y['C'] >= y['B'], name="B_implies_C")
    
    # 约束5: 变量链接约束
    # 5a: 如果不从制造商 m 订货 (y_m=0)，则其订货次数必须为0
    for m in manufacturers:
        model.addConstr(x[m] <= K[m] * y[m], name=f"link_upper_{m}")
    
    # 5b: 如果从制造商 m 订货 (y_m=1)，则其订货次数至少为1
    for m in manufacturers:
        model.addConstr(x[m] >= y[m], name=f"link_lower_{m}")

    # 6. 设置目标函数：最小化总成本
    total_cost = cp.quicksum(costs[m] * quantities_per_order[m] * x[m] for m in manufacturers)
    model.setObjective(total_cost, sense=COPT.MINIMIZE)

    # 7. 求解模型
    model.solve()

    # 8. 分析求解结果
    if model.status == COPT.OPTIMAL:
        print("\n--- 求解结果 ---")
        print("模型状态: 最优解 (COPT.OPTIMAL)")
        print(f"最小总成本: ${model.objval:.2f}")
        
        print("\n决策方案:")
        total_chairs = 0
        for m in manufacturers:
            orders = int(x[m].x)
            chairs = orders * quantities_per_order[m]
            total_chairs += chairs
            print(f"  制造商 {m}: 订货 {orders} 次, 椅子数 {chairs} 把, 成本 ${orders * quantities_per_order[m] * costs[m]:.2f}")
        
        print(f"\n总椅子数: {total_chairs} 把")
        
        print("\n约束条件检查:")
        print(f"  椅子数范围: {min_chairs} <= {total_chairs} <= {max_chairs} ✓")
        
        # 检查条件约束
        a_ordered = int(y['A'].x) > 0.5
        b_ordered = int(y['B'].x) > 0.5
        c_ordered = int(y['C'].x) > 0.5
        
        if a_ordered:
            b_chairs = int(x['B'].x) * quantities_per_order['B']
            print(f"  A→B约束: 从A订货，从B订了{b_chairs}把椅子 >= {b_min_chairs} ✓")
        
        if b_ordered:
            print(f"  B→C约束: 从B订货，从C也订货了 ✓" if c_ordered else "  B→C约束: 违反！")
        
        # 将结果写入文件
        with open('/Users/jiale.cheng/Documents/mcp/test/result.txt', 'w') as f:
            f.write(f"最优目标函数值（最小总成本）: ${model.objval:.2f}\n")
            f.write(f"总椅子数: {total_chairs} 把\n")
            f.write("\n决策方案:\n")
            for m in manufacturers:
                orders = int(x[m].x)
                chairs = orders * quantities_per_order[m]
                f.write(f"制造商 {m}: 订货 {orders} 次, 椅子数 {chairs} 把\n")
                
        print(f"\n结果已保存到 result.txt")
        
        print("\nMIP 求解统计信息:")
        print(f"  最优界 (Best Bound): ${model.getAttr(COPT.Attr.BestBnd):.2f}")
        print(f"  最优间隙 (Optimality Gap): {model.getAttr(COPT.Attr.BestGap) * 100:.4f}%")
        print(f"  搜索节点数 (Node Count): {model.getAttr(COPT.Attr.NodeCnt)}")

    else:
        print(f"\n模型未找到最优解。状态码: {model.status}")
        status_map = {
            COPT.INFEASIBLE: "模型无可行解",
            COPT.UNBOUNDED: "目标函数无界",
            COPT.TIMEOUT: "求解超时",
            COPT.INTERRUPTED: "用户中断"
        }
        print(f"状态描述: {status_map.get(model.status, '未知状态')}")

except cp.CoptError as e:
    print(f"COPT Error: {e.retcode} - {e.message}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    if 'env' in locals() and env is not None:
        env.close()