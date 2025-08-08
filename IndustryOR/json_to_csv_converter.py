#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON to CSV Converter for IndustryOR.json
将IndustryOR.json文件转换为CSV格式
"""

import json
import csv
import sys
import os
from typing import List, Dict, Any


def read_json_file(file_path: str) -> List[Dict[str, Any]]:
    """
    读取JSON文件并返回数据列表
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        包含所有JSON对象的列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # 由于文件包含多个JSON对象（每行一个），需要逐行读取
            data = []
            for line in file:
                line = line.strip()
                if line:  # 跳过空行
                    try:
                        json_obj = json.loads(line)
                        data.append(json_obj)
                    except json.JSONDecodeError as e:
                        print(f"警告: 跳过无效的JSON行: {e}")
                        continue
            return data
    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 不存在")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 读取文件时发生错误: {e}")
        sys.exit(1)


def write_csv_file(data: List[Dict[str, Any]], output_file: str) -> None:
    """
    将数据写入CSV文件
    
    Args:
        data: 要写入的数据列表
        output_file: 输出CSV文件路径
    """
    try:
        # 获取所有字段名
        if not data:
            print("警告: 没有数据可写入")
            return
            
        fieldnames = list(data[0].keys())
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # 写入表头
            writer.writeheader()
            
            # 写入数据
            for row in data:
                writer.writerow(row)
                
        print(f"成功: 已将 {len(data)} 条记录写入 '{output_file}'")
        
    except Exception as e:
        print(f"错误: 写入CSV文件时发生错误: {e}")
        sys.exit(1)


def main():
    """
    主函数
    """
    # 输入和输出文件路径
    input_file = "IndustryOR.json"
    output_file = "IndustryOR.csv"
    
    print("开始转换 JSON 到 CSV...")
    print(f"输入文件: {input_file}")
    print(f"输出文件: {output_file}")
    print("-" * 50)
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误: 输入文件 '{input_file}' 不存在")
        sys.exit(1)
    
    # 读取JSON数据
    print("正在读取JSON文件...")
    data = read_json_file(input_file)
    print(f"成功读取 {len(data)} 条记录")
    
    # 显示数据结构信息
    if data:
        print(f"数据字段: {list(data[0].keys())}")
        print(f"示例数据:")
        for i, record in enumerate(data[:3]):  # 显示前3条记录
            print(f"  记录 {i+1}: ID={record.get('id', 'N/A')}, "
                  f"难度={record.get('difficulty', 'N/A')}")
    
    # 写入CSV文件
    print("\n正在写入CSV文件...")
    write_csv_file(data, output_file)
    
    print("\n转换完成!")
    print(f"CSV文件已保存为: {output_file}")


if __name__ == "__main__":
    main()
