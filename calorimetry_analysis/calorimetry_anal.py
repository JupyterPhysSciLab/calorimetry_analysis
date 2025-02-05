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
# TODO What to do about axes labels?

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
    global range_points
    range_points = []

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
                               marker_size=range_plot_marker_size,
                               name = "data")
        range_plot.data[0].on_click(update_range_point)
        pass

    def update_range_point(trace, points, selector):
        # size and color must be done separately as they may not be updated
        # in sync.
        try:
            from collections.abc import Iterable
        except ImportError as e:
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
            if c[i] == range_plot_line_color and len(range_points)<4:
                c[i] = range_plot_hilight
                s[i] = range_plot_hilight_size
                range_points.append(i)
            else:
                c[i] = range_plot_line_color
                s[i] = range_plot_marker_size
                range_points.remove(i)
        with range_plot.batch_update():
            trace.marker.color = c
            trace.marker.size = s
        pass

    def fit_line_before():
        """Takes the left two selected points and fits a line to those points
        and all in between.
        """
        from lmfit.models import LinearModel
        range_points.sort()
        df = global_dict[whichframe.value]
        rangex = df[Xcoord.value]
        rangey = df[Ycoord.value]
        tofitx = rangex[range_points[0]:range_points[1]]
        tofity = rangey[range_points[0]:range_points[1]]
        #with output:
        #    display(len(tofitx))
        fitmod = LinearModel()
        fitmod.set_param_hint("slope", vary=True, value=0.0)
        fitmod.set_param_hint("intercept", vary=True, value=0.0)
        # Do fit
        fit = fitmod.fit(tofity, x=tofitx, nan_policy="omit")
        slope = fit.params['slope'].value
        intercept = fit.params['intercept'].value
        # Add to plot
        result = rangex*slope+intercept
        range_plot.add_scatter(y=result,x=rangex,mode="lines",
                               line_color="black", name = "left slope")
        with output:
            display(print("left = " + str(slope) + "*x+" + str(intercept)))
        return slope,intercept

    def fit_line_after():
        """Takes the right two selected points and fits a line to those points
        and all in between.
        """
        from lmfit.models import LinearModel
        range_points.sort()
        df = global_dict[whichframe.value]
        rangex = df[Xcoord.value]
        rangey = df[Ycoord.value]
        tofitx = rangex[range_points[2]:range_points[3]]
        tofity = rangey[range_points[2]:range_points[3]]
        fitmod = LinearModel()
        fitmod.set_param_hint("slope", vary=True, value=0.0)
        fitmod.set_param_hint("intercept", vary=True, value=0.0)
        # Do fit
        fit = fitmod.fit(tofity, x=tofitx, nan_policy="omit")
        slope = fit.params['slope'].value
        intercept = fit.params['intercept'].value
        # Add to plot
        result = rangex*slope+intercept
        range_plot.add_scatter(y=result,x=rangex,mode="lines",
                               line_color="red", name = "right slope")
        with output:
            display(print("right = "+str(slope)+"*x+"+str(intercept)))
        return slope,intercept

    def findDT(change):
        """Find the temperature change when button clicked.
        Does nothing if there are not four selected points in `range_points`.
        """
        if len(range_points) != 4:
           return
        # fit the right and left slopes.
        slope_left, intercept_left = fit_line_before()
        slope_right, intercept_right = fit_line_after()
        # Find T change and draw vertical line at location
        # 1-estimate by finding crossing with average of the before and after
        range_points.sort()
        df = global_dict[whichframe.value]
        rangex = df[Xcoord.value]
        rangey = df[Ycoord.value]
        x_m_guess = None
        for k in range(range_points[1], range_points[2]):
            avg_slope = 0.5*(slope_left+slope_right)
            avg_int = 0.5*(intercept_left+intercept_right)
            avg = avg_slope*rangex[k]+avg_int
            if (avg <= rangey[k+1] and avg > rangey[k]) or (avg >= rangey[k+1]
                                                           and avg < rangey[k]):
                data_slope = (rangey[k+1]-rangey[k])/(rangex[k+1]-rangex[k])
                data_int = rangey[k]-data_slope*rangex[k]
                x_m_guess = (data_int-avg_int)/(avg_slope-data_slope)
        DT_guess = None
        if x_m_guess:
            DT_guess = (slope_right*x_m_guess+intercept_right-slope_left
                        *x_m_guess-intercept_left)
        with output:
            display(print('x_m_guess:' + str(x_m_guess)+' DT_guess:'+str(
                DT_guess), end=''))
        pass

    GetDT = Button(description = "Find Change in T",
                   disabled = False)
    GetDT.on_click(findDT)
    with output:
        display(whichframe,Xcoord,Ycoord,GetDT)
        display(range_plot)
    display(output)
    return