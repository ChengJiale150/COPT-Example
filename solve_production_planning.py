#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生产规划与人员培训优化问题求解器
使用COPT求解器解决多周期动态规划问题
"""

import coptpy as cp
from coptpy import COPT
import json
import csv
import os

def solve_production_planning():
    """
    求解生产规划与人员培训优化问题
    """
    try:
        # 1. 创建COPT求解环境
        env = cp.Envr()
        model = env.createModel("production_planning")
        
        # 2. 定义问题参数
        # 时间周期
        T = list(range(1, 9))  # 1-8周
        
        # 产品类型
        P = ['I', 'II']
        
        # 基础参数
        S_orig = 50  # 初始熟练工数量
        N_target = 50  # 目标培训新工人数
        H_reg = 40  # 常规工作时长(小时/周)
        H_ot = 60  # 加班工作时长(小时/周)
        K = 3  # 每名培训师可带学员数
        tau = 2  # 培训周期(周)
        
        # 生产效率(小时/公斤)
        R = {
            'I': 0.1,    # 1/10 小时/公斤
            'II': 1/6    # 1/6 小时/公斤
        }
        
        # 工资参数
        W_orig_reg = 360  # 初始熟练工常规周薪
        W_new_reg = 240   # 新熟练工常规周薪
        W_ot = 540        # 加班周薪(新老员工相同)
        W_trainee = 120   # 学员周薪
        
        # 罚款参数
        C = {
            'I': 0.5,   # 食品I延期罚款(元/公斤/周)
            'II': 0.6   # 食品II延期罚款(元/公斤/周)
        }
        
        # 需求数据
        D = {
            ('I', 1): 10000, ('I', 2): 10000, ('I', 3): 12000, ('I', 4): 12000,
            ('I', 5): 16000, ('I', 6): 16000, ('I', 7): 20000, ('I', 8): 20000,
            ('II', 1): 6000, ('II', 2): 7200, ('II', 3): 8400, ('II', 4): 10800,
            ('II', 5): 10800, ('II', 6): 12000, ('II', 7): 12000, ('II', 8): 12000
        }
        
        print("=== 生产规划与人员培训优化问题 ===")
        print(f"计划周期: {len(T)} 周")
        print(f"产品类型: {len(P)} 种")
        print(f"初始熟练工: {S_orig} 名")
        print(f"目标培训新工人: {N_target} 名")
        
        # 3. 定义决策变量
        print("\n正在创建决策变量...")
        
        # 人员分配决策变量(整数类型)
        s_orig_reg = model.addVars(T, vtype=COPT.INTEGER, lb=0, nameprefix="s_orig_reg")
        s_orig_ot = model.addVars(T, vtype=COPT.INTEGER, lb=0, nameprefix="s_orig_ot")
        s_new_reg = model.addVars(T, vtype=COPT.INTEGER, lb=0, nameprefix="s_new_reg")
        s_new_ot = model.addVars(T, vtype=COPT.INTEGER, lb=0, nameprefix="s_new_ot")
        T_orig = model.addVars(T, vtype=COPT.INTEGER, lb=0, nameprefix="T_orig")
        T_new = model.addVars(T, vtype=COPT.INTEGER, lb=0, nameprefix="T_new")
        n_start = model.addVars(T, vtype=COPT.INTEGER, lb=0, nameprefix="n_start")
        
        # 状态与生产变量(连续非负类型)
        S_new_avail = model.addVars(T, vtype=COPT.CONTINUOUS, lb=0, nameprefix="S_new_avail")
        X = model.addVars(P, T, vtype=COPT.CONTINUOUS, lb=0, nameprefix="X")
        B = model.addVars(P, T, vtype=COPT.CONTINUOUS, lb=0, nameprefix="B")
        
        # 4. 设置目标函数
        print("正在设置目标函数...")
        
        # 工资成本
        wage_cost = cp.quicksum(
            # 生产人员工资
            W_orig_reg * s_orig_reg[t] + W_ot * s_orig_ot[t] +
            W_new_reg * s_new_reg[t] + W_ot * s_new_ot[t] +
            # 培训师工资(当前周开始的培训和上周开始仍在进行的培训)
            W_orig_reg * (T_orig[t] + (T_orig[t-1] if t > 1 else 0)) +
            W_new_reg * (T_new[t] + (T_new[t-1] if t > 1 else 0)) +
            # 学员工资(当前周开始的培训和上周开始仍在进行的培训)
            W_trainee * (n_start[t] + (n_start[t-1] if t > 1 else 0))
            for t in T
        )
        
        # 罚款成本
        penalty_cost = cp.quicksum(C[p] * B[p, t] for p in P for t in T)
        
        # 总成本
        total_cost = wage_cost + penalty_cost
        model.setObjective(total_cost, sense=COPT.MINIMIZE)
        
        # 5. 添加约束条件
        print("正在添加约束条件...")
        
        # 约束1: 劳动力守恒约束
        for t in T:
            # 计算上一周开始的培训师数量（他们在第t周仍在培训）
            prev_orig_trainers = T_orig[t-1] if t > 1 else 0
            prev_new_trainers = T_new[t-1] if t > 1 else 0
            
            # 初始熟练工守恒
            model.addConstr(
                s_orig_reg[t] + s_orig_ot[t] + T_orig[t] + prev_orig_trainers == S_orig,
                name=f"workforce_conservation_orig_{t}"
            )
            
            # 新熟练工守恒
            model.addConstr(
                s_new_reg[t] + s_new_ot[t] + T_new[t] + prev_new_trainers == S_new_avail[t],
                name=f"workforce_conservation_new_{t}"
            )
        
        # 约束2: 劳动力动态演化约束
        for t in T:
            if t == 1:
                # 第1周初可用新熟练工为0
                model.addConstr(S_new_avail[t] == 0, name=f"workforce_dynamics_{t}")
            elif t == 2:
                # 第2周初 = 第1周初 + 0(因为第-1周没有开始培训的人)
                model.addConstr(S_new_avail[t] == S_new_avail[t-1], name=f"workforce_dynamics_{t}")
            else:
                # 第t周初 = 第t-1周初 + 第t-2周开始培训的人数
                model.addConstr(
                    S_new_avail[t] == S_new_avail[t-1] + n_start[t-2],
                    name=f"workforce_dynamics_{t}"
                )
        
        # 约束3: 培训约束
        for t in T:
            # 培训能力约束
            model.addConstr(
                n_start[t] <= K * (T_orig[t] + T_new[t]),
                name=f"training_capacity_{t}"
            )
        
        # 总培训目标约束(最晚第7周开始培训)
        model.addConstr(
            cp.quicksum(n_start[t] for t in range(1, 8)) == N_target,
            name="total_training_target"
        )
        
        # 约束4: 生产能力约束
        for t in T:
            model.addConstr(
                cp.quicksum(R[p] * X[p, t] for p in P) <= 
                H_reg * (s_orig_reg[t] + s_new_reg[t]) + H_ot * (s_orig_ot[t] + s_new_ot[t]),
                name=f"production_capacity_{t}"
            )
        
        # 约束5: 积压平衡约束
        for p in P:
            for t in T:
                if t == 1:
                    # 第1周: B_p_1 = 0 + D_p_1 - X_p_1
                    model.addConstr(
                        B[p, t] == D[p, t] - X[p, t],
                        name=f"backlog_balance_{p}_{t}"
                    )
                else:
                    # 第t周: B_p_t = B_p_(t-1) + D_p_t - X_p_t
                    model.addConstr(
                        B[p, t] == B[p, t-1] + D[p, t] - X[p, t],
                        name=f"backlog_balance_{p}_{t}"
                    )
        
        # 约束6: 边界条件已经在变量定义时通过lb=0处理
        
        # 6. 求解模型
        print("正在求解模型...")
        model.solve()
        
        # 7. 分析求解结果
        if model.status == COPT.OPTIMAL:
            print(f"\n=== 求解成功 ===")
            print(f"模型状态: 最优解 (COPT.OPTIMAL)")
            print(f"最优目标函数值(总成本): {model.objval:,.2f} 元")
            
            # 准备详细结果数据
            detailed_results = {
                "objective_value": model.objval,
                "total_weeks": len(T),
                "weekly_results": {}
            }
            
            # 创建CSV结果文件
            csv_filename = "output/weekly_results.csv"
            os.makedirs("output", exist_ok=True)
            
            # 准备CSV数据
            csv_data = []
            
            print(f"\n=== 周度详细结果 ===")
            for t in T:
                week_data = {
                    "week": t,
                    "orig_workers_regular": round(s_orig_reg[t].x),
                    "orig_workers_overtime": round(s_orig_ot[t].x),
                    "new_workers_regular": round(s_new_reg[t].x),
                    "new_workers_overtime": round(s_new_ot[t].x),
                    "orig_trainers": round(T_orig[t].x),
                    "new_trainers": round(T_new[t].x),
                    "new_trainees_start": round(n_start[t].x),
                    "new_workers_available": S_new_avail[t].x,
                    "production_I": X['I', t].x,
                    "production_II": X['II', t].x,
                    "backlog_I": B['I', t].x,
                    "backlog_II": B['II', t].x
                }
                
                detailed_results["weekly_results"][t] = week_data
                csv_data.append(week_data)
                
                print(f"\n第 {t} 周:")
                print(f"  人员分配:")
                print(f"    初始熟练工 - 常规: {round(s_orig_reg[t].x)}名, 加班: {round(s_orig_ot[t].x)}名")
                print(f"    新熟练工   - 常规: {round(s_new_reg[t].x)}名, 加班: {round(s_new_ot[t].x)}名")
                print(f"    培训师     - 初始: {round(T_orig[t].x)}名, 新: {round(T_new[t].x)}名")
                print(f"    本周开始培训新工人: {round(n_start[t].x)}名")
                print(f"    可用新熟练工总数: {S_new_avail[t].x:.1f}名")
                print(f"  生产情况:")
                print(f"    食品I生产量: {X['I', t].x:,.1f} 公斤")
                print(f"    食品II生产量: {X['II', t].x:,.1f} 公斤")
                print(f"  积压情况:")
                print(f"    食品I积压: {B['I', t].x:,.1f} 公斤")
                print(f"    食品II积压: {B['II', t].x:,.1f} 公斤")
            
            # 写入CSV文件
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = csv_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
            
            print(f"\n周度结果已保存至: {csv_filename}")
            
            # 写入详细JSON结果
            json_filename = "output/detailed_results.json"
            with open(json_filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(detailed_results, jsonfile, indent=2, ensure_ascii=False)
            
            print(f"详细结果已保存至: {json_filename}")
            
            # 写入目标函数值到result.txt
            with open("result.txt", 'w', encoding='utf-8') as result_file:
                result_file.write(f"最优目标函数值: {model.objval:.2f} 元\n")
                result_file.write(f"求解状态: 最优解\n")
                result_file.write(f"总成本: {model.objval:,.2f} 元\n")
            
            print(f"最终目标函数结果已保存至: result.txt")
            
            # 保存模型文件
            model.write("output/production_planning.lp")
            model.write("output/production_planning.sol")
            
            print(f"模型文件已保存至: output/production_planning.lp")
            print(f"解文件已保存至: output/production_planning.sol")
            
            # 统计信息
            print(f"\n=== 求解统计信息 ===")
            print(f"最优界: {model.getAttr(COPT.Attr.BestBnd):,.2f}")
            print(f"最优间隙: {model.getAttr(COPT.Attr.BestGap)*100:.4f}%")
            print(f"搜索节点数: {model.getAttr(COPT.Attr.NodeCnt)}")
            
            return True, model.objval
            
        else:
            print(f"\n模型未找到最优解")
            print(f"状态码: {model.status}")
            status_map = {
                COPT.INFEASIBLE: "模型无可行解",
                COPT.UNBOUNDED: "目标函数无界",
                COPT.TIMEOUT: "求解超时",
                COPT.INTERRUPTED: "用户中断"
            }
            print(f"状态描述: {status_map.get(model.status, '未知状态')}")
            
            # 写入失败结果
            with open("result.txt", 'w', encoding='utf-8') as result_file:
                result_file.write(f"求解失败\n")
                result_file.write(f"状态码: {model.status}\n")
                result_file.write(f"状态描述: {status_map.get(model.status, '未知状态')}\n")
            
            return False, None
    
    except cp.CoptError as e:
        print(f"COPT Error: {e.retcode} - {e.message}")
        with open("result.txt", 'w', encoding='utf-8') as result_file:
            result_file.write(f"COPT错误: {e.retcode} - {e.message}\n")
        return False, None
    
    except Exception as e:
        print(f"发生意外错误: {e}")
        with open("result.txt", 'w', encoding='utf-8') as result_file:
            result_file.write(f"意外错误: {e}\n")
        return False, None
    
    finally:
        if 'env' in locals() and env is not None:
            env.close()

if __name__ == "__main__":
    print("开始求解生产规划与人员培训优化问题...")
    success, objective_value = solve_production_planning()
    
    if success:
        print(f"\n✅ 求解成功! 最优总成本: {objective_value:,.2f} 元")
    else:
        print(f"\n❌ 求解失败!")