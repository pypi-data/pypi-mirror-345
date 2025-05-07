import html
import pandas as pd

def format_concordance_line(line_df, left_node_right=False, html=False, table=False, p=["word"], style={},
                            l=-float('Inf'), u=float('Inf')):

    """
    Formats the given concordance line as a string.

    Parameters:
    - line_df (DataFrame): The dataframe representing the line.
    - left_node_right: A boolean flag. If set to True, it will return a dictionary structure
      dividing the line into left, node, and right sections. If set to False, it will just
      format the line as a single string.

    Returns:
    - A formatted string or a dictionary structure with the 'left', 'node', and 'right'
      parts of the line, depending on the `left_node_right` parameter.
    """

    # If just formatting the entire line as a single string
    if not left_node_right:
        output = ''
        right_punctuation = ['.', '?', '!', ',', '…', ';', ':', '"', "'", "n't"]
        left_punctuation = ['(', '`', '``']
        words = list(line_df.word.astype(str))
        offsets = list(line_df.offset)

        # Check if there are spaces provided in the concordance, else default to None
        spaces = list(line_df.space.astype(str)) if 'space' in line_df else None

        for i, word in enumerate(words):
            if offsets[i] < l or offsets[i] > u:
                continue
            if 'offset' in style and offsets[i] in style['offset']:
                output += style['offset'][offsets[i]].format(word)
            else:
                output += word

            # If explicit spaces are provided, use them
            if spaces is not None:
                output += spaces[i]
            else:
                # Check conditions to decide whether to add space or not
                if word in left_punctuation:
                    continue
                elif i < len(words) - 1 and (words[i + 1] in right_punctuation or words[i + 1][0] == "'"):
                    continue
                else:
                    output += ' '

        return output

    # If splitting the line into left, node, and right sections
    else:
        return {
            'left': format_concordance_line(line_df[line_df["offset"] < 0], html=html, table=table, p=p, style=style),
            'node': format_concordance_line(line_df[line_df["offset"] == 0], html=html, table=table, p=p, style=style),
            'right': format_concordance_line(line_df[line_df["offset"] > 0], html=html, table=table, p=p, style=style)
        }


