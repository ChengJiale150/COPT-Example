"""
晚餐食材选择优化问题 - 混合整数线性规划(MILP)
目标：最大化总蛋白质摄入量
"""

import coptpy as cp
from coptpy import COPT

try:
    # 1. 创建COPT求解环境
    env = cp.Envr()
    model = env.createModel("meal_planning_milp")

    # 2. 定义问题数据
    
    # 蛋白质主食数据 (索引: 鸡肉=0, 三文鱼=1, 豆腐=2)
    proteins = ["鸡肉", "三文鱼", "豆腐"]
    protein_nutrition = [23, 20, 8]  # 每100g蛋白质含量(g)
    protein_costs = [3.00, 5.00, 1.50]  # 每100g价格($)
    
    # 蔬菜数据 (索引: 西兰花=0, 胡萝卜=1, 菠菜=2, 甜椒=3, 蘑菇=4)
    vegetables = ["西兰花", "胡萝卜", "菠菜", "甜椒", "蘑菇"]
    vegetable_nutrition = [2.8, 0.9, 2.9, 1.0, 3.1]  # 每包(100g)蛋白质含量(g)
    vegetable_costs = [1.20, 0.80, 1.50, 1.00, 2.00]  # 每包价格($)
    vegetable_weights = [100] * 5  # 每包重量(g) - 都是100g
    
    # 全局参数
    max_budget = 20  # 最大预算($)
    max_weight = 800  # 最大重量(g)
    min_vegetable_types = 3  # 最少蔬菜种类数
    M = 8  # 大M约束中的M值

    # 3. 添加决策变量
    
    # x_p: 购买蛋白质主食p的份数(每份100g) - 连续非负变量
    x = model.addVars(len(proteins), lb=0.0, vtype=COPT.CONTINUOUS, nameprefix="x_protein")
    
    # y_v: 购买蔬菜v的包装数 - 整数非负变量
    y = model.addVars(len(vegetables), lb=0.0, vtype=COPT.INTEGER, nameprefix="y_vegetable")
    
    # z_v: 是否购买蔬菜v - 二元变量
    z = model.addVars(len(vegetables), vtype=COPT.BINARY, nameprefix="z_choice")

    # 4. 添加约束条件
    
    # 约束1: 预算约束
    # ∑cost_p × x_p + ∑cost_v × y_v ≤ max_budget
    budget_constraint = cp.quicksum(protein_costs[p] * x[p] for p in range(len(proteins))) + \
                       cp.quicksum(vegetable_costs[v] * y[v] for v in range(len(vegetables)))
    model.addConstr(budget_constraint <= max_budget, name="budget_constraint")
    
    # 约束2: 重量约束
    # ∑100 × x_p + ∑100 × y_v ≤ max_weight
    weight_constraint = cp.quicksum(100 * x[p] for p in range(len(proteins))) + \
                       cp.quicksum(vegetable_weights[v] * y[v] for v in range(len(vegetables)))
    model.addConstr(weight_constraint <= max_weight, name="weight_constraint")
    
    # 约束3: 蔬菜种类数量约束
    # ∑z_v ≥ min_vegetable_types
    model.addConstr(cp.quicksum(z[v] for v in range(len(vegetables))) >= min_vegetable_types, 
                   name="min_vegetable_types")
    
    # 约束4: 变量关联约束
    # y_v ≤ M × z_v 和 y_v ≥ z_v
    for v in range(len(vegetables)):
        # 如果z_v=0，则y_v必须为0；如果z_v=1，则y_v可以在[0,M]范围内
        model.addConstr(y[v] <= M * z[v], name=f"logic_upper_{v}")
        # 如果z_v=1，则y_v至少为1；如果z_v=0，则y_v为0
        model.addConstr(y[v] >= z[v], name=f"logic_lower_{v}")

    # 5. 设置目标函数
    # 最大化总蛋白质摄入量: max(∑prot_p × x_p + ∑prot_v × y_v)
    total_protein = cp.quicksum(protein_nutrition[p] * x[p] for p in range(len(proteins))) + \
                   cp.quicksum(vegetable_nutrition[v] * y[v] for v in range(len(vegetables)))
    
    model.setObjective(total_protein, sense=COPT.MAXIMIZE)

    # 6. 求解模型
    print("正在求解混合整数线性规划问题...")
    model.solve()

    # 7. 分析求解结果
    if model.status == COPT.OPTIMAL:
        print("\n" + "="*60)
        print("         晚餐食材选择优化 - 求解结果")
        print("="*60)
        print(f"模型状态: 最优解")
        print(f"最大总蛋白质摄入量: {model.objval:.2f} 克")
        
        # 计算总成本和总重量
        total_cost = sum(protein_costs[p] * x[p].x for p in range(len(proteins))) + \
                    sum(vegetable_costs[v] * y[v].x for v in range(len(vegetables)))
        total_weight_used = sum(100 * x[p].x for p in range(len(proteins))) + \
                           sum(vegetable_weights[v] * y[v].x for v in range(len(vegetables)))
        
        print(f"总成本: ${total_cost:.2f} / ${max_budget} (使用率: {total_cost/max_budget:.1%})")
        print(f"总重量: {total_weight_used:.1f}g / {max_weight}g (使用率: {total_weight_used/max_weight:.1%})")
        
        print("\n" + "-"*40)
        print("蛋白质主食选择:")
        print("-"*40)
        for p in range(len(proteins)):
            if x[p].x > 1e-6:  # 避免显示极小的数值
                amount_grams = x[p].x * 100
                protein_amount = protein_nutrition[p] * x[p].x
                cost = protein_costs[p] * x[p].x
                print(f"  {proteins[p]}: {amount_grams:.1f}g (蛋白质: {protein_amount:.1f}g, 成本: ${cost:.2f})")
        
        print("\n" + "-"*40)
        print("蔬菜选择:")
        print("-"*40)
        selected_vegetables = 0
        for v in range(len(vegetables)):
            if y[v].x > 0.5:  # 整数变量
                selected_vegetables += 1
                packages = int(y[v].x)
                total_grams = packages * 100
                protein_amount = vegetable_nutrition[v] * packages
                cost = vegetable_costs[v] * packages
                print(f"  {vegetables[v]}: {packages}包 ({total_grams}g, 蛋白质: {protein_amount:.1f}g, 成本: ${cost:.2f})")
        
        print(f"\n选择的蔬菜种类数: {selected_vegetables} (要求至少: {min_vegetable_types})")
        
        print("\n" + "-"*40)
        print("营养成分分析:")
        print("-"*40)
        protein_from_main = sum(protein_nutrition[p] * x[p].x for p in range(len(proteins)))
        protein_from_veg = sum(vegetable_nutrition[v] * y[v].x for v in range(len(vegetables)))
        print(f"  来自蛋白质主食: {protein_from_main:.1f}g ({protein_from_main/model.objval:.1%})")
        print(f"  来自蔬菜: {protein_from_veg:.1f}g ({protein_from_veg/model.objval:.1%})")
        
        print("\n" + "-"*40)
        print("MIP求解统计信息:")
        print("-"*40)
        print(f"  最优界: {model.getAttr(COPT.Attr.BestBnd):.4f}")
        print(f"  最优间隙: {model.getAttr(COPT.Attr.BestGap)*100:.4f}%")
        print(f"  搜索节点数: {model.getAttr(COPT.Attr.NodeCnt)}")
        
        # 将结果写入result.txt文件
        with open("result.txt", "w", encoding="utf-8") as f:
            f.write("晚餐食材选择优化 - 求解结果\n")
            f.write("="*60 + "\n")
            f.write(f"最优目标函数值（最大总蛋白质摄入量）: {model.objval:.2f} 克\n")
            f.write(f"总成本: ${total_cost:.2f}\n")
            f.write(f"总重量: {total_weight_used:.1f}g\n\n")
            
            f.write("蛋白质主食选择:\n")
            for p in range(len(proteins)):
                if x[p].x > 1e-6:
                    amount_grams = x[p].x * 100
                    protein_amount = protein_nutrition[p] * x[p].x
                    cost = protein_costs[p] * x[p].x
                    f.write(f"  {proteins[p]}: {amount_grams:.1f}g (蛋白质: {protein_amount:.1f}g, 成本: ${cost:.2f})\n")
            
            f.write("\n蔬菜选择:\n")
            for v in range(len(vegetables)):
                if y[v].x > 0.5:
                    packages = int(y[v].x)
                    total_grams = packages * 100
                    protein_amount = vegetable_nutrition[v] * packages
                    cost = vegetable_costs[v] * packages
                    f.write(f"  {vegetables[v]}: {packages}包 ({total_grams}g, 蛋白质: {protein_amount:.1f}g, 成本: ${cost:.2f})\n")
        
        print(f"\n结果已保存到 result.txt 文件")
        
    else:
        print(f"\n模型未找到最优解。状态码: {model.status}")
        status_map = {
            COPT.INFEASIBLE: "模型无可行解",
            COPT.UNBOUNDED: "目标函数无界",
            COPT.TIMEOUT: "求解超时",
            COPT.INTERRUPTED: "用户中断"
        }
        print(f"状态描述: {status_map.get(model.status, '未知状态')}")
        
        # 即使没有最优解也写入result.txt
        with open("result.txt", "w", encoding="utf-8") as f:
            f.write("晚餐食材选择优化 - 求解失败\n")
            f.write(f"模型状态: {status_map.get(model.status, '未知状态')}\n")

    # 8. 将模型保存到文件
    model.write("meal_planning.lp")
    model.write("meal_planning.mps")
    if model.status == COPT.OPTIMAL:
        model.write("meal_planning.sol")

except cp.CoptError as e:
    print(f"COPT Error: {e.retcode} - {e.message}")
    with open("result.txt", "w", encoding="utf-8") as f:
        f.write(f"COPT错误: {e.retcode} - {e.message}\n")
except Exception as e:
    print(f"程序运行出错: {e}")
    with open("result.txt", "w", encoding="utf-8") as f:
        f.write(f"程序运行出错: {e}\n")
finally:
    # 确保在程序结束时关闭COPT环境
    if 'env' in locals() and env is not None:
        env.close()