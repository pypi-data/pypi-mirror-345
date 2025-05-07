from ipywidgets import (
    Dropdown, VBox, HBox, Button, Output, Label, RadioButtons, Text,
    IntText, FloatText, Checkbox
)
import ipywidgets as widgets
from IPython.display import clear_output, display, HTML, Javascript
from IPython import get_ipython
import json
import ast
from flexiconc.visualization.html_visualizer import generate_concordance_html, generate_analysis_tree_html


def show_algorithm_dropdown(node, algo_type_filter=None):
    """Return (widget_box, collector_fn) for picking any algorithm on *node*.

    The collector returns (algorithm_name, args_dict) ready for
    add_subset_node / add_arrangement_node.
    """
    import json

    # ------------------------------------------------------------------ #
    # available algorithms → dropdown options
    # ------------------------------------------------------------------ #
    available = node.available_algorithms()
    opts = [
        (meta.get("name", name), name)
        for name, meta in available.items()
        if (
            algo_type_filter is None
            or meta.get("algorithm_type") == algo_type_filter
            or meta.get("algorithm_type") in algo_type_filter
        )
    ]

    if not opts:
        return VBox([Label("No algorithms available.")]), lambda: ("", {})

    algo_drop = Dropdown(options=opts, description="Algorithm:")
    args_box = VBox()
    widgets_dict = {}  # arg-name → widget

    # ------------------------------------------------------------------ #
    # helper – build argument widgets for the chosen algorithm
    # ------------------------------------------------------------------ #
    def build_widgets(algo_name):
        schema = node.schema_for(algo_name)
        widgets_dict.clear()
        items = []

        for arg, spec in schema.get("properties", {}).items():
            dtype = spec.get("type")
            default = spec.get("default")
            enum = spec.get("enum")
            item_type = spec.get("items", {}).get("type") if dtype == "array" else None

            # ----- enums -------------------------------------------------- #
            if enum:
                w = Dropdown(
                    options=enum,
                    value=default if default in enum else enum[0],
                    description=arg,
                )

            # ----- primitive strings -------------------------------------- #
            elif dtype == "string":
                w = Text(value=default or "", description=arg)

            # ----- numbers ------------------------------------------------ #
            elif dtype in ("integer", "number"):
                # Optional numbers → Text widget so it can stay blank
                if default is None:
                    placeholder = "int" if dtype == "integer" else "float"
                    w = Text(value="", description=arg, placeholder=placeholder)
                    w._expect_num = dtype  # mark for later parsing
                else:  # required or has meaningful default
                    if dtype == "integer":
                        w = IntText(value=default, description=arg)
                    else:
                        w = FloatText(value=default, description=arg)

            # ----- booleans ---------------------------------------------- #
            elif dtype == "boolean":
                w = Checkbox(value=bool(default), description=arg)

            # ----- homogeneous array via comma-separated list ------------- #
            elif dtype == "array":
                placeholder = f"(comma-separated {item_type or 'string'}s)"
                w = Text(
                    value=",".join(map(str, default)) if isinstance(default, list) else "",
                    description=arg,
                    placeholder=placeholder,
                )
                w._item_type = item_type or "string"

            # ----- union / free-form literal ------------------------------ #
            elif isinstance(dtype, list):
                w = Text(
                    value=json.dumps(default) if default not in (None, {}) else "",
                    description=arg,
                    placeholder="JSON value (string | number | array)",
                )
                w._expect_json = True

            # ----- generic object ---------------------------------------- #
            elif dtype == "object":
                try:
                    default_value = repr(default) if default is not None else ""
                except:
                    default_value = ""
                w = widgets.Textarea(
                    value=default_value,
                    description=arg,
                    placeholder="Python expression, e.g. {'attr': ['val1']}",
                    layout={"width": "400px", "height": "60px"},
                )
                w._expect_pyexpr = True

            else:
                continue  # unsupported spec

            widgets_dict[arg] = w
            items.append(w)

        args_box.children = items

    build_widgets(algo_drop.value)
    algo_drop.observe(lambda c: build_widgets(c["new"]), names="value")

    # ------------------------------------------------------------------ #
    # collector – turn widget states into Python args
    # ------------------------------------------------------------------ #
    def collect():
        args = {}
        for arg_name, w in widgets_dict.items():
            val = w.value

            # array widgets (comma-separated)
            if isinstance(w, Text) and getattr(w, "_item_type", None):
                parts = [p.strip() for p in val.split(",") if p.strip()]
                if parts:
                    conv = (
                        int
                        if w._item_type == "integer"
                        else float
                        if w._item_type == "number"
                        else str
                    )
                    val = [conv(p) for p in parts]
                else:
                    continue  # left blank → skip optional

            # numeric fields entered as Text
            elif getattr(w, "_expect_num", None):
                if str(val).strip() == "":
                    continue  # left blank
                try:
                    val = int(val) if w._expect_num == "integer" else float(val)
                except ValueError as e:
                    raise ValueError(f"Argument '{arg_name}' expects a number: {e}") from None

            # widgets that expect raw JSON literal
            elif getattr(w, "_expect_json", False):
                if str(val).strip() == "":
                    continue
                try:
                    val = json.loads(val)
                except Exception as e:
                    raise ValueError(
                        f"Argument '{arg_name}' expects a valid JSON literal: {e}"
                    ) from None

            # widgets that expect Python expression
            elif getattr(w, "_expect_pyexpr", False):
                if str(val).strip() == "":
                    continue
                try:
                    val = ast.literal_eval(val)  # ← safe evaluation
                except Exception as e:
                    raise ValueError(
                        f"Argument '{arg_name}' expects a valid Python expression: {e}"
                    ) from None

            # primitives – skip if left blank
            elif isinstance(w, Text) and val.strip() == "":
                continue

            args[arg_name] = val
        return algo_drop.value, args

    container = VBox([algo_drop, args_box])
    return container, collect



class _NodeHandle:
    """Light‑weight proxy returned by *add_node_ui*.
    After the user clicks **OK** it exposes the freshly created
    :class:`AnalysisTreeNode` via attribute access **and** the textual
    *code* that reproduces the action.
    """
    def __init__(self):
        self._t = None       # the real AnalysisTreeNode once created
        self.code = None     # Python snippet shown / inserted for this action

    def __getattr__(self, name):
        if self._t is None:
            raise AttributeError("Node not created yet – click OK")
        return getattr(self._t, name)

    def __repr__(self):
        return (
            "<Pending Node>" if self._t is None else
            f"<{self._t!r} – code={self.code!r}>"
        )

def _disable(widget):
    if hasattr(widget, "disabled"):
        widget.disabled = True
    for c in getattr(widget, "children", ()):
        _disable(c)


def add_node_ui(parent, *, execute: bool = True):
    """Interactive helper to add *subset* / *arrangement* nodes.

    Parameters
    ----------
    parent   : AnalysisTreeNode
        Parent node below which the new node will be attached (when
        *execute=True*).
    execute  : bool, default **True**
        * **True** – create the node immediately and print the generated
          snippet below the widget.
        * **False** – *dry‑run*: the analysis tree is untouched; instead the
          snippet is inserted into a new notebook cell right below the current
          one so the user can inspect / run it manually.
    """

    handle = _NodeHandle()

    # ------------- top‑level widgets ---------------------------------- #
    node_type   = RadioButtons(options=["subset", "arrangement"], description="Node:")
    config_box  = VBox()
    ok_btn      = Button(description="OK", button_style="success")
    log         = Output(layout={"border": "1px solid #dee2e6", "padding": "2px"})

    # ------------------------------------------------------------------ #
    # UI factory helpers – each returns (ui_widget, collect_fn)          #
    # ------------------------------------------------------------------ #

    def subset_ui():
        box, coll = show_algorithm_dropdown(parent, "selecting")
        return VBox([box]), coll  # coll → (algo_name, args)

    def arrangement_ui():
        # ---------- grouping selector ---------------------------------- #
        grp_container, grp_collect = VBox(), []

        def add_group(_=None):
            box, coll = show_algorithm_dropdown(parent, "partitioning")
            rm = Button(description="🗑", layout={"width": "28px"})
            rm.on_click(lambda _: (grp_collect.clear(), setattr(grp_container, 'children', (add_grp_btn,))))
            grp_collect[:] = [coll]
            grp_container.children = (
                VBox([box, rm], layout={"border": "1px solid #ccc", "padding": "4px"}),
            )

        add_grp_btn = Button(description="+", layout={"width": "28px"})
        add_grp_btn.on_click(add_group)
        grp_container.children = (add_grp_btn,)

        # ---------- ordering stack ------------------------------------ #
        ord_container, ord_blocks = HBox(), []

        def refresh_ord():
            ord_container.children = tuple(b["w"] for b in ord_blocks) + (add_ord_btn,)
            for i, b in enumerate(ord_blocks):
                b["left"].disabled  = i == 0
                b["right"].disabled = i == len(ord_blocks) - 1

        def add_order(_=None):
            box, coll = show_algorithm_dropdown(parent, ["sorting", "ranking"])
            left  = Button(description="⬅️", layout={"width": "28px"})
            right = Button(description="➡️", layout={"width": "28px"})
            rm    = Button(description="🗑", layout={"width": "28px"})

            wrapper = VBox(
                [box, HBox([left, right, rm], layout={"justify_content": "center"})],
                layout={"border": "1px solid #ccc", "padding": "4px", "margin": "0 6px"},
            )
            blk = {"w": wrapper, "c": coll, "left": left, "right": right, "rm": rm}

            left .on_click(lambda _:(ord_blocks.insert(ord_blocks.index(blk) - 1, ord_blocks.pop(ord_blocks.index(blk))), refresh_ord()))
            right.on_click(lambda _:(ord_blocks.insert(ord_blocks.index(blk) + 1, ord_blocks.pop(ord_blocks.index(blk))), refresh_ord()))
            rm   .on_click(lambda _:(ord_blocks.remove(blk), refresh_ord()))

            ord_blocks.append(blk); refresh_ord()

        add_ord_btn = Button(description="+", layout={"width": "28px"})
        add_ord_btn.on_click(add_order)
        refresh_ord()

        layout = HBox(
            [VBox([Label("Grouping"), grp_container]), VBox([Label("Ordering"), ord_container])],
            layout={"gap": "60px"},
        )

        def collect_specs():
            grouping  = grp_collect[0]() if grp_collect else None
            ordering  = [b["c"]() for b in ord_blocks]
            return grouping, ordering

        return layout, collect_specs

    # ------------------------------------------------------------------ #
    # Track currently selected builder                                  #
    # ------------------------------------------------------------------ #

    current = {"collect": None, "kind": None, "creator": None}

    def switch(kind):
        if kind == "subset":
            ui, collect = subset_ui()
            creator = lambda spec: parent.add_subset_node(spec)  # type: ignore[arg-type]
        else:
            ui, collect = arrangement_ui()
            creator = lambda spec: parent.add_arrangement_node(ordering=spec[1], grouping=spec[0])
        current.update(collect=collect, kind=kind, creator=creator)
        config_box.children = (ui,)

    switch(node_type.value)
    node_type.observe(lambda c: switch(c["new"]), names="value")

    # ------------------------------------------------------------------ #
    # OK handler – build snippet, then execute / insert ---------------- #
    # ------------------------------------------------------------------ #

    def on_ok(_):
        with log:
            clear_output()
            try:
                spec = current["collect"]()
                if current["kind"] == "subset":
                    algo_name, args = spec
                    code_snippet = f"add_subset_node(({algo_name!r}, {args!r}))"
                else:
                    grouping, ordering = spec
                    code_snippet = (
                        "add_arrangement_node("  # noqa: E501
                        f"grouping={None if grouping is None else (grouping[0], grouping[1])!r}, "
                        f"ordering={[(o[0], o[1]) for o in ordering]!r})"
                    )

                handle.code = code_snippet  # expose snippet

                if execute:
                    new_node = current["creator"](spec)
                    handle._t = new_node
                    print(code_snippet)
                else:
                    get_ipython().set_next_input(code_snippet, replace=False)
                    display(Javascript(
                        """(function() {
                              try {
                                const nb = (typeof Jupyter !== 'undefined' && Jupyter.notebook) ? Jupyter.notebook :
                                           (typeof IPython !== 'undefined' && IPython.notebook) ? IPython.notebook : null;
                                if (nb) {
                                    const idx = nb.get_selected_index();
                                    nb.select(idx + 1);
                                }
                              } catch (e) { console.warn(e); }
                            })();"""
                    ))
                    print(code_snippet)
            except Exception as e:
                # all errors go to the log box
                print("Error:", e)

    ok_btn.on_click(on_ok)

    display(VBox([node_type, config_box, ok_btn, log]))
    return handle


def show_kwic(node, n: int = 25):
    """
    Display a KWIC (Key Word in Context) table for the given analysis-tree node
    inside a Jupyter notebook.

    Parameters
    ----------
    node : AnalysisTreeNode
        The node whose concordance subset / arrangement should be shown.
    n : int, default 25
        Maximum number of lines per partition (or overall if un-partitioned).

    Notes
    -----
    * The function automatically retrieves the parent ``Concordance`` from
      ``node.concordance()`` and delegates the heavy lifting to
      ``flexiconc.visualization.generate_concordance_html``.
    * The resulting HTML is rendered inline via :pyfunc:`IPython.display.display`.
    """
    conc = node.concordance()
    html = generate_concordance_html(conc, node, n=n)
    display(HTML(html))

def show_analysis_tree(concordance, suppress_line_info: bool = True, mark=None):
    """
    Display an analysis-tree overview for *concordance* inside a Jupyter notebook.
    """
    html = generate_analysis_tree_html(
        concordance,
        suppress_line_info=suppress_line_info,
        mark=mark,
    )
    display(HTML(html))