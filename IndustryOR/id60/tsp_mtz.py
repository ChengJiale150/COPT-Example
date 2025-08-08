import os
import coptpy as cp
from coptpy import COPT


def build_symmetric_distance_matrix() -> list[list[int]]:
    # Upper triangular distances from problem.md (1-based nodes 1..7)
    # Row-wise upper triangle (excluding diagonal):
    # 1: to 2..7
    r1 = [86, 49, 57, 31, 69, 50]
    # 2: to 3..7
    r2 = [68, 79, 93, 24, 5]
    # 3: to 4..7
    r3 = [16, 7, 72, 67]
    # 4: to 5..7
    r4 = [90, 69, 1]
    # 5: to 6..7
    r5 = [86, 59]
    # 6: to 7
    r6 = [81]

    n = 7
    # Initialize full matrix with zeros
    c = [[0 for _ in range(n)] for _ in range(n)]

    # Fill upper triangle
    uppers = [r1, r2, r3, r4, r5, r6]
    for i in range(n - 1):  # i = 0..5 corresponds to node i+1
        values = uppers[i]
        for k, val in enumerate(values, start=i + 1):  # k = i+1..n-1 corresponds to node k+1
            c[i][k] = val

    # Mirror to lower triangle and set diagonal to a large number
    big_m = 10**6
    for i in range(n):
        for j in range(n):
            if i == j:
                c[i][j] = big_m
            elif c[i][j] == 0 and c[j][i] != 0:
                c[i][j] = c[j][i]

    return c


def solve_tsp_mtz():
    env = None
    try:
        env = cp.Envr()
        model = env.createModel("tsp_mtz_7nodes")

        # Sets
        n = 7
        V = list(range(1, n + 1))
        V_prime = list(range(2, n + 1))  # exclude depot 1

        # Parameters: distance matrix c[i][j] using 1-based node ids
        c_mat = build_symmetric_distance_matrix()

        # Decision variables
        arcs = [(i, j) for i in V for j in V if i != j]
        x = model.addVars(arcs, vtype=COPT.BINARY, nameprefix="x")
        # MTZ order variables for nodes 2..n
        u = model.addVars(V_prime, lb=2.0, ub=float(n), nameprefix="u")

        # Objective: minimize total distance
        obj = cp.quicksum(c_mat[i - 1][j - 1] * x[i, j] for i, j in arcs)
        model.setObjective(obj, sense=COPT.MINIMIZE)

        # Degree constraints
        for i in V:
            model.addConstr(cp.quicksum(x[i, j] for j in V if j != i) == 1, name=f"depart_{i}")
        for j in V:
            model.addConstr(cp.quicksum(x[i, j] for i in V if i != j) == 1, name=f"arrive_{j}")

        # MTZ subtour elimination: for i,j in V' and i!=j
        for i in V_prime:
            for j in V_prime:
                if i == j:
                    continue
                model.addConstr(u[i] - u[j] + n * x[i, j] <= n - 1, name=f"mtz_{i}_{j}")

        # Solve
        model.solve()

        # Output objective to result.txt
        workspace_dir = "/Users/jiale.cheng/Documents/mcp/test"
        result_path = os.path.join(workspace_dir, "result.txt")

        if model.status == COPT.OPTIMAL:
            obj_val = model.objval
            with open(result_path, "w", encoding="utf-8") as f:
                f.write(f"objective_value={obj_val:.6f}\n")
            # Optional: also print a brief route summary to stdout
            print(f"Optimal objective: {obj_val:.6f}")
        else:
            with open(result_path, "w", encoding="utf-8") as f:
                f.write(f"solve_status={model.status}\n")
            print(f"Model did not reach optimality. Status: {model.status}")

        # Optionally write solution files
        model.write("tsp_mtz_7nodes.lp")
        model.write("tsp_mtz_7nodes.sol")

    except cp.CoptError as e:
        # Ensure errors are propagated to result.txt for visibility
        workspace_dir = "/Users/jiale.cheng/Documents/mcp/test"
        result_path = os.path.join(workspace_dir, "result.txt")
        with open(result_path, "w", encoding="utf-8") as f:
            f.write(f"COPT Error: {e.retcode} - {e.message}\n")
        raise
    finally:
        if env is not None:
            env.close()


if __name__ == "__main__":
    solve_tsp_mtz()

