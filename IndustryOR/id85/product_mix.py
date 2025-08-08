import coptpy as cp
from coptpy import COPT


def main() -> None:
    env = None
    try:
        # Create environment and model
        env = cp.Envr()
        model = env.createModel("product_mix_ilp")

        # Parameters (units in minutes and £/minute)
        revenue_X = 20.0
        revenue_Y = 30.0

        machine_time_X = 13.0
        machine_time_Y = 19.0
        craftsman_time_X = 20.0
        craftsman_time_Y = 29.0

        available_machine = 40.0 * 60.0  # 2400 minutes
        available_craftsman = 35.0 * 60.0  # 2100 minutes

        machine_cost_per_min = 10.0 / 60.0  # £/min
        craftsman_cost_per_min = 2.0 / 60.0  # £/min

        min_demand_X = 10

        # Decision variables (nonnegative integers)
        x_X = model.addVar(vtype=COPT.INTEGER, lb=0.0, name="x_X")
        x_Y = model.addVar(vtype=COPT.INTEGER, lb=0.0, name="x_Y")

        # Constraints
        model.addConstr(machine_time_X * x_X + machine_time_Y * x_Y <= available_machine, name="machine_time")
        model.addConstr(craftsman_time_X * x_X + craftsman_time_Y * x_Y <= available_craftsman, name="craftsman_time")
        model.addConstr(x_X >= min_demand_X, name="contract_X_min")

        # Objective: maximize profit = revenue - resource costs
        revenue_expr = revenue_X * x_X + revenue_Y * x_Y
        cost_expr = (
            (machine_time_X * x_X + machine_time_Y * x_Y) * machine_cost_per_min
            + (craftsman_time_X * x_X + craftsman_time_Y * x_Y) * craftsman_cost_per_min
        )
        model.setObjective(revenue_expr - cost_expr, sense=COPT.MAXIMIZE)

        # Solve
        model.solve()

        # Write result
        if model.status == COPT.OPTIMAL:
            with open("result.txt", "w", encoding="utf-8") as f:
                f.write(f"{model.objval:.6f}\n")

            # Optional: print solution details
            print("Optimal objective:", model.objval)
            for var in model.getVars():
                print(f"{var.name} = {var.x}")
        else:
            raise RuntimeError(f"Model not optimal. Status: {model.status}")

    except cp.CoptError as e:
        raise RuntimeError(f"COPT Error: {e.retcode} - {e.message}") from e
    finally:
        if env is not None:
            env.close()


if __name__ == "__main__":
    main()

