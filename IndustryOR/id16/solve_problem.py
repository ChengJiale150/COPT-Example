#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多周期库存管理问题求解
使用COPT求解器求解线性规划问题

问题描述：
一家商店需要为明年第一季度的某商品制定采购与销售计划。
目标是确定每个月应采购和销售多少单位的商品，以实现总利润的最大化。

数据：
- 仓库最大容量：500单位
- 初始库存：200单位
- 月份：1月、2月、3月
- 采购价：[8, 6, 9] 元/单位
- 销售价：[9, 8, 10] 元/单位

决策变量：
- x_t: 在月份t初采购的商品数量
- y_t: 在月份t内销售的商品数量  
- I_t: 在月份t末的库存数量

目标函数：
最大化总利润 = Σ(p_t * y_t - c_t * x_t) + c_3 * I_3

约束条件：
1. 库存平衡约束：I_t = I_{t-1} + x_t - y_t
2. 峰值库存容量约束：I_{t-1} + x_t ≤ C_max
3. 非负约束：x_t ≥ 0, y_t ≥ 0, I_t ≥ 0
"""

import coptpy as cp
from coptpy import COPT

def solve_inventory_problem():
    """求解多周期库存管理问题"""
    
    try:
        # 1. 数据定义
        # 时间周期
        periods = [1, 2, 3]  # 1月、2月、3月
        
        # 参数定义
        c = {1: 8, 2: 6, 3: 9}  # 采购价 (元/单位)
        p = {1: 9, 2: 8, 3: 10}  # 销售价 (元/单位)
        C_max = 500  # 仓库最大容量 (单位)
        I_0 = 200    # 初始库存 (单位)
        
        print("=" * 60)
        print("多周期库存管理问题求解")
        print("=" * 60)
        print(f"仓库最大容量: {C_max} 单位")
        print(f"初始库存: {I_0} 单位")
        print("\n各月份价格信息:")
        for t in periods:
            print(f"  {t}月: 采购价={c[t]}元/单位, 销售价={p[t]}元/单位")
        print()
        
        # 2. 创建COPT求解环境和模型
        env = cp.Envr()
        model = env.createModel("inventory_management")
        
        # 3. 添加决策变量
        # x_t: 月份t的采购量
        x = model.addVars(periods, lb=0.0, nameprefix="purchase")
        
        # y_t: 月份t的销售量
        y = model.addVars(periods, lb=0.0, nameprefix="sales")
        
        # I_t: 月份t末的库存量
        I = model.addVars(periods, lb=0.0, nameprefix="inventory")
        
        # 4. 设置目标函数
        # 最大化总利润 = Σ(p_t * y_t - c_t * x_t) + c_3 * I_3
        # 月度利润 = 销售收入 - 采购成本
        monthly_profit = cp.quicksum(p[t] * y[t] - c[t] * x[t] for t in periods)
        # 期末库存价值（按第3个月的采购成本计算）
        final_inventory_value = c[3] * I[3]
        # 总利润
        total_profit = monthly_profit + final_inventory_value
        
        model.setObjective(total_profit, sense=COPT.MAXIMIZE)
        
        # 5. 添加约束条件
        
        # 约束1: 库存平衡约束 I_t = I_{t-1} + x_t - y_t
        for t in periods:
            if t == 1:
                # 第1个月：I_1 = I_0 + x_1 - y_1
                model.addConstr(I[t] == I_0 + x[t] - y[t], 
                              name=f"inventory_balance_{t}")
            else:
                # 其他月份：I_t = I_{t-1} + x_t - y_t
                model.addConstr(I[t] == I[t-1] + x[t] - y[t], 
                              name=f"inventory_balance_{t}")
        
        # 约束2: 峰值库存容量约束 I_{t-1} + x_t ≤ C_max
        for t in periods:
            if t == 1:
                # 第1个月：I_0 + x_1 ≤ C_max
                model.addConstr(I_0 + x[t] <= C_max, 
                              name=f"capacity_constraint_{t}")
            else:
                # 其他月份：I_{t-1} + x_t ≤ C_max
                model.addConstr(I[t-1] + x[t] <= C_max, 
                              name=f"capacity_constraint_{t}")
        
        # 约束3: 非负约束已在变量定义时设置 (lb=0.0)
        
        # 6. 设置求解参数
        model.setParam(COPT.Param.TimeLimit, 30.0)  # 设置30秒时间限制
        
        # 7. 求解模型
        print("开始求解...")
        model.solve()
        
        # 8. 分析求解结果
        if model.status == COPT.OPTIMAL:
            print("求解成功！找到最优解。\n")
            print("=" * 60)
            print("最优解结果")
            print("=" * 60)
            
            # 输出目标函数值
            print(f"最大总利润: {model.objval:.2f} 元")
            
            # 输出决策变量的最优值
            print("\n各月份最优决策:")
            print("-" * 40)
            print(f"{'月份':<6} {'采购量':<10} {'销售量':<10} {'期末库存':<10}")
            print("-" * 40)
            
            total_purchase = 0
            total_sales = 0
            
            for t in periods:
                purchase_amount = x[t].x
                sales_amount = y[t].x
                inventory_amount = I[t].x
                
                total_purchase += purchase_amount
                total_sales += sales_amount
                
                print(f"{t}月{'':<4} {purchase_amount:<10.2f} {sales_amount:<10.2f} {inventory_amount:<10.2f}")
            
            print("-" * 40)
            print(f"总计{'':<4} {total_purchase:<10.2f} {total_sales:<10.2f}")
            
            # 计算各项利润明细
            print("\n利润明细:")
            print("-" * 50)
            monthly_profits = []
            for t in periods:
                monthly_revenue = p[t] * y[t].x
                monthly_cost = c[t] * x[t].x
                monthly_net = monthly_revenue - monthly_cost
                monthly_profits.append(monthly_net)
                print(f"{t}月利润: {monthly_revenue:.2f} - {monthly_cost:.2f} = {monthly_net:.2f} 元")
            
            final_inventory_val = c[3] * I[3].x
            print(f"期末库存价值: {final_inventory_val:.2f} 元")
            print(f"总利润: {sum(monthly_profits) + final_inventory_val:.2f} 元")
            
            # 验证约束条件
            print("\n约束条件验证:")
            print("-" * 30)
            
            # 验证库存平衡
            print("库存平衡验证:")
            current_inventory = I_0
            for t in periods:
                expected_inventory = current_inventory + x[t].x - y[t].x
                actual_inventory = I[t].x
                print(f"  {t}月: {current_inventory:.2f} + {x[t].x:.2f} - {y[t].x:.2f} = {expected_inventory:.2f} (实际: {actual_inventory:.2f})")
                current_inventory = actual_inventory
            
            # 验证容量约束
            print("\n容量约束验证:")
            current_inventory = I_0
            for t in periods:
                peak_inventory = current_inventory + x[t].x
                print(f"  {t}月峰值库存: {current_inventory:.2f} + {x[t].x:.2f} = {peak_inventory:.2f} ≤ {C_max}")
                current_inventory = I[t].x
            
            # 将结果写入文件
            with open('/Users/jiale.cheng/Documents/mcp/test/result.txt', 'w', encoding='utf-8') as f:
                f.write("多周期库存管理问题求解结果\n")
                f.write("=" * 40 + "\n\n")
                f.write(f"最大总利润: {model.objval:.2f} 元\n\n")
                
                f.write("各月份最优决策:\n")
                f.write(f"{'月份':<6} {'采购量':<10} {'销售量':<10} {'期末库存':<10}\n")
                f.write("-" * 40 + "\n")
                
                for t in periods:
                    f.write(f"{t}月{'':<4} {x[t].x:<10.2f} {y[t].x:<10.2f} {I[t].x:<10.2f}\n")
                
                f.write(f"\n总采购量: {total_purchase:.2f} 单位\n")
                f.write(f"总销售量: {total_sales:.2f} 单位\n")
                f.write(f"最终库存: {I[3].x:.2f} 单位\n")
                
                f.write(f"\n目标函数最优值: {model.objval:.2f} 元\n")
            
            print(f"\n结果已保存到 result.txt 文件中。")
            
            # 保存模型文件
            model.write("/Users/jiale.cheng/Documents/mcp/test/inventory_model.lp")
            model.write("/Users/jiale.cheng/Documents/mcp/test/inventory_solution.sol")
            print("模型文件已保存: inventory_model.lp, inventory_solution.sol")
            
        else:
            print(f"求解失败！模型状态码: {model.status}")
            if model.status == COPT.INFEASIBLE:
                print("模型无可行解，请检查约束条件。")
            elif model.status == COPT.UNBOUNDED:
                print("目标函数无界，请检查模型设置。")
            else:
                print("其他求解错误，请检查模型定义。")
    
    except cp.CoptError as e:
        print(f"COPT错误: {e.retcode} - {e.message}")
    except Exception as e:
        print(f"程序运行出错: {e}")
    finally:
        # 关闭COPT环境
        if 'env' in locals() and env is not None:
            env.close()

if __name__ == "__main__":
    solve_inventory_problem()