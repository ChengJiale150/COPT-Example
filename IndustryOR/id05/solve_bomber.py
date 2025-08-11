"""
Mary的晚餐规划问题求解器
使用COPT求解器解决混合整数线性规划(MILP)问题

问题描述：
- 目标：在满足约束条件下最大化膳食纤维摄入量
- 约束：预算≤$15，总重量=600克，选择1种蛋白质，至少2种蔬菜
"""

import coptpy as cp
from coptpy import COPT


def solve_mary_dinner_planning():
    """求解Mary的晚餐规划问题"""
    
    try:
        # 1. 创建COPT求解环境
        env = cp.Envr()
        
        # 2. 创建优化模型
        model = env.createModel("mary_dinner_planning")
        
        # 3. 定义问题数据
        # 食物集合
        proteins = ['salmon', 'beef', 'pork']
        vegetables = ['okra', 'carrots', 'celery', 'cabbage']
        all_foods = proteins + vegetables
        
        # 价格 (美元/100克)
        prices = {
            'salmon': 4.0,
            'beef': 3.6, 
            'pork': 1.8,
            'okra': 2.6,
            'carrots': 1.2,
            'celery': 1.6,
            'cabbage': 2.3
        }
        
        # 纤维含量 (克/100克) - 只有蔬菜含有纤维
        fiber_content = {
            'salmon': 0,
            'beef': 0,
            'pork': 0,
            'okra': 3.2,
            'carrots': 2.7,
            'celery': 1.6,
            'cabbage': 2.0
        }
        
        # 约束参数
        budget_limit = 15  # 美元
        total_weight = 600  # 克
        weight_units = total_weight / 100  # 转换为100克单位，即6个单位
        
        # Big-M参数和epsilon参数
        M = weight_units  # 6个单位
        epsilon = 0.001  # 最小购买量
        
        # 4. 添加决策变量
        # x[i]: 购买食物i的数量（单位：100克）
        x = model.addVars(all_foods, lb=0.0, nameprefix="x")
        
        # y[i]: 是否选择食物i（二元变量）
        y = model.addVars(all_foods, vtype=COPT.BINARY, nameprefix="y")
        
        # 5. 添加约束条件
        
        # 约束1: 总预算约束
        model.addConstr(
            cp.quicksum(prices[i] * x[i] for i in all_foods) <= budget_limit,
            name="budget_constraint"
        )
        
        # 约束2: 总重量约束 (恰好等于600克，即6个100克单位)
        model.addConstr(
            cp.quicksum(x[i] for i in all_foods) == weight_units,
            name="total_weight_constraint"
        )
        
        # 约束3: 蛋白质选择约束 (必须选择且仅选择一种)
        model.addConstr(
            cp.quicksum(y[i] for i in proteins) == 1,
            name="protein_selection_constraint"
        )
        
        # 约束4: 蔬菜选择约束 (至少选择两种)
        model.addConstr(
            cp.quicksum(y[i] for i in vegetables) >= 2,
            name="vegetable_selection_constraint"
        )
        
        # 约束5: 采购量与选择决策的联动约束
        # 5a: x[i] <= M * y[i] (如果不选择食物i，则不能购买)
        for i in all_foods:
            model.addConstr(
                x[i] <= M * y[i],
                name=f"linking_upper_{i}"
            )
        
        # 5b: x[i] >= epsilon * y[i] (如果选择食物i，则必须购买至少epsilon数量)
        for i in all_foods:
            model.addConstr(
                x[i] >= epsilon * y[i],
                name=f"linking_lower_{i}"
            )
        
        # 6. 设置目标函数：最大化总膳食纤维摄入量
        model.setObjective(
            cp.quicksum(fiber_content[i] * x[i] for i in vegetables),
            sense=COPT.MAXIMIZE
        )
        
        # 7. 求解模型
        print("开始求解Mary的晚餐规划问题...")
        model.solve()
        
        # 8. 分析求解结果
        if model.status == COPT.OPTIMAL:
            print("\n" + "="*50)
            print("求解成功！找到最优解")
            print("="*50)
            
            # 目标函数值（最大膳食纤维摄入量）
            max_fiber = model.objval
            print(f"最大膳食纤维摄入量: {max_fiber:.4f} 克")
            
            print("\n【食物选择方案】")
            total_cost = 0
            total_weight_check = 0
            actual_fiber = 0
            
            print("选择的蛋白质:")
            for protein in proteins:
                if y[protein].x > 0.5:
                    amount_100g = x[protein].x
                    amount_grams = amount_100g * 100
                    cost = prices[protein] * amount_100g
                    print(f"  - {protein}: {amount_grams:.1f}克 (${cost:.2f})")
                    total_cost += cost
                    total_weight_check += amount_grams
            
            print("\n选择的蔬菜:")
            for vegetable in vegetables:
                if y[vegetable].x > 0.5:
                    amount_100g = x[vegetable].x
                    amount_grams = amount_100g * 100
                    cost = prices[vegetable] * amount_100g
                    fiber = fiber_content[vegetable] * amount_100g
                    print(f"  - {vegetable}: {amount_grams:.1f}克 (${cost:.2f}, {fiber:.2f}g纤维)")
                    total_cost += cost
                    total_weight_check += amount_grams
                    actual_fiber += fiber
            
            print(f"\n【约束验证】")
            print(f"总花费: ${total_cost:.2f} / ${budget_limit} (预算约束)")
            print(f"总重量: {total_weight_check:.1f}克 / {total_weight}克 (重量约束)")
            print(f"实际纤维: {actual_fiber:.4f}克 (与目标函数值一致)")
            
            # 选择统计
            selected_proteins = sum(1 for p in proteins if y[p].x > 0.5)
            selected_vegetables = sum(1 for v in vegetables if y[v].x > 0.5)
            print(f"选择的蛋白质数量: {selected_proteins} (应为1)")
            print(f"选择的蔬菜数量: {selected_vegetables} (应≥2)")
            
            print(f"\n【求解统计】")
            print(f"最优界: {model.getAttr(COPT.Attr.BestBnd):.4f}")
            print(f"最优间隙: {model.getAttr(COPT.Attr.BestGap)*100:.4f}%")
            print(f"搜索节点数: {model.getAttr(COPT.Attr.NodeCnt)}")
            
            # 将结果写入文件
            with open('/Users/jiale.cheng/Documents/mcp/test/result.txt', 'w', encoding='utf-8') as f:
                f.write(f"Mary晚餐规划问题求解结果\n")
                f.write(f"========================\n\n")
                f.write(f"最大膳食纤维摄入量: {max_fiber:.4f} 克\n\n")
                
                f.write(f"选择的蛋白质:\n")
                for protein in proteins:
                    if y[protein].x > 0.5:
                        amount_100g = x[protein].x
                        amount_grams = amount_100g * 100
                        cost = prices[protein] * amount_100g
                        f.write(f"  - {protein}: {amount_grams:.1f}克 (${cost:.2f})\n")
                
                f.write(f"\n选择的蔬菜:\n")
                for vegetable in vegetables:
                    if y[vegetable].x > 0.5:
                        amount_100g = x[vegetable].x
                        amount_grams = amount_100g * 100
                        cost = prices[vegetable] * amount_100g
                        fiber = fiber_content[vegetable] * amount_100g
                        f.write(f"  - {vegetable}: {amount_grams:.1f}克 (${cost:.2f}, {fiber:.2f}g纤维)\n")
                
                f.write(f"\n约束验证:\n")
                f.write(f"总花费: ${total_cost:.2f} / ${budget_limit}\n")
                f.write(f"总重量: {total_weight_check:.1f}克 / {total_weight}克\n")
                f.write(f"蛋白质选择数量: {selected_proteins}\n")
                f.write(f"蔬菜选择数量: {selected_vegetables}\n")
            
            print(f"\n结果已保存到 result.txt")
            
            return max_fiber
            
        else:
            error_msg = f"模型未找到最优解。状态码: {model.status}"
            print(error_msg)
            
            # 状态码映射
            status_map = {
                COPT.INFEASIBLE: "模型无可行解",
                COPT.UNBOUNDED: "目标函数无界", 
                COPT.TIMEOUT: "求解超时",
                COPT.INTERRUPTED: "用户中断"
            }
            status_desc = status_map.get(model.status, "未知状态")
            print(f"状态描述: {status_desc}")
            
            # 将错误信息写入文件
            with open('/Users/jiale.cheng/Documents/mcp/test/result.txt', 'w', encoding='utf-8') as f:
                f.write(f"Mary晚餐规划问题求解失败\n")
                f.write(f"========================\n\n")
                f.write(f"错误: {error_msg}\n")
                f.write(f"状态描述: {status_desc}\n")
            
            return None
            
    except cp.CoptError as e:
        error_msg = f"COPT Error: {e.retcode} - {e.message}"
        print(error_msg)
        
        with open('/Users/jiale.cheng/Documents/mcp/test/result.txt', 'w', encoding='utf-8') as f:
            f.write(f"Mary晚餐规划问题求解错误\n")
            f.write(f"========================\n\n")
            f.write(f"COPT错误: {error_msg}\n")
        
        return None
        
    except Exception as e:
        error_msg = f"意外错误: {e}"
        print(error_msg)
        
        with open('/Users/jiale.cheng/Documents/mcp/test/result.txt', 'w', encoding='utf-8') as f:
            f.write(f"Mary晚餐规划问题求解错误\n")
            f.write(f"========================\n\n")
            f.write(f"意外错误: {error_msg}\n")
        
        return None
        
    finally:
        # 确保释放COPT环境资源
        if 'env' in locals() and env is not None:
            env.close()


if __name__ == "__main__":
    print("Mary的晚餐规划问题求解器")
    print("使用COPT求解混合整数线性规划(MILP)问题\n")
    
    result = solve_mary_dinner_planning()
    
    if result is not None:
        print(f"\n求解完成！最优目标函数值: {result:.4f} 克膳食纤维")
    else:
        print("\n求解失败，请检查问题设置或求解器配置")