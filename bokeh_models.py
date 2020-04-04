"""Modelos Bokeh customizados."""

from bokeh.plotting import figure


def Figure(title, axis_labels, **kw):
    """Figura Bokeh básica customizada.

    Args:
        title (str): título da figura.
        axis_labels (list): lista com o títulos dos eixos: (x, y)

    Returns:
        bokeh.plotting.Figure: figura.
    """
    fig_opts = {
        "title": title,
        "x_axis_label": axis_labels[0],
        "y_axis_label": axis_labels[1],
        "tooltips": [(axis_labels[1], "@y"), (axis_labels[0], "@x")],
        "sizing_mode": "stretch_both",
        "tools": "wheel_zoom,pan,hover,reset,save",
        "active_scroll": "wheel_zoom",
        "toolbar_location": "above",
    }
    fig_opts.update(**kw)
    return figure(**fig_opts)
