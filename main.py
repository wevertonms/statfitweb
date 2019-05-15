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
    numbins_slider = Slider(title="Number of bins", value=10, start=5, end=15, step=1)
    div = Div(text="<h2>Goodness of fit tests (p-values)</h2>")
    pvalue_slider = Slider(title="Min p-value (%)", value=5, start=1, end=10, step=1)
    table = Table([dist.name for dist in DISTS])

    def numbins_slider_callback(attr, old, new):
        """Função que atualiza o histograma e a CDF dos observações."""
        hist, edges = np.histogram(plot.values, density=True, bins=new)
        plot.update_histogram(hist, edges)
        data = plot.cumulative_source.data
        chi = [chi_squared(plot.values, dist.cdf, new) for dist in DISTS]
        ks = [kolmogorov_smirnov(plot.values, dist.cdf) for dist in DISTS]
        wms = [weverton(dist.cdf, data["x"], data["y"]) for dist in DISTS]
        table.source.data.update(ks=ks, chi=chi, wms=wms)

    def pvalue_slider_callback(attr, old, new):
        pass

    def make_plot(attr, old, new):
        """Função que atualiza os dados do arquivo aberto."""
        observed = np.loadtxt(new)
        plot.update_data(observed)
        numbins_slider.value = plot.num_bins
        numbins_slider.end = len(observed) // 3
        numbins_slider_callback(attr, old, numbins_slider.value)

    button = UploadButton("Open file ...", make_plot, button_type="success")
    numbins_slider.on_change("value", numbins_slider_callback)
    pvalue_slider.on_change("value", pvalue_slider_callback)
    controls = column(button, numbins_slider, div, pvalue_slider, table.table)
    doc.add_root(row(controls, plot.layout, sizing_mode="scale_height"))
    doc.title = "Statfit Web"


server = Server({"/": modify_doc})
server.start()

if __name__ == "__main__":
    print("Opening Bokeh application on http://localhost:5006/")
    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()