def generate_concordance_html(concordance, node, n=25, n_groups=None, token_attr='word', metadata_columns=None, detokenize=True):
    """
    Generates HTML for concordance lines from the tokens in the subset at the given node,
    with optional custom metadata columns inserted between the line ID and the KWIC display.

    Parameters:
        concordance: The Concordance object.
        node: The analysis tree node whose subset is to be displayed.
        n (int, optional): The number of lines to display per partition or overall. Default is 25.
        n_groups (int, optional): If concordance view is partitioned, show only first `n_groups` groups. Default None shows all groups.
        token_attr (str, optional): The token attribute to display (e.g., 'word', 'lemma'). Default is 'word'.
        metadata_columns (list of str, optional): A list of metadata column names to display for each line.
            These columns will be shown between the "Line ID" column and the KWIC display columns.
        detokenize (bool, optional): Whether to detokenize text in the kwic display. Defaults to heuristics for English, should be extended
            to make use of suitable token-level annotation in future.

    Returns:
        str: An HTML string representing the concordance lines.
    """
    # Get the subset at the specified node.
    subset = concordance.subset_at_node(node)
    tokens = subset.tokens
    metadata = subset.metadata

    # ── gather ranking columns from node.view() ────────────────────────────
    ranking_cols = []          # list of (key, short_label)
    ranking_values = {}        # {line_id: {key: value …}}

    v = node.view()
    if "line_info" in v:
        col_info  = v["line_info"]["column_info"]
        ranking_values = v["line_info"]["data"]

        for info in col_info:
            key  = info["key"]                  # full human-readable key
            # make a short label (R0, R1, …) instead of the long key
            short = f"R{info.get('algorithm_index_withing_ordering', 0)}"
            ranking_cols.append((key, short))


    # Start building the HTML.

    CAT_COLOURS = {"A": "#ffe08a",  # warm yellow-orange
                   "B": "#9ddfff",  # light blue-cyan
                   "C": "#ffb3c9"}  # soft pink

    html_output = """
    <script>
    function togglePartition(className) {
        const rows = document.querySelectorAll('.' + className);
        for (const row of rows) {
            row.style.display = (row.style.display === 'none') ? '' : 'none';
        }
    }
    </script>

    <style>
        table.concordance {
            border-collapse: collapse;
            width: 100%;
            table-layout: auto;
        }
        table.concordance th, table.concordance td {
            border: 1px solid #dddddd;
            padding: 4px;
            vertical-align: top;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        table.concordance th {
            background-color: #f2f2f2;
            text-align: center;
        }
        table.concordance th.line-id, table.concordance td.line-id {
            text-align: center;
            white-space: nowrap;
        }
        table.concordance th.metadata, table.concordance td.metadata {
            text-align: center;
            white-space: nowrap;
        }
        table.concordance th.left-context, table.concordance td.left-context {
            text-align: right;
            overflow: hidden;
            white-space: nowrap;
            width: 40%;
            max-width: 0px;
        }
        table.concordance th.node, table.concordance td.node {
            text-align: center;
            font-weight: bold;
            white-space: nowrap;
        }
        table.concordance th.right-context, table.concordance td.right-context {
            text-align: left;
            overflow: hidden;
            white-space: nowrap;
            width: 40%;
            max-width: 0px;
        }
        table.concordance div.left-context {
            float: right;
            white-space: nowrap;
        }
        table.concordance div.right-context {
            float: left;
            white-space: nowrap;
        }
    """
    for cat, col in CAT_COLOURS.items():
        html_output += f"        .mark-{cat} {{ background-color: {col}; }}\n"
    html_output += """
    </style>
    <table class="concordance">
        <colgroup>
            <col>
    """
    # If metadata_columns are provided, add one <col> per column.
    if metadata_columns:
        for _ in metadata_columns:
            html_output += "            <col>\n"
    html_output += """            <col>
            <col>
            <col>
        </colgroup>
        <tr>
            <th class="line-id">Line ID</th>
    """
    # Add header cells for custom metadata columns.
    # metadata columns first …
    if metadata_columns:
        for col in metadata_columns:
            html_output += f'            <th class="metadata">{col}</th>\n'
    # … then any ranking columns
    for _k, short in ranking_cols:
        html_output += f'            <th class="metadata">{short}</th>\n'

    html_output += """            <th class="left-context">Left Context</th>
            <th class="node">Node</th>
            <th class="right-context">Right Context</th>
        </tr>
    """

    def _generate_lines_html(subset, line_ids, token_attr, metadata_columns=None, row_class="", hidden=False):

        tokens   = subset.tokens
        metadata = subset.metadata
        html_rows = ""

        # ---------- pre-compute marking info --------------------------------

        span_lookup: dict[int, list[tuple[int,int,str]]] = {}

        if hasattr(node, "token_spans") and node.token_spans is not None:
            spans = node.token_spans
            # accept either a DataFrame or list-of-dicts
            if isinstance(spans, pd.DataFrame):
                for _, row in spans.iterrows():
                    span_lookup.setdefault(int(row["line_id"]), []).append(
                        (int(row["start_id_in_line"]),
                         int(row["end_id_in_line"]),
                         row["category"] if "category" in row else "A")
                    )
            else:   # list / iterable of dicts
                for span in spans:
                    span_lookup.setdefault(span["line_id"], []).append(
                        (span["start_id_in_line"],
                         span["end_id_in_line"],
                         span.get("category", "A"))
                    )

        # punctuation heuristics for spacing
        LEFT_PUNCT  = {'(', '[', '{', '“'}
        RIGHT_PUNCT = {'.', ',', '!', '?', ';', ':', '”', ')', ']', '}', "...",
                       "'s", "'m", "'d", "'ve", "'re", "'ll", "'t", "n't"}

        # ---------- token-to-HTML helper ------------------------------------
        def tokens_to_html(tok_df, line_id):
            parts, prev_tok = [], ''
            spans_here = span_lookup.get(line_id, [])

            for _, tok in tok_df.iterrows():
                tok_id   = tok["id_in_line"]
                tok_text = str(tok[token_attr])

                # --- highlight via CSS classes ---------------------------------
                mark_cls = next(
                    (f"mark-{cat}"
                     for start, end, cat in spans_here
                     if start <= tok_id <= end),
                    None
                )
                cls_attr  = f' class="{mark_cls}"' if mark_cls else ""
                span_html = f'<span data-id="{tok_id}"{cls_attr}>{html.escape(tok_text)}</span>'

                # --- spacing heuristics ----------------------------------------
                needs_space = (
                    parts and
                    tok_text not in RIGHT_PUNCT and
                    prev_tok not in LEFT_PUNCT
                )
                if needs_space:
                    parts.append(' ')
                parts.append(span_html)
                prev_tok = tok_text

            return ''.join(parts)

        # ---------- build table rows ---------------------------------------
        for line_id in line_ids:
            line_tok = tokens.loc[tokens['line_id'] == line_id].sort_values(
                by=['offset', 'id_in_line']
            )
            left_html  = tokens_to_html(line_tok[line_tok['offset'] < 0],  line_id)
            node_html  = tokens_to_html(line_tok[line_tok['offset'] == 0], line_id)
            right_html = tokens_to_html(line_tok[line_tok['offset'] > 0],  line_id)

            # metadata cells if requested
            meta_cells = ""
            if metadata_columns:
                row_meta = metadata.loc[metadata['line_id'] == line_id].iloc[0] \
                           if not metadata.empty else None
                for col in metadata_columns:
                    meta_cells += f'<td class="metadata">{html.escape(str(row_meta.get(col,"")) if row_meta is not None else "")}</td>\n'

            # ranking cells (may be empty)
            rank_cells = ""
            rv = ranking_values.get(line_id, {})
            for key, _short in ranking_cols:
                val = rv.get(key, "")
                rank_cells += f'<td class="metadata">{html.escape(str(val))}</td>\n'

            display_style = "display: none;" if hidden else ""
            html_rows += f"""
            <tr class="{row_class}" style="{display_style}">
                <td class="line-id">{line_id}</td>
                {meta_cells}{rank_cells}
                <td class="left-context"><div class="left-context">{left_html}</div></td>
                <td class="node">{node_html}</td>
                <td class="right-context"><div class="right-context">{right_html}</div></td>
            </tr>
            """
        return html_rows

    # Process partitions if available.
    if hasattr(node, 'grouping_result') and 'partitions' in node.grouping_result:
        partitions = node.grouping_result['partitions']
        grouping_view = node.view().get("grouping", {})
        col_order_names = [ci["name"] for ci in grouping_view.get("column_info", [])]
        for i, partition in enumerate(partitions):
            if n_groups is not None and i >= n_groups:
                break
            partition_id = partition.get('id', 0)
            partition_label = partition.get('label', f'Partition {partition_id}')
            line_ids = partition.get('line_ids', [])
            line_count = len(line_ids)

            info = partition.get("info", {})
            if info:
                ordered = [(k, info[k]) for k in col_order_names if k in info]
                info_str = ", ".join(f"{k}: {v:g}" if isinstance(v, float) else f"{k}: {v}"
                                     for k, v in ordered)
                info_html = (f"<br><span style='font-size:90%;color:#555;'>"
                             f"{info_str}</span>")
            else:
                info_html = ""

            # Apply ordering if available.
            if hasattr(node, 'ordering_result') and 'sort_keys' in node.ordering_result:
                partition_sort_keys = {line_id: node.ordering_result["sort_keys"][line_id]
                                       for line_id in line_ids if line_id in node.ordering_result["sort_keys"]}
                sorted_line_ids = sorted(partition_sort_keys, key=partition_sort_keys.get)
            else:
                sorted_line_ids = line_ids

            partition_line_ids = sorted_line_ids[:n]

            partition_class = f"partition-{i}"
            html_output += f"""
            <tr onclick="togglePartition('{partition_class}')" style="cursor: pointer; background-color: #eee;">
                <td style="text-align: center;" colspan="{4 + (len(metadata_columns) if metadata_columns else 0)}">
                    <b>▶ {partition_label} ({line_count} line{'s' if line_count != 1 else ''})</b>{info_html}
                </td>
            </tr>
            """
            html_output += _generate_lines_html(
                subset,
                partition_line_ids,
                token_attr,
                metadata_columns,
                row_class=f"partition-row {partition_class}",
                hidden=True
            )

    else:
        # Non-partitioned node.
        line_ids = metadata['line_id'].unique().tolist()
        if hasattr(node, 'ordering_result') and 'sort_keys' in node.ordering_result:
            sort_keys = node.ordering_result['sort_keys']
            node_sort_keys = {line_id: sort_keys[line_id] for line_id in line_ids if line_id in sort_keys}
            sorted_line_ids = sorted(node_sort_keys, key=node_sort_keys.get)
        else:
            sorted_line_ids = line_ids

        selected_line_ids = sorted_line_ids[:n]
        html_output += _generate_lines_html(subset, selected_line_ids, token_attr, metadata_columns)

    html_output += "</table>"
    return html_output


