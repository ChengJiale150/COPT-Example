#!/usr/bin/env python3
"""
意大利运输公司集装箱调运问题求解器

这是一个混合整数线性规划(MILP)问题，目标是最小化总运输成本。
问题特点：
- 6个仓库(维罗纳、佩鲁贾、罗马、佩斯卡拉、塔兰托、拉默齐亚)
- 5个港口(热那亚、威尼斯、安科纳、那不勒斯、巴里)
- 每辆卡车最多运输2个集装箱
- 运输成本：30欧元/公里 × 距离 × 卡车数量
"""

import coptpy as cp
from coptpy import COPT

def solve_transportation_problem():
    try:
        # 1. 创建COPT求解环境
        env = cp.Envr()
        model = env.createModel("italian_container_transportation")

        # 2. 定义问题数据
        # 仓库名称
        warehouses = ["维罗纳", "佩鲁贾", "罗马", "佩斯卡拉", "塔兰托", "拉默齐亚"]
        # 港口名称
        ports = ["热那亚", "威尼斯", "安科纳", "那不勒斯", "巴里"]
        
        # 供应量 (各仓库的空集装箱数量)
        supply = {
            "维罗纳": 10,
            "佩鲁贾": 12,
            "罗马": 20,
            "佩斯卡拉": 24,
            "塔兰托": 18,
            "拉默齐亚": 40
        }
        
        # 需求量 (各港口的集装箱需求)
        demand = {
            "热那亚": 20,
            "威尼斯": 15,
            "安科纳": 25,
            "那不勒斯": 33,
            "巴里": 21
        }
        
        # 距离矩阵 (公里)
        distance = {
            ("维罗纳", "热那亚"): 290,
            ("维罗纳", "威尼斯"): 115,
            ("维罗纳", "安科纳"): 355,
            ("维罗纳", "那不勒斯"): 715,
            ("维罗纳", "巴里"): 810,
            ("佩鲁贾", "热那亚"): 380,
            ("佩鲁贾", "威尼斯"): 340,
            ("佩鲁贾", "安科纳"): 165,
            ("佩鲁贾", "那不勒斯"): 380,
            ("佩鲁贾", "巴里"): 610,
            ("罗马", "热那亚"): 505,
            ("罗马", "威尼斯"): 530,
            ("罗马", "安科纳"): 285,
            ("罗马", "那不勒斯"): 220,
            ("罗马", "巴里"): 450,
            ("佩斯卡拉", "热那亚"): 655,
            ("佩斯卡拉", "威尼斯"): 450,
            ("佩斯卡拉", "安科纳"): 155,
            ("佩斯卡拉", "那不勒斯"): 240,
            ("佩斯卡拉", "巴里"): 315,
            ("塔兰托", "热那亚"): 1010,
            ("塔兰托", "威尼斯"): 840,
            ("塔兰托", "安科纳"): 550,
            ("塔兰托", "那不勒斯"): 305,
            ("塔兰托", "巴里"): 95,
            ("拉默齐亚", "热那亚"): 1072,
            ("拉默齐亚", "威尼斯"): 1097,
            ("拉默齐亚", "安科纳"): 747,
            ("拉默齐亚", "那不勒斯"): 372,
            ("拉默齐亚", "巴里"): 333
        }
        
        # 参数
        cost_per_km = 30  # 每公里30欧元
        truck_capacity = 2  # 每辆卡车最多装载2个集装箱
        
        # 3. 创建所有可能的路线
        routes = [(w, p) for w in warehouses for p in ports]
        
        # 4. 添加决策变量
        # x[i,j]: 从仓库i运输到港口j的集装箱数量 (非负整数)
        x = model.addVars(routes, vtype=COPT.INTEGER, lb=0, nameprefix="containers")
        
        # t[i,j]: 从仓库i派遣到港口j的卡车数量 (非负整数)
        t = model.addVars(routes, vtype=COPT.INTEGER, lb=0, nameprefix="trucks")
        
        # 5. 添加约束条件
        # 约束1: 供应约束 - 每个仓库运出的集装箱不能超过其库存
        for w in warehouses:
            model.addConstr(
                cp.quicksum(x[w, p] for p in ports) <= supply[w],
                name=f"supply_{w}"
            )
        
        # 约束2: 需求满足约束 - 每个港口必须收到恰好其需求数量的集装箱
        for p in ports:
            model.addConstr(
                cp.quicksum(x[w, p] for w in warehouses) == demand[p],
                name=f"demand_{p}"
            )
        
        # 约束3: 卡车-集装箱关联约束 - 卡车数量必须足够运输集装箱
        # 这个约束确保：t[i,j] >= ceil(x[i,j] / truck_capacity)
        for w, p in routes:
            model.addConstr(
                x[w, p] <= truck_capacity * t[w, p],
                name=f"truck_capacity_{w}_{p}"
            )
        
        # 6. 设置目标函数 - 最小化总运输成本
        total_cost = cp.quicksum(
            cost_per_km * distance[w, p] * t[w, p] 
            for w, p in routes
        )
        model.setObjective(total_cost, sense=COPT.MINIMIZE)
        
        # 7. 求解模型
        print("正在求解模型...")
        model.solve()
        
        # 8. 分析求解结果
        if model.status == COPT.OPTIMAL:
            print("\n" + "="*60)
            print("           意大利集装箱运输优化求解结果")
            print("="*60)
            print(f"模型状态: 最优解")
            print(f"最优总运输成本: {model.objval:,.2f} 欧元")
            
            # 验证供需平衡
            total_supply = sum(supply.values())
            total_demand = sum(demand.values())
            print(f"\n总供应量: {total_supply} 个集装箱")
            print(f"总需求量: {total_demand} 个集装箱")
            print(f"剩余集装箱: {total_supply - total_demand} 个")
            
            print("\n" + "-"*60)
            print("详细运输方案:")
            print("-"*60)
            
            total_containers_shipped = 0
            total_trucks_used = 0
            
            # 显示所有非零的运输方案
            for w in warehouses:
                warehouse_total_containers = 0
                warehouse_total_trucks = 0
                has_shipment = False
                
                for p in ports:
                    containers = x[w, p].x
                    trucks = t[w, p].x
                    
                    if containers > 0.5:  # 考虑数值精度
                        if not has_shipment:
                            print(f"\n从 {w}:")
                            has_shipment = True
                        
                        cost = cost_per_km * distance[w, p] * trucks
                        efficiency = containers / trucks if trucks > 0 else 0
                        
                        print(f"  → {p}: {int(containers):2d} 个集装箱, "
                              f"{int(trucks):2d} 辆卡车, "
                              f"距离: {distance[w, p]:4d}km, "
                              f"成本: {cost:8,.0f} 欧元, "
                              f"装载率: {efficiency:.1f}/2")
                        
                        warehouse_total_containers += containers
                        warehouse_total_trucks += trucks
                        total_containers_shipped += containers
                        total_trucks_used += trucks
                
                if has_shipment:
                    print(f"  小计: {int(warehouse_total_containers)} 个集装箱, "
                          f"{int(warehouse_total_trucks)} 辆卡车")
            
            print(f"\n总计: {int(total_containers_shipped)} 个集装箱, "
                  f"{int(total_trucks_used)} 辆卡车")
            
            # 验证需求满足情况
            print("\n" + "-"*60)
            print("需求满足情况验证:")
            print("-"*60)
            for p in ports:
                received = sum(x[w, p].x for w in warehouses)
                print(f"{p}: 需求 {demand[p]}, 收到 {int(received)}, "
                      f"{'✓' if abs(received - demand[p]) < 0.1 else '✗'}")
            
            # 计算平均装载率
            avg_load_rate = total_containers_shipped / total_trucks_used if total_trucks_used > 0 else 0
            print(f"\n平均卡车装载率: {avg_load_rate:.2f}/2 ({avg_load_rate/2:.1%})")
            
            # MIP求解统计信息
            print("\n" + "-"*60)
            print("MIP 求解统计信息:")
            print("-"*60)
            print(f"最优界: {model.getAttr(COPT.Attr.BestBnd):,.2f} 欧元")
            print(f"最优间隙: {model.getAttr(COPT.Attr.BestGap) * 100:.4f}%")
            print(f"搜索节点数: {model.getAttr(COPT.Attr.NodeCnt)}")
            
            # 将结果写入文件
            with open("result.txt", "w", encoding="utf-8") as f:
                f.write(f"最优总运输成本: {model.objval:.2f} 欧元\n")
            
            print(f"\n结果已保存到 result.txt")
            return model.objval
            
        else:
            error_msg = f"模型未找到最优解。状态码: {model.status}"
            print(error_msg)
            
            # 状态码说明
            status_descriptions = {
                COPT.INFEASIBLE: "模型无可行解",
                COPT.UNBOUNDED: "目标函数无界", 
                COPT.TIMEOUT: "求解超时",
                COPT.INTERRUPTED: "用户中断"
            }
            
            if model.status in status_descriptions:
                print(f"状态描述: {status_descriptions[model.status]}")
            
            # 仍然写入错误信息到结果文件
            with open("result.txt", "w", encoding="utf-8") as f:
                f.write(f"求解失败: {error_msg}\n")
            
            return None

    except cp.CoptError as e:
        error_msg = f"COPT Error: {e.retcode} - {e.message}"
        print(error_msg)
        with open("result.txt", "w", encoding="utf-8") as f:
            f.write(f"COPT错误: {error_msg}\n")
        return None
        
    except Exception as e:
        error_msg = f"意外错误: {e}"
        print(error_msg)
        with open("result.txt", "w", encoding="utf-8") as f:
            f.write(f"程序错误: {error_msg}\n")
        return None
        
    finally:
        # 确保环境被正确关闭
        if 'env' in locals() and env is not None:
            env.close()

if __name__ == "__main__":
    print("开始求解意大利运输公司集装箱调运问题")
    result = solve_transportation_problem()
    if result is not None:
        print(f"\n程序执行完成，最优解: {result:.2f} 欧元")
    else:
        print("\n程序执行失败")