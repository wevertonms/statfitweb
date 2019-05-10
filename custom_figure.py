"""Figura Bokeh básica customizada."""

import bokeh.plotting as plt
from bokeh.palettes import Category10_10 as colors  # pylint: disable=no-name-in-module
from bokeh.plotting import Figure, output_file


class CustomFigure(Figure):
    """Figura Bokeh básica customizada."""

    def __init__(self, title, axis_labels, **kw):
        """Construtor.

        Args:
            title (str): título da figura.
            axis_labels (list): lista com o títulos dos eixos: (x, y)
        """
        fig_opts = dict(
            title=title,
            x_axis_label=axis_labels[0],
            y_axis_label=axis_labels[1],
            tooltips=[(axis_labels[1], "@y"), (axis_labels[0], "@x")],
            sizing_mode="stretch_both",
            tools="wheel_zoom,pan,hover,reset,save",
            active_scroll="wheel_zoom",
            toolbar_location="above",
            output_backend="webgl",
        )
        fig_opts.update(**kw)
        self.__dict__.update(Figure(**fig_opts).__dict__)
        self.__view_model__ = "Plot"
        self.__subtype__ = "Figure"

    def lines(self, x_list, y_list, legends, **kw):
        """Plot um conjunto de dados numa figura Bokeh.

        Args:
            x_list (list): lista de valores de x.
            y_list (list): lista de valores de y.
            legends (list): lista de nome para as legendas (default: {[""]})
        """
        for x, y, legend, color in zip(x_list, y_list, legends, colors):
            self.line(x=x, y=y, legend=legend, color=color, line_width=2, **kw)
        self.legend.click_policy = "hide"

    def save(self, folder_path="./"):
        """Salva o plot em um arquivo html.

        Args:
            folder_path (str): caminho da pasta para onde salvar o arquivo.
        """
        title = self.title.text  # pylint: disable=no-member
        output_file(
            filename=f"{folder_path}{title.lower().replace(' ', '_')}.html",
            title=title,
            mode="inline",
        )
        plt.save(self)

    def show(self):
        """Exibe a figura em html no navegador."""
        plt.show(self)