import sys
from typing import List, Tuple

import coptpy as cp
from coptpy import COPT


def solve_parking_minimax(lengths: List[float], cap_per_side: float | None = None) -> Tuple[float, List[int]]:
    """
    Solve the two-side parking minimax problem:
    - Minimize L subject to each car assigned to exactly one side, and
      sum(lengths on side j) <= L for j in {0,1}.
    - Optionally enforce per-side capacity: sum(lengths on side j) <= cap_per_side.

    Returns a tuple: (optimal_L, assignment), where assignment[i] in {0,1} is the chosen side for car i.
    Raises a RuntimeError if the model is infeasible or not solved to optimality.
    """
    num_cars = len(lengths)

    env = None
    try:
        env = cp.Envr()
        model = env.createModel("parking_load_balance")

        # Decision variables: x[i, j] in {0,1}
        x = model.addVars(num_cars, 2, vtype=COPT.BINARY, nameprefix="x")
        # Objective variable: L >= 0
        L = model.addVar(lb=0.0, name="L")

        # Each car assigned to exactly one side
        for i in range(num_cars):
            model.addConstr(x.sum(i, '*') == 1.0, name=f"assign_{i}")

        # L bounds each side's total length
        for j in range(2):
            model.addConstr(cp.quicksum(lengths[i] * x[i, j] for i in range(num_cars)) <= L, name=f"max_side_{j}")

        # Optional symmetry breaking: fix car 0 to side 0 (accelerates solving, does not change optimal value)
        model.addConstr(x[0, 0] == 1.0, name="symmetry_break_car0_side0")

        # Optional side capacity
        if cap_per_side is not None:
            for j in range(2):
                model.addConstr(
                    cp.quicksum(lengths[i] * x[i, j] for i in range(num_cars)) <= cap_per_side,
                    name=f"cap_side_{j}"
                )

        # Objective: minimize L
        model.setObjective(L, sense=COPT.MINIMIZE)

        model.solve()

        if model.status != COPT.OPTIMAL:
            status_map = {
                COPT.INFEASIBLE: "infeasible",
                COPT.UNBOUNDED: "unbounded",
                COPT.TIMEOUT: "timeout",
                COPT.INTERRUPTED: "interrupted",
            }
            raise RuntimeError(f"Model not optimal (status {model.status}: {status_map.get(model.status, 'unknown')})")

        # Extract assignment based on x values
        assignment: List[int] = []
        for i in range(num_cars):
            side1 = x[i, 1].x
            side0 = x[i, 0].x
            chosen = 1 if side1 > side0 else 0
            assignment.append(chosen)

        return model.objval, assignment

    except cp.CoptError as e:
        raise RuntimeError(f"COPT Error: {e.retcode} - {e.message}") from e
    finally:
        if env is not None:
            env.close()


def main() -> int:
    # Problem data from problem.md
    lengths = [
        4.0, 4.5, 5.0, 4.1, 2.4,
        5.2, 3.7, 3.5, 3.2, 4.5,
        2.3, 3.3, 3.8, 4.6, 3.0,
    ]

    # Base model (no side capacity)
    base_failed_msg = None
    try:
        base_obj, base_assign = solve_parking_minimax(lengths, cap_per_side=None)
    except RuntimeError as e:
        base_obj = float("nan")
        base_assign = []
        base_failed_msg = f"FAILED: {e}"

    # Model with 30m per-side capacity
    try:
        cap30_obj, cap30_assign = solve_parking_minimax(lengths, cap_per_side=30.0)
        cap30_status = "OPTIMAL"
    except RuntimeError as e:
        cap30_obj = float("nan")
        cap30_assign = []
        cap30_status = f"FAILED: {e}"

    # Write results
    result_lines = [
        "Two-Side Parking Minimax Results",
    ]

    if base_assign:
        side0_len_base = sum(lengths[i] for i, s in enumerate(base_assign) if s == 0)
        side1_len_base = sum(lengths[i] for i, s in enumerate(base_assign) if s == 1)
        result_lines.append(f"Base model objective L*: {base_obj:.4f}")
        result_lines.append(f"  Side lengths (base) => side0: {side0_len_base:.4f}, side1: {side1_len_base:.4f}")
    else:
        result_lines.append(f"Base model status: {base_failed_msg if base_failed_msg else 'UNKNOWN FAILURE'}")

    result_lines.append(f"Capacity-30 model status: {cap30_status}")

    if cap30_assign:
        side0_len_cap = sum(lengths[i] for i, s in enumerate(cap30_assign) if s == 0)
        side1_len_cap = sum(lengths[i] for i, s in enumerate(cap30_assign) if s == 1)
        result_lines.append(f"Capacity-30 model objective L*: {cap30_obj:.4f}")
        result_lines.append(f"  Side lengths (cap30) => side0: {side0_len_cap:.4f}, side1: {side1_len_cap:.4f}")

    # Persist final objective(s) to result.txt (as requested)
    # Include both base and cap-30, if available, for completeness.
    with open("result.txt", "w", encoding="utf-8") as f:
        for line in result_lines:
            f.write(line + "\n")

    # Also print to stdout
    print("\n".join(result_lines))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

