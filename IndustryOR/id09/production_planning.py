"""
玩具制造商生产规划优化问题 - COPT求解器实现

这是一个混合整数线性规划(MILP)问题，目标是在满足资源和逻辑约束的前提下，
最大化玩具生产的总利润。

问题涉及四种玩具：卡车(1)、飞机(2)、船(3)、火车(4)
资源约束：木材(890单位)、钢材(500单位)
逻辑约束：互斥、依存、数量比例关系
"""

import coptpy as cp
from coptpy import COPT
import os

def solve_toy_production_planning():
    """求解玩具制造商生产规划问题"""
    
    try:
        # 1. 创建COPT求解环境
        env = cp.Envr()
        
        # 2. 创建优化模型
        model = env.createModel("toy_production_planning")
        
        # 3. 定义问题数据
        # 玩具索引：1=卡车, 2=飞机, 3=船, 4=火车
        toys = [1, 2, 3, 4]
        toy_names = {1: "卡车", 2: "飞机", 3: "船", 4: "火车"}
        
        # 单位利润 ($)
        profits = {1: 5, 2: 10, 3: 8, 4: 7}
        
        # 木材需求 (单位)
        wood_demand = {1: 12, 2: 20, 3: 15, 4: 10}
        
        # 钢材需求 (单位)
        steel_demand = {1: 6, 2: 3, 3: 5, 4: 4}
        
        # 资源可用量
        wood_available = 890
        steel_available = 500
        
        # 计算大M参数 (用于逻辑约束)
        # M_i = min(wood_available // wood_demand[i], steel_available // steel_demand[i])
        big_M = {}
        for i in toys:
            wood_limit = wood_available // wood_demand[i]
            steel_limit = steel_available // steel_demand[i]
            big_M[i] = min(wood_limit, steel_limit)
        
        print("问题参数:")
        print("-" * 50)
        for i in toys:
            print(f"{toy_names[i]}(#{i}): 利润=${profits[i]}, 木材={wood_demand[i]}, 钢材={steel_demand[i]}, 大M={big_M[i]}")
        print(f"资源可用量: 木材={wood_available}, 钢材={steel_available}")
        print()
        
        # 4. 添加决策变量
        # x_i: 玩具i的生产数量 (非负整数)
        x = model.addVars(toys, vtype=COPT.INTEGER, lb=0, nameprefix="x")
        
        # y_i: 是否生产玩具i (二元变量)
        y = model.addVars(toys, vtype=COPT.BINARY, nameprefix="y")
        
        # 5. 设置目标函数 - 最大化总利润
        objective = cp.quicksum(profits[i] * x[i] for i in toys)
        model.setObjective(objective, sense=COPT.MAXIMIZE)
        
        # 6. 添加约束条件
        # 约束1: 木材资源约束
        wood_constraint = cp.quicksum(wood_demand[i] * x[i] for i in toys) <= wood_available
        model.addConstr(wood_constraint, name="wood_resource")
        
        # 约束2: 钢材资源约束  
        steel_constraint = cp.quicksum(steel_demand[i] * x[i] for i in toys) <= steel_available
        model.addConstr(steel_constraint, name="steel_resource")
        
        # 约束3: 生产互斥约束 - 如果生产卡车，则不能生产火车
        model.addConstr(y[1] + y[4] <= 1, name="truck_train_exclusive")
        
        # 约束4: 生产依存约束 - 如果生产船，则必须生产飞机
        model.addConstr(y[3] <= y[2], name="boat_requires_plane")
        
        # 约束5: 生产数量比例约束 - 船的数量不能超过火车的数量
        model.addConstr(x[3] <= x[4], name="boat_not_exceed_train")
        
        # 约束6: 生产决策与产量的关联约束
        # 6a: 产量上限关联 - 如果不生产某种玩具，其产量必须为0
        for i in toys:
            model.addConstr(x[i] <= big_M[i] * y[i], name=f"quantity_upper_bound_{i}")
        
        # 6b: 生产激活关联 - 如果生产某种玩具，其产量至少为1
        for i in toys:
            model.addConstr(x[i] >= y[i], name=f"production_activation_{i}")
        
        # 7. 打印模型信息
        print("模型构建完成:")
        print(f"- 决策变量数: {model.getAttr(COPT.Attr.Cols)}个")
        print(f"- 约束条件数: {model.getAttr(COPT.Attr.Rows)}个")
        print(f"- 整数变量数: {len(toys)}个")
        print(f"- 二元变量数: {len(toys)}个")
        print()
        
        # 8. 求解模型
        print("开始求解...")
        model.solve()
        
        # 9. 分析求解结果
        print("=" * 60)
        print("求解结果分析")
        print("=" * 60)
        
        if model.status == COPT.OPTIMAL:
            print("✅ 模型状态: 找到最优解 (OPTIMAL)")
            print(f"🎯 最大总利润: ${model.objval:.2f}")
            print()
            
            # 输出生产决策
            print("📋 最优生产决策:")
            print("-" * 40)
            total_production = 0
            total_wood_used = 0
            total_steel_used = 0
            
            for i in toys:
                quantity = int(round(x[i].x))
                produces = int(round(y[i].x))
                
                if produces > 0:
                    print(f"{toy_names[i]}(#{i}): 生产 {quantity} 个")
                    print(f"  - 利润贡献: ${profits[i]} × {quantity} = ${profits[i] * quantity}")
                    print(f"  - 木材消耗: {wood_demand[i]} × {quantity} = {wood_demand[i] * quantity}")
                    print(f"  - 钢材消耗: {steel_demand[i]} × {quantity} = {steel_demand[i] * quantity}")
                    
                    total_production += quantity
                    total_wood_used += wood_demand[i] * quantity
                    total_steel_used += steel_demand[i] * quantity
                else:
                    print(f"{toy_names[i]}(#{i}): 不生产")
                print()
            
            # 资源利用情况
            print("📊 资源利用情况:")
            print("-" * 40)
            print(f"木材: {total_wood_used} / {wood_available} 单位 (利用率: {total_wood_used/wood_available:.1%})")
            print(f"钢材: {total_steel_used} / {steel_available} 单位 (利用率: {total_steel_used/steel_available:.1%})")
            print(f"总生产量: {total_production} 个玩具")
            print()
            
            # 逻辑约束验证
            print("✅ 逻辑约束验证:")
            print("-" * 40)
            truck_produced = int(round(y[1].x))
            train_produced = int(round(y[4].x))
            plane_produced = int(round(y[2].x))
            boat_produced = int(round(y[3].x))
            
            print(f"约束1 - 卡车火车互斥: 卡车={truck_produced}, 火车={train_produced} (满足: {truck_produced + train_produced <= 1})")
            print(f"约束2 - 船需要飞机: 船={boat_produced}, 飞机={plane_produced} (满足: {boat_produced <= plane_produced})")
            
            boat_quantity = int(round(x[3].x))
            train_quantity = int(round(x[4].x))
            print(f"约束3 - 船不超过火车: 船数量={boat_quantity}, 火车数量={train_quantity} (满足: {boat_quantity <= train_quantity})")
            print()
            
            # MIP求解统计信息
            print("📈 MIP求解统计:")
            print("-" * 40)
            print(f"最优界 (Best Bound): ${model.getAttr(COPT.Attr.BestBnd):.2f}")
            print(f"最优间隙 (Gap): {model.getAttr(COPT.Attr.BestGap) * 100:.4f}%")
            print(f"搜索节点数: {model.getAttr(COPT.Attr.NodeCnt)}")
            print(f"求解时间: {model.getAttr(COPT.Attr.SolvingTime):.2f} 秒")
            
            # 将结果写入文件
            create_output_files(model, toys, toy_names, x, y, profits, wood_demand, steel_demand, 
                              wood_available, steel_available, total_wood_used, total_steel_used)
            
        else:
            print("❌ 模型未找到最优解")
            print(f"状态码: {model.status}")
            
            # 状态码解释
            status_descriptions = {
                COPT.INFEASIBLE: "模型无可行解 (约束矛盾)",
                COPT.UNBOUNDED: "目标函数无界 (可无限增长)",
                COPT.TIMEOUT: "求解超时",
                COPT.INTERRUPTED: "用户中断求解",
                COPT.NUMERICAL: "数值困难"
            }
            
            description = status_descriptions.get(model.status, "未知状态")
            print(f"状态描述: {description}")
            
        # 10. 保存模型文件（可选）
        model.write("toy_production.lp")  # 保存模型为LP格式
        model.write("toy_production.mps") # 保存模型为MPS格式
        if model.status == COPT.OPTIMAL:
            model.write("toy_production.sol") # 保存解文件
            
        print("\n📁 模型文件已保存:")
        print("- toy_production.lp (模型定义)")
        print("- toy_production.mps (MPS格式)")
        if model.status == COPT.OPTIMAL:
            print("- toy_production.sol (最优解)")
        
    except cp.CoptError as e:
        print(f"❌ COPT错误: {e.retcode} - {e.message}")
        raise
    except Exception as e:
        print(f"❌ 程序执行错误: {e}")
        raise
    finally:
        # 确保释放COPT环境资源
        if 'env' in locals() and env is not None:
            env.close()

