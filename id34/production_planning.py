#!/usr/bin/env python3
"""
集装箱装载优化问题求解
使用COPT求解器求解混合整数线性规划问题

问题描述：
- 目标：最小化使用的集装箱数量
- 约束：载重限制、货物依赖关系、最小装载要求等
"""

import coptpy as cp
from coptpy import COPT

def solve_container_packing():
    """求解集装箱装载优化问题"""
    
    try:
        # 1. 创建COPT求解环境
        env = cp.Envr()
        model = env.createModel("container_packing_optimization")
        
        # 2. 定义问题数据
        # 货物类型
        goods = ['A', 'B', 'C', 'D', 'E']
        
        # 需求量
        demands = {
            'A': 120,
            'B': 90,
            'C': 300,
            'D': 90,
            'E': 120
        }
        
        # 单位重量 (吨)
        weights = {
            'A': 0.5,
            'B': 1.0,
            'C': 0.4,
            'D': 0.6,
            'E': 0.65
        }
        
        # 集装箱参数
        max_capacity = 60  # 最大载重 (吨)
        min_capacity = 18  # 最小载重 (吨)
        min_d_quantity = 12  # 每个集装箱最少装载D的数量
        min_c_when_a = 1   # 装载A时C的最小数量
        
        # 估算集装箱数量上限
        total_weight = sum(demands[i] * weights[i] for i in goods)
        max_containers = int(total_weight / min_capacity) + 5  # 安全余量
        
        print(f"货物总重量: {total_weight:.2f} 吨")
        print(f"估算最大集装箱需求: {max_containers} 个")
        print(f"集装箱编号: 1 到 {max_containers}")
        
        # 集装箱编号
        containers = list(range(1, max_containers + 1))
        
        # 3. 添加决策变量
        # x[i,j]: 在集装箱j中装载货物i的数量
        x = {}
        for i in goods:
            for j in containers:
                x[i, j] = model.addVar(vtype=COPT.INTEGER, lb=0, name=f"x_{i}_{j}")
        
        # y[j]: 是否使用集装箱j
        y = {}
        for j in containers:
            y[j] = model.addVar(vtype=COPT.BINARY, name=f"y_{j}")
        
        # a[j]: 集装箱j是否装载了货物A
        a = {}
        for j in containers:
            a[j] = model.addVar(vtype=COPT.BINARY, name=f"a_{j}")
        
        # 4. 设置目标函数：最小化使用的集装箱数量
        model.setObjective(cp.quicksum(y[j] for j in containers), sense=COPT.MINIMIZE)
        
        # 5. 添加约束条件
        
        # 约束1: 需求满足约束
        for i in goods:
            model.addConstr(
                cp.quicksum(x[i, j] for j in containers) == demands[i],
                name=f"demand_{i}"
            )
        
        # 约束2: 集装箱使用关联约束
        for i in goods:
            for j in containers:
                model.addConstr(
                    x[i, j] <= demands[i] * y[j],
                    name=f"usage_link_{i}_{j}"
                )
        
        # 约束3: 集装箱最大载重约束
        for j in containers:
            model.addConstr(
                cp.quicksum(weights[i] * x[i, j] for i in goods) <= max_capacity * y[j],
                name=f"max_capacity_{j}"
            )
        
        # 约束4: 集装箱最小载重约束
        for j in containers:
            model.addConstr(
                cp.quicksum(weights[i] * x[i, j] for i in goods) >= min_capacity * y[j],
                name=f"min_capacity_{j}"
            )
        
        # 约束5: 货物D最小装载量约束
        for j in containers:
            model.addConstr(
                x['D', j] >= min_d_quantity * y[j],
                name=f"min_d_quantity_{j}"
            )
        
        # 约束6: 货物A与C的装载关联逻辑
        # 6a: 货物A装载指示
        for j in containers:
            model.addConstr(
                x['A', j] <= demands['A'] * a[j],
                name=f"a_indicator_upper_{j}"
            )
            model.addConstr(
                x['A', j] >= a[j],
                name=f"a_indicator_lower_{j}"
            )
        
        # 6b: 货物C关联装载
        for j in containers:
            model.addConstr(
                x['C', j] >= min_c_when_a * a[j],
                name=f"c_when_a_{j}"
            )
        
        # 约束7: 对称性破除约束
        for j in range(1, max_containers):
            model.addConstr(
                y[j] >= y[j + 1],
                name=f"symmetry_breaking_{j}"
            )
        
        # 6. 求解模型
        print("\n开始求解...")
        model.solve()
        
        # 7. 分析求解结果
        if model.status == COPT.OPTIMAL:
            print("\n" + "="*50)
            print("求解结果")
            print("="*50)
            print(f"模型状态: 最优解 (COPT.OPTIMAL)")
            print(f"最少使用集装箱数量: {int(model.objval)}")
            
            # 打印使用的集装箱详情
            used_containers = []
            for j in containers:
                if y[j].x > 0.5:
                    used_containers.append(j)
            
            print(f"\n使用的集装箱编号: {used_containers}")
            
            # 详细装载方案
            print("\n详细装载方案:")
            total_weight_check = 0
            for j in used_containers:
                print(f"\n集装箱 {j}:")
                container_weight = 0
                container_goods = []
                
                for i in goods:
                    quantity = int(x[i, j].x)
                    if quantity > 0:
                        item_weight = quantity * weights[i]
                        container_weight += item_weight
                        container_goods.append(f"  {i}: {quantity} 件 ({item_weight:.2f} 吨)")
                
                for item in container_goods:
                    print(item)
                
                print(f"  总重量: {container_weight:.2f} 吨 [{min_capacity}-{max_capacity}]")
                total_weight_check += container_weight
                
                # 验证约束
                if container_weight < min_capacity:
                    print(f"  ⚠️  警告: 重量低于最小要求!")
                if container_weight > max_capacity:
                    print(f"  ⚠️  警告: 重量超过最大限制!")
                
                # 检查D的数量
                d_quantity = int(x['D', j].x)
                if d_quantity < min_d_quantity:
                    print(f"  ⚠️  警告: D的数量({d_quantity})低于最小要求({min_d_quantity})!")
                
                # 检查A-C关联
                a_quantity = int(x['A', j].x)
                c_quantity = int(x['C', j].x)
                if a_quantity > 0 and c_quantity < min_c_when_a:
                    print(f"  ⚠️  警告: 装载A但C不足!")
            
            print(f"\n验证总重量: {total_weight_check:.2f} 吨 (期望: {total_weight:.2f} 吨)")
            
            # 需求满足验证
            print("\n需求满足验证:")
            for i in goods:
                total_loaded = sum(int(x[i, j].x) for j in containers)
                print(f"  {i}: 装载 {total_loaded} / 需求 {demands[i]} = {'✓' if total_loaded == demands[i] else '✗'}")
            
            # MIP求解统计
            print(f"\nMIP求解统计:")
            print(f"  最优界: {model.getAttr(COPT.Attr.BestBnd):.4f}")
            print(f"  最优间隙: {model.getAttr(COPT.Attr.BestGap) * 100:.4f}%")
            print(f"  搜索节点数: {model.getAttr(COPT.Attr.NodeCnt)}")
            
            # 返回目标函数值
            return model.objval
            
        else:
            print(f"\n模型未找到最优解。状态码: {model.status}")
            status_map = {
                COPT.INFEASIBLE: "模型无可行解",
                COPT.UNBOUNDED: "目标函数无界", 
                COPT.TIMEOUT: "求解超时",
                COPT.INTERRUPTED: "用户中断"
            }
            print(f"状态描述: {status_map.get(model.status, '未知状态')}")
            return None
            
    except cp.CoptError as e:
        print(f"COPT Error: {e.retcode} - {e.message}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    finally:
        if 'env' in locals() and env is not None:
            env.close()

if __name__ == "__main__":
    result = solve_container_packing()
    if result is not None:
        # 将结果写入文件
        with open("result.txt", "w", encoding="utf-8") as f:
            f.write(f"最少使用集装箱数量: {int(result)}\n")
        print(f"\n结果已保存到 result.txt")
    else:
        print("求解失败，无法保存结果")