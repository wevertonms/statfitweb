#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Small python web application for statistical characterization."""

import base64
import io

import numpy as np
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models.widgets import Div, FileInput, Slider
from bokeh.server.server import Server

from plot import Plot, fit_table
from stats import DISTS, chi_squared, kolmogorov_smirnov, weverton


def make_layout():
    """Inclui o gráficos e os controles no curdoc do Bokeh Server."""
    plot = Plot(DISTS)
    numbins_slider = Slider(title="Number of bins", value=10, start=5, end=15, step=1)
    div = Div(text="<b>Goodness of fit tests (p-values)</b>")
    table = fit_table([dist.name for dist in DISTS])

    def numbins_slider_callback(attr, old, new):  # pylint: disable=unused-argument
        """Função que atualiza o histograma e a CDF dos observações."""
        hist, edges = np.histogram(plot.values, density=True, bins=new)
        plot.update_histogram(hist, edges)
        data = plot.cumulative_source.data
        chi = [chi_squared(plot.values, dist.cdf, new) for dist in DISTS]
        ks = [kolmogorov_smirnov(plot.values, dist.cdf) for dist in DISTS]
        wms = [weverton(dist.cdf, data["x"], data["y"]) for dist in DISTS]
        table.source.data.update(ks=ks, chi=chi, wms=wms)  # pylint: disable=no-member

    def upload_callback(attr, old, new):
        """Função que atualiza os dados do plot com os dados do arquivo enviado."""
        file_contents = base64.b64decode(new)
        file_contents_bytes = io.BytesIO(file_contents)
        observed = np.loadtxt(file_contents_bytes)
        plot.update_data(observed)
        numbins_slider.value = plot.num_bins
        numbins_slider.end = len(observed) // 3
        numbins_slider_callback(attr, old, numbins_slider.value)

    button = FileInput()
    button.on_change("value", upload_callback)
    numbins_slider.on_change("value", numbins_slider_callback)
    controls = column(button, numbins_slider, div, table, width=300)
    return row(controls, plot.layout, sizing_mode="scale_height")


def modify_doc(doc):
    """Inclui o gráficos e os controles no curdoc do Bokeh Server."""
    doc.add_root(make_layout())
    doc.title = "Statfit Web"


if __name__ == "__main__":
    SERVER = Server({"/": modify_doc})
    SERVER.start()
    print(f"Opening Bokeh application on http://localhost:5006/")
    SERVER.io_loop.add_callback(SERVER.show, "/")
    SERVER.io_loop.start()
else:
    curdoc().add_root(make_layout())
    curdoc().title = "Statfit Web"
