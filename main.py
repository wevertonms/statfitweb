#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Small python web application for statistical characterization."""

import base64
import io

import numpy as np
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.models.widgets import Slider, Div
from bokeh.server.server import Server
from scipy import stats

from bokeh_models import UploadButton
from plot import Plot, Table
from stats import DISTS, chi_squared, kolmogorov_smirnov, weverton


def modify_doc(doc):
    """Inclui o gráficos e os controles no curdoc do Bokeh Server."""
    plot = Plot(DISTS)
    slider = Slider(title="Number of bins", value=10, start=5, end=15, step=1)
    div = Div(text="<h3>Goodness of fit tests</h3>")
    table = Table([dist.name for dist in DISTS])

    def slider_callback(attr, old, new):
        """Função que atualiza o histograma e a CDF dos observações."""
        hist, edges = np.histogram(plot.values, density=True, bins=new)
        plot.update_histogram(hist, edges)
        data = plot.cumulative_source.data
        chi = [chi_squared(plot.values, dist.cdf, new) for dist in DISTS]
        ks = [kolmogorov_smirnov(plot.values, dist.cdf) for dist in DISTS]
        wms = [weverton(dist.cdf, data["x"], data["y"]) for dist in DISTS]
        table.source.data.update(
            ks=np.round(ks, 4), chi=np.round(chi, 4), wms=np.round(wms, 6)
        )

    def make_plot(attr, old, new):
        """Função que atualiza os dados do arquivo aberto."""
        observed = np.loadtxt(new)
        plot.update_data(observed)
        slider.value = plot.num_bins
        slider.end = len(observed) // 3

    button = UploadButton("Open file ...", make_plot, button_type="success")
    slider.on_change("value", slider_callback)
    doc.add_root(
        row(
            column(button, slider, div, table.table),
            plot.layout,
            sizing_mode="scale_height",
        )
    )
    doc.title = "Statfit Web"


server = Server({"/": modify_doc})
server.start()

if __name__ == "__main__":
    print("Opening Bokeh application on http://localhost:5006/")
    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()
