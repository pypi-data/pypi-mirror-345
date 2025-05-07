import operator

def select_by_rank(conc, **args):
    """
    Selects lines based on rank values obtained from a specific ranking key in the ordering_result["rank_keys"]
    of the current node. The ranking key corresponds to supplementary ranking information.
    """
    # Metadata for the algorithm
    select_by_rank._algorithm_metadata = {
        "name": "Select by Rank",
        "description": (
            "Selects lines based on rank values obtained from the first ranking key in the ordering_result['rank_keys'] "
            "of the current node."
        ),
        "algorithm_type": "selecting",
        "status": "experimental",
        "args_schema": {
            "type": "object",
            "properties": {
                "comparison_operator": {
                    "type": "string",
                    "enum": ["==", "<=", ">=", "<", ">"],
                    "description": "The comparison operator to use for the ranking scores.",
                    "default": "=="
                },
                "value": {
                    "type": "number",
                    "description": "The numeric value to compare the ranking scores against.",
                    "default": 0
                }
            },
            "required": []
        }
    }

    # Use the current active node.
    node = conc.active_node
    algo_key = args.get("algo_key", None)
    comparison_operator = args.get("comparison_operator", "==")
    value = args.get("value", 0)

    if not hasattr(node, "ordering_result") or "rank_keys" not in node.ordering_result:
        raise ValueError("The active node does not contain 'ordering_result' with 'rank_keys'.")

    rank_keys = node.ordering_result["rank_keys"]

    if algo_key is None:
        algo_candidates = [key for key in rank_keys.keys() if key.startswith("algo_")]
        if not algo_candidates:
            raise ValueError("No ranking keys found in the active node.")
        algo_key = sorted(algo_candidates, key=lambda k: int(k.split("_")[1]))[0]

    ranks = rank_keys[algo_key]

    ops = {
        "==": operator.eq,
        "<=": operator.le,
        ">=": operator.ge,
        "<": operator.lt,
        ">": operator.gt
    }
    comp_func = ops[comparison_operator]

    selected_lines = [line_id for line_id, rank in ranks.items() if comp_func(rank, value)]

    return {"selected_lines": sorted(selected_lines)}