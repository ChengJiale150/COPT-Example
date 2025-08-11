#!/usr/bin/env python3
"""
修正后的工具购买与维修最优化问题
引入实际使用的工具数量作为决策变量

核心洞察：
1. 可用工具 = 新购 + 慢修返回 + 快修返回
2. 实际使用工具 = min(可用工具, 需求) = 需求 (因为必须满足需求)
3. 送修工具 = 实际使用工具 (只有使用过的工具才需要维修)
4. 多余的工具可以闲置，不需要维修

修正后的约束：
1. 可用工具 >= 需求：x_j + y_{j-p} + z_{j-q} >= r_j
2. 维修分配 = 需求：y_j + z_j = r_j (因为实际使用=需求)
"""

import coptpy as cp
from coptpy import COPT


def solve_corrected_tool_optimization():
    """求解修正后的工具购买与维修优化问题"""
    
    # 1. 问题数据定义
    n = 10  # 总阶段数
    r = [3, 5, 2, 4, 6, 5, 4, 3, 2, 1]  # 各阶段需求量 (索引0对应阶段1)
    a = 10  # 新购工具成本
    b = 1   # 慢修成本
    c = 3   # 快修成本  
    p = 3   # 慢修周期
    q = 1   # 快修周期
    
    print("=== 修正后的工具购买与维修优化问题 ===")
    print(f"阶段数: {n}")
    print(f"需求量: {r}")
    print(f"新购成本: {a}, 慢修成本: {b}, 快修成本: {c}")
    print(f"慢修周期: {p}, 快修周期: {q}")
    print()
    
    try:
        # 2. 创建COPT求解环境和模型
        env = cp.Envr()
        model = env.createModel("corrected_tool_optimization")
        
        # 3. 添加决策变量
        stages = range(1, n + 1)
        
        # x_j: 阶段j购买的新工具数量
        x = model.addVars(stages, vtype=COPT.INTEGER, lb=0, nameprefix="x")
        
        # y_j: 阶段j送去慢修的工具数量
        y = model.addVars(stages, vtype=COPT.INTEGER, lb=0, nameprefix="y")
        
        # z_j: 阶段j送去快修的工具数量
        z = model.addVars(stages, vtype=COPT.INTEGER, lb=0, nameprefix="z")
        
        # 4. 添加约束条件
        
        print("=== 修正后的约束条件 ===")
        
        # 约束1: 工具供应充足约束（修正为 >= ）
        # x_j + y_{j-p} + z_{j-q} >= r_j, ∀j ∈ {1,...,n}
        for j in stages:
            # 计算慢修返回量：如果j-p≤0则为0，否则为y[j-p]
            slow_repair_return = y[j-p] if j-p >= 1 else 0
            
            # 计算快修返回量：如果j-q≤0则为0，否则为z[j-q]
            fast_repair_return = z[j-q] if j-q >= 1 else 0
            
            # 添加供应充足约束（可以有多余的工具）
            model.addConstr(
                x[j] + slow_repair_return + fast_repair_return >= r[j-1],
                name=f"supply_sufficient_{j}"
            )
            
            slow_str = f"y[{j-p}]" if j-p >= 1 else "0"
            fast_str = f"z[{j-q}]" if j-q >= 1 else "0"
            print(f"阶段{j}: x[{j}] + {slow_str} + {fast_str} >= {r[j-1]} (供应充足)")
        
        # 约束2: 维修分配约束（保持不变）
        # y_j + z_j = r_j, ∀j ∈ {1,...,n}
        # 每个阶段使用的r_j个工具都必须送去维修
        for j in stages:
            model.addConstr(
                y[j] + z[j] == r[j-1],
                name=f"repair_allocation_{j}"
            )
            print(f"阶段{j}: y[{j}] + z[{j}] = {r[j-1]} (维修分配)")
        
        print()
        
        # 5. 设置目标函数
        # 最小化总成本：Σ(a*x_j + b*y_j + c*z_j)
        total_cost = cp.quicksum(
            a * x[j] + b * y[j] + c * z[j] for j in stages
        )
        model.setObjective(total_cost, sense=COPT.MINIMIZE)
        
        # 6. 求解模型
        print("开始求解修正后的模型...")
        model.solve()
        
        # 7. 分析和输出结果
        if model.status == COPT.OPTIMAL:
            print("求解成功！找到最优解。")
            print(f"最小总成本: {model.objval:.2f}")
            print()
            
            # 详细的决策方案
            print("=== 最优决策方案 ===")
            print("阶段 | 需求 | 新购 | 慢修 | 快修 | 慢修返回 | 快修返回 | 总供应 | 富余 | 阶段成本")
            print("-" * 85)
            
            total_purchase = 0
            total_slow_repair = 0
            total_fast_repair = 0
            stage_costs = []
            
            for j in stages:
                # 获取决策变量的值
                purchase = int(x[j].x + 0.5)  # 四舍五入到整数
                slow_repair = int(y[j].x + 0.5)
                fast_repair = int(z[j].x + 0.5)
                
                # 计算返回的维修工具数量
                slow_return = int(y[j-p].x + 0.5) if j-p >= 1 else 0
                fast_return = int(z[j-q].x + 0.5) if j-q >= 1 else 0
                
                # 计算总供应和富余
                total_supply = purchase + slow_return + fast_return
                surplus = total_supply - r[j-1]
                
                # 计算该阶段的成本
                stage_cost = a * purchase + b * slow_repair + c * fast_repair
                stage_costs.append(stage_cost)
                
                # 累计统计
                total_purchase += purchase
                total_slow_repair += slow_repair
                total_fast_repair += fast_repair
                
                # 输出该阶段的详细信息
                print(f" {j:2d}  | {r[j-1]:2d}   | {purchase:2d}   | {slow_repair:2d}   | {fast_repair:2d}   |"
                      f"    {slow_return:2d}    |    {fast_return:2d}    |   {total_supply:2d}   | {surplus:2d}   |  {stage_cost:6.2f}")
            
            print("-" * 85)
            print(f"总计 | {sum(r):2d}   | {total_purchase:2d}   | {total_slow_repair:2d}   | {total_fast_repair:2d}   |"
                  f"     -     |     -     |    -   |  -   | {sum(stage_costs):7.2f}")
            
            print()
            print("=== 成本分析 ===")
            print(f"新购成本: {total_purchase} × {a} = {total_purchase * a:.2f}")
            print(f"慢修成本: {total_slow_repair} × {b} = {total_slow_repair * b:.2f}")
            print(f"快修成本: {total_fast_repair} × {c} = {total_fast_repair * c:.2f}")
            print(f"总成本: {model.objval:.2f}")
            
            # 验证约束满足情况
            print()
            print("=== 约束验证 ===")
            constraint_satisfied = True
            
            for j in stages:
                # 验证供应充足性
                purchase = int(x[j].x + 0.5)
                slow_return = int(y[j-p].x + 0.5) if j-p >= 1 else 0
                fast_return = int(z[j-q].x + 0.5) if j-q >= 1 else 0
                supply = purchase + slow_return + fast_return
                demand = r[j-1]
                
                if supply < demand:
                    print(f"阶段{j}供应不足: 供应{supply} < 需求{demand}")
                    constraint_satisfied = False
                
                # 验证维修分配
                slow_repair = int(y[j].x + 0.5)
                fast_repair = int(z[j].x + 0.5)
                total_repair = slow_repair + fast_repair
                
                if total_repair != demand:
                    print(f"阶段{j}维修分配错误: 维修总量{total_repair} ≠ 使用量{demand}")
                    constraint_satisfied = False
            
            if constraint_satisfied:
                print("所有约束条件均满足 ✓")
            
            # 保存结果到文件
            with open("result.txt", "w", encoding="utf-8") as f:
                f.write("工具购买与维修优化问题求解结果\n")
                f.write("=" * 40 + "\n")
                f.write(f"最优目标函数值（最小总成本）: {model.objval:.2f}\n")
                f.write(f"新购工具总数: {total_purchase}\n")
                f.write(f"慢修工具总数: {total_slow_repair}\n") 
                f.write(f"快修工具总数: {total_fast_repair}\n")
                f.write(f"新购总成本: {total_purchase * a:.2f}\n")
                f.write(f"慢修总成本: {total_slow_repair * b:.2f}\n")
                f.write(f"快修总成本: {total_fast_repair * c:.2f}\n")
            
            print(f"\n结果已保存到 result.txt")
            
            return model.objval
            
        else:
            print(f"求解失败。状态码: {model.status}")
            status_map = {
                COPT.INFEASIBLE: "模型无可行解",
                COPT.UNBOUNDED: "目标函数无界", 
                COPT.TIMEOUT: "求解超时",
                COPT.INTERRUPTED: "用户中断"
            }
            print(f"状态描述: {status_map.get(model.status, '未知状态')}")
            return None
            
    except cp.CoptError as e:
        print(f"COPT错误: {e.retcode} - {e.message}")
        return None
    except Exception as e:
        print(f"程序执行出错: {e}")
        return None
    finally:
        # 清理资源
        if 'env' in locals() and env is not None:
            env.close()


if __name__ == "__main__":
    solve_corrected_tool_optimization()