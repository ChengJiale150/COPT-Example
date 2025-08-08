import sys

import coptpy as cp
from coptpy import COPT


def build_and_solve_model() -> float:
    env = None
    try:
        env = cp.Envr()
        model = env.createModel("product_mix")

        # Decision variables
        # x_M: Meaties packs (bounded by machine capacity)
        # x_Y: Yummies packs
        x_M = model.addVar(lb=0.0, ub=90000.0, name="x_M")
        x_Y = model.addVar(lb=0.0, name="x_Y")

        # Resource constraints
        # Grains: 2.0 * x_M + 3.0 * x_Y <= 400000
        model.addConstr(2.0 * x_M + 3.0 * x_Y <= 400000.0, name="grains")

        # Meat: 3.0 * x_M + 1.5 * x_Y <= 300000
        model.addConstr(3.0 * x_M + 1.5 * x_Y <= 300000.0, name="meat")

        # Objective: maximize profit = 0.65 * x_M + 0.45 * x_Y
        model.setObjective(0.65 * x_M + 0.45 * x_Y, sense=COPT.MAXIMIZE)

        model.solve()

        if model.status != COPT.OPTIMAL:
            raise RuntimeError(f"Model did not solve to optimality. Status: {model.status}")

        # Export artifacts
        try:
            model.write("product_mix.lp")
            model.write("product_mix.sol")
        except Exception:
            # Export is optional; continue if writing fails (e.g., due to permissions)
            pass

        # Write objective value to result.txt (no extra text)
        with open("result.txt", "w", encoding="utf-8") as f:
            f.write(f"{model.objval}\n")

        # Also print a concise summary to stdout for interactive runs
        print(f"Objective: {model.objval}")
        for var in model.getVars():
            print(f"{var.name} = {var.x}")

        return model.objval

    finally:
        if env is not None:
            env.close()


if __name__ == "__main__":
    try:
        build_and_solve_model()
    except cp.CoptError as e:
        print(f"COPT Error: {e.retcode} - {e.message}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

