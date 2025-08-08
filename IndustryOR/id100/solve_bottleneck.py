import coptpy as cp
from coptpy import COPT


def build_and_solve_max_bottleneck_path(env: cp.Envr, nodes: list[str], capacities: dict[tuple[str, str], float], start_node: str, end_node: str, allowed_nodes: list[str]):
    model = env.createModel(f"bottleneck_{start_node}_to_{end_node}")

    # Allowed arcs: directed arcs with positive capacity whose endpoints lie in allowed nodes
    allowed_arcs: list[tuple[str, str]] = [
        (i, j)
        for (i, j), cap in capacities.items()
        if cap > 0 and i in allowed_nodes and j in allowed_nodes and i != j
    ]

    # Decision variables
    x = model.addVars(allowed_arcs, vtype=COPT.BINARY, nameprefix="x")
    b = model.addVar(lb=0.0, name="bottleneck")

    # Objective: maximize bottleneck b
    model.setObjective(b, sense=COPT.MAXIMIZE)

    # Big-M constraints linking b to selected arcs
    max_capacity = max(capacities.values()) if capacities else 0.0
    for i, j in allowed_arcs:
        model.addConstr(b <= capacities[(i, j)] + max_capacity * (1 - x[i, j]), name=f"bdef_{i}_{j}")

    # Flow constraints
    for k in allowed_nodes:
        if k == start_node:
            model.addConstr(x.sum(start_node, '*') - x.sum('*', start_node) == 1, name=f"flow_start_{start_node}")
        elif k == end_node:
            model.addConstr(x.sum('*', end_node) - x.sum(end_node, '*') == 1, name=f"flow_end_{end_node}")
        else:
            model.addConstr(x.sum(k, '*') - x.sum('*', k) == 0, name=f"flow_{k}")

    # In-degree constraints (each node at most entered once, except the start node)
    for k in allowed_nodes:
        if k != start_node:
            model.addConstr(x.sum('*', k) <= 1, name=f"indeg_le1_{k}")

    # MTZ subtour elimination variables for all nodes except the start
    non_start_nodes = [k for k in allowed_nodes if k != start_node]
    if len(non_start_nodes) > 0:
        u = model.addVars(non_start_nodes, lb=1.0, ub=len(allowed_nodes) - 1, nameprefix="u")
        # MTZ constraints only apply on arcs whose endpoints are not the start node
        for i, j in allowed_arcs:
            if i != start_node and j != start_node and i != j:
                model.addConstr(u[i] - u[j] + 1 <= (len(allowed_nodes) - 1) * (1 - x[i, j]), name=f"mtz_{i}_{j}")

    # Solve
    model.solve()

    if model.status != COPT.OPTIMAL:
        raise RuntimeError(f"Model {model.name} not optimal. Status: {model.status}")

    # Extract selected arcs and visited nodes
    selected_arcs: list[tuple[str, str]] = [(i, j) for (i, j) in allowed_arcs if x[i, j].x > 0.5]
    visited_nodes: set[str] = {start_node, end_node}
    for i, j in selected_arcs:
        visited_nodes.add(i)
        visited_nodes.add(j)

    return b.x, selected_arcs, visited_nodes


def main():
    # Problem data per problem.md
    nodes = ['A', 'B', 'C', 'D', 'E']
    capacities: dict[tuple[str, str], float] = {}

    # Fill capacities from the table (only positive entries)
    data = {
        ('A', 'B'): 90, ('A', 'C'): 85, ('A', 'E'): 65,
        ('B', 'A'): 95, ('B', 'C'): 70, ('B', 'D'): 65, ('B', 'E'): 34,
        ('C', 'A'): 60, ('C', 'D'): 88, ('C', 'E'): 80,
        ('D', 'A'): 67, ('D', 'B'): 30, ('D', 'C'): 25, ('D', 'E'): 84,
        ('E', 'B'): 51, ('E', 'D'): 56,
    }
    capacities.update(data)

    result_value: float = -1.0

    env: cp.Envr | None = None
    try:
        env = cp.Envr()

        # Stage 1: A -> C
        b_ac, arcs_ac, nodes_ac = build_and_solve_max_bottleneck_path(
            env=env,
            nodes=nodes,
            capacities=capacities,
            start_node='A',
            end_node='C',
            allowed_nodes=nodes,
        )

        # Stage 2: C -> E, excluding intermediate nodes used in stage 1 (except A and C)
        intermediate_nodes_stage1 = set(nodes_ac) - {'A', 'C'}
        allowed_nodes_stage2 = [n for n in nodes if n not in intermediate_nodes_stage1]

        b_ce, arcs_ce, nodes_ce = build_and_solve_max_bottleneck_path(
            env=env,
            nodes=nodes,
            capacities=capacities,
            start_node='C',
            end_node='E',
            allowed_nodes=allowed_nodes_stage2,
        )

        result_value = min(b_ac, b_ce)

        # Optional console outputs for clarity
        print(f"Stage1 A->C bottleneck: {b_ac}")
        print(f"Stage1 arcs: {arcs_ac}")
        print(f"Stage2 C->E bottleneck: {b_ce}")
        print(f"Stage2 arcs: {arcs_ce}")
        print(f"Final max link bandwidth (min of two stages): {result_value}")

    except cp.CoptError as e:
        raise RuntimeError(f"COPT Error: {e.retcode} - {e.message}")
    finally:
        if env is not None:
            env.close()

    # Write final objective value to result.txt
    with open('result.txt', 'w', encoding='utf-8') as f:
        # Write only the final objective value as required
        f.write(f"{result_value}\n")


if __name__ == '__main__':
    main()

