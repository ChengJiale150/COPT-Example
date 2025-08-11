import coptpy as cp
from coptpy import COPT


def main() -> None:
    # Problem data
    toy_names = ["robot", "model_car", "blocks", "doll"]
    profits = [15, 8, 12, 5]
    plastic_use = [30, 10, 20, 15]
    elec_use = [8, 5, 3, 2]
    plastic_capacity = 1200
    elec_capacity = 800

    num_types = len(toy_names)

    # Compute tight big-M values as per description
    max_by_plastic = [plastic_capacity // plastic_use[i] for i in range(num_types)]
    max_by_elec = [elec_capacity // elec_use[i] for i in range(num_types)]
    big_m = [min(max_by_plastic[i], max_by_elec[i]) for i in range(num_types)]

    env = None
    try:
        env = cp.Envr()
        model = env.createModel("bright_future_toys_mip")

        # Decision variables
        x = model.addVars(num_types, vtype=COPT.INTEGER, lb=0, nameprefix="x")  # production quantities
        y = model.addVars(num_types, vtype=COPT.BINARY, nameprefix="y")          # production decisions

        # Resource constraints
        model.addConstr(cp.quicksum(plastic_use[i] * x[i] for i in range(num_types)) <= plastic_capacity,
                        name="plastic_capacity")
        model.addConstr(cp.quicksum(elec_use[i] * x[i] for i in range(num_types)) <= elec_capacity,
                        name="elec_capacity")

        # Logical constraints
        # If robots are produced, dolls are not: y1 + y4 <= 1  (indices 0 and 3)
        model.addConstr(y[0] + y[3] <= 1, name="robot_vs_doll")

        # If model cars are produced, blocks must be produced: y2 <= y3 (indices 1 and 2)
        model.addConstr(y[1] <= y[2], name="model_car_implies_blocks")

        # Dolls produced cannot exceed model cars produced: x4 <= x2 (indices 3 <= 1)
        model.addConstr(x[3] <= x[1], name="doll_leq_model_car")

        # Linking constraints: ensure x_i is positive only if y_i = 1, and bounded by Big-M
        for i in range(num_types):
            model.addConstr(x[i] <= big_m[i] * y[i], name=f"link_ub_{i}")
            model.addConstr(x[i] >= y[i], name=f"link_lb_{i}")

        # Objective: maximize total profit
        model.setObjective(cp.quicksum(profits[i] * x[i] for i in range(num_types)), sense=COPT.MAXIMIZE)

        # Solve
        model.solve()

        # Write objective value to result.txt
        result_path = "result.txt"
        if model.status == COPT.OPTIMAL:
            with open(result_path, "w", encoding="utf-8") as f:
                f.write(f"{model.objval:.6f}\n")
        else:
            with open(result_path, "w", encoding="utf-8") as f:
                f.write(f"Solve status {model.status}, no optimal solution.\n")

    except cp.CoptError as e:
        # On COPT errors, write message to result.txt for visibility
        with open("result.txt", "w", encoding="utf-8") as f:
            f.write(f"COPT Error: {e.retcode} - {e.message}\n")
    except Exception as e:
        with open("result.txt", "w", encoding="utf-8") as f:
            f.write(f"Unexpected Error: {e}\n")
    finally:
        if env is not None:
            env.close()


if __name__ == "__main__":
    main()

