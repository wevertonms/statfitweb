# -*- coding: utf-8 -*-
"""Small python web application for statistical characterization."""

import base64
import io

import numpy as np
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.models.widgets import Button, Slider
from eliot import log_call, to_file


from plot import Plot, PARAMS_MAPPER

to_file(open("out.log", "w"))

file_source = ColumnDataSource({"file_contents": [], "file_name": []})

plot = Plot()
button = Button(label="Open file ...", button_type="success")
num_bins = Slider(title="Number of bins", value=10, start=1, end=19, step=1)


@log_call
def update_observed(attr, old, new):
    """Função que atualiza o histograma e a CDF dos observações."""
    plot.update_observed(num_bins.value)


@log_call
def make_plot(attr, old, new):
    """Função que atualiza os dados do arquivo aberto."""
    raw_contents = file_source.data["file_contents"][0]
    prefix, b64_contents = raw_contents.split(",", 1)  # pylint: disable=unused-variable
    file_contents = base64.b64decode(b64_contents)
    file_io = io.BytesIO(file_contents)
    observed = np.loadtxt(file_io)
    if 30 <= len(observed) <= 100:
        num_bins_value = np.sqrt(len(observed))
    elif len(observed) <= 30:
        num_bins_value = 2 * np.sqrt(len(observed))
    else:
        num_bins_value = max(
            np.log(len(observed)) + 1,  # Fórmula de Sturges
            3.5 * np.std(observed) / (len(observed) ** (1 / 3)),  # Fórmula de Scott
        )
    num_bins_value = int(num_bins_value)
    plot.update_observed(num_bins_value, observed)
    plot.update_numeric()
    num_bins.value = num_bins_value
    num_bins.end = num_bins_value * 2


file_source.on_change("data", make_plot)

with open("button_callback.js", "r") as f:
    code = f.read()

button.callback = CustomJS(args=dict(file_source=file_source), code=code)
num_bins.on_change("value", update_observed)

panel = row(column(button, num_bins), plot.tabs, sizing_mode="scale_height")

curdoc().add_root(panel)
curdoc().title = "StatFit"
