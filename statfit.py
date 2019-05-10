# -*- coding: utf-8 -*-
"""
Created on Wed May 03 11:26:21 2017

@author: Kevin Anderson
"""

import base64
import io

import numpy as np
from scipy import stats
from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models import (
    ColumnDataSource,
    CustomJS,
    HoverTool,
    BoxSelectTool,
    Circle,
    Tabs,
    Panel,
    LegendItem,
    BoxAnnotation,
)
from bokeh.models.widgets import Button, CheckboxGroup, Slider
from bokeh.plotting import figure
from bokeh.palettes import Category10_10 as colors

from plots import basic_figure


file_source = ColumnDataSource({"file_contents": [], "file_name": []})
button = Button(label="Abrir arquivo ...", button_type="success")
num_bins = Slider(title="Intervalos no histograma", value=5, start=0, end=10, step=1)
plot = basic_figure([], num_bins.value)


def make_plot(attr, old, new):
    # print("filename:", file_source.data["file_name"])
    raw_contents = file_source.data["file_contents"][0]
    prefix, b64_contents = raw_contents.split(",", 1)
    file_contents = base64.b64decode(b64_contents)
    file_io = io.BytesIO(file_contents)
    measured = np.loadtxt(file_io)
    # print(measured[:5])
    params = dict(
        norm=dict(loc=None, scale=None),
        lognorm=dict(s=None, loc=None, scale=None),
        weibull_min=dict(c=None, loc=None, scale=None),
        gamma=dict(a=None, loc=None, scale=None),
    )
    fig = basic_figure(measured, num_bins.value)
    plot.tabs = fig.tabs
    if len(measured) > 1:
        pdf_plot, cdf_plot = (
            fig.tabs[0].child.children[0],
            fig.tabs[1].child.children[0],
        )
        for dist_name in params.keys():
            param = {}
            param[dist_name] = getattr(stats, dist_name).fit(measured)
            for key, value in zip(params[dist_name].keys(), param[dist_name]):
                params[dist_name][key] = value
        x = np.linspace(min(measured), max(measured), len(measured))
        for dist_name, color in zip(params.keys(), colors[1:]):
            dist = getattr(stats, dist_name)(**params[dist_name])
            legend = dist_name[0].upper() + dist_name[1:]
            line_opts = dict(legend=legend, line_width=2, color=color)
            pdf_plot.line(x=x, y=dist.pdf(x), **line_opts)
            cdf_plot.line(x=x, y=dist.cdf(x), **line_opts)


file_source.on_change("data", make_plot)

with open("statfit/button_callback.js", "r") as f:
    code = f.read()

button.callback = CustomJS(args=dict(file_source=file_source), code=code)
num_bins.on_change("value", make_plot)

panel = row(column(button, num_bins), plot, sizing_mode="scale_height")


curdoc().add_root(panel)
curdoc().title = "StatFit"