def generate_analysis_tree_html(concordance, suppress_line_info=True, mark=None):
    """
    Generates an HTML representation of the analysis tree in a human-readable manner.

    Parameters:
        concordance: The Concordance object.
        suppress_line_info (bool, optional): If True, suppresses output of 'selected_lines',
            'order_result', 'sort_keys', and 'rank_keys'. Default is True.

    Returns:
        str: An HTML string representing the analysis tree.
    """
    # Display the query above the tree.
    html_output = (
        f"<div style='margin-bottom:10px;'><strong>Query:</strong> "
        f"{concordance.info.get('query', '')}</div>\n<ul style='list-style-type:none;'>\n"
    )

    def process_node(node):
        nt = node.node_type
        node_id = node.id
        depth = node.depth
        has_children = bool(node.children)
        # Use 👉 for marked node, 🔎 for subset nodes and 🔀 for arrangement nodes.
        icon = "🔎" if nt == "subset" else "🔀"
        if mark is not None and node_id == mark:
            icon = "👉 " + icon

        indent = "    " * depth

        # For subset nodes, display the line count.
        line_count = f'({node.line_count})' if nt == "subset" else ""
        html = f"{indent}<li>[{node_id}] {icon} {nt} {line_count}: "

        # Add algorithm information if available.
        if hasattr(node, "algorithms"):
            algo_html = ""
            i = 0
            for algo_type in node.algorithms:
                algos = node.algorithms[algo_type]
                if algos is None:
                    continue
                if not isinstance(algos, list):
                    algos = [algos]
                for a in algos:
                    if i > 0:
                        algo_html += "<br/>"
                    i += 1
                    args = a['args'].copy()
                    if suppress_line_info:
                        args.pop('active_node', None)
                        args.pop('selected_lines', None)
                        args.pop('order_result', None)
                        args.pop('sort_keys', None)
                        args.pop('rank_keys', None)
                    algo_html += f"&#9881; {a['algorithm_name']} {args}"
            html += algo_html
        html += "</li>\n"

        # Process child nodes recursively.
        if has_children:
            html += f"{indent}<ul style='list-style-type:none;'>\n"
            for child in node.children:
                html += process_node(child)
            html += f"{indent}</ul>\n"

        return html

    html_output += process_node(concordance.root)
    html_output += "</ul>\n"

    return html_output
