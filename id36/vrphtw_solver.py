#!/usr/bin/env python3
"""
VRPHTW (Vehicle Routing Problem with Hard Time Windows) Solver using COPT
带硬时间窗的车辆路径问题求解器

问题描述：
- 20个客户需要配送服务
- 最多5辆卡车，每辆容量200单位  
- 中心仓库坐标：(40, 50)，营业时间窗：[0, 1236]分钟
- 每个客户都有严格的硬时间窗约束
- 固定服务时间：90分钟
- 目标：最小化所有车辆的总行驶距离
"""

import coptpy as cp
from coptpy import COPT
import math

def calculate_distance(x1, y1, x2, y2):
    """计算两点之间的欧几里得距离"""
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def solve_vrphtw():
    try:
        # 1. 创建COPT求解环境
        env = cp.Envr()
        
        # 2. 创建优化模型
        model = env.createModel("VRPHTW")
        
        # 3. 定义问题数据
        
        # 节点数据：仓库(0) + 20个客户(1-20)
        # 坐标数据
        coordinates = {
            0: (40, 50),    # 仓库
            1: (45, 68), 2: (45, 70), 3: (42, 66), 4: (42, 68), 5: (42, 65),
            6: (40, 69), 7: (40, 66), 8: (38, 68), 9: (38, 70), 10: (35, 66),
            11: (35, 69), 12: (25, 85), 13: (22, 75), 14: (22, 85), 15: (20, 80),
            16: (20, 85), 17: (18, 75), 18: (15, 75), 19: (15, 80), 20: (30, 50)
        }
        
        # 需求数据
        demands = {
            0: 0,   # 仓库需求为0
            1: 10, 2: 30, 3: 10, 4: 10, 5: 10,
            6: 20, 7: 20, 8: 20, 9: 10, 10: 10,
            11: 10, 12: 20, 13: 30, 14: 10, 15: 40,
            16: 40, 17: 20, 18: 20, 19: 10, 20: 10
        }
        
        # 时间窗数据 [最早时间, 最晚时间]
        time_windows = {
            0: (0, 1236),       # 仓库
            1: (912, 967), 2: (825, 870), 3: (65, 146), 4: (727, 782), 5: (15, 67),
            6: (621, 702), 7: (170, 225), 8: (255, 324), 9: (534, 605), 10: (357, 410),
            11: (448, 505), 12: (652, 721), 13: (30, 92), 14: (567, 620), 15: (384, 429),
            16: (475, 528), 17: (99, 148), 18: (179, 254), 19: (278, 345), 20: (10, 73)
        }
        
        # 服务时间
        service_times = {i: 90 if i > 0 else 0 for i in range(21)}  # 客户服务时间90分钟，仓库为0
        
        # 车辆数据
        num_vehicles = 5
        vehicle_capacity = 200
        
        # 节点集合
        nodes = list(range(21))  # 0-20
        customers = list(range(1, 21))  # 1-20
        vehicles = list(range(num_vehicles))  # 0-4
        
        # 计算距离矩阵
        distances = {}
        for i in nodes:
            for j in nodes:
                x1, y1 = coordinates[i]
                x2, y2 = coordinates[j]
                distances[i, j] = calculate_distance(x1, y1, x2, y2)
        
        # Big M 值 - 用于线性化逻辑约束
        M = 10000
        
        # 4. 添加决策变量
        
        # x[i,j,k] = 1 如果车辆k从节点i直接行驶到节点j
        x = model.addVars(nodes, nodes, vehicles, vtype=COPT.BINARY, nameprefix="x")
        
        # B[i] = 在节点i的服务开始时间
        B = model.addVars(nodes, lb=0, nameprefix="B")
        
        # 5. 设置目标函数：最小化总行驶距离
        model.setObjective(
            cp.quicksum(distances[i, j] * x[i, j, k] 
                       for i in nodes for j in nodes for k in vehicles),
            sense=COPT.MINIMIZE
        )
        
        # 6. 添加约束条件
        
        # 约束1：客户服务唯一性 - 每个客户必须被访问一次
        for j in customers:
            model.addConstr(
                cp.quicksum(x[i, j, k] for i in nodes for k in vehicles) == 1,
                name=f"customer_visit_{j}"
            )
        
        # 约束2：车辆路径连续性 - 流平衡约束
        for p in customers:
            for k in vehicles:
                model.addConstr(
                    cp.quicksum(x[i, p, k] for i in nodes) - 
                    cp.quicksum(x[p, j, k] for j in nodes) == 0,
                    name=f"flow_balance_{p}_{k}"
                )
        
        # 约束3：车辆调度 - 每辆车从仓库出发并返回仓库
        for k in vehicles:
            model.addConstr(
                cp.quicksum(x[0, j, k] for j in customers) == 
                cp.quicksum(x[i, 0, k] for i in customers),
                name=f"depot_balance_{k}"
            )
            
            # 每辆车最多从仓库出发一次
            model.addConstr(
                cp.quicksum(x[0, j, k] for j in customers) <= 1,
                name=f"max_one_departure_{k}"
            )
        
        # 约束4：车辆容量约束
        for k in vehicles:
            model.addConstr(
                cp.quicksum(demands[i] * cp.quicksum(x[i, j, k] for j in nodes) 
                           for i in customers) <= vehicle_capacity,
                name=f"capacity_{k}"
            )
        
        # 约束5：时间窗约束
        for i in nodes:
            e_i, l_i = time_windows[i]
            model.addConstr(B[i] >= e_i, name=f"time_window_early_{i}")
            model.addConstr(B[i] <= l_i, name=f"time_window_late_{i}")
        
        # 约束6：时间流一致性与子路径消除
        for i in nodes:
            for j in customers:
                if i != j:
                    for k in vehicles:
                        model.addConstr(
                            B[i] + service_times[i] + distances[i, j] - M * (1 - x[i, j, k]) <= B[j],
                            name=f"time_flow_{i}_{j}_{k}"
                        )
        
        # 约束7：车辆返回时间约束
        for i in customers:
            model.addConstr(
                B[i] + service_times[i] + distances[i, 0] - 
                M * (1 - cp.quicksum(x[i, 0, k] for k in vehicles)) <= time_windows[0][1],
                name=f"return_time_{i}"
            )
        
        # 约束8：禁止自环
        for i in nodes:
            for k in vehicles:
                model.addConstr(x[i, i, k] == 0, name=f"no_self_loop_{i}_{k}")
        
        # 7. 求解模型
        print("开始求解VRPHTW问题...")
        model.solve()
        
        # 8. 分析求解结果
        if model.status == COPT.OPTIMAL:
            print("\n=== 求解结果 ===")
            print(f"模型状态: 最优解")
            print(f"最小总距离: {model.objval:.2f}")
            
            # 输出车辆路径
            print("\n=== 车辆路径 ===")
            total_distance = 0
            active_vehicles = 0
            
            for k in vehicles:
                route = []
                current_node = 0  # 从仓库开始
                
                # 检查是否有车辆从仓库出发
                has_departure = any(x[0, j, k].x > 0.5 for j in customers)
                if not has_departure:
                    continue
                    
                active_vehicles += 1
                route.append(current_node)
                
                # 构建路径
                while True:
                    next_node = None
                    for j in nodes:
                        if current_node != j and x[current_node, j, k].x > 0.5:
                            next_node = j
                            break
                    
                    if next_node is None or next_node == 0:
                        if next_node == 0:
                            route.append(0)
                        break
                    
                    route.append(next_node)
                    current_node = next_node
                
                # 计算路径距离和载重
                route_distance = 0
                route_load = 0
                for i in range(len(route) - 1):
                    route_distance += distances[route[i], route[i+1]]
                
                for node in route[1:-1]:  # 排除仓库
                    route_load += demands[node]
                
                total_distance += route_distance
                
                print(f"车辆 {k+1}: {' -> '.join(map(str, route))}")
                print(f"  距离: {route_distance:.2f}, 载重: {route_load}/{vehicle_capacity}")
                
                # 显示时间安排
                print("  时间安排:")
                for node in route:
                    if node in B and B[node].x is not None:
                        service_start = B[node].x
                        service_end = service_start + service_times[node]
                        window = time_windows[node]
                        print(f"    节点{node}: 到达/服务开始={service_start:.1f}, 服务结束={service_end:.1f}, 时间窗=[{window[0]}, {window[1]}]")
            
            print(f"\n活跃车辆数: {active_vehicles}/{num_vehicles}")
            print(f"总距离验证: {total_distance:.2f}")
            
            # 将结果写入文件
            with open("/Users/jiale.cheng/Documents/mcp/test/result.txt", "w") as f:
                f.write(f"VRPHTW问题求解结果\n")
                f.write(f"===================\n")
                f.write(f"最优目标函数值（最小总距离）: {model.objval:.2f}\n")
                f.write(f"活跃车辆数: {active_vehicles}/{num_vehicles}\n")
                f.write(f"求解状态: 最优解\n")
            
            print(f"\n结果已保存到 result.txt")
            
        else:
            print(f"\n模型未找到最优解，状态码: {model.status}")
            with open("/Users/jiale.cheng/Documents/mcp/test/result.txt", "w") as f:
                f.write(f"VRPHTW问题求解失败\n")
                f.write(f"状态码: {model.status}\n")
        
        return model.objval if model.status == COPT.OPTIMAL else None
        
    except cp.CoptError as e:
        print(f"COPT错误: {e.retcode} - {e.message}")
        return None
    except Exception as e:
        print(f"发生错误: {e}")
        return None
    finally:
        if 'env' in locals() and env is not None:
            env.close()

if __name__ == "__main__":
    solve_vrphtw()