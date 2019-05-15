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


class Dist:
    def __init__(self, name, scipy, params):
        self.name = name
        self.scipy = scipy
        self.params = params
        self.frozen = None


DISTS = [
    Dist("Normal", stats.norm, dict(loc=None, scale=None)),
    Dist("Log-Normal", stats.lognorm, dict(s=None, loc=None, scale=None)),
    Dist("Weibull", stats.weibull_min, dict(c=None, loc=None, scale=None)),
    Dist("Gamma", stats.gamma, dict(a=None, loc=None, scale=None)),
    Dist("Logistic", stats.logistic, dict(loc=None, scale=None)),
]


def modify_doc(doc):
    """Inclui o gráficos e os controles no curdoc do Bokeh Server."""
    plot = Plot(DISTS)
    slider = Slider(title="Number of bins", value=10, start=5, end=15, step=1)
    div = Div(text="<h3>Goodness of fit tests</h3>")
    table = Table(DISTS)

    def slider_callback(attr, old, new):
        """Função que atualiza o histograma e a CDF dos observações."""
        hist, edges = plot.update_histogram(new)
        data = plot.cumulative_source.data
        ks = []
        chi = []
        wms = []
        for dist in DISTS:
            cdf = dist.frozen.cdf
            ks.append(np.max(np.abs(cdf(data["x"]) - data["y"])))
            Ei = (cdf(edges)[1:] - cdf(edges)[:-1]) * len(plot.values)
            Oi = hist * (edges[1] - edges[0]) * len(plot.values)
            chi.append(np.sum((Ei - Oi) ** 2 / Ei))
            wms.append(np.sum((cdf(data["x"]) - data["y"]) ** 2))
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
    doc.title = "Statfit"


server = Server({"/": modify_doc})
server.start()

if __name__ == "__main__":
    print("Opening Bokeh application on http://localhost:5006/")
    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()
