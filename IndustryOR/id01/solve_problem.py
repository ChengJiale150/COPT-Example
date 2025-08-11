#!/usr/bin/env python3
"""
工厂生产规划问题求解器
多周期混合整数线性规划 (Multi-period Mixed-Integer Linear Programming, MILP) 问题

问题描述：
一家工厂在未来8周内需要满足两种食品（I和II）的合同需求。
工厂现有50名熟练工人，并计划在第8周结束前完成对50名新工人的培训。
目标是制定最优的周度劳动力分配、生产和培训计划，以最小化未来8周的总成本。
"""

import coptpy as cp
from coptpy import COPT
import json

def solve_factory_planning():
    """求解工厂生产规划问题"""
    
    try:
        # 1. 创建COPT求解环境
        env = cp.Envr()
        model = env.createModel("factory_planning_milp")
        
        # 2. 定义问题数据
        # 时间周期
        T = 8  # 8周规划期
        weeks = list(range(1, T + 1))
        
        # 食品类型
        foods = [1, 2]  # 食品I和食品II
        
        # 需求数据 D_{it} (kg)
        demand = {
            (1, 1): 10000, (1, 2): 10000, (1, 3): 12000, (1, 4): 12000,
            (1, 5): 16000, (1, 6): 16000, (1, 7): 20000, (1, 8): 20000,
            (2, 1): 6000,  (2, 2): 7200,  (2, 3): 8400,  (2, 4): 10800,
            (2, 5): 10800, (2, 6): 12000, (2, 7): 12000, (2, 8): 12000
        }
        
        # 生产效率参数 P_i (kg/h)
        productivity = {1: 10, 2: 6}  # 食品I: 10kg/h, 食品II: 6kg/h
        
        # 其他参数
        W0 = 50           # 初始熟练工人数
        N_total = 50      # 计划培训的新工总人数
        H_norm = 40       # 标准周工作时长 (h)
        H_ot = 60         # 加班周工作时长 (h)
        R_train = 3       # 每名培训师最多可培训的新工人数
        
        # 薪酬参数 (元)
        C_S_norm = 360    # 熟练工人标准周薪
        C_N_norm = 240    # 新晋工人标准周薪
        C_ot = 540        # 加班周薪 (对所有工人)
        C_T = 120         # 受训工人的周薪
        
        # 延期交付罚款 (元/kg/周)
        penalty = {1: 0.5, 2: 0.6}
        
        print("=== 工厂生产规划问题求解 ===")
        print(f"规划周期: {T}周")
        print(f"初始熟练工人数: {W0}人")
        print(f"计划培训新工人数: {N_total}人")
        print()
        
        # 3. 添加决策变量
        
        # 初始熟练工分配变量
        W_S_n = model.addVars(weeks, vtype=COPT.INTEGER, lb=0, nameprefix="W_S_n")    # 标准工时生产
        W_S_o = model.addVars(weeks, vtype=COPT.INTEGER, lb=0, nameprefix="W_S_o")    # 加班生产
        W_S_tr = model.addVars(weeks, vtype=COPT.INTEGER, lb=0, nameprefix="W_S_tr")  # 培训
        
        # 新晋熟练工分配变量
        W_N_n = model.addVars(weeks, vtype=COPT.INTEGER, lb=0, nameprefix="W_N_n")    # 标准工时生产
        W_N_o = model.addVars(weeks, vtype=COPT.INTEGER, lb=0, nameprefix="W_N_o")    # 加班生产
        
        # 培训开始变量
        N_start = model.addVars(weeks, vtype=COPT.INTEGER, lb=0, nameprefix="N_start")
        
        # 生产变量
        X = model.addVars(foods, weeks, lb=0, nameprefix="X")  # 产量
        
        # 库存和缺货变量
        Inv = model.addVars(foods, weeks, lb=0, nameprefix="Inv")  # 库存
        B = model.addVars(foods, weeks, lb=0, nameprefix="B")      # 缺货(延期交付)
        
        print("决策变量已定义")
        
        # 4. 添加约束条件
        
        # 约束1: 初始熟练工平衡约束
        for t in weeks:
            model.addConstr(
                W_S_n[t] + W_S_o[t] + W_S_tr[t] == W0,
                name=f"skilled_worker_balance_{t}"
            )
        
        # 约束2: 新晋熟练工平衡约束
        for t in weeks:
            if t >= 3:  # 从第3周开始，才有完成培训的新工人
                available_new_workers = cp.quicksum(N_start[k] for k in range(1, t-1))
                model.addConstr(
                    W_N_n[t] + W_N_o[t] == available_new_workers,
                    name=f"new_worker_balance_{t}"
                )
            else:
                model.addConstr(
                    W_N_n[t] + W_N_o[t] == 0,
                    name=f"new_worker_balance_{t}"
                )
        
        # 约束3: 总培训人数约束
        model.addConstr(
            cp.quicksum(N_start[t] for t in range(1, 8)) == N_total,  # 第1-7周开始培训
            name="total_training_constraint"
        )
        
        # 约束4: 培训能力约束
        for t in weeks:
            # 第t周在训学员数 = 本周开始的 + 上周开始的
            trainees_this_week = N_start[t]
            if t > 1:
                trainees_this_week += N_start[t-1]
            
            model.addConstr(
                R_train * W_S_tr[t] >= trainees_this_week,
                name=f"training_capacity_{t}"
            )
        
        # 约束5: 生产能力约束
        for t in weeks:
            total_production_hours = (
                X[1, t] / productivity[1] + X[2, t] / productivity[2]
            )
            available_hours = (
                (W_S_n[t] + W_N_n[t]) * H_norm + 
                (W_S_o[t] + W_N_o[t]) * H_ot
            )
            model.addConstr(
                total_production_hours <= available_hours,
                name=f"production_capacity_{t}"
            )
        
        # 约束6: 库存-缺货平衡约束
        for i in foods:
            for t in weeks:
                if t == 1:
                    # 第1周：初始库存和缺货为0
                    model.addConstr(
                        X[i, t] == demand[i, t] + Inv[i, t] - B[i, t],
                        name=f"inventory_balance_{i}_{t}"
                    )
                else:
                    # 其他周：库存平衡方程
                    model.addConstr(
                        Inv[i, t-1] - B[i, t-1] + X[i, t] == demand[i, t] + Inv[i, t] - B[i, t],
                        name=f"inventory_balance_{i}_{t}"
                    )
        
        print("约束条件已添加")
        
        # 5. 设置目标函数
        total_cost = 0
        
        for t in weeks:
            # 初始熟练工薪酬
            skilled_worker_cost = (W_S_n[t] + W_S_tr[t]) * C_S_norm + W_S_o[t] * C_ot
            
            # 新晋熟练工薪酬
            new_worker_cost = W_N_n[t] * C_N_norm + W_N_o[t] * C_ot
            
            # 受训工人薪酬（本周开始的 + 上周开始的）
            trainee_cost = N_start[t] * C_T
            if t > 1:
                trainee_cost += N_start[t-1] * C_T
            
            # 延期交付罚款
            penalty_cost = cp.quicksum(B[i, t] * penalty[i] for i in foods)
            
            total_cost += skilled_worker_cost + new_worker_cost + trainee_cost + penalty_cost
        
        model.setObjective(total_cost, sense=COPT.MINIMIZE)
        print("目标函数已设置")
        
        # 6. 求解模型
        print("\n开始求解...")
        model.solve()
        
        # 7. 分析求解结果
        if model.status == COPT.OPTIMAL:
            print("\n=== 求解成功！===")
            print(f"模型状态: 最优解")
            print(f"最小总成本: {model.objval:,.2f} 元")
            
            # 保存详细结果
            results = {
                "status": "OPTIMAL",
                "objective_value": model.objval,
                "workforce_allocation": {},
                "production_plan": {},
                "training_schedule": {},
                "inventory_backlog": {}
            }
            
            # 劳动力分配结果
            print("\n--- 劳动力分配计划 ---")
            for t in weeks:
                print(f"\n第{t}周:")
                print(f"  初始熟练工: 标准工时{int(W_S_n[t].x)}人, 加班{int(W_S_o[t].x)}人, 培训{int(W_S_tr[t].x)}人")
                print(f"  新晋熟练工: 标准工时{int(W_N_n[t].x)}人, 加班{int(W_N_o[t].x)}人")
                print(f"  新开始培训: {int(N_start[t].x)}人")
                
                results["workforce_allocation"][f"week_{t}"] = {
                    "skilled_normal": int(W_S_n[t].x),
                    "skilled_overtime": int(W_S_o[t].x),
                    "skilled_training": int(W_S_tr[t].x),
                    "new_normal": int(W_N_n[t].x),
                    "new_overtime": int(W_N_o[t].x),
                    "new_trainees": int(N_start[t].x)
                }
            
            # 生产计划
            print("\n--- 生产计划 ---")
            for t in weeks:
                print(f"\n第{t}周生产:")
                for i in foods:
                    print(f"  食品{['I', 'II'][i-1]}: {X[i, t].x:,.2f} kg (需求: {demand[i, t]:,} kg)")
                
                results["production_plan"][f"week_{t}"] = {
                    "food_I": X[1, t].x,
                    "food_II": X[2, t].x
                }
            
            # 库存和缺货情况
            print("\n--- 库存与缺货情况 ---")
            for t in weeks:
                print(f"\n第{t}周末:")
                for i in foods:
                    if Inv[i, t].x > 1e-6 or B[i, t].x > 1e-6:
                        print(f"  食品{['I', 'II'][i-1]}: 库存{Inv[i, t].x:,.2f} kg, 缺货{B[i, t].x:,.2f} kg")
                
                results["inventory_backlog"][f"week_{t}"] = {
                    "food_I_inventory": Inv[1, t].x,
                    "food_I_backlog": B[1, t].x,
                    "food_II_inventory": Inv[2, t].x,
                    "food_II_backlog": B[2, t].x
                }
            
            # 培训进度
            print("\n--- 培训进度总结 ---")
            total_started = sum(int(N_start[t].x) for t in range(1, 8))
            print(f"总培训人数: {total_started} / {N_total}")
            
            results["training_schedule"] = {
                f"week_{t}": int(N_start[t].x) for t in weeks
            }
            
            # 写入结果文件
            with open('/Users/jiale.cheng/Documents/mcp/test/result.txt', 'w', encoding='utf-8') as f:
                f.write(f"工厂生产规划问题求解结果\n")
                f.write(f"========================\n\n")
                f.write(f"最优目标函数值: {model.objval:,.2f} 元\n")
                f.write(f"求解状态: 最优解\n\n")
                
                # 写入详细的JSON结果
                f.write("详细结果 (JSON格式):\n")
                f.write(json.dumps(results, ensure_ascii=False, indent=2))
            
            return model.objval, results
            
        else:
            error_msg = f"模型未找到最优解。状态码: {model.status}"
            print(f"\n{error_msg}")
            
            # 写入错误结果
            with open('/Users/jiale.cheng/Documents/mcp/test/result.txt', 'w', encoding='utf-8') as f:
                f.write(f"工厂生产规划问题求解结果\n")
                f.write(f"========================\n\n")
                f.write(f"求解失败: {error_msg}\n")
            
            return None, None
    
    except cp.CoptError as e:
        error_msg = f"COPT Error: {e.retcode} - {e.message}"
        print(error_msg)
        
        # 写入错误信息
        with open('/Users/jiale.cheng/Documents/mcp/test/result.txt', 'w', encoding='utf-8') as f:
            f.write(f"工厂生产规划问题求解结果\n")
            f.write(f"========================\n\n")
            f.write(f"求解错误: {error_msg}\n")
        
        return None, None
    
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        print(error_msg)
        
        # 写入错误信息
        with open('/Users/jiale.cheng/Documents/mcp/test/result.txt', 'w', encoding='utf-8') as f:
            f.write(f"工厂生产规划问题求解结果\n")
            f.write(f"========================\n\n")
            f.write(f"程序错误: {error_msg}\n")
        
        return None, None
    
    finally:
        # 确保关闭COPT环境
        if 'env' in locals() and env is not None:
            env.close()

if __name__ == "__main__":
    objective_value, results = solve_factory_planning()
    if objective_value is not None:
        print(f"\n>>> 求解完成！最优目标函数值: {objective_value:,.2f} 元")
        print(">>> 详细结果已保存到 result.txt")
    else:
        print("\n>>> 求解失败，请检查错误信息")