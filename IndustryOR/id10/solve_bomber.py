import coptpy as cp
from coptpy import COPT

def solve_set_covering_problem():
    """
    求解集合覆盖问题：超市连锁店最优选址问题
    
    目标：最小化建立的连锁店数量，使得每个居民区都被至少一家店覆盖
    """
    
    try:
        # 1. 创建COPT求解环境
        env = cp.Envr()
        
        # 2. 创建优化模型
        model = env.createModel("supermarket_location_set_covering")
        
        # 3. 定义问题数据
        # 所有居民区列表 (也是潜在的连锁店位置)
        areas = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        
        # 定义覆盖关系 a_ij：如果在区域j建店能覆盖区域i，则a_ij=1
        # 基于问题描述的表格数据
        coverage = {
            'A': ['A', 'C', 'E', 'G', 'H', 'I'],
            'B': ['B', 'H', 'I'],
            'C': ['A', 'C', 'G', 'H', 'I'],
            'D': ['D', 'J'],
            'E': ['A', 'E', 'G'],
            'F': ['F', 'J', 'K'],
            'G': ['A', 'C', 'E', 'G'],
            'H': ['A', 'B', 'C', 'H', 'I'],
            'I': ['A', 'B', 'C', 'H', 'I'],
            'J': ['D', 'F', 'J', 'K', 'L'],
            'K': ['F', 'J', 'K', 'L'],
            'L': ['J', 'K', 'L']
        }
        
        # 4. 添加决策变量
        # x_j: 是否在区域j建立连锁店 (1表示建立，0表示不建立)
        x = model.addVars(areas, vtype=COPT.BINARY, nameprefix="x")
        
        # 5. 添加约束条件
        # 全覆盖约束：每个居民区都必须被至少一个连锁店覆盖
        for i in areas:
            # 对于每个居民区i，找到所有能够覆盖它的潜在店址
            covering_stores = []
            for j in areas:
                if i in coverage[j]:  # 如果在j建店能覆盖区域i
                    covering_stores.append(x[j])
            
            # 添加约束：至少有一个覆盖区域i的店铺被建立
            if covering_stores:
                model.addConstr(cp.quicksum(covering_stores) >= 1, name=f"coverage_{i}")
        
        # 6. 设置目标函数
        # 最小化建立的连锁店总数
        model.setObjective(cp.quicksum(x[j] for j in areas), sense=COPT.MINIMIZE)
        
        # 7. 求解模型
        print("开始求解集合覆盖问题...")
        model.solve()
        
        # 8. 分析求解结果
        if model.status == COPT.OPTIMAL:
            print("\n=== 求解结果 ===")
            print("模型状态: 最优解 (COPT.OPTIMAL)")
            print(f"最少需要建立的连锁店数量: {int(model.objval)}")
            
            print("\n建立连锁店的最优位置:")
            selected_locations = []
            for j in areas:
                if x[j].x > 0.5:  # 二进制变量大于0.5表示选中
                    selected_locations.append(j)
                    print(f"  - 在居民区 {j} 建立连锁店")
            
            print(f"\n总共需要建立 {len(selected_locations)} 家连锁店")
            
            # 验证覆盖情况
            print("\n=== 覆盖验证 ===")
            all_covered = True
            for i in areas:
                covered = False
                covering_stores = []
                for j in selected_locations:
                    if i in coverage[j]:
                        covered = True
                        covering_stores.append(j)
                
                if covered:
                    print(f"居民区 {i}: 被覆盖 ✓ (覆盖店铺: {', '.join(covering_stores)})")
                else:
                    print(f"居民区 {i}: 未被覆盖 ✗")
                    all_covered = False
            
            if all_covered:
                print("\n✓ 所有居民区都被正确覆盖!")
            else:
                print("\n✗ 存在未被覆盖的居民区!")
            
            # MIP求解统计信息
            print(f"\n=== MIP 求解统计信息 ===")
            print(f"最优界 (Best Bound): {model.getAttr(COPT.Attr.BestBnd):.4f}")
            print(f"最优间隙 (Optimality Gap): {model.getAttr(COPT.Attr.BestGap) * 100:.4f}%")
            print(f"搜索节点数 (Node Count): {model.getAttr(COPT.Attr.NodeCnt)}")
            
            # 返回结果用于写入文件
            return {
                'optimal_value': int(model.objval),
                'selected_locations': selected_locations,
                'all_covered': all_covered
            }
            
        else:
            print(f"\n模型未找到最优解。状态码: {model.status}")
            # 打印模型状态的文字描述
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
        # 确保在程序结束时关闭COPT环境，释放所有相关资源
        if 'env' in locals() and env is not None:
            env.close()

if __name__ == "__main__":
    result = solve_set_covering_problem()
    
    # 将结果写入result.txt文件
    if result:
        with open('result.txt', 'w', encoding='utf-8') as f:
            f.write(f"超市连锁店最优选址问题求解结果\n")
            f.write(f"{'='*50}\n\n")
            f.write(f"最少需要建立的连锁店数量: {result['optimal_value']}\n\n")
            f.write(f"建立连锁店的最优位置:\n")
            for location in result['selected_locations']:
                f.write(f"  - 居民区 {location}\n")
            f.write(f"\n总共需要建立 {len(result['selected_locations'])} 家连锁店\n")
            f.write(f"\n所有居民区是否都被覆盖: {'是' if result['all_covered'] else '否'}\n")
            
        print(f"\n结果已保存到 result.txt 文件中")
    else:
        with open('result.txt', 'w', encoding='utf-8') as f:
            f.write("求解失败，未能找到最优解\n")
        print(f"\n求解失败信息已保存到 result.txt 文件中")