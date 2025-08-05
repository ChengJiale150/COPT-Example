#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证生产规划问题解的合理性
"""

import json

def validate_solution():
    """验证解是否满足所有约束条件"""
    
    # 读取结果
    with open('output/detailed_results.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    print("=== 解的验证 ===")
    print(f"总成本: {results['objective_value']:,.2f} 元")
    
    # 基础参数
    S_orig = 50
    N_target = 50
    K = 3
    
    # 需求数据
    D = {
        ('I', 1): 10000, ('I', 2): 10000, ('I', 3): 12000, ('I', 4): 12000,
        ('I', 5): 16000, ('I', 6): 16000, ('I', 7): 20000, ('I', 8): 20000,
        ('II', 1): 6000, ('II', 2): 7200, ('II', 3): 8400, ('II', 4): 10800,
        ('II', 5): 10800, ('II', 6): 12000, ('II', 7): 12000, ('II', 8): 12000
    }
    
    weekly_results = results['weekly_results']
    
    print("\n=== 约束验证 ===")
    
    # 1. 验证劳动力守恒约束
    print("\n1. 劳动力守恒约束:")
    all_workforce_ok = True
    tolerance = 1e-3  # 允许数值精度误差
    
    for week_str in weekly_results:
        week = int(week_str)
        data = weekly_results[week_str]
        
        # 初始熟练工守恒
        orig_total = (data['orig_workers_regular'] + data['orig_workers_overtime'] + 
                     data['orig_trainers'])
        if week > 1:
            prev_data = weekly_results[str(week-1)]
            orig_total += prev_data['orig_trainers']
        
        if abs(orig_total - S_orig) > tolerance:
            print(f"  ❌ 第{week}周初始熟练工约束不满足: {orig_total:.3f} ≠ {S_orig}")
            all_workforce_ok = False
        
        # 新熟练工守恒
        new_total = (data['new_workers_regular'] + data['new_workers_overtime'] + 
                    data['new_trainers'])
        if week > 1:
            prev_data = weekly_results[str(week-1)]
            new_total += prev_data['new_trainers']
        
        if abs(new_total - data['new_workers_available']) > tolerance:
            print(f"  ❌ 第{week}周新熟练工约束不满足: {new_total:.3f} ≠ {data['new_workers_available']:.3f}")
            all_workforce_ok = False
    
    if all_workforce_ok:
        print("  ✅ 所有劳动力守恒约束都满足")
    
    # 2. 验证劳动力动态演化约束
    print("\n2. 劳动力动态演化约束:")
    dynamics_ok = True
    for week_str in weekly_results:
        week = int(week_str)
        data = weekly_results[week_str]
        
        if week == 1:
            if data['new_workers_available'] != 0:
                print(f"  ❌ 第1周新熟练工可用数量应为0: {data['new_workers_available']}")
                dynamics_ok = False
        elif week == 2:
            prev_data = weekly_results['1']
            if data['new_workers_available'] != prev_data['new_workers_available']:
                print(f"  ❌ 第2周动态演化不正确")
                dynamics_ok = False
        else:
            prev_data = weekly_results[str(week-1)]
            prev_prev_data = weekly_results[str(week-2)]
            expected = prev_data['new_workers_available'] + prev_prev_data['new_trainees_start']
            if abs(data['new_workers_available'] - expected) > 1e-6:
                print(f"  ❌ 第{week}周动态演化不正确: {data['new_workers_available']} ≠ {expected}")
                dynamics_ok = False
    
    if dynamics_ok:
        print("  ✅ 所有劳动力动态演化约束都满足")
    
    # 3. 验证培训约束
    print("\n3. 培训约束:")
    training_ok = True
    total_trainees = 0
    
    for week_str in weekly_results:
        week = int(week_str)
        data = weekly_results[week_str]
        
        # 培训能力约束
        max_trainees = K * (data['orig_trainers'] + data['new_trainers'])
        if data['new_trainees_start'] > max_trainees:
            print(f"  ❌ 第{week}周培训能力不足: {data['new_trainees_start']} > {max_trainees}")
            training_ok = False
        
        if week <= 7:  # 最晚第7周开始培训
            total_trainees += data['new_trainees_start']
    
    if total_trainees != N_target:
        print(f"  ❌ 总培训目标不满足: {total_trainees} ≠ {N_target}")
        training_ok = False
    
    if training_ok:
        print(f"  ✅ 培训约束满足，总共培训{total_trainees}名新工人")
    
    # 4. 验证生产能力约束
    print("\n4. 生产能力约束:")
    capacity_ok = True
    R = {'I': 0.1, 'II': 1/6}
    H_reg, H_ot = 40, 60
    
    for week_str in weekly_results:
        week = int(week_str)
        data = weekly_results[week_str]
        
        # 计算所需工时
        required_hours = (R['I'] * data['production_I'] + 
                         R['II'] * data['production_II'])
        
        # 计算可用工时
        available_hours = (H_reg * (data['orig_workers_regular'] + data['new_workers_regular']) +
                          H_ot * (data['orig_workers_overtime'] + data['new_workers_overtime']))
        
        if required_hours > available_hours + tolerance:  # 允许数值精度误差
            print(f"  ❌ 第{week}周生产能力不足: 需要{required_hours:.1f}小时 > 可用{available_hours:.1f}小时")
            capacity_ok = False
    
    if capacity_ok:
        print("  ✅ 所有生产能力约束都满足")
    
    # 5. 验证积压平衡约束
    print("\n5. 积压平衡约束:")
    backlog_ok = True
    
    for p in ['I', 'II']:
        prev_backlog = 0
        for week_str in weekly_results:
            week = int(week_str)
            data = weekly_results[week_str]
            
            # 计算期望积压
            demand_key = f"production_{p}"
            backlog_key = f"backlog_{p}"
            
            expected_backlog = prev_backlog + D[(p, week)] - data[demand_key.replace('production_', 'production_')]
            
            if abs(data[backlog_key] - expected_backlog) > 1e-6:
                print(f"  ❌ 第{week}周产品{p}积压计算错误: {data[backlog_key]} ≠ {expected_backlog}")
                backlog_ok = False
            
            prev_backlog = data[backlog_key]
    
    if backlog_ok:
        print("  ✅ 所有积压平衡约束都满足")
    
    # 6. 总结最终积压
    print("\n=== 最终积压情况 ===")
    final_week = weekly_results['8']
    print(f"食品I最终积压: {final_week['backlog_I']:.1f} 公斤")
    print(f"食品II最终积压: {final_week['backlog_II']:.1f} 公斤")
    
    # 7. 成本分析
    print("\n=== 成本分析 ===")
    penalty_cost = 0.5 * final_week['backlog_I'] + 0.6 * final_week['backlog_II']
    print(f"最终罚款成本: {penalty_cost:,.2f} 元")
    print(f"工资成本(估算): {results['objective_value'] - penalty_cost:,.2f} 元")
    
    return True

if __name__ == "__main__":
    validate_solution()