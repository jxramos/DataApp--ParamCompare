"""
Module dedicated to encapsulating all the data plotting functionality for the app
"""

#region imports
# BASE PYTHON
import logging
import requests

# THIRD PARTY
from bokeh.layouts  import column
from bokeh.models   import AjaxDataSource, ColumnDataSource, HoverTool
from bokeh.plotting import figure

# USER DEFINED
import session_info
#endregion

logger = logging.getLogger(__name__)

#region BOKEH SOURCE
def lin_reg_plot(doc):
    logger.debug("")

    # get param and session id from query string
    args      = doc.session_context.request.arguments
    param = str( args['param'][0].decode('utf-8') )
    stat_type = str( args['stat_type'][0].decode('utf-8') )
    session_id = str( args['session_id'][0].decode('utf-8') )
    logger.debug(f"param={param}, session_id={session_id}")

    # Construct ColumnDataSource
    param_x = f"{param}_x"
    param_y = f"{param}_y"
    model = session_info.get_user_model_from_key(session_id)
    df = model.dfMerged[[ model.id_col , param_x , param_y ]]
    cds = ColumnDataSource(df)

    # Determine the bounds of the data
    x_extrema = [ model.dfMerged[param_x].min() , model.dfMerged[param_x].max() ]
    x_range = x_extrema[1] - x_extrema[0]
    x_margin = 0.02 * x_range

    # Construct plot figure
    plot = figure( title = f'{param}' ,
                   x_axis_label=model.label_x,
                   y_axis_label=model.label_y)

    # Render identity line y=x
    x_lr = [ x_extrema[0] - x_margin , x_extrema[1] + x_margin ]
    plot.line( x_lr , x_lr , color='lightgray' , line_dash='dashed', name='identity')

    # Render the linear regression line
    lin_reg_result = model.param_results[param][stat_type]
    y_lr = [ lin_reg_result['slope'] * x_lr[0] + lin_reg_result['intercept'] ,
             lin_reg_result['slope'] * x_lr[1] + lin_reg_result['intercept'] ]
    plot.line( x_lr , y_lr , color='black' , name='LinReg')

    # Render the raw parameter data
    plot.circle( param_x,
                 param_y,
                 source=cds,
                 color='blue',
                 size = 2,
                 name='ParamData')

    # Configure tooltips for interactivity
    plot.add_tools( HoverTool(tooltips=[ ("ID"     , f"@{model.id_col}" ),
                                         ( param_x , f"@{param_x}"      ),
                                         ( param_y , f"@{param_y}"      ),
                                         ("(x,y)"  , "($x, $y)"         ),
                                         ("index"  , "$index"           ),
                                       ]))

    doc.add_root(column(plot))

def modify_doc2(doc):
    # get column name from query string
    args    = doc.session_context.request.arguments
    colName = str( args['colName'][0].decode('utf-8') )

    # get model data from Flask
    url = "http://localhost:8080/sendModelData/%s" % colName
    #pdb.set_trace()
    res = requests.get( url , timeout=None , verify=False )
    print( "CODE %s" % res.status_code )
    print( "ENCODING %s" % res.encoding )
    print( "TEXT %s" % res.text )
    data = res.json()

    # plot the model data
    plot = figure()
    plot.circle( 'x' , 'y' , source=data , size=2 )
    doc.add_root(column(plot))
#endregion