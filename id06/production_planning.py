import coptpy as cp
from coptpy import COPT
import numpy as np

try:
    # 1. 数据定义
    # 产品集合 P = {1, 2, 3} 对应产品 I, II, III
    products = [1, 2, 3]
    # 时间周期集合 T = {1, 2, 3, 4} 对应四个季度
    periods = [1, 2, 3, 4]
    
    # 需求量数据 D_{it}
    demand = {
        (1, 1): 1500, (1, 2): 1000, (1, 3): 2000, (1, 4): 1200,  # 产品I
        (2, 1): 1500, (2, 2): 1500, (2, 3): 1200, (2, 4): 1500,  # 产品II
        (3, 1): 1000, (3, 2): 2000, (3, 3): 1500, (3, 4): 2500   # 产品III
    }
    
    # 生产工时参数 h_i (小时/件)
    production_hours = {1: 2, 2: 4, 3: 3}  # 产品I: 2小时/件，产品II: 4小时/件，产品III: 3小时/件
    
    # 每季度最大可用生产工时
    max_hours = 15000
    
    # 库存成本 C^I_i (元/件/季度) - 所有产品都是5元/件/季度
    inventory_cost = {1: 5, 2: 5, 3: 5}
    
    # 延期交付罚金 C^B_i (元/件/季度)
    backorder_cost = {1: 20, 2: 20, 3: 10}  # 产品I和II: 20元，产品III: 10元
    
    # 期末库存要求
    final_inventory_requirement = 150
    
    # 初始库存和积压订单 (都为0)
    initial_inventory = {1: 0, 2: 0, 3: 0}
    initial_backorder = {1: 0, 2: 0, 3: 0}
    
    # 2. 创建COPT环境和模型
    env = cp.Envr()
    model = env.createModel("production_planning")
    
    # 3. 添加决策变量
    # P_{it}: 在季度t生产的产品i的数量
    P = model.addVars(products, periods, lb=0.0, nameprefix="produce")
    
    # I_{it}: 在季度t结束时产品i的库存数量
    I = model.addVars(products, periods, lb=0.0, nameprefix="inventory")
    
    # B_{it}: 在季度t结束时产品i的积压订单数量
    B = model.addVars(products, periods, lb=0.0, nameprefix="backorder")
    
    # 4. 设置目标函数：最小化总成本
    # 总成本 = 库存成本 + 延期交付罚金
    total_inventory_cost = cp.quicksum(inventory_cost[i] * I[i, t] for i in products for t in periods)
    total_backorder_cost = cp.quicksum(backorder_cost[i] * B[i, t] for i in products for t in periods)
    
    model.setObjective(total_inventory_cost + total_backorder_cost, sense=COPT.MINIMIZE)
    
    # 5. 添加约束条件
    
    # 约束1: 库存平衡约束
    # I_{it} - B_{it} = (I_{i,t-1} - B_{i,t-1}) + P_{it} - D_{it}
    for i in products:
        for t in periods:
            if t == 1:
                # 第一季度使用初始库存和初始积压订单
                model.addConstr(
                    I[i, t] - B[i, t] == 
                    (initial_inventory[i] - initial_backorder[i]) + P[i, t] - demand[i, t],
                    name=f"inventory_balance_{i}_{t}"
                )
            else:
                model.addConstr(
                    I[i, t] - B[i, t] == 
                    (I[i, t-1] - B[i, t-1]) + P[i, t] - demand[i, t],
                    name=f"inventory_balance_{i}_{t}"
                )
    
    # 约束2: 生产工时约束
    # sum(h_i * P_{it}) <= H_max for all t
    for t in periods:
        model.addConstr(
            cp.quicksum(production_hours[i] * P[i, t] for i in products) <= max_hours,
            name=f"production_hours_{t}"
        )
    
    # 约束3: 特殊生产限制 - 产品I在第二季度不能生产
    # P_{1,2} = 0
    model.addConstr(P[1, 2] == 0, name="product_I_restriction_Q2")
    
    # 约束4: 期末库存要求
    # I_{i,4} >= 150 for all i
    for i in products:
        model.addConstr(
            I[i, 4] >= final_inventory_requirement,
            name=f"final_inventory_requirement_{i}"
        )
    
    # 约束5: 期末积压清零约束
    # B_{i,4} = 0 for all i
    for i in products:
        model.addConstr(
            B[i, 4] == 0,
            name=f"final_backorder_elimination_{i}"
        )
    
    # 约束6: 非负约束已经在变量定义时通过lb=0.0设置
    
    # 6. 求解模型
    print("开始求解生产规划问题...")
    model.solve()
    
    # 7. 分析和输出结果
    if model.status == COPT.OPTIMAL:
        print("\n" + "="*60)
        print("求解成功！找到最优解")
        print("="*60)
        print(f"最小总成本: {model.objval:.2f} 元")
        
        # 分析成本构成
        total_inv_cost_value = sum(inventory_cost[i] * I[i, t].x for i in products for t in periods)
        total_back_cost_value = sum(backorder_cost[i] * B[i, t].x for i in products for t in periods)
        
        print(f"其中:")
        print(f"  库存成本: {total_inv_cost_value:.2f} 元")
        print(f"  延期交付罚金: {total_back_cost_value:.2f} 元")
        
        print("\n" + "-"*60)
        print("生产计划 (P_{it})")
        print("-"*60)
        print("季度\\产品    产品I      产品II     产品III")
        print("-"*60)
        for t in periods:
            print(f"季度{t}      {P[1,t].x:8.2f}   {P[2,t].x:8.2f}   {P[3,t].x:8.2f}")
        
        print("\n" + "-"*60)
        print("期末库存 (I_{it})")
        print("-"*60)
        print("季度\\产品    产品I      产品II     产品III")
        print("-"*60)
        for t in periods:
            print(f"季度{t}      {I[1,t].x:8.2f}   {I[2,t].x:8.2f}   {I[3,t].x:8.2f}")
        
        print("\n" + "-"*60)
        print("期末积压订单 (B_{it})")
        print("-"*60)
        print("季度\\产品    产品I      产品II     产品III")
        print("-"*60)
        for t in periods:
            print(f"季度{t}      {B[1,t].x:8.2f}   {B[2,t].x:8.2f}   {B[3,t].x:8.2f}")
        
        print("\n" + "-"*60)
        print("每季度工时使用情况")
        print("-"*60)
        for t in periods:
            used_hours = sum(production_hours[i] * P[i, t].x for i in products)
            print(f"季度{t}: {used_hours:.2f} / {max_hours} 小时 (使用率: {used_hours/max_hours*100:.1f}%)")
        
        # 8. 保存结果到文件
        with open("/Users/jiale.cheng/Documents/mcp/test/output/detailed_results.txt", "w", encoding="utf-8") as f:
            f.write("生产规划问题求解结果\n")
            f.write("="*60 + "\n")
            f.write(f"最小总成本: {model.objval:.2f} 元\n")
            f.write(f"库存成本: {total_inv_cost_value:.2f} 元\n")
            f.write(f"延期交付罚金: {total_back_cost_value:.2f} 元\n\n")
            
            f.write("生产计划 (P_{it})\n")
            f.write("-"*60 + "\n")
            f.write("季度\\产品    产品I      产品II     产品III\n")
            f.write("-"*60 + "\n")
            for t in periods:
                f.write(f"季度{t}      {P[1,t].x:8.2f}   {P[2,t].x:8.2f}   {P[3,t].x:8.2f}\n")
            
            f.write("\n期末库存 (I_{it})\n")
            f.write("-"*60 + "\n")
            f.write("季度\\产品    产品I      产品II     产品III\n")
            f.write("-"*60 + "\n")
            for t in periods:
                f.write(f"季度{t}      {I[1,t].x:8.2f}   {I[2,t].x:8.2f}   {I[3,t].x:8.2f}\n")
            
            f.write("\n期末积压订单 (B_{it})\n")
            f.write("-"*60 + "\n")
            f.write("季度\\产品    产品I      产品II     产品III\n")
            f.write("-"*60 + "\n")
            for t in periods:
                f.write(f"季度{t}      {B[1,t].x:8.2f}   {B[2,t].x:8.2f}   {B[3,t].x:8.2f}\n")
            
            f.write("\n每季度工时使用情况\n")
            f.write("-"*60 + "\n")
            for t in periods:
                used_hours = sum(production_hours[i] * P[i, t].x for i in products)
                f.write(f"季度{t}: {used_hours:.2f} / {max_hours} 小时 (使用率: {used_hours/max_hours*100:.1f}%)\n")
        
        # 保存目标函数值到result.txt
        with open("/Users/jiale.cheng/Documents/mcp/test/result.txt", "w", encoding="utf-8") as f:
            f.write(f"最优目标函数值: {model.objval:.2f}")
        
        print(f"\n详细结果已保存到: /Users/jiale.cheng/Documents/mcp/test/output/detailed_results.txt")
        print(f"目标函数值已保存到: /Users/jiale.cheng/Documents/mcp/test/result.txt")
        
    else:
        print(f"\n求解失败！模型状态码: {model.status}")
        error_status = {
            COPT.INFEASIBLE: "模型无可行解",
            COPT.UNBOUNDED: "模型无界",
            COPT.INF_OR_UNB: "模型无可行解或无界",
            COPT.NUMERICAL: "数值问题",
            COPT.TIMEOUT: "求解超时"
        }
        if model.status in error_status:
            print(f"错误原因: {error_status[model.status]}")

except cp.CoptError as e:
    print(f"COPT错误: {e.retcode} - {e.message}")
except Exception as e:
    print(f"发生意外错误: {e}")
finally:
    # 关闭COPT环境
    if 'env' in locals() and env is not None:
        env.close()