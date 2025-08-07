"""
折叠桌公司6个月生产与人力资源规划问题 - 使用COPT求解器
这是一个混合整数线性规划(MILP)问题，目标是最大化总净利润
"""

import coptpy as cp
from coptpy import COPT
import json
import os

def solve_production_planning():
    """
    求解折叠桌公司的生产与人力资源规划问题
    """
    try:
        # 1. 创建COPT求解环境
        env = cp.Envr()
        
        # 2. 创建优化模型
        model = env.createModel("production_planning")
        
        # 3. 定义问题数据
        # 集合
        T = list(range(1, 7))  # 月份集合: {1, 2, 3, 4, 5, 6}
        
        # 初始状态 (t=0)
        W_0 = 1000  # 初始员工数量 (人)
        I_0 = 15000  # 初始库存 (件)
        B_0 = 0      # 初始缺货订单 (件)
        
        # 收入与成本参数
        R = 300          # 单位产品售价 (元/件)
        C_mat = 90       # 单位产品原材料成本 (元/件)
        C_out = 200      # 单位产品外包成本 (元/件)
        C_inv = 15       # 单位产品月度库存持有成本 (元/件)
        C_back = 35      # 单位产品月度缺货成本 (元/件)
        C_hire = 5000    # 每位员工的招聘成本 (元/人)
        C_fire = 8000    # 每位员工的解雇成本 (元/人)
        C_wage_reg = 30  # 每小时正常工资 (元/小时)
        C_wage_ot = 40   # 每小时加班工资 (元/小时)
        
        # 生产与劳动力参数
        L_req = 5        # 生产单位产品所需工时 (小时/件)
        H_reg = 160      # 每位员工每月正常工作时长 (小时/人)
        H_ot_max = 20    # 每位员工每月最大加班时长 (小时/人)
        
        # 需求预测
        D = {1: 20000, 2: 40000, 3: 42000, 4: 35000, 5: 19000, 6: 18500}
        
        # 期末条件
        I_final = 10000  # 期末最低库存要求 (件)
        B_final = 0      # 期末缺货订单要求 (件)
        
        print("问题数据已加载完成")
        print(f"规划期间: {len(T)}个月")
        print(f"初始状态: 员工{W_0}人, 库存{I_0}件, 缺货{B_0}件")
        print(f"需求预测: {list(D.values())}")
        
        # 4. 添加决策变量
        # 连续变量
        P = model.addVars(T, lb=0.0, nameprefix="P")    # 第t月内部生产数量
        O = model.addVars(T, lb=0.0, nameprefix="O")    # 第t月外包采购数量
        I = model.addVars(T, lb=0.0, nameprefix="I")    # 第t月末库存数量
        B = model.addVars(T, lb=0.0, nameprefix="B")    # 第t月末缺货订单数量
        OT = model.addVars(T, lb=0.0, nameprefix="OT")  # 第t月总加班工时
        
        # 整数变量
        W = model.addVars(T, vtype=COPT.INTEGER, lb=0, nameprefix="W")  # 第t月员工总数
        H = model.addVars(T, vtype=COPT.INTEGER, lb=0, nameprefix="H")  # 第t月招聘数量
        F = model.addVars(T, vtype=COPT.INTEGER, lb=0, nameprefix="F")  # 第t月解雇数量
        
        print("决策变量已添加完成")
        
        # 5. 添加约束条件
        
        # 约束1: 员工数量平衡约束
        # W_t = W_{t-1} + H_t - F_t, ∀t∈T
        # 对于t=1: W_1 = W_0 + H_1 - F_1
        model.addConstr(W[1] == W_0 + H[1] - F[1], name="workforce_balance_1")
        for t in range(2, 7):
            model.addConstr(W[t] == W[t-1] + H[t] - F[t], name=f"workforce_balance_{t}")
        
        # 约束2: 库存与缺货平衡约束
        # I_t - B_t = (I_{t-1} - B_{t-1}) + P_t + O_t - D_t, ∀t∈T
        # 对于t=1: I_1 - B_1 = (I_0 - B_0) + P_1 + O_1 - D_1
        model.addConstr(I[1] - B[1] == (I_0 - B_0) + P[1] + O[1] - D[1], 
                       name="inventory_balance_1")
        for t in range(2, 7):
            model.addConstr(I[t] - B[t] == (I[t-1] - B[t-1]) + P[t] + O[t] - D[t], 
                           name=f"inventory_balance_{t}")
        
        # 约束3: 生产工时约束
        # L_req * P_t ≤ H_reg * W_t + OT_t, ∀t∈T
        for t in T:
            model.addConstr(L_req * P[t] <= H_reg * W[t] + OT[t], 
                           name=f"production_hour_{t}")
        
        # 约束4: 加班工时上限约束
        # OT_t ≤ H_ot_max * W_t, ∀t∈T
        for t in T:
            model.addConstr(OT[t] <= H_ot_max * W[t], name=f"overtime_limit_{t}")
        
        # 约束5: 期末状态约束
        # I_6 ≥ I_final, B_6 = B_final
        model.addConstr(I[6] >= I_final, name="final_inventory")
        model.addConstr(B[6] == B_final, name="final_backorder")
        
        print("约束条件已添加完成")
        
        # 6. 设置目标函数
        # 最大化总净利润 = 总收入 - 总成本
        # 销售量 = D_t + B_{t-1} - B_t
        
        # 收入项: R * (销售量)
        revenue_terms = []
        # 对于t=1: 销售量 = D_1 + B_0 - B_1 = D_1 + 0 - B_1 = D_1 - B_1
        revenue_terms.append(R * (D[1] - B[1]))
        # 对于t≥2: 销售量 = D_t + B_{t-1} - B_t
        for t in range(2, 7):
            revenue_terms.append(R * (D[t] + B[t-1] - B[t]))
        
        total_revenue = cp.quicksum(revenue_terms)
        
        # 成本项
        # 原材料成本
        material_cost = cp.quicksum(C_mat * P[t] for t in T)
        
        # 外包成本
        outsourcing_cost = cp.quicksum(C_out * O[t] for t in T)
        
        # 库存持有成本
        inventory_cost = cp.quicksum(C_inv * I[t] for t in T)
        
        # 缺货成本
        backorder_cost = cp.quicksum(C_back * B[t] for t in T)
        
        # 正常工资成本
        regular_wage_cost = cp.quicksum(C_wage_reg * H_reg * W[t] for t in T)
        
        # 加班工资成本
        overtime_wage_cost = cp.quicksum(C_wage_ot * OT[t] for t in T)
        
        # 招聘成本
        hiring_cost = cp.quicksum(C_hire * H[t] for t in T)
        
        # 解雇成本
        firing_cost = cp.quicksum(C_fire * F[t] for t in T)
        
        # 总成本
        total_cost = (material_cost + outsourcing_cost + inventory_cost + 
                     backorder_cost + regular_wage_cost + overtime_wage_cost + 
                     hiring_cost + firing_cost)
        
        # 目标函数: 最大化总净利润
        objective = total_revenue - total_cost
        model.setObjective(objective, sense=COPT.MAXIMIZE)
        
        print("目标函数已设置完成")
        
        # 7. 求解模型
        print("\n开始求解模型...")
        model.solve()
        
        # 8. 分析求解结果
        results = {}
        
        if model.status == COPT.OPTIMAL:
            print("\n=== 求解成功 ===")
            print(f"模型状态: 最优解 (COPT.OPTIMAL)")
            print(f"最优目标函数值(总净利润): {model.objval:,.2f} 元")
            
            results['status'] = 'OPTIMAL'
            results['objective_value'] = model.objval
            results['detailed_solution'] = {}
            
            # 详细解决方案
            print("\n=== 详细解决方案 ===")
            
            # 月度计划
            monthly_plan = {}
            total_production = 0
            total_outsourcing = 0
            
            for t in T:
                plan = {
                    'production': P[t].x,
                    'outsourcing': O[t].x,
                    'inventory': I[t].x,
                    'backorder': B[t].x,
                    'workforce': int(W[t].x),
                    'hiring': int(H[t].x),
                    'firing': int(F[t].x),
                    'overtime_hours': OT[t].x,
                    'demand': D[t]
                }
                monthly_plan[f'month_{t}'] = plan
                total_production += P[t].x
                total_outsourcing += O[t].x
                
                print(f"\n第{t}月计划:")
                print(f"  需求量: {D[t]:,} 件")
                print(f"  内部生产: {P[t].x:,.0f} 件")
                print(f"  外包采购: {O[t].x:,.0f} 件")
                print(f"  库存: {I[t].x:,.0f} 件")
                print(f"  缺货: {B[t].x:,.0f} 件")
                print(f"  员工数量: {int(W[t].x)} 人")
                print(f"  招聘: {int(H[t].x)} 人")
                print(f"  解雇: {int(F[t].x)} 人")
                print(f"  加班工时: {OT[t].x:,.0f} 小时")
            
            results['monthly_plan'] = monthly_plan
            
            # 汇总统计
            print(f"\n=== 汇总统计 ===")
            print(f"总内部生产量: {total_production:,.0f} 件")
            print(f"总外包采购量: {total_outsourcing:,.0f} 件")
            print(f"总供给量: {total_production + total_outsourcing:,.0f} 件")
            print(f"总需求量: {sum(D.values()):,} 件")
            
            results['summary'] = {
                'total_production': total_production,
                'total_outsourcing': total_outsourcing,
                'total_supply': total_production + total_outsourcing,
                'total_demand': sum(D.values())
            }
            
            # 成本分解
            print(f"\n=== 成本分解 ===")
            actual_material_cost = sum(C_mat * P[t].x for t in T)
            actual_outsourcing_cost = sum(C_out * O[t].x for t in T)
            actual_inventory_cost = sum(C_inv * I[t].x for t in T)
            actual_backorder_cost = sum(C_back * B[t].x for t in T)
            actual_regular_wage = sum(C_wage_reg * H_reg * W[t].x for t in T)
            actual_overtime_wage = sum(C_wage_ot * OT[t].x for t in T)
            actual_hiring_cost = sum(C_hire * H[t].x for t in T)
            actual_firing_cost = sum(C_fire * F[t].x for t in T)
            
            print(f"原材料成本: {actual_material_cost:,.2f} 元")
            print(f"外包成本: {actual_outsourcing_cost:,.2f} 元")
            print(f"库存成本: {actual_inventory_cost:,.2f} 元")
            print(f"缺货成本: {actual_backorder_cost:,.2f} 元")
            print(f"正常工资: {actual_regular_wage:,.2f} 元")
            print(f"加班工资: {actual_overtime_wage:,.2f} 元")
            print(f"招聘成本: {actual_hiring_cost:,.2f} 元")
            print(f"解雇成本: {actual_firing_cost:,.2f} 元")
            
            total_actual_cost = (actual_material_cost + actual_outsourcing_cost + 
                               actual_inventory_cost + actual_backorder_cost + 
                               actual_regular_wage + actual_overtime_wage + 
                               actual_hiring_cost + actual_firing_cost)
            print(f"总成本: {total_actual_cost:,.2f} 元")
            
            # 收入计算
            actual_revenue = 0
            for t in T:
                if t == 1:
                    sales = D[t] - B[t].x
                else:
                    sales = D[t] + B[t-1].x - B[t].x
                actual_revenue += R * sales
            print(f"总收入: {actual_revenue:,.2f} 元")
            print(f"净利润: {actual_revenue - total_actual_cost:,.2f} 元")
            
            results['cost_breakdown'] = {
                'material_cost': actual_material_cost,
                'outsourcing_cost': actual_outsourcing_cost,
                'inventory_cost': actual_inventory_cost,
                'backorder_cost': actual_backorder_cost,
                'regular_wage_cost': actual_regular_wage,
                'overtime_wage_cost': actual_overtime_wage,
                'hiring_cost': actual_hiring_cost,
                'firing_cost': actual_firing_cost,
                'total_cost': total_actual_cost,
                'total_revenue': actual_revenue,
                'net_profit': actual_revenue - total_actual_cost
            }
            
            print(f"\n=== MIP求解统计信息 ===")
            print(f"最优界 (Best Bound): {model.getAttr(COPT.Attr.BestBnd):,.2f}")
            print(f"最优间隙 (Optimality Gap): {model.getAttr(COPT.Attr.BestGap) * 100:.6f}%")
            print(f"搜索节点数 (Node Count): {model.getAttr(COPT.Attr.NodeCnt)}")
            
            results['solver_stats'] = {
                'best_bound': model.getAttr(COPT.Attr.BestBnd),
                'optimality_gap': model.getAttr(COPT.Attr.BestGap),
                'node_count': model.getAttr(COPT.Attr.NodeCnt)
            }
            
        else:
            print(f"\n模型未找到最优解。状态码: {model.status}")
            results['status'] = f'NOT_OPTIMAL_{model.status}'
            
            status_map = {
                COPT.INFEASIBLE: "模型无可行解",
                COPT.UNBOUNDED: "目标函数无界",
                COPT.TIMEOUT: "求解超时",
                COPT.INTERRUPTED: "用户中断"
            }
            error_msg = status_map.get(model.status, "未知状态")
            print(f"状态描述: {error_msg}")
            results['error_message'] = error_msg
        
        return results
        
    except cp.CoptError as e:
        print(f"COPT Error: {e.retcode} - {e.message}")
        return {'status': 'COPT_ERROR', 'error': f"{e.retcode} - {e.message}"}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {'status': 'UNEXPECTED_ERROR', 'error': str(e)}
    finally:
        if 'env' in locals() and env is not None:
            env.close()

def main():
    """主函数"""
    print("折叠桌公司6个月生产与人力资源规划问题")
    print("=" * 50)
    
    # 求解问题
    results = solve_production_planning()
    
    # 确保output目录存在
    os.makedirs('output', exist_ok=True)
    
    # 保存详细结果到JSON文件
    with open('output/detailed_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 保存目标函数结果到result.txt
    with open('result.txt', 'w', encoding='utf-8') as f:
        if results['status'] == 'OPTIMAL':
            f.write(f"最优目标函数值(总净利润): {results['objective_value']:,.2f} 元\n")
            f.write(f"求解状态: {results['status']}\n")
            f.write(f"最优间隙: {results['solver_stats']['optimality_gap'] * 100:.6f}%\n")
        else:
            f.write(f"求解状态: {results['status']}\n")
            if 'error_message' in results:
                f.write(f"错误信息: {results['error_message']}\n")
    
    print(f"\n结果已保存:")
    print(f"- 详细结果: output/detailed_results.json")
    print(f"- 目标函数结果: result.txt")

if __name__ == "__main__":
    main()