#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产规划问题求解 - 使用COPT线性规划求解器

问题描述：
一家工厂生产三种产品（I, II, III），每种产品需经过A、B两个加工阶段。
工厂拥有不同类型的设备，不同产品在不同设备上的加工路径受到限制。
目标是制定生产计划，最大化工厂总利润。

作者：AI Assistant
日期：2024
"""

import coptpy as cp
from coptpy import COPT

def solve_production_planning():
    """求解生产规划问题"""
    
    try:
        # 1. 创建COPT求解环境
        env = cp.Envr()
        model = env.createModel("production_planning")
        
        # 2. 数据定义
        # 产品集合
        products = ['I', 'II', 'III']
        
        # 设备集合
        equipment_A = ['A1', 'A2']
        equipment_B = ['B1', 'B2', 'B3']
        all_equipment = equipment_A + equipment_B
        
        # 可行工艺路径集合 R_valid
        valid_routes = [
            # 产品I的可行路径
            ('I', 'A1', 'B1'), ('I', 'A1', 'B2'), ('I', 'A1', 'B3'),
            ('I', 'A2', 'B1'), ('I', 'A2', 'B2'), ('I', 'A2', 'B3'),
            # 产品II的可行路径
            ('II', 'A1', 'B1'), ('II', 'A2', 'B1'),
            # 产品III的可行路径
            ('III', 'A2', 'B2')
        ]
        
        # 加工时间数据 T_{p,m} (小时/件)
        processing_time = {
            # 产品I的加工时间
            ('I', 'A1'): 5, ('I', 'A2'): 7,
            ('I', 'B1'): 6, ('I', 'B2'): 4, ('I', 'B3'): 7,
            # 产品II的加工时间  
            ('II', 'A1'): 10, ('II', 'A2'): 9,
            ('II', 'B1'): 8,
            # 产品III的加工时间
            ('III', 'A2'): 12, ('III', 'B2'): 11
        }
        
        # 设备可用工时 H_m (小时)
        machine_hours = {
            'A1': 6000, 'A2': 10000,
            'B1': 4000, 'B2': 7000, 'B3': 4000
        }
        
        # 设备加工成本 C_m^{proc} (元/小时)
        processing_cost = {
            'A1': 0.05, 'A2': 0.03,
            'B1': 0.06, 'B2': 0.11, 'B3': 0.05
        }
        
        # 产品原料成本 C_p^{raw} (元/件)
        raw_material_cost = {
            'I': 0.25, 'II': 0.35, 'III': 0.5
        }
        
        # 产品销售价格 S_p (元/件)
        selling_price = {
            'I': 1.25, 'II': 2.0, 'III': 2.8
        }
        
        # 3. 计算单位路径利润 π_{p,a,b}
        route_profit = {}
        for p, a, b in valid_routes:
            # 利润 = 销售价格 - 原料成本 - A阶段加工成本 - B阶段加工成本
            profit = (selling_price[p] - raw_material_cost[p] - 
                     processing_time[p, a] * processing_cost[a] - 
                     processing_time[p, b] * processing_cost[b])
            route_profit[p, a, b] = profit
            print(f"路径 ({p}, {a}, {b}) 的单位利润: {profit:.4f} 元")
        
        # 4. 添加决策变量 x_{p,a,b}
        # 每个变量表示通过路径 (p,a,b) 生产的产品数量
        x = {}
        for p, a, b in valid_routes:
            x[p, a, b] = model.addVar(lb=0.0, 
                                    name=f"x_{p}_{a}_{b}")
        
        # 5. 设置目标函数 - 最大化总利润
        objective = cp.quicksum(route_profit[p, a, b] * x[p, a, b] 
                               for p, a, b in valid_routes)
        model.setObjective(objective, sense=COPT.MAXIMIZE)
        
        # 6. 添加约束条件
        
        # 6.1 A阶段设备工时约束
        for a in equipment_A:
            # 对于设备a，计算所有使用该设备的路径的工时消耗
            constraint_expr = cp.quicksum(
                processing_time[p, a] * x[p, a, b] 
                for p, a_used, b in valid_routes 
                if a_used == a
            )
            model.addConstr(constraint_expr <= machine_hours[a], 
                          name=f"capacity_A_{a}")
        
        # 6.2 B阶段设备工时约束  
        for b in equipment_B:
            # 对于设备b，计算所有使用该设备的路径的工时消耗
            constraint_expr = cp.quicksum(
                processing_time[p, b] * x[p, a, b_used] 
                for p, a, b_used in valid_routes 
                if b_used == b
            )
            model.addConstr(constraint_expr <= machine_hours[b], 
                          name=f"capacity_B_{b}")
        
        # 7. 求解模型
        print("\n开始求解模型...")
        model.solve()
        
        # 8. 分析求解结果
        if model.status == COPT.OPTIMAL:
            print("\n=== 求解成功！找到最优解 ===")
            print(f"最大总利润: {model.objval:.4f} 元")
            
            print("\n--- 最优生产计划 ---")
            total_production = {'I': 0, 'II': 0, 'III': 0}
            
            for p, a, b in valid_routes:
                production = x[p, a, b].x
                if production > 1e-6:  # 只显示非零产量
                    print(f"路径 ({p}, {a}, {b}): 生产 {production:.4f} 件")
                    total_production[p] += production
            
            print("\n--- 各产品总产量 ---")
            for p in products:
                print(f"产品 {p}: {total_production[p]:.4f} 件")
            
            print("\n--- 设备利用情况 ---")
            # A阶段设备利用率
            for a in equipment_A:
                used_hours = sum(processing_time[p, a] * x[p, a_used, b].x 
                               for p, a_used, b in valid_routes 
                               if a_used == a)
                utilization = (used_hours / machine_hours[a]) * 100
                print(f"设备 {a}: 使用 {used_hours:.2f} / {machine_hours[a]} 小时 "
                      f"(利用率: {utilization:.2f}%)")
            
            # B阶段设备利用率  
            for b in equipment_B:
                used_hours = sum(processing_time[p, b] * x[p, a, b_used].x 
                               for p, a, b_used in valid_routes 
                               if b_used == b)
                utilization = (used_hours / machine_hours[b]) * 100
                print(f"设备 {b}: 使用 {used_hours:.2f} / {machine_hours[b]} 小时 "
                      f"(利用率: {utilization:.2f}%)")
            
            # 9. 输出结果到文件
            with open('/Users/jiale.cheng/Documents/mcp/test/result.txt', 'w', encoding='utf-8') as f:
                f.write("生产规划问题求解结果\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"最大总利润: {model.objval:.4f} 元\n\n")
                
                f.write("最优生产计划:\n")
                for p, a, b in valid_routes:
                    production = x[p, a, b].x
                    if production > 1e-6:
                        f.write(f"路径 ({p}, {a}, {b}): 生产 {production:.4f} 件\n")
                
                f.write("\n各产品总产量:\n")
                for p in products:
                    f.write(f"产品 {p}: {total_production[p]:.4f} 件\n")
            
            print(f"\n结果已保存到 result.txt 文件")
            return model.objval
            
        else:
            print(f"\n求解失败，模型状态码: {model.status}")
            return None
            
    except cp.CoptError as e:
        print(f"COPT Error: {e.retcode} - {e.message}")
        return None
    except Exception as e:
        print(f"发生未预期的错误: {e}")
        return None
    finally:
        # 关闭COPT环境
        if 'env' in locals() and env is not None:
            env.close()

if __name__ == "__main__":
    print("生产规划问题求解程序")
    print("=" * 50)
    result = solve_production_planning()
    if result is not None:
        print(f"\n求解完成，最优目标函数值: {result:.4f}")
    else:
        print("\n求解失败")