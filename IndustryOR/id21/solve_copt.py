import os
import coptpy as cp
from coptpy import COPT


def main() -> None:
    # Absolute path for result output
    workspace_root = "/Users/jiale.cheng/Documents/mcp/test"
    result_path = os.path.join(workspace_root, "result.txt")

    # Problem data (from problem.md)
    batch_size_A = 20
    batch_size_B = 15
    batch_size_C = 15

    batch_cost_A = 120 * batch_size_A  # 2400
    batch_cost_B = 110 * batch_size_B  # 1650
    batch_cost_C = 100 * batch_size_C  # 1500

    total_min = 150
    total_max = 600

    # Big-M valid upper bounds inferred from total_max
    # 20 x_A <= 600 -> x_A <= 30
    # 15 x_B <= 600 -> x_B <= 40
    M_A = 30
    M_B = 40

    try:
        env = cp.Envr()
        model = env.createModel("restaurant_tables_mip")

        # Decision variables
        xA = model.addVar(vtype=COPT.INTEGER, name="xA")  # batches from A
        xB = model.addVar(vtype=COPT.INTEGER, name="xB")  # batches from B
        xC = model.addVar(vtype=COPT.INTEGER, name="xC")  # batches from C
        yA = model.addVar(vtype=COPT.BINARY, name="yA")   # whether A used
        yB = model.addVar(vtype=COPT.BINARY, name="yB")   # whether B used

        # Quantity bounds
        model.addConstr(
            batch_size_A * xA + batch_size_B * xB + batch_size_C * xC >= total_min,
            name="min_total",
        )
        model.addConstr(
            batch_size_A * xA + batch_size_B * xB + batch_size_C * xC <= total_max,
            name="max_total",
        )

        # Logical constraints via Big-M
        # If xA > 0 then yA = 1, and require xB >= 2
        model.addConstr(xA <= M_A * yA, name="link_A")
        model.addConstr(xB >= 2 * yA, name="A_implies_B_min30")

        # If xB > 0 then yB = 1, and require xC >= 1
        model.addConstr(xB <= M_B * yB, name="link_B")
        model.addConstr(xC >= 1 * yB, name="B_implies_C")

        # Objective: minimize total cost
        model.setObjective(
            batch_cost_A * xA + batch_cost_B * xB + batch_cost_C * xC,
            sense=COPT.MINIMIZE,
        )

        model.solve()

        # Write objective value to result.txt
        with open(result_path, "w", encoding="utf-8") as f:
            if model.status == COPT.OPTIMAL:
                f.write(f"{model.objval:.6f}")
            else:
                # Fallback: write status for visibility
                f.write(f"STATUS_{model.status}")

    except cp.CoptError as e:
        with open(result_path, "w", encoding="utf-8") as f:
            f.write(f"COPT_ERROR_{e.retcode}")
    except Exception as e:
        with open(result_path, "w", encoding="utf-8") as f:
            f.write(f"ERROR_{type(e).__name__}")
    finally:
        try:
            if 'env' in locals() and env is not None:
                env.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()

