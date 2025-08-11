#!/usr/bin/env python3
"""
农场土地分配优化问题 - 线性规划求解
使用COPT求解器求解最大化利润的农场作物种植面积分配问题

问题描述：
- 100英亩农场分配给4种作物：玉米(x1)、小麦(x2)、大豆(x3)、高粱(x4)
- 目标：最大化总利润 = 1500*x1 + 1200*x2 + 1800*x3 + 1600*x4
- 约束条件：
  1. 总面积约束：x1 + x2 + x3 + x4 ≤ 100
  2. 玉米-小麦约束：x1 ≥ 2*x2
  3. 大豆-高粱约束：x3 ≥ 0.5*x4
  4. 小麦-高粱约束：x2 = 3*x4
  5. 非负约束：x1, x2, x3, x4 ≥ 0
"""

import coptpy as cp
from coptpy import COPT

def solve_farm_allocation():
    """求解农场土地分配优化问题"""
    
    try:
        # 1. 创建COPT求解环境
        print("正在初始化COPT求解器...")
        env = cp.Envr()
        
        # 2. 创建优化模型
        model = env.createModel("farm_allocation")
        
        # 3. 定义问题参数
        # 作物利润 (美元/英亩)
        profits = {
            'corn': 1500,      # 玉米
            'wheat': 1200,     # 小麦  
            'soybeans': 1800,  # 大豆
            'sorghum': 1600    # 高粱
        }
        
        # 农场总面积 (英亩)
        total_area = 100
        
        print(f"农场总面积: {total_area} 英亩")
        print("作物利润:")
        for crop, profit in profits.items():
            print(f"  {crop}: ${profit}/英亩")
        
        # 4. 添加决策变量
        # x1: 玉米种植面积, x2: 小麦种植面积, x3: 大豆种植面积, x4: 高粱种植面积
        x1 = model.addVar(lb=0.0, name="corn_area")      # 玉米面积
        x2 = model.addVar(lb=0.0, name="wheat_area")     # 小麦面积  
        x3 = model.addVar(lb=0.0, name="soybeans_area")  # 大豆面积
        x4 = model.addVar(lb=0.0, name="sorghum_area")   # 高粱面积
        
        print("\n决策变量已定义:")
        print("  x1 = 玉米种植面积 (英亩)")
        print("  x2 = 小麦种植面积 (英亩)")
        print("  x3 = 大豆种植面积 (英亩)")
        print("  x4 = 高粱种植面积 (英亩)")
        
        # 5. 设置目标函数 - 最大化总利润
        objective = profits['corn'] * x1 + profits['wheat'] * x2 + profits['soybeans'] * x3 + profits['sorghum'] * x4
        model.setObjective(objective, sense=COPT.MAXIMIZE)
        
        print(f"\n目标函数: 最大化总利润")
        print(f"  Max Z = {profits['corn']}*x1 + {profits['wheat']}*x2 + {profits['soybeans']}*x3 + {profits['sorghum']}*x4")
        
        # 6. 添加约束条件
        print("\n添加约束条件:")
        
        # 约束1: 总面积约束
        c1 = model.addConstr(x1 + x2 + x3 + x4 <= total_area, name="total_area")
        print(f"  约束1 (总面积): x1 + x2 + x3 + x4 ≤ {total_area}")
        
        # 约束2: 玉米-小麦比例约束 (玉米面积 ≥ 2倍小麦面积)
        c2 = model.addConstr(x1 >= 2 * x2, name="corn_wheat_ratio")
        print("  约束2 (玉米-小麦): x1 ≥ 2*x2")
        
        # 约束3: 大豆-高粱比例约束 (大豆面积 ≥ 0.5倍高粱面积)
        c3 = model.addConstr(x3 >= 0.5 * x4, name="soybeans_sorghum_ratio")
        print("  约束3 (大豆-高粱): x3 ≥ 0.5*x4")
        
        # 约束4: 小麦-高粱比例约束 (小麦面积 = 3倍高粱面积)
        c4 = model.addConstr(x2 == 3 * x4, name="wheat_sorghum_ratio")
        print("  约束4 (小麦-高粱): x2 = 3*x4")
        
        # 约束5: 非负约束 (已在变量定义时通过lb=0.0设置)
        print("  约束5 (非负性): x1, x2, x3, x4 ≥ 0 (已在变量定义时设置)")
        
        # 7. 设置求解参数
        model.setParam(COPT.Param.TimeLimit, 60.0)  # 设置60秒时间限制
        
        # 8. 求解模型
        print("\n开始求解...")
        model.solve()
        
        # 9. 分析求解结果
        if model.status == COPT.OPTIMAL:
            print("\n" + "="*60)
            print("求解成功! 找到最优解")
            print("="*60)
            
            # 输出目标函数最优值
            optimal_profit = model.objval
            print(f"\n最大总利润: ${optimal_profit:,.2f}")
            
            # 输出变量最优解
            print(f"\n最优种植面积分配:")
            print(f"  玉米 (x1): {x1.x:.4f} 英亩")
            print(f"  小麦 (x2): {x2.x:.4f} 英亩") 
            print(f"  大豆 (x3): {x3.x:.4f} 英亩")
            print(f"  高粱 (x4): {x4.x:.4f} 英亩")
            
            # 验证总面积
            total_used = x1.x + x2.x + x3.x + x4.x
            print(f"\n总使用面积: {total_used:.4f} 英亩")
            print(f"剩余面积: {total_area - total_used:.4f} 英亩")
            
            # 验证约束条件
            print(f"\n约束验证:")
            print(f"  约束1 (总面积): {x1.x + x2.x + x3.x + x4.x:.4f} ≤ {total_area} ✓")
            print(f"  约束2 (玉米≥2倍小麦): {x1.x:.4f} ≥ {2*x2.x:.4f} ✓")
            print(f"  约束3 (大豆≥0.5倍高粱): {x3.x:.4f} ≥ {0.5*x4.x:.4f} ✓")
            print(f"  约束4 (小麦=3倍高粱): {x2.x:.4f} = {3*x4.x:.4f} ✓")
            
            # 计算各作物利润贡献
            print(f"\n各作物利润贡献:")
            corn_profit = profits['corn'] * x1.x
            wheat_profit = profits['wheat'] * x2.x
            soybeans_profit = profits['soybeans'] * x3.x
            sorghum_profit = profits['sorghum'] * x4.x
            
            print(f"  玉米: ${corn_profit:,.2f} ({corn_profit/optimal_profit*100:.1f}%)")
            print(f"  小麦: ${wheat_profit:,.2f} ({wheat_profit/optimal_profit*100:.1f}%)")
            print(f"  大豆: ${soybeans_profit:,.2f} ({soybeans_profit/optimal_profit*100:.1f}%)")
            print(f"  高粱: ${sorghum_profit:,.2f} ({sorghum_profit/optimal_profit*100:.1f}%)")
            
            # 输出约束松弛量和对偶值
            print(f"\n约束分析:")
            for constr in model.getConstrs():
                print(f"  {constr.name}: 松弛量={constr.slack:.4f}, 对偶值=${constr.pi:.2f}")
            
            # 将结果写入文件
            with open('result.txt', 'w', encoding='utf-8') as f:
                f.write("农场土地分配优化问题求解结果\n")
                f.write("=" * 40 + "\n\n")
                f.write(f"最大总利润: ${optimal_profit:,.2f}\n\n")
                f.write("最优种植面积分配:\n")
                f.write(f"  玉米: {x1.x:.4f} 英亩\n")
                f.write(f"  小麦: {x2.x:.4f} 英亩\n")
                f.write(f"  大豆: {x3.x:.4f} 英亩\n")
                f.write(f"  高粱: {x4.x:.4f} 英亩\n")
                f.write(f"\n总使用面积: {total_used:.4f} 英亩\n")
                f.write(f"剩余面积: {total_area - total_used:.4f} 英亩\n")
                
            print(f"\n结果已保存到 result.txt 文件")
            
            # 保存模型文件
            model.write("farm_allocation.lp")
            model.write("farm_allocation.sol")
            print("模型文件已保存: farm_allocation.lp, farm_allocation.sol")
            
            return optimal_profit
            
        else:
            print(f"\n求解失败! 模型状态码: {model.status}")
            status_map = {
                COPT.INFEASIBLE: "无可行解",
                COPT.UNBOUNDED: "目标函数无界",
                COPT.INFORPINFEAS: "无可行解或无界",
                COPT.TIMELIMIT: "时间限制",
                COPT.NODELIMIT: "节点限制",
                COPT.INTERRUPTED: "用户中断"
            }
            status_desc = status_map.get(model.status, "未知状态")
            print(f"状态描述: {status_desc}")
            return None
            
    except cp.CoptError as e:
        print(f"COPT错误: {e.retcode} - {e.message}")
        return None
    except Exception as e:
        print(f"发生意外错误: {e}")
        return None
    finally:
        # 确保关闭COPT环境
        if 'env' in locals() and env is not None:
            env.close()

if __name__ == "__main__":
    print("农场土地分配优化问题求解器")
    print("使用COPT线性规划求解器")
    print("=" * 60)
    
    optimal_profit = solve_farm_allocation()
    
    if optimal_profit is not None:
        print("\n" + "="*60)
        print("求解完成!")
        print(f"最优总利润: ${optimal_profit:,.2f}")
        print("="*60)
    else:
        print("\n求解失败，请检查问题设置或求解器配置。")