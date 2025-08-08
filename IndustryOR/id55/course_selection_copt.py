import sys
from pathlib import Path

try:
    import coptpy as cp
    from coptpy import COPT
except Exception as import_err:
    # 如果 COPT 未安装，直接将错误写入 result.txt 并退出
    Path("result.txt").write_text(f"ERROR: {import_err}\n", encoding="utf-8")
    sys.exit(1)


def build_and_solve():
    env = None
    try:
        env = cp.Envr()
        model = env.createModel("course_selection")

        # 课程索引与名称映射（按 problem.md 的顺序）
        courses = {
            1: "微积分",
            2: "运筹学",
            3: "数据结构",
            4: "管理统计学",
            5: "计算机仿真",
            6: "计算机程序设计",
            7: "预测学",
        }

        # 决策变量：x_i ∈ {0,1}
        x = {i: model.addVar(vtype=COPT.BINARY, name=f"x_{i}_{courses[i]}") for i in courses}

        # 目标：min sum x_i
        model.setObjective(cp.quicksum(x[i] for i in courses), sense=COPT.MINIMIZE)

        # 类别数量约束
        # 数学类: x1 + x2 + x3 + x4 + x7 >= 2
        model.addConstr(x[1] + x[2] + x[3] + x[4] + x[7] >= 2, name="cat_math")
        # 运筹学类: x2 + x4 + x5 + x7 >= 2
        model.addConstr(x[2] + x[4] + x[5] + x[7] >= 2, name="cat_or")
        # 计算机科学类: x3 + x5 + x6 >= 2
        model.addConstr(x[3] + x[5] + x[6] >= 2, name="cat_cs")

        # 先修课程约束
        # x3 ≤ x6 （数据结构 ← 计算机程序设计）
        model.addConstr(x[3] <= x[6], name="prereq_ds_prog")
        # x5 ≤ x6 （计算机仿真 ← 计算机程序设计）
        model.addConstr(x[5] <= x[6], name="prereq_sim_prog")
        # x4 ≤ x1 （管理统计学 ← 微积分）
        model.addConstr(x[4] <= x[1], name="prereq_stat_calc")
        # x7 ≤ x4 （预测学 ← 管理统计学）
        model.addConstr(x[7] <= x[4], name="prereq_fore_stat")

        # 求解
        model.solve()

        if model.status == COPT.OPTIMAL:
            # 将目标函数最优值（最少课程数）写入 result.txt，仅写数值
            Path("result.txt").write_text(f"{int(round(model.objval))}\n", encoding="utf-8")
            # 同时在控制台打印详细选择，便于调试
            chosen = [f"{i}:{courses[i]}" for i in courses if x[i].x > 0.5]
            print(f"Optimal objective (min number of courses): {model.objval}")
            print("Chosen courses:", ", ".join(chosen))
        else:
            Path("result.txt").write_text(f"no_optimal_solution(status={model.status})\n", encoding="utf-8")
            print(f"Model did not reach OPTIMAL. Status = {model.status}")

    except cp.CoptError as e:
        Path("result.txt").write_text(f"COPT Error: {e.retcode} - {e.message}\n", encoding="utf-8")
        raise
    except Exception as e:
        Path("result.txt").write_text(f"ERROR: {e}\n", encoding="utf-8")
        raise
    finally:
        if env is not None:
            env.close()


if __name__ == "__main__":
    build_and_solve()

