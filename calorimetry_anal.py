from utils import find_pandas_dataframe_names

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
            dflist.append(global_dict[k])
    else:
        dflist.append(global_dict[dfname])
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
                          description='DataFrame: ', )

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
        pass
    whichframe.observe(update_columns, names='value')

    # Data selection
    Xcoord = Dropdown(options=['Choose X-coordinate (time).'],
                           description='X-coordinate (time): ',
                           disabled = True)
    Ycoord = Dropdown(options=['Choose Y-coordinate (temperature).'],
                           description='Y-coordinate (temperature): ',
                           disabled = True)
    def trace_name_update(change):
        if change['new'] != 'Choose column for coordinate.':
            trace_name.value = Ycoord.value
        pass
    Xcoord.observe(trace_name_update,names='value')
    Ycoord.observe(trace_name_update,names='value')

    # Trace name
    trace_name = Text(placeholder = 'Trace name for legend',
                      description = 'Trace name: ',
                      disabled = True)
# TODO need to update plot if X, Y or tracename is changed...What to do
#  about axes labels?