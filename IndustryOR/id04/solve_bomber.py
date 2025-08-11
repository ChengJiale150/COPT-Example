#!/usr/bin/env python3
"""
农场动物饲养优化问题求解器
使用COPT求解整数线性规划问题

问题描述：
- 决策变量：牛(x1)、羊(x2)、鸡(x3)的饲养数量
- 目标函数：最大化总利润 = 400*x1 + 120*x2 + 3*x3
- 约束条件：
  1. 粪便处理：10*x1 + 5*x2 + 3*x3 <= 800
  2. 动物总数：x1 + x2 + x3 <= 100
  3. 最小牛数：x1 >= 10
  4. 最小羊数：x2 >= 20
  5. 最大鸡数：x3 <= 50
  6. 变量类型：x1, x2, x3 为非负整数
"""

import coptpy as cp
from coptpy import COPT

def solve_farm_optimization():
    """求解农场动物饲养优化问题"""
    
    try:
        # 1. 创建COPT求解环境
        env = cp.Envr()
        
        # 2. 创建优化模型
        model = env.createModel("farm_optimization")
        
        # 3. 定义问题数据
        # 利润系数（售价-成本）
        profits = [400, 120, 3]  # 牛、羊、鸡的单位利润
        
        # 粪便产量系数
        manure = [10, 5, 3]  # 牛、羊、鸡的每日粪便产量
        
        # 约束参数
        max_manure = 800      # 最大粪便处理量
        max_animals = 100     # 最大动物总数
        min_cows = 10         # 最小牛数
        min_sheep = 20        # 最小羊数
        max_chickens = 50     # 最大鸡数
        
        # 4. 添加决策变量
        # x[0] = 牛的数量, x[1] = 羊的数量, x[2] = 鸡的数量
        x = model.addVars(3, vtype=COPT.INTEGER, lb=0, nameprefix="x")
        
        # 5. 添加约束条件
        # 约束1: 粪便处理能力约束
        model.addConstr(
            cp.quicksum(manure[i] * x[i] for i in range(3)) <= max_manure,
            name="manure_constraint"
        )
        
        # 约束2: 动物总数约束
        model.addConstr(
            cp.quicksum(x[i] for i in range(3)) <= max_animals,
            name="total_animals_constraint"
        )
        
        # 约束3: 最小牛数约束
        model.addConstr(x[0] >= min_cows, name="min_cows_constraint")
        
        # 约束4: 最小羊数约束
        model.addConstr(x[1] >= min_sheep, name="min_sheep_constraint")
        
        # 约束5: 最大鸡数约束
        model.addConstr(x[2] <= max_chickens, name="max_chickens_constraint")
        
        # 6. 设置目标函数 - 最大化总利润
        model.setObjective(
            cp.quicksum(profits[i] * x[i] for i in range(3)),
            sense=COPT.MAXIMIZE
        )
        
        # 7. 求解模型
        print("开始求解农场优化问题...")
        model.solve()
        
        # 8. 分析求解结果
        if model.status == COPT.OPTIMAL:
            print("\n=== 求解成功：找到最优解 ===")
            
            # 获取最优解
            optimal_cows = int(round(x[0].x))
            optimal_sheep = int(round(x[1].x))
            optimal_chickens = int(round(x[2].x))
            optimal_profit = model.objval
            
            print(f"\n最优饲养方案：")
            print(f"  牛的数量: {optimal_cows}")
            print(f"  羊的数量: {optimal_sheep}")
            print(f"  鸡的数量: {optimal_chickens}")
            print(f"  最大总利润: ${optimal_profit:,.2f}")
            
            # 验证约束条件
            print(f"\n约束条件验证：")
            total_manure = manure[0]*optimal_cows + manure[1]*optimal_sheep + manure[2]*optimal_chickens
            total_animals = optimal_cows + optimal_sheep + optimal_chickens
            
            print(f"  粪便产量: {total_manure} / {max_manure} (约束: <= {max_manure})")
            print(f"  动物总数: {total_animals} / {max_animals} (约束: <= {max_animals})")
            print(f"  牛数量: {optimal_cows} (约束: >= {min_cows})")
            print(f"  羊数量: {optimal_sheep} (约束: >= {min_sheep})")
            print(f"  鸡数量: {optimal_chickens} (约束: <= {max_chickens})")
            
            # 计算利润构成
            print(f"\n利润构成：")
            cow_profit = profits[0] * optimal_cows
            sheep_profit = profits[1] * optimal_sheep
            chicken_profit = profits[2] * optimal_chickens
            print(f"  牛的利润: ${cow_profit:,.2f} ({optimal_cows} × ${profits[0]})")
            print(f"  羊的利润: ${sheep_profit:,.2f} ({optimal_sheep} × ${profits[1]})")
            print(f"  鸡的利润: ${chicken_profit:,.2f} ({optimal_chickens} × ${profits[2]})")
            print(f"  总利润: ${optimal_profit:,.2f}")
            
            # MIP求解统计信息
            print(f"\nMIP求解统计：")
            print(f"  最优界: ${model.getAttr(COPT.Attr.BestBnd):,.2f}")
            print(f"  最优间隙: {model.getAttr(COPT.Attr.BestGap)*100:.4f}%")
            print(f"  搜索节点数: {model.getAttr(COPT.Attr.NodeCnt)}")
            
            # 将结果写入文件
            with open("result.txt", "w", encoding="utf-8") as f:
                f.write("=== 农场动物饲养优化问题求解结果 ===\n\n")
                f.write(f"最优饲养方案：\n")
                f.write(f"  牛的数量: {optimal_cows}\n")
                f.write(f"  羊的数量: {optimal_sheep}\n")
                f.write(f"  鸡的数量: {optimal_chickens}\n")
                f.write(f"  最大总利润: ${optimal_profit:,.2f}\n\n")
                
                f.write(f"约束条件验证：\n")
                f.write(f"  粪便产量: {total_manure} / {max_manure} (满足约束)\n")
                f.write(f"  动物总数: {total_animals} / {max_animals} (满足约束)\n")
                f.write(f"  牛数量: {optimal_cows} >= {min_cows} (满足约束)\n")
                f.write(f"  羊数量: {optimal_sheep} >= {min_sheep} (满足约束)\n")
                f.write(f"  鸡数量: {optimal_chickens} <= {max_chickens} (满足约束)\n\n")
                
                f.write(f"利润构成：\n")
                f.write(f"  牛的利润: ${cow_profit:,.2f}\n")
                f.write(f"  羊的利润: ${sheep_profit:,.2f}\n")
                f.write(f"  鸡的利润: ${chicken_profit:,.2f}\n")
                f.write(f"  总利润: ${optimal_profit:,.2f}\n")
            
            print(f"\n结果已保存到 result.txt 文件")
            return optimal_profit
            
        else:
            print(f"\n求解失败！模型状态: {model.status}")
            
            # 状态码映射
            status_map = {
                COPT.INFEASIBLE: "模型无可行解",
                COPT.UNBOUNDED: "目标函数无界", 
                COPT.TIMEOUT: "求解超时",
                COPT.INTERRUPTED: "用户中断"
            }
            
            status_desc = status_map.get(model.status, "未知状态")
            print(f"状态描述: {status_desc}")
            
            with open("result.txt", "w", encoding="utf-8") as f:
                f.write("=== 农场动物饲养优化问题求解结果 ===\n\n")
                f.write(f"求解失败！\n")
                f.write(f"模型状态: {model.status}\n")
                f.write(f"状态描述: {status_desc}\n")
            
            return None
            
    except cp.CoptError as e:
        print(f"COPT错误: {e.retcode} - {e.message}")
        with open("result.txt", "w", encoding="utf-8") as f:
            f.write("=== 农场动物饲养优化问题求解结果 ===\n\n")
            f.write(f"COPT错误: {e.retcode} - {e.message}\n")
        return None
        
    except Exception as e:
        print(f"程序执行错误: {e}")
        with open("result.txt", "w", encoding="utf-8") as f:
            f.write("=== 农场动物饲养优化问题求解结果 ===\n\n")
            f.write(f"程序执行错误: {e}\n")
        return None
        
    finally:
        # 关闭COPT环境
        if 'env' in locals() and env is not None:
            env.close()

if __name__ == "__main__":
    print("农场动物饲养优化问题求解器")
    print("=" * 50)
    
    result = solve_farm_optimization()
    
    if result is not None:
        print(f"\n求解完成！最优目标函数值: ${result:,.2f}")
    else:
        print("\n求解失败！")