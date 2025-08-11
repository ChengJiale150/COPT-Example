"""
非均衡指派问题求解脚本
使用COPT求解器求解5名工人选4名完成4项任务的最优指派方案
目标：最小化总工时
"""

import coptpy as cp
from coptpy import COPT

def solve_assignment_problem():
    """求解非均衡指派问题"""
    try:
        # 1. 创建COPT求解环境
        env = cp.Envr()
        
        # 2. 创建优化模型
        model = env.createModel("unbalanced_assignment_problem")
        
        # 3. 定义问题数据
        # 工人集合 (I, II, III, IV, V)
        workers = ['I', 'II', 'III', 'IV', 'V']
        # 任务集合 (A, B, C, D) 
        tasks = ['A', 'B', 'C', 'D']
        
        # 成本矩阵 c_ij: 工人i完成任务j所需的时间(小时)
        # 按照problem.md中的表格数据
        cost_matrix = {
            ('I', 'A'): 9,   ('I', 'B'): 4,   ('I', 'C'): 3,   ('I', 'D'): 7,
            ('II', 'A'): 4,  ('II', 'B'): 6,  ('II', 'C'): 5,  ('II', 'D'): 6,
            ('III', 'A'): 5, ('III', 'B'): 4, ('III', 'C'): 7, ('III', 'D'): 5,
            ('IV', 'A'): 7,  ('IV', 'B'): 5,  ('IV', 'C'): 2,  ('IV', 'D'): 3,
            ('V', 'A'): 10,  ('V', 'B'): 6,   ('V', 'C'): 7,   ('V', 'D'): 4
        }
        
        # 4. 添加决策变量
        # x_ij: 二元变量，如果指派工人i去完成任务j，则x_ij=1，否则x_ij=0
        x = {}
        for i in workers:
            for j in tasks:
                x[i, j] = model.addVar(vtype=COPT.BINARY, name=f"x_{i}_{j}")
        
        # 5. 添加约束条件
        # 约束1: 任务分配唯一性约束
        # 每一项任务都必须被指派给且仅被指派给一名工人
        for j in tasks:
            model.addConstr(
                cp.quicksum(x[i, j] for i in workers) == 1,
                name=f"task_assignment_{j}"
            )
        
        # 约束2: 工人工作限制约束  
        # 每一名工人最多只能被指派一项任务(使用<=处理非均衡问题)
        for i in workers:
            model.addConstr(
                cp.quicksum(x[i, j] for j in tasks) <= 1,
                name=f"worker_limit_{i}"
            )
        
        # 6. 设置目标函数
        # 最小化完成所有任务所需的总工时
        objective = cp.quicksum(cost_matrix[i, j] * x[i, j] for i in workers for j in tasks)
        model.setObjective(objective, sense=COPT.MINIMIZE)
        
        # 7. 求解模型
        print("开始求解非均衡指派问题...")
        model.solve()
        
        # 8. 分析求解结果
        if model.status == COPT.OPTIMAL:
            print("\n=== 求解结果 ===")
            print(f"模型状态: 找到最优解")
            print(f"最优目标函数值: {model.objval:.0f} 小时")
            
            print("\n=== 最优指派方案 ===")
            total_time = 0
            assigned_workers = []
            unassigned_workers = []
            
            # 输出指派方案
            for i in workers:
                assigned = False
                for j in tasks:
                    if x[i, j].x > 0.5:  # 判断变量是否为1
                        print(f"工人 {i} 被指派完成任务 {j}，需要时间: {cost_matrix[i, j]} 小时")
                        total_time += cost_matrix[i, j]
                        assigned_workers.append(i)
                        assigned = True
                        break
                if not assigned:
                    unassigned_workers.append(i)
            
            print(f"\n未分配的工人: {', '.join(unassigned_workers) if unassigned_workers else '无'}")
            print(f"总工时: {total_time} 小时")
            
            # 验证结果
            print("\n=== 方案验证 ===")
            print(f"分配的工人数量: {len(assigned_workers)}/4 (需要4名)")
            print(f"未分配的工人数量: {len(unassigned_workers)}/1 (预期1名)")
            print(f"所有任务是否都被分配: {'是' if len(assigned_workers) == 4 else '否'}")
            
            # 保存结果到文件
            with open('result.txt', 'w', encoding='utf-8') as f:
                f.write("非均衡指派问题求解结果\n")
                f.write("="*30 + "\n")
                f.write(f"最优目标函数值: {model.objval:.0f} 小时\n\n")
                f.write("最优指派方案:\n")
                for i in workers:
                    for j in tasks:
                        if x[i, j].x > 0.5:
                            f.write(f"工人 {i} -> 任务 {j} (时间: {cost_matrix[i, j]} 小时)\n")
                f.write(f"\n未分配的工人: {', '.join(unassigned_workers)}\n")
                f.write(f"总工时: {total_time} 小时\n")
            
            print(f"\n结果已保存到 result.txt 文件")
            
            return model.objval
            
        else:
            print(f"\n模型未找到最优解。状态码: {model.status}")
            status_descriptions = {
                COPT.INFEASIBLE: "模型无可行解",
                COPT.UNBOUNDED: "目标函数无界", 
                COPT.TIMEOUT: "求解超时",
                COPT.INTERRUPTED: "用户中断"
            }
            print(f"状态描述: {status_descriptions.get(model.status, '未知状态')}")
            return None
            
    except cp.CoptError as e:
        print(f"COPT错误: {e.retcode} - {e.message}")
        return None
    except Exception as e:
        print(f"发生未预期的错误: {e}")
        return None
    finally:
        # 确保释放资源
        if 'env' in locals() and env is not None:
            env.close()

if __name__ == "__main__":
    result = solve_assignment_problem()
    if result is not None:
        print(f"\n求解完成，最优总工时为: {result:.0f} 小时")
    else:
        print("\n求解失败")