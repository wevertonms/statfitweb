"""Modelos Bokeh customizados."""
import base64
import io

import bokeh.plotting as plt
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.models.widgets import Button, Paragraph
from bokeh.palettes import Category10_10 as colors  # pylint: disable=no-name-in-module
from bokeh.plotting import figure, output_file
from bokeh.server.server import Server


def Figure(title, axis_labels, **kw):
    """Figura Bokeh básica customizada.
    
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
    )
    fig_opts.update(**kw)
    fig = figure(**fig_opts)
    return fig


def UploadButton(label, callback, **kw):
    """Botão para upload de um arquivo.
    
    Args:
        label (str): 
        callback (function): função a ser chamada.
        Os mesmo para um botão qualquer: label, button_type,...
    """
    button = Button(label=label, **kw)
    file_source = ColumnDataSource({"file_contents": [], "file_name": []})
    # with open("upload_button_callback.js", "r") as f:
    code = """
    function read_file(filename) {
        var reader = new FileReader();
        reader.onload = load_handler;
        reader.onerror = error_handler;
        // readAsDataURL represents the file's data as a base64 encoded string
        reader.readAsDataURL(filename);
    }
    function load_handler(event) {
        var b64string = event.target.result;
        file_source.data = { 'file_contents': [b64string], 'file_name': [input.files[0].name] };
        file_source.trigger("change");
    }
    function error_handler(evt) {
        if (evt.target.error.name == "NotReadableError") {
            alert("Can't read file!");
        }
    }
    var input = document.createElement('input');
    input.setAttribute('type', 'file');
    input.onchange = function () {
        if (window.FileReader) {
            read_file(input.files[0]);
        } else {
            alert('FileReader is not supported in this browser');
        }
    }
    input.click();
    """
    button.callback = CustomJS(args=dict(file_source=file_source), code=code)
    # Define mma função a ser chamada após o upload do arquivo.
    def upload_callback(attr, old, new):
        raw_contents = file_source.data["file_contents"][0]
        contents = raw_contents.split(",", 1)
        file_contents = base64.b64decode(contents[1])
        new = io.BytesIO(file_contents)
        callback(attr, old, new)

    file_source.on_change("data", upload_callback)
    return button
