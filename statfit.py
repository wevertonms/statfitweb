# -*- coding: utf-8 -*-
"""
Created on Wed May 03 11:26:21 2017

@author: Kevin Anderson
"""

import base64
import io

import numpy as np
from bokeh.io import curdoc
from bokeh.layouts import column, layout, row
from bokeh.models import ColumnDataSource, CustomJS, Panel, Tabs
from bokeh.models.widgets import Button, Slider
from scipy import stats

from custom_figure import CustomFigure, colors

PARAMS_MAPPER = dict(
    norm=dict(loc=None, scale=None),
    lognorm=dict(s=None, loc=None, scale=None),
    weibull_min=dict(c=None, loc=None, scale=None),
    gamma=dict(a=None, loc=None, scale=None),
)


def cdf(hist, edges):
    x = [edges[i // 2] for i in range(2 * len(edges[:-1]))]
    x.append(edges[-1])
    cdf = np.cumsum(hist * (edges[1] - edges[0]))
    y = [cdf[(i - 1) // 2] for i in range(2 * len(cdf))]
    y[0] = 0
    y.append(cdf[-1])
    return x, y


button = Button(label="Open file ...", button_type="success")
num_bins = Slider(title="Number of bins", value=10, start=1, end=19, step=1)

file_source = ColumnDataSource({"file_contents": [], "file_name": []})
observed_source = ColumnDataSource(
    dict(
        observed=[],
        x=[],
        cdf_x=[],
        cdf_y=[],
        cdf_quad_top=[],
        cdf_quad_left=[],
        cdf_quad_right=[],
    )
)

# Cria o plot base
pdf_plot = CustomFigure("Probability Density", ("Values", "Relative frequency"))
pdf_plot.quad(
    source=observed_source,
    top="cdf_quad_top",
    bottom=0,
    left="cdf_quad_left",
    right="cdf_quad_right",
    line_color="white",
    legend="Observed",
    color=colors[0],
)

cdf_plot = CustomFigure("Cumulative Probability", ("Values", "Relative frequency"))
cdf_plot.line(
    source=observed_source,
    x="cdf_x",
    y="cdf_y",
    legend="Observed",
    line_width=2,
    color=colors[0],
)

numeric_source = ColumnDataSource(dict(x=[]))
for dist_name, color in zip(PARAMS_MAPPER.keys(), colors[1:]):
    pdf_name = f"{dist_name}_pdf_y"
    cdf_name = f"{dist_name}_cdf_y"
    legend = dist_name[0].upper() + dist_name[1:]
    numeric_source.data.update({pdf_name: [], cdf_name: []})
    line_opts = dict(legend=legend, line_width=2, color=color)
    pdf_plot.line(source=numeric_source, x="x", y=pdf_name, **line_opts)
    cdf_plot.line(source=numeric_source, x="x", y=cdf_name, **line_opts)

pdf_plot.legend.click_policy = cdf_plot.legend.click_policy = "hide"
pdf_plot.legend.location = cdf_plot.legend.location = "top_left"

plot = Tabs(
    tabs=[
        Panel(child=layout(pdf_plot, sizing_mode="scale_width"), title="PDF"),
        Panel(child=layout(cdf_plot, sizing_mode="scale_width"), title="CDF"),
    ]
)


def update_observed(attr, old, new):
    observed = observed_source.data["observed"]
    x = np.linspace(min(observed), max(observed), len(observed))
    hist, edges = np.histogram(observed, density=True, bins=num_bins.value)
    cdf_x, cdf_y = cdf(hist, edges)
    observed_source.data.update(
        dict(
            observed=observed,
            x=x,
            cdf_x=cdf_x,
            cdf_y=cdf_y,
            cdf_quad_top=hist,
            cdf_quad_left=edges[:-1],
            cdf_quad_right=edges[1:],
        )
    )


def update_numeric(attr, old, new):
    for dist_name in PARAMS_MAPPER.keys():
        param = {}
        param[dist_name] = getattr(stats, dist_name).fit(
            observed_source.data["observed"]
        )
        for key, value in zip(PARAMS_MAPPER[dist_name].keys(), param[dist_name]):
            PARAMS_MAPPER[dist_name][key] = value
    x = numeric_source.data["x"] = observed_source.data["x"]
    for dist_name in PARAMS_MAPPER.keys():
        dist = getattr(stats, dist_name)(**PARAMS_MAPPER[dist_name])
        pdf_name = f"{dist_name}_pdf_y"
        cdf_name = f"{dist_name}_cdf_y"
        numeric_source.data.update({pdf_name: dist.pdf(x), cdf_name: dist.cdf(x)})


def make_plot(attr, old, new):
    # print("filename:", file_source.data["file_name"])
    raw_contents = file_source.data["file_contents"][0]
    prefix, b64_contents = raw_contents.split(",", 1)  # pylint: disable=unused-variable
    file_contents = base64.b64decode(b64_contents)
    file_io = io.BytesIO(file_contents)
    observed_source.data["observed"] = np.loadtxt(file_io)
    observed_size = len(observed_source.data["observed"])
    num_bins.value = int(np.sqrt(observed_size))
    num_bins.end = observed_size // 3
    update_observed(attr, old, new)
    update_numeric(attr, old, new)


file_source.on_change("data", make_plot)

with open("button_callback.js", "r") as f:
    code = f.read()

button.callback = CustomJS(args=dict(file_source=file_source), code=code)
num_bins.on_change("value", update_observed)

panel = row(column(button, num_bins), plot, sizing_mode="scale_height")

curdoc().add_root(panel)
curdoc().title = "StatFit"
