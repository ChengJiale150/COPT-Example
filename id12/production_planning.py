#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
红星塑料厂生产规划问题求解
带有固定费用的生产规划问题 (Fixed-Charge Production Planning Problem)
使用COPT求解器解决混合整数线性规划问题
"""

import coptpy as cp
from coptpy import COPT

def solve_production_planning():
    """
    求解红星塑料厂的生产规划问题
    """
    try:
        # 1. 创建COPT求解环境
        env = cp.Envr()
        
        # 2. 创建优化模型
        model = env.createModel("plastic_container_production")
        
        # 3. 定义问题数据
        # 容器型号（按体积升序排列）
        containers = [1, 2, 3, 4, 5, 6]
        
        # 容器数据
        volumes = {1: 1500, 2: 2500, 3: 4000, 4: 6000, 5: 9000, 6: 12000}  # 体积 (cm³)
        demands = {1: 500, 2: 550, 3: 700, 4: 900, 5: 400, 6: 300}  # 需求量 (件)
        var_costs = {1: 5, 2: 8, 3: 10, 4: 12, 5: 16, 6: 18}  # 单位可变成本 (元/件)
        fixed_cost = 1200  # 设备启用固定成本 (元)
        
        # Big M 常数 (用于固定成本触发约束)
        M = sum(demands.values())  # 3350
        
        print("=== 问题数据 ===")
        print("容器型号   体积(cm³)   需求(件)   单位成本(元/件)")
        for i in containers:
            print(f"   {i}       {volumes[i]:5d}     {demands[i]:3d}        {var_costs[i]:2d}")
        print(f"设备启用固定成本: {fixed_cost} 元")
        print(f"Big M 参数: {M}")
        
        # 4. 添加决策变量
        # x_ij: 用生产品种i满足需求品种j的容器数量 (仅当 i >= j 时有效)
        x = {}
        for i in containers:
            for j in containers:
                if i >= j:  # 只有体积大于等于的容器才能替代
                    x[i, j] = model.addVar(vtype=COPT.INTEGER, lb=0, 
                                         name=f"x_{i}_{j}")
        
        # y_i: 是否启用型号i的生产设备 (二进制变量)
        y = model.addVars(containers, vtype=COPT.BINARY, nameprefix="y")
        
        # 5. 添加约束条件
        
        # 约束1: 需求满足约束
        # 对于每种型号j，其需求必须被完全满足
        # ∑(i≥j) x_ij = D_j, ∀j ∈ I
        for j in containers:
            constraint_expr = cp.quicksum(x[i, j] for i in containers if i >= j)
            model.addConstr(constraint_expr == demands[j], 
                          name=f"demand_satisfaction_{j}")
        
        # 约束2: 固定成本触发约束  
        # 只要生产型号i的容器，就必须启用对应设备
        # ∑(j≤i) x_ij ≤ M * y_i, ∀i ∈ I
        for i in containers:
            production_amount = cp.quicksum(x[i, j] for j in containers if j <= i)
            model.addConstr(production_amount <= M * y[i], 
                          name=f"fixed_cost_trigger_{i}")
        
        # 6. 设置目标函数
        # 最小化总成本 = 可变成本 + 固定成本
        # min ∑i C_i * (∑(j≤i) x_ij) + ∑i F * y_i
        
        # 可变成本: 每种型号的总生产量 × 单位成本
        variable_cost = cp.quicksum(
            var_costs[i] * cp.quicksum(x[i, j] for j in containers if j <= i)
            for i in containers
        )
        
        # 固定成本: 启用设备的固定费用
        fixed_cost_total = cp.quicksum(fixed_cost * y[i] for i in containers)
        
        # 设置目标函数为最小化总成本
        model.setObjective(variable_cost + fixed_cost_total, sense=COPT.MINIMIZE)
        
        # 7. 求解模型
        print("\n=== 开始求解 ===")
        model.solve()
        
        # 8. 分析和输出求解结果
        if model.status == COPT.OPTIMAL:
            print("\n=== 求解结果 ===")
            print("模型状态: 最优解 (COPT.OPTIMAL)")
            print(f"最小总成本: {model.objval:.2f} 元")
            
            # 输出启用的设备
            print("\n启用的生产设备:")
            activated_equipment = []
            for i in containers:
                if y[i].x > 0.5:
                    activated_equipment.append(i)
                    print(f"  型号 {i}: 启用 (固定成本: {fixed_cost} 元)")
            
            if not activated_equipment:
                print("  无设备启用")
            
            # 输出生产方案
            print("\n生产分配方案:")
            print("生产型号 -> 满足需求型号   数量")
            total_variable_cost = 0
            for i in containers:
                for j in containers:
                    if (i, j) in x and x[i, j].x > 1e-6:
                        quantity = int(round(x[i, j].x))
                        cost = quantity * var_costs[i]
                        total_variable_cost += cost
                        print(f"   {i}     ->      {j}        {quantity:3d} 件 (成本: {cost:4.0f} 元)")
            
            # 输出成本分解
            print(f"\n成本分解:")
            print(f"  可变成本: {total_variable_cost:.2f} 元")
            print(f"  固定成本: {len(activated_equipment) * fixed_cost:.2f} 元")
            print(f"  总成本:   {model.objval:.2f} 元")
            
            # 验证需求满足情况
            print(f"\n需求满足验证:")
            for j in containers:
                satisfied = sum(x[i, j].x for i in containers if (i, j) in x)
                print(f"  型号 {j}: 需求 {demands[j]} 件, 满足 {satisfied:.0f} 件")
            
            # 输出MIP求解统计信息
            print(f"\nMIP 求解统计信息:")
            print(f"  最优界 (Best Bound): {model.getAttr(COPT.Attr.BestBnd):.2f}")
            print(f"  最优间隙 (Optimality Gap): {model.getAttr(COPT.Attr.BestGap) * 100:.4f}%")
            print(f"  搜索节点数 (Node Count): {model.getAttr(COPT.Attr.NodeCnt)}")
            
            # 将结果写入文件
            with open("result.txt", "w", encoding="utf-8") as f:
                f.write("红星塑料厂生产规划问题求解结果\n")
                f.write("="*40 + "\n\n")
                f.write(f"最优目标函数值: {model.objval:.2f} 元\n\n")
                f.write("启用的生产设备:\n")
                for i in activated_equipment:
                    f.write(f"  型号 {i}: 启用\n")
                f.write(f"\n总固定成本: {len(activated_equipment) * fixed_cost:.2f} 元\n")
                f.write(f"总可变成本: {total_variable_cost:.2f} 元\n")
                f.write(f"总成本: {model.objval:.2f} 元\n")
            
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
        
        # 可选：保存模型文件
        model.write("toy_production.lp")
        model.write("toy_production.sol")
        
        return model.objval if model.status == COPT.OPTIMAL else None
        
    except cp.CoptError as e:
        print(f"COPT Error: {e.retcode} - {e.message}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    finally:
        # 确保释放资源
        if 'env' in locals() and env is not None:
            env.close()

if __name__ == "__main__":
    print("红星塑料厂生产规划问题求解")
    print("=" * 50)
    result = solve_production_planning()
    if result is not None:
        print(f"\n求解完成，最优总成本: {result:.2f} 元")
    else:
        print("\n求解失败")