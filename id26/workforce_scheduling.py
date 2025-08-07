"""
24小时便利店劳动力排班问题求解
使用COPT优化求解器解决整数线性规划问题

问题描述：
- 24小时便利店分为6个时间段
- 每个销售人员工作连续8小时
- 班次开始时间只能是6个指定时间点之一
- 目标：最小化总雇佣人数，同时满足每个时间段的最低人数需求
"""

import coptpy as cp
from coptpy import COPT

def solve_workforce_scheduling():
    """解决劳动力排班问题"""
    
    try:
        # 1. 创建COPT求解环境
        env = cp.Envr()
        model = env.createModel("workforce_scheduling")
        
        # 2. 定义问题数据
        # 时间段索引：1-6 对应 2:00, 6:00, 10:00, 14:00, 18:00, 22:00
        time_periods = [1, 2, 3, 4, 5, 6]
        time_ranges = ["2:00-6:00", "6:00-10:00", "10:00-14:00", 
                      "14:00-18:00", "18:00-22:00", "22:00-2:00"]
        
        # 每个时间段的最低人数需求
        requirements = {
            1: 10,  # 2:00-6:00
            2: 15,  # 6:00-10:00  
            3: 25,  # 10:00-14:00
            4: 20,  # 14:00-18:00
            5: 18,  # 18:00-22:00
            6: 12   # 22:00-2:00
        }
        
        print("=== 24小时便利店劳动力排班问题 ===")
        print("\n时间段需求:")
        for t in time_periods:
            print(f"  时间段 {t} ({time_ranges[t-1]}): {requirements[t]} 人")
        
        # 3. 添加决策变量
        # x[t]: 在时间段t开始时安排的销售人员数量
        x = model.addVars(time_periods, vtype=COPT.INTEGER, lb=0, nameprefix="x")
        
        # 4. 添加约束条件
        # 约束1: 第一个时间段的需求约束 (具有周期性)
        # x_1 + x_6 >= R_1 (第一个时间段的在岗人员来自本时段开始的x_1和前一天最后时段开始的x_6)
        model.addConstr(x[1] + x[6] >= requirements[1], name="demand_period_1")
        
        # 约束2: 其他时间段的需求约束
        # x_t + x_{t-1} >= R_t (每个时间段的在岗人员来自本时段开始的和上一时段开始的)
        for t in range(2, 7):  # t = 2, 3, 4, 5, 6
            model.addConstr(x[t] + x[t-1] >= requirements[t], name=f"demand_period_{t}")
        
        # 5. 设置目标函数
        # 最小化总雇佣人数
        model.setObjective(cp.quicksum(x[t] for t in time_periods), sense=COPT.MINIMIZE)
        
        # 6. 求解模型
        print("\n开始求解...")
        model.solve()
        
        # 7. 分析求解结果
        if model.status == COPT.OPTIMAL:
            print("\n=== 求解结果 ===")
            print("模型状态: 最优解")
            print(f"最少总雇佣人数: {int(model.objval)} 人")
            
            print("\n各时间段安排的人员数量:")
            schedule = {}
            for t in time_periods:
                staff_count = int(x[t].x)
                schedule[t] = staff_count
                print(f"  时间段 {t} ({time_ranges[t-1]}) 开始工作: {staff_count} 人")
            
            print("\n各时间段实际在岗人数验证:")
            for t in time_periods:
                if t == 1:
                    # 第一个时间段的在岗人数 = 本时段开始的 + 前一天最后时段开始的
                    actual_staff = schedule[1] + schedule[6]
                else:
                    # 其他时间段的在岗人数 = 本时段开始的 + 上一时段开始的
                    actual_staff = schedule[t] + schedule[t-1]
                
                print(f"  时间段 {t} ({time_ranges[t-1]}): {actual_staff} 人 (需求: {requirements[t]} 人)")
                
                # 验证约束是否满足
                if actual_staff >= requirements[t]:
                    print(f"    ✓ 满足需求")
                else:
                    print(f"    ✗ 不满足需求!")
            
            print("\nMIP 求解统计信息:")
            print(f"  最优界: {model.getAttr(COPT.Attr.BestBnd):.4f}")
            print(f"  最优间隙: {model.getAttr(COPT.Attr.BestGap) * 100:.4f}%")
            print(f"  搜索节点数: {model.getAttr(COPT.Attr.NodeCnt)}")
            
            # 8. 将结果写入文件
            with open("result.txt", "w", encoding="utf-8") as f:
                f.write("=== 24小时便利店劳动力排班问题求解结果 ===\n")
                f.write(f"最少总雇佣人数: {int(model.objval)} 人\n\n")
                f.write("各时间段安排的人员数量:\n")
                for t in time_periods:
                    f.write(f"时间段 {t} ({time_ranges[t-1]}) 开始工作: {int(x[t].x)} 人\n")
                f.write("\n各时间段实际在岗人数验证:\n")
                for t in time_periods:
                    if t == 1:
                        actual_staff = schedule[1] + schedule[6]
                    else:
                        actual_staff = schedule[t] + schedule[t-1]
                    f.write(f"时间段 {t} ({time_ranges[t-1]}): {actual_staff} 人 (需求: {requirements[t]} 人)\n")
            
            print(f"\n结果已保存到 result.txt 文件")
            
            # 9. 保存模型文件（可选）
            model.write("workforce_scheduling.mps")
            model.write("workforce_scheduling.lp")
            model.write("workforce_scheduling.sol")
            
            return True
            
        else:
            print(f"\n模型未找到最优解。状态码: {model.status}")
            status_map = {
                COPT.INFEASIBLE: "模型无可行解",
                COPT.UNBOUNDED: "目标函数无界",
                COPT.TIMEOUT: "求解超时",
                COPT.INTERRUPTED: "用户中断"
            }
            print(f"状态描述: {status_map.get(model.status, '未知状态')}")
            return False
            
    except cp.CoptError as e:
        print(f"COPT Error: {e.retcode} - {e.message}")
        return False
    except Exception as e:
        print(f"发生未知错误: {e}")
        return False
    finally:
        # 关闭COPT环境
        if 'env' in locals() and env is not None:
            env.close()

if __name__ == "__main__":
    solve_workforce_scheduling()