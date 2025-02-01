import pandas


def Cal_Anal_GUI(dfname = None):
    """Graphical interface for selecting where a temperature change occurs
    and where to fit the before and after lines used to account for
    temperature changes from heat leakage or stirring.

    :param dfname: string value for name of dataframe to use. If not provided
     will search the user namespace for dataframes and provide a menu for
     selecting one.
    :return:
    """
    from ipywidgets import Layout, Box, HBox, VBox, GridBox, Tab, \
        Accordion, Dropdown, Label, Text, Button, Checkbox, FloatText, \
        RadioButtons, BoundedIntText, Output
    from ipywidgets import HTML as richLabel
    from ipywidgets import HTMLMath as texLabel
    from IPython.display import display, HTML
    from IPython import get_ipython
    from lmfit import models
    from .utils import find_pandas_dataframe_names
    import plotly.graph_objects as go

    global_dict = get_ipython().user_ns
    dflist = []
    if not dfname:
        for k in find_pandas_dataframe_names():
            dflist.append(k)
    else:
        dflist.append(dfname)
    output = Output()
    with output:
        display(HTML(
            "<h3 id ='Cal_Anal_GUI' style='text-align:center;'>Calorimetry "
            "Analysis GUI</h3> <div style='text-align:center;'>"
            "<span style='color:green;'>Steps with a * are required.</span> "))

    longdesc = {'description_width': 'initial'}

    # DataFrame selection
    tempopts = []
    tempopts.append('Choose data set.')
    for k in dflist:
        tempopts.append(k)
    whichframe = Dropdown(options=tempopts,
                          description='DataFrame: ',
                          style=longdesc)

    def update_columns(change):
        if change['new'] == 'Choose data set.':
            Xcoord.disabled = True
            Ycoord.disabled = True
            return
        df = global_dict[whichframe.value]
        tempcols = df.columns.values
        tempopt = ['Choose column for coordinate.']
        for k in tempcols:
            if df[k].dtype != 'O':
                tempopt.append(k)
        Xcoord.options = tempopt
        Xcoord.value = tempopt[0]
        Ycoord.options = tempopt
        Ycoord.value = tempopt[0]
        Xcoord.disabled = False
        Ycoord.disabled = False
        return

    whichframe.observe(update_columns, names='value')

    # Data selection
    Xcoord = Dropdown(options=['Choose X-coordinate (time).'],
                           description='X-coordinate (time): ',
                           disabled = True,
                           style=longdesc)
    Ycoord = Dropdown(options=['Choose Y-coordinate (temperature).'],
                           description='Y-coordinate (temperature): ',
                           disabled = True,
                           style=longdesc)
    def trace_name_update(change):
        if change['new'] != 'Choose column for coordinate.':
            trace_name.value = Ycoord.value
        if Xcoord.value != 'Choose column for coordinate.' and Ycoord.value \
                != 'Choose column for coordinate.':
            range_plot_init()
        pass

    Xcoord.observe(trace_name_update,names='value')
    Ycoord.observe(trace_name_update,names='value')

    # Trace name
    trace_name = Text(placeholder = 'Trace name for legend',
                      description = 'Trace name: ',
                      disabled = True)
# TODO need to update plot if X, Y or tracename is changed...What to do
#  about axes labels?

    global range_plot
    range_plot = go.FigureWidget(layout_template='simple_white')
    global range_plot_line_color
    range_plot_line_color = 'blue'
    global range_plot_hilight
    range_plot_hilight = 'cyan'
    global range_plot_marker_size
    range_plot_marker_size = 6
    global range_plot_hilight_size
    range_plot_hilight_size = 20
    global ranges
    ranges = []

    def range_plot_init():
        """Initialize the range plot with the latest data choice"""
        # TODO I think this duplicates  update_range_plot()
        df = global_dict[whichframe.value]
        rangex = df[Xcoord.value]
        rangey = df[Ycoord.value]
        range_plot.data = []
        c = []
        s = []
        range_plot.add_scatter(x=rangex, y=rangey, mode='markers',
                               line_color=range_plot_line_color,
                               marker_size=range_plot_marker_size)
        range_plot.data[0].on_click(update_range_point)
        pass

    def update_range_point(trace, points, selector):
        # size and color must be done separately as they may not be updated
        # in sync.
        try:
            from collections.abc import Iterable
        except ImportError(e):
            from collections import Iterable
        if not isinstance(trace['marker']['size'], Iterable):
            s = [range_plot_marker_size] * len(trace['x'])
        else:
            s = list(trace['marker']['size'])
        if (not isinstance(trace['marker']['color'], Iterable)) or isinstance(
                trace['marker']['color'], str):
            c = [range_plot_line_color] * len(trace['x'])
        else:
            c = list(trace['marker']['color'])
        for i in points.point_inds:
            if c[i] == range_plot_line_color:
                c[i] = range_plot_hilight
                s[i] = range_plot_hilight_size
            else:
                c[i] = range_plot_line_color
                s[i] = range_plot_marker_size
        with range_plot.batch_update():
            trace.marker.color = c
            trace.marker.size = s
        pass

    with output:
        display(whichframe,Xcoord,Ycoord)
        display(range_plot)
    display(output)
    return