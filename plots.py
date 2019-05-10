#!/usr/bin/env python
# coding: utf-8


import numpy as np
from scipy import stats
import scipy.special

from bokeh.plotting import figure, show, save, output_file
from bokeh.models import Panel, Tabs
from bokeh.layouts import layout

from custom_figure import CustomFigure, colors


def cdf(hist, edges):
    x = [edges[i // 2] for i in range(2 * len(edges[:-1]))]
    x.append(edges[-1])
    cdf = np.cumsum(hist * (edges[1] - edges[0]))
    y = [cdf[(i - 1) // 2] for i in range(2 * len(cdf))]
    y[0] = 0
    y.append(cdf[-1])
    return x, y


def basic_figure(measured, num_bins):
    pdf_plot = CustomFigure("Probability Density", ("Values", "Relative frequency"))
    cdf_plot = CustomFigure("Cumulative Probability", ("Values", "Relative frequency"))
    if len(measured) > 1:
        x = np.linspace(min(measured), max(measured), len(measured))
        hist, edges = np.histogram(measured, density=True, bins=num_bins)
        cdf_x, cdf_y = cdf(hist, edges)
        pdf_plot.quad(
            top=hist,
            bottom=0,
            left=edges[:-1],
            right=edges[1:],
            line_color="white",
            legend="Observed",
            color=colors[0],
        )
        cdf_plot.line(
            x=cdf_x, y=cdf_y, legend="Observed", line_width=2, color=colors[0]
        )
        pdf_plot.legend.click_policy = cdf_plot.legend.click_policy = "hide"
        pdf_plot.legend.location = cdf_plot.legend.location = "top_left"
    return Tabs(
        tabs=[
            Panel(child=layout(pdf_plot, sizing_mode="scale_width"), title="PDF"),
            Panel(child=layout(cdf_plot, sizing_mode="scale_width"), title="CDF"),
        ]
    )


def main(measured):
    fig = basic_figure(measured)
    pdf_plot, cdf_plot = fig.tabs[0].child.children[0], fig.tabs[1].child.children[0]
    params = dict(
        norm=dict(loc=None, scale=None),
        lognorm=dict(s=None, loc=None, scale=None),
        weibull_min=dict(c=None, loc=None, scale=None),
        gamma=dict(a=None, loc=None, scale=None),
    )
    if measured:
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
    output_file("full_plot.html", title="Statfit", mode="inline")
    show(fig)


if __name__ == "__main__":
    main(np.random.normal(300, 0.5, size=100))
    # main([])