def create_output_files(model, toys, toy_names, x, y, profits, wood_demand, steel_demand, 
                       wood_available, steel_available, total_wood_used, total_steel_used):
    """创建输出文件"""
    
    # 确保output目录存在
    os.makedirs("output", exist_ok=True)
    
    # 1. 写入详细结果到output/detailed_results.txt
    with open("output/detailed_results.txt", "w", encoding="utf-8") as f:
        f.write("玩具制造商生产规划优化 - 详细求解结果\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"最优目标函数值: ${model.objval:.2f}\n")
        f.write(f"求解状态: OPTIMAL (最优解)\n\n")
        
        f.write("最优生产决策:\n")
        f.write("-" * 40 + "\n")
        
        for i in toys:
            quantity = int(round(x[i].x))
            produces = int(round(y[i].x))
            
            f.write(f"{toy_names[i]}(#{i}):\n")
            f.write(f"  是否生产: {'是' if produces else '否'} (y[{i}] = {produces})\n")
            f.write(f"  生产数量: {quantity} 个 (x[{i}] = {quantity})\n")
            
            if produces > 0:
                f.write(f"  利润贡献: ${profits[i]} × {quantity} = ${profits[i] * quantity}\n")
                f.write(f"  木材消耗: {wood_demand[i]} × {quantity} = {wood_demand[i] * quantity} 单位\n")
                f.write(f"  钢材消耗: {steel_demand[i]} × {quantity} = {steel_demand[i] * quantity} 单位\n")
            f.write("\n")
        
        f.write("资源利用情况:\n")
        f.write("-" * 40 + "\n")
        f.write(f"木材使用: {total_wood_used} / {wood_available} 单位 (利用率: {total_wood_used/wood_available:.1%})\n")
        f.write(f"钢材使用: {total_steel_used} / {steel_available} 单位 (利用率: {total_steel_used/steel_available:.1%})\n\n")
        
        f.write("约束满足情况:\n")
        f.write("-" * 40 + "\n")
        truck_produced = int(round(y[1].x))
        train_produced = int(round(y[4].x))
        plane_produced = int(round(y[2].x))
        boat_produced = int(round(y[3].x))
        boat_quantity = int(round(x[3].x))
        train_quantity = int(round(x[4].x))
        
        f.write(f"卡车-火车互斥约束: y[1] + y[4] = {truck_produced} + {train_produced} = {truck_produced + train_produced} ≤ 1 ✓\n")
        f.write(f"船-飞机依存约束: y[3] ≤ y[2] => {boat_produced} ≤ {plane_produced} ✓\n")
        f.write(f"船-火车数量约束: x[3] ≤ x[4] => {boat_quantity} ≤ {train_quantity} ✓\n\n")
        
        f.write("MIP求解统计:\n")
        f.write("-" * 40 + "\n")
        f.write(f"最优界: ${model.getAttr(COPT.Attr.BestBnd):.2f}\n")
        f.write(f"最优间隙: {model.getAttr(COPT.Attr.BestGap) * 100:.6f}%\n")
        f.write(f"分支定界节点数: {model.getAttr(COPT.Attr.NodeCnt)}\n")
        f.write(f"求解时间: {model.getAttr(COPT.Attr.SolvingTime):.4f} 秒\n")
    
    # 2. 写入最终目标函数值到result.txt
    with open("result.txt", "w", encoding="utf-8") as f:
        f.write(f"{model.objval:.2f}\n")
    
    # 3. 写入总结到output/final_summary.txt
    with open("output/final_summary.txt", "w", encoding="utf-8") as f:
        f.write("玩具制造商生产规划 - 最优解总结\n")
        f.write("=" * 40 + "\n\n")
        
        f.write(f"📈 最大总利润: ${model.objval:.2f}\n\n")
        
        f.write("🏭 生产方案:\n")
        for i in toys:
            quantity = int(round(x[i].x))
            produces = int(round(y[i].x))
            if produces > 0:
                f.write(f"   • {toy_names[i]}: {quantity} 个\n")
        
        if not any(int(round(y[i].x)) for i in toys):
            f.write("   • 不生产任何玩具\n")
        
        f.write(f"\n📊 资源利用:\n")
        f.write(f"   • 木材: {total_wood_used}/{wood_available} ({total_wood_used/wood_available:.1%})\n")
        f.write(f"   • 钢材: {total_steel_used}/{steel_available} ({total_steel_used/steel_available:.1%})\n")
    
    print("\n📁 输出文件已生成:")
    print("- result.txt (最终目标函数值)")
    print("- output/detailed_results.txt (详细求解结果)")
    print("- output/final_summary.txt (结果总结)")

if __name__ == "__main__":
    print("🚀 玩具制造商生产规划优化问题求解")
    print("使用COPT求解器进行混合整数线性规划(MILP)")
    print("=" * 60)
    solve_toy_production_planning()