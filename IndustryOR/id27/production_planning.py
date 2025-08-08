import coptpy as cp
from coptpy import COPT

try:
    # 1. 创建COPT求解环境
    env = cp.Envr()
    
    # 2. 创建优化模型
    model = env.createModel("production_planning_milp")
    
    # 3. 定义问题数据
    
    # 产品集合
    products = ['I', 'II', 'III']
    
    # 设备集合
    equipment_A = ['A1', 'A2']
    equipment_B = ['B1', 'B2', 'B3']
    all_equipment = equipment_A + equipment_B
    
    # 有效生产路径集合 R = {(产品, A设备, B设备)}
    # 根据问题描述的设备限制定义
    routes = [
        # 产品I可在任意A、B设备上加工
        ('I', 'A1', 'B1'), ('I', 'A1', 'B2'), ('I', 'A1', 'B3'),
        ('I', 'A2', 'B1'), ('I', 'A2', 'B2'), ('I', 'A2', 'B3'),
        # 产品II可在任意A设备上加工，但B工序只能在设备B1上完成
        ('II', 'A1', 'B1'), ('II', 'A2', 'B1'),
        # 产品III: A工序只能在设备A2上完成，B工序只能在设备B2上完成
        ('III', 'A2', 'B2')
    ]
    
    # 产品售价 (元/件)
    sell_price = {'I': 1.25, 'II': 2.00, 'III': 2.80}
    
    # 产品原材料成本 (元/件)
    material_cost = {'I': 0.25, 'II': 0.35, 'III': 0.50}
    
    # 设备有效工作时长 (小时)
    machine_hours = {
        'A1': 6000, 'A2': 10000,
        'B1': 4000, 'B2': 7000, 'B3': 4000
    }
    
    # 设备固定运行成本 (元)
    fixed_cost = {
        'A1': 300, 'A2': 321,
        'B1': 250, 'B2': 783, 'B3': 200
    }
    
    # 产品在各设备上的单位加工时间 (小时/件)
    # 只定义有效路径上的加工时间
    processing_time = {
        # 产品I的加工时间
        ('I', 'A1'): 5, ('I', 'A2'): 7,
        ('I', 'B1'): 6, ('I', 'B2'): 4, ('I', 'B3'): 7,
        # 产品II的加工时间
        ('II', 'A1'): 10, ('II', 'A2'): 9,
        ('II', 'B1'): 8,
        # 产品III的加工时间
        ('III', 'A2'): 12,
        ('III', 'B2'): 11
    }
    
    # 4. 添加决策变量
    
    # x[p,a,b]: 通过路径(p,a,b)生产的产品p的数量 (件)
    x = model.addVars(routes, lb=0.0, nameprefix="x")
    
    # y[m]: 设备m是否被启用的二元变量
    y = model.addVars(all_equipment, vtype=COPT.BINARY, nameprefix="y")
    
    # 5. 添加约束条件
    
    # 约束1: 设备A工时约束
    for a in equipment_A:
        # 对于每台A设备，总加工时间不超过有效工时
        a_workload = cp.quicksum(
            processing_time[(p, a)] * x[p, a, b]
            for p, a_eq, b in routes
            if a_eq == a and (p, a) in processing_time
        )
        model.addConstr(a_workload <= machine_hours[a], name=f"capacity_A_{a}")
    
    # 约束2: 设备B工时约束
    for b in equipment_B:
        # 对于每台B设备，总加工时间不超过有效工时
        b_workload = cp.quicksum(
            processing_time[(p, b)] * x[p, a, b]
            for p, a, b_eq in routes
            if b_eq == b and (p, b) in processing_time
        )
        model.addConstr(b_workload <= machine_hours[b], name=f"capacity_B_{b}")
    
    # 约束3: 设备启用逻辑约束 (大M方法)
    # 计算合理的Big-M值：设备在有效时长内能生产的最大产品数量
    big_M = {}
    for m in all_equipment:
        relevant_times = [processing_time[(p, m)] for (p, m_eq) in processing_time.keys() if m_eq == m]
        if relevant_times:
            big_M[m] = machine_hours[m] / min(relevant_times)
        else:
            big_M[m] = 0  # 该设备没有相关的加工任务
    
    # 设备A的启用约束
    for a in equipment_A:
        if big_M[a] > 0:
            a_production = cp.quicksum(
                x[p, a, b]
                for p, a_eq, b in routes
                if a_eq == a
            )
            model.addConstr(a_production <= big_M[a] * y[a], name=f"activation_A_{a}")
    
    # 设备B的启用约束
    for b in equipment_B:
        if big_M[b] > 0:
            b_production = cp.quicksum(
                x[p, a, b]
                for p, a, b_eq in routes
                if b_eq == b
            )
            model.addConstr(b_production <= big_M[b] * y[b], name=f"activation_B_{b}")
    
    # 6. 设置目标函数：最大化总利润
    # 总利润 = 总销售收入 - 总原材料成本 - 总设备运行成本
    
    # 计算总边际利润 (销售收入 - 原材料成本)
    total_margin = cp.quicksum(
        (sell_price[p] - material_cost[p]) * x[p, a, b]
        for p, a, b in routes
    )
    
    # 计算总设备固定成本
    total_fixed_cost = cp.quicksum(fixed_cost[m] * y[m] for m in all_equipment)
    
    # 目标函数：最大化利润
    model.setObjective(total_margin - total_fixed_cost, sense=COPT.MAXIMIZE)
    
    # 7. 求解模型
    print("开始求解生产规划优化问题...")
    model.solve()
    
    # 8. 分析求解结果
    if model.status == COPT.OPTIMAL:
        print("\n" + "="*60)
        print("求解结果")
        print("="*60)
        print(f"模型状态: 最优解 (COPT.OPTIMAL)")
        print(f"最大利润: {model.objval:.2f} 元")
        
        # 统计各产品总产量
        print("\n产品生产计划:")
        product_totals = {}
        for p in products:
            total = sum(x[p, a, b].x for p_route, a, b in routes if p_route == p)
            product_totals[p] = total
            if total > 0.001:  # 只显示有意义的产量
                print(f"  产品{p}: {total:.2f} 件")
        
        print("\n详细生产路径 (仅显示非零生产):")
        for p, a, b in routes:
            if x[p, a, b].x > 0.001:
                print(f"  路径 ({p}, {a}, {b}): {x[p, a, b].x:.2f} 件")
        
        print("\n设备启用情况:")
        activated_equipment = []
        for m in all_equipment:
            if y[m].x > 0.5:
                activated_equipment.append(m)
                print(f"  设备{m}: 启用 (固定成本: {fixed_cost[m]} 元)")
            else:
                print(f"  设备{m}: 未启用")
        
        print("\n设备资源使用情况:")
        for m in all_equipment:
            if m in activated_equipment:
                if m in equipment_A:
                    usage = sum(
                        processing_time[(p, m)] * x[p, a, b].x
                        for p, a, b in routes
                        if a == m and (p, m) in processing_time
                    )
                else:  # m in equipment_B
                    usage = sum(
                        processing_time[(p, m)] * x[p, a, b].x
                        for p, a, b in routes
                        if b == m and (p, m) in processing_time
                    )
                utilization = usage / machine_hours[m] * 100
                print(f"  设备{m}: 使用 {usage:.2f} / {machine_hours[m]} 小时 (利用率: {utilization:.2f}%)")
        
        print("\n财务分析:")
        total_revenue = sum((sell_price[p] - material_cost[p]) * x[p, a, b].x for p, a, b in routes)
        total_equipment_cost = sum(fixed_cost[m] * y[m].x for m in all_equipment)
        print(f"  总边际收入: {total_revenue:.2f} 元")
        print(f"  总设备成本: {total_equipment_cost:.2f} 元")
        print(f"  净利润: {model.objval:.2f} 元")
        
        print("\nMIP 求解统计信息:")
        print(f"  最优界 (Best Bound): {model.getAttr(COPT.Attr.BestBnd):.2f}")
        print(f"  最优间隙 (Optimality Gap): {model.getAttr(COPT.Attr.BestGap) * 100:.4f}%")
        print(f"  搜索节点数 (Node Count): {model.getAttr(COPT.Attr.NodeCnt)}")
        
        # 将结果写入文件
        with open("result.txt", "w", encoding="utf-8") as f:
            f.write("生产规划优化求解结果\n")
            f.write("="*40 + "\n")
            f.write(f"最大利润: {model.objval:.2f} 元\n\n")
            
            f.write("产品生产计划:\n")
            for p in products:
                total = product_totals[p]
                if total > 0.001:
                    f.write(f"  产品{p}: {total:.2f} 件\n")
            
            f.write("\n详细生产路径:\n")
            for p, a, b in routes:
                if x[p, a, b].x > 0.001:
                    f.write(f"  路径 ({p}, {a}, {b}): {x[p, a, b].x:.2f} 件\n")
            
            f.write("\n设备启用情况:\n")
            for m in all_equipment:
                status = "启用" if y[m].x > 0.5 else "未启用"
                f.write(f"  设备{m}: {status}\n")
        
        print(f"\n结果已保存到 result.txt 文件")
        
    else:
        print(f"\n模型未找到最优解。状态码: {model.status}")
        status_map = {
            COPT.INFEASIBLE: "模型无可行解",
            COPT.UNBOUNDED: "目标函数无界",
            COPT.TIMEOUT: "求解超时",
            COPT.INTERRUPTED: "用户中断"
        }
        print(f"状态描述: {status_map.get(model.status, '未知状态')}")
    
    # 9. 将模型保存到文件 (可选)
    model.write("production_planning.lp")
    model.write("production_planning.sol")
    
except cp.CoptError as e:
    print(f"COPT Error: {e.retcode} - {e.message}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    # 确保在程序结束时关闭COPT环境
    if 'env' in locals() and env is not None:
        env.close()