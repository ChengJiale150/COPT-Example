#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
农场资源分配优化问题求解
使用COPT求解器求解混合整数线性规划问题

问题描述：
- 农场有100公顷土地，15000元资金
- 季节性劳动力：秋冬季3500人日，春夏季4000人日
- 可种植三种作物：大豆、玉米、小麦
- 可养殖两种动物：奶牛、鸡
- 剩余劳动力可外派获得收入
- 目标：最大化年净总收入
"""

import coptpy as cp
from coptpy import COPT

def solve_farm_optimization():
    try:
        # 1. 创建COPT求解环境
        env = cp.Envr()
        
        # 2. 创建优化模型
        model = env.createModel("farm_optimization")
        
        # 3. 定义问题数据
        # 资源总量
        total_land = 100  # 公顷
        total_capital = 15000  # 元
        labor_aw = 3500  # 秋冬劳动力（人日）
        labor_ss = 4000  # 春夏劳动力（人日）
        
        # 作物参数 [大豆, 玉米, 小麦]
        crop_names = ["大豆", "玉米", "小麦"]
        crop_labor_aw = [20, 35, 10]  # 每公顷秋冬劳动力需求
        crop_labor_ss = [50, 75, 40]  # 每公顷春夏劳动力需求
        crop_income = [175, 300, 120]  # 每公顷年净收入
        
        # 动物参数 [奶牛, 鸡]
        animal_names = ["奶牛", "鸡"]
        animal_land = [1.5, 0]  # 每头/只占用土地
        animal_capital = [400, 3]  # 每头/只资金投入
        animal_labor_aw = [100, 0.6]  # 每头/只秋冬劳动力需求
        animal_labor_ss = [50, 0.3]  # 每头/只春夏劳动力需求
        animal_income = [400, 2]  # 每头/只年净收入
        animal_capacity = [32, 3000]  # 养殖容量上限
        
        # 外派劳务收入
        labor_income_aw = 1.8  # 秋冬外派收入（元/人日）
        labor_income_ss = 2.1  # 春夏外派收入（元/人日）
        
        # 4. 添加决策变量
        # 作物种植面积（连续变量）
        x = model.addVars(3, lb=0.0, nameprefix="crop_area")
        
        # 动物养殖数量（整数变量）
        y = model.addVars(2, vtype=COPT.INTEGER, lb=0, nameprefix="animal_count")
        
        # 外派劳动力（整数变量）
        L_aw = model.addVar(vtype=COPT.INTEGER, lb=0, name="labor_external_aw")
        L_ss = model.addVar(vtype=COPT.INTEGER, lb=0, name="labor_external_ss")
        
        # 5. 添加约束条件
        # 约束1: 土地资源约束
        land_constraint = model.addConstr(
            cp.quicksum(x[i] for i in range(3)) + animal_land[0] * y[0] + animal_land[1] * y[1] <= total_land,
            name="land_constraint"
        )
        
        # 约束2: 资金约束
        capital_constraint = model.addConstr(
            animal_capital[0] * y[0] + animal_capital[1] * y[1] <= total_capital,
            name="capital_constraint"
        )
        
        # 约束3: 秋冬劳动力平衡约束（等式）
        labor_aw_constraint = model.addConstr(
            cp.quicksum(crop_labor_aw[i] * x[i] for i in range(3)) + 
            cp.quicksum(animal_labor_aw[i] * y[i] for i in range(2)) + 
            L_aw == labor_aw,
            name="labor_aw_balance"
        )
        
        # 约束4: 春夏劳动力平衡约束（等式）
        labor_ss_constraint = model.addConstr(
            cp.quicksum(crop_labor_ss[i] * x[i] for i in range(3)) + 
            cp.quicksum(animal_labor_ss[i] * y[i] for i in range(2)) + 
            L_ss == labor_ss,
            name="labor_ss_balance"
        )
        
        # 约束5: 养殖容量约束
        # 奶牛容量约束
        cow_capacity_constraint = model.addConstr(
            y[0] <= animal_capacity[0],
            name="cow_capacity"
        )
        
        # 鸡容量约束
        chicken_capacity_constraint = model.addConstr(
            y[1] <= animal_capacity[1],
            name="chicken_capacity"
        )
        
        # 6. 设置目标函数（最大化年净总收入）
        # 作物收入
        crop_revenue = cp.quicksum(crop_income[i] * x[i] for i in range(3))
        # 动物收入
        animal_revenue = cp.quicksum(animal_income[i] * y[i] for i in range(2))
        # 外派劳务收入
        external_labor_revenue = labor_income_aw * L_aw + labor_income_ss * L_ss
        
        # 总收入
        total_revenue = crop_revenue + animal_revenue + external_labor_revenue
        
        model.setObjective(total_revenue, sense=COPT.MAXIMIZE)
        
        # 7. 求解模型
        print("开始求解农场资源分配优化问题...")
        model.solve()
        
        # 8. 分析求解结果
        if model.status == COPT.OPTIMAL:
            print("\n" + "="*50)
            print("求解成功！找到最优解")
            print("="*50)
            
            # 输出最优目标函数值
            optimal_value = model.objval
            print(f"\n最大年净总收入: {optimal_value:.2f} 元")
            
            print("\n--- 最优决策方案 ---")
            
            # 作物种植计划
            print("\n1. 作物种植计划:")
            total_crop_area = 0
            total_crop_income = 0
            for i in range(3):
                area = x[i].x
                total_crop_area += area
                income = area * crop_income[i]
                total_crop_income += income
                print(f"   {crop_names[i]}: {area:.2f} 公顷, 收入: {income:.2f} 元")
            print(f"   作物总面积: {total_crop_area:.2f} 公顷")
            print(f"   作物总收入: {total_crop_income:.2f} 元")
            
            # 动物养殖计划
            print("\n2. 动物养殖计划:")
            total_animal_income = 0
            total_animal_land = 0
            total_animal_investment = 0
            for i in range(2):
                count = int(y[i].x)
                income = count * animal_income[i]
                land_used = count * animal_land[i]
                investment = count * animal_capital[i]
                total_animal_income += income
                total_animal_land += land_used
                total_animal_investment += investment
                print(f"   {animal_names[i]}: {count} 头/只, 收入: {income:.2f} 元, 占地: {land_used:.2f} 公顷, 投资: {investment:.2f} 元")
            print(f"   动物总收入: {total_animal_income:.2f} 元")
            print(f"   动物占地总计: {total_animal_land:.2f} 公顷")
            print(f"   动物投资总计: {total_animal_investment:.2f} 元")
            
            # 外派劳务计划
            print("\n3. 外派劳务计划:")
            external_aw = int(L_aw.x)
            external_ss = int(L_ss.x)
            external_income_aw = external_aw * labor_income_aw
            external_income_ss = external_ss * labor_income_ss
            total_external_income = external_income_aw + external_income_ss
            print(f"   秋冬外派: {external_aw} 人日, 收入: {external_income_aw:.2f} 元")
            print(f"   春夏外派: {external_ss} 人日, 收入: {external_income_ss:.2f} 元")
            print(f"   外派总收入: {total_external_income:.2f} 元")
            
            # 资源使用情况分析
            print("\n--- 资源使用情况 ---")
            
            # 土地使用
            used_land = total_crop_area + total_animal_land
            print(f"\n1. 土地使用:")
            print(f"   已用土地: {used_land:.2f} / {total_land} 公顷")
            print(f"   土地利用率: {used_land/total_land:.2%}")
            
            # 资金使用
            print(f"\n2. 资金使用:")
            print(f"   已用资金: {total_animal_investment:.2f} / {total_capital} 元")
            print(f"   资金利用率: {total_animal_investment/total_capital:.2%}")
            
            # 劳动力使用
            print(f"\n3. 劳动力使用:")
            
            # 秋冬劳动力
            used_labor_aw = sum(crop_labor_aw[i] * x[i].x for i in range(3)) + \
                           sum(animal_labor_aw[i] * y[i].x for i in range(2))
            print(f"   秋冬季: 生产用工 {used_labor_aw:.2f} + 外派 {external_aw} = {used_labor_aw + external_aw:.2f} / {labor_aw} 人日")
            
            # 春夏劳动力
            used_labor_ss = sum(crop_labor_ss[i] * x[i].x for i in range(3)) + \
                           sum(animal_labor_ss[i] * y[i].x for i in range(2))
            print(f"   春夏季: 生产用工 {used_labor_ss:.2f} + 外派 {external_ss} = {used_labor_ss + external_ss:.2f} / {labor_ss} 人日")
            
            # 收入结构分析
            print(f"\n--- 收入结构分析 ---")
            print(f"作物收入: {total_crop_income:.2f} 元 ({total_crop_income/optimal_value:.2%})")
            print(f"动物收入: {total_animal_income:.2f} 元 ({total_animal_income/optimal_value:.2%})")
            print(f"外派收入: {total_external_income:.2f} 元 ({total_external_income/optimal_value:.2%})")
            print(f"总收入: {optimal_value:.2f} 元")
            
            # 将结果写入文件
            with open("result.txt", "w", encoding="utf-8") as f:
                f.write(f"农场资源分配优化问题求解结果\n")
                f.write(f"最大年净总收入: {optimal_value:.2f} 元\n")
                f.write(f"\n详细方案:\n")
                f.write(f"作物种植: {crop_names[0]} {x[0].x:.2f}公顷, {crop_names[1]} {x[1].x:.2f}公顷, {crop_names[2]} {x[2].x:.2f}公顷\n")
                f.write(f"动物养殖: {animal_names[0]} {int(y[0].x)}头, {animal_names[1]} {int(y[1].x)}只\n")
                f.write(f"外派劳务: 秋冬 {external_aw}人日, 春夏 {external_ss}人日\n")
            
            print(f"\n结果已保存到 result.txt 文件")
            
            return optimal_value
            
        else:
            print(f"\n模型未找到最优解。状态码: {model.status}")
            # 状态描述
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
        print(f"发生意外错误: {e}")
        return None
    finally:
        if 'env' in locals() and env is not None:
            env.close()

if __name__ == "__main__":
    result = solve_farm_optimization()
    if result is not None:
        print(f"\n程序执行完成，最优目标函数值: {result:.2f} 元")
    else:
        print("\n程序执行失败")