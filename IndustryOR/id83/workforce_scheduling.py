import sys
from typing import List

try:
    import coptpy as cp
    from coptpy import COPT
except Exception as import_error:
    print(f"Failed to import COPT Python API: {import_error}")
    sys.exit(1)


def solve_cyclic_staffing(demands: List[int]) -> float:
    env = None
    try:
        env = cp.Envr()
        model = env.createModel("cyclic_staffing_ilp")

        num_periods = len(demands)

        # Decision variables: x_t >= 0, integer
        x = model.addVars(num_periods, vtype=COPT.INTEGER, lb=0.0, nameprefix="x")

        # Coverage constraints: x_{t-1} + x_t >= D_t (with wrap-around)
        for t in range(num_periods):
            prev_t = (t - 1) % num_periods
            model.addConstr(x[prev_t] + x[t] >= demands[t], name=f"demand_t{t+1}")

        # Objective: minimize total number of waiters
        model.setObjective(cp.quicksum(x[t] for t in range(num_periods)), sense=COPT.MINIMIZE)

        model.solve()

        if model.status != COPT.OPTIMAL:
            raise RuntimeError(f"Optimization did not reach OPTIMAL status, status code: {model.status}")

        # Write artifacts (optional for inspection)
        try:
            model.write("workforce_scheduling.lp")
            model.write("workforce_scheduling.sol")
        except Exception:
            # Writing artifacts is optional; ignore failures here
            pass

        return model.objval
    finally:
        if env is not None:
            env.close()


def main() -> None:
    # Data as per problem.md (Table 1.1): [4, 8, 10, 7, 12, 4]
    demands = [4, 8, 10, 7, 12, 4]
    try:
        obj_value = solve_cyclic_staffing(demands)
    except cp.CoptError as e:
        print(f"COPT Error: {e.retcode} - {e.message}")
        sys.exit(2)
    except Exception as e:
        print(f"Solve error: {e}")
        sys.exit(3)

    # Persist the optimal objective value to result.txt (integer formatting for ILP)
    try:
        with open("result.txt", "w", encoding="utf-8") as f:
            f.write(f"{int(round(obj_value))}\n")
    except Exception as e:
        print(f"Failed to write result.txt: {e}")
        sys.exit(4)

    # Also print to stdout for convenience
    print(f"Optimal total number of waiters: {int(round(obj_value))}")


if __name__ == "__main__":
    main()

