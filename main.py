#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Small python web application for statistical characterization."""

import base64
import io

import numpy as np
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.models.widgets import Slider
from bokeh.server.server import Server

from bokeh_models import UploadButton
from plot import Plot


def modify_doc(doc):
    """Inclui o gráficos e os controles no curdoc do Bokeh Server."""
    plot = Plot()
    num_bins = Slider(title="Number of bins", value=10, start=1, end=19, step=1)

    def update_observed(attr, old, new):
        """Função que atualiza o histograma e a CDF dos observações."""
        plot.update_observed(num_bins.value)

    def make_plot(attr, old, new):
        """Função que atualiza os dados do arquivo aberto."""
        observed = np.loadtxt(new)
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
        num_bins.end = len(observed)

    button = UploadButton("Open file ...", make_plot, button_type="success")
    num_bins.on_change("value", update_observed)
    doc.add_root(row(column(button, num_bins), plot.tabs, sizing_mode="scale_height"))


server = Server({"/": modify_doc})
server.start()

if __name__ == "__main__":
    print("Opening Bokeh application on http://localhost:5006/")
    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()
