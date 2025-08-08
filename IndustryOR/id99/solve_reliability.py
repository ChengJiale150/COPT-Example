import math
from typing import Dict, List, Tuple

import coptpy as cp
from coptpy import COPT


def build_and_solve_model() -> Tuple[float, float, Dict[int, int]]:
    """
    Build and solve the reliability maximization model using COPT.

    Returns:
        log_objective_value: Optimal value of the transformed objective (sum of logs)
        product_reliability_value: Optimal value of the original objective (product of reliabilities)
        chosen_spares_per_component: Mapping component -> chosen number of spares j
    """
    # Sets I (components) and J (number of spares)
    components: List[int] = [1, 2, 3]
    spares: List[int] = [0, 1, 2, 3, 4, 5]

    # Parameters: reliability R[i][j], unit price c[i], unit weight w[i]
    reliability: Dict[Tuple[int, int], float] = {
        (1, 0): 0.5,
        (1, 1): 0.6,
        (1, 2): 0.7,
        (1, 3): 0.8,
        (1, 4): 0.9,
        (1, 5): 1.0,
        (2, 0): 0.6,
        (2, 1): 0.75,
        (2, 2): 0.95,
        (2, 3): 1.0,
        (2, 4): 1.0,
        (2, 5): 1.0,
        (3, 0): 0.7,
        (3, 1): 0.9,
        (3, 2): 1.0,
        (3, 3): 1.0,
        (3, 4): 1.0,
        (3, 5): 1.0,
    }
    unit_price: Dict[int, float] = {1: 20.0, 2: 30.0, 3: 40.0}
    unit_weight: Dict[int, float] = {1: 2.0, 2: 4.0, 3: 6.0}
    budget_max: float = 150.0
    weight_max: float = 20.0

    # Validate inputs
    for i in components:
        for j in spares:
            rij = reliability[i, j]
            if rij <= 0.0:
                raise ValueError(f"Reliability must be positive for log transform, got R[{i},{j}]={rij}")

    env = cp.Envr()
    try:
        model = env.createModel("reliability_maximization")

        # Decision variables: x[i,j] in {0,1}
        x = model.addVars(components, spares, vtype=COPT.BINARY, nameprefix="x")

        # Objective: maximize sum_{i,j} log(R[i,j]) * x[i,j]
        objective_expr = cp.quicksum(math.log(reliability[i, j]) * x[i, j] for i in components for j in spares)
        model.setObjective(objective_expr, sense=COPT.MAXIMIZE)

        # Unique choice per component: sum_j x[i,j] == 1
        model.addConstrs((cp.quicksum(x[i, j] for j in spares) == 1 for i in components), nameprefix="unique_choice")

        # Budget constraint: sum_{i,j} (c_i * j) * x[i,j] <= budget_max
        budget_expr = cp.quicksum(unit_price[i] * j * x[i, j] for i in components for j in spares)
        model.addConstr(budget_expr <= budget_max, name="budget")

        # Weight constraint: sum_{i,j} (w_i * j) * x[i,j] <= weight_max
        weight_expr = cp.quicksum(unit_weight[i] * j * x[i, j] for i in components for j in spares)
        model.addConstr(weight_expr <= weight_max, name="weight")

        # Optional: limit time for robustness
        model.setParam(COPT.Param.TimeLimit, 30.0)

        model.solve()

        if model.status != COPT.OPTIMAL:
            raise RuntimeError(f"Model did not reach optimality. Status: {model.status}")

        # Extract decisions
        chosen_spares: Dict[int, int] = {}
        for i in components:
            best_j = max(spares, key=lambda j: x[i, j].x)
            chosen_spares[i] = best_j

        log_obj = model.objval
        product_val = math.exp(log_obj)

        return log_obj, product_val, chosen_spares
    finally:
        env.close()


def main() -> None:
    log_sum_value, product_value, chosen = build_and_solve_model()

    # Print a concise summary to stdout
    print("Optimization successful.")
    print(f"Sum of logs objective: {log_sum_value:.10f}")
    print(f"System reliability (product): {product_value:.10f}")
    print("Chosen spares per component (component -> j):")
    for comp in sorted(chosen.keys()):
        print(f"  {comp} -> {chosen[comp]}")

    # Write the final objective value (original product reliability) into result.txt
    with open("result.txt", "w", encoding="utf-8") as f:
        f.write(f"{product_value:.10f}\n")


if __name__ == "__main__":
    main()

