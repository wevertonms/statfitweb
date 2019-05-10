# StatFit

Small python web application for statistical characterization of data using [SciPy](https://docs.scipy.org/doc/scipy/reference/tutorial/stats.html) and [Bokeh](https://bokeh.pydata.org/en/latest/).

# Using

## Install dependencies

If you use Windows, you need to install Python in your system:
 - [Windows 32 bits](https://www.python.org/ftp/python/3.7.3/python-3.7.3.exe)
 - [Windows 64 bits](https://www.python.org/ftp/python/3.7.3/python-3.7.3-amd64.exe)

After that, you need to install de dependencies using the running command bellow in cmd:

```
python3 -m pip install --user scipy bokeh
```

## Running

```
python3 -m bokeh serve --show statfit.py
```
