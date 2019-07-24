#region imports
# BASE PYTHON
from datetime import datetime
from enum import Enum
import logging
import os

# THIRD PARTY
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_wtf import FlaskForm
import pandas
from tornado.ioloop import IOLoop
from wtforms import FileField, SelectMultipleField, StringField, SubmitField

from bokeh.application          import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.embed                import server_document
from bokeh.server.server        import Server

# USER DEFINED
import CommonLogging
import param_plotting
import param_stats
import session_info
#endregion

"""
Data comparison web application for comparing common parameters across two independent
csv files.

Remote Repo: https://github.com/jxramos/DataApp--ParamCompare
"""

#region GLOBALS
launch_time = datetime.now()
app_name = os.path.basename( __file__ ).replace( '.py' , '' )
logger = logging.getLogger(__name__)

class ParamTypes(Enum) :
    p1 = "Param1"
    p2 = "Param2"
    p3 = "Param3"

# Flask infrastructure
flask_app = Flask(__name__)
flask_app.config['SECRET_KEY'] = 'the secret to life'
flask_app.jinja_env.trim_blocks = True
flask_app.jinja_env.lstrip_blocks = True

class CompareInputForm(FlaskForm):
    id_col = StringField("ID", default="id")
    file_x = FileField( "File X" )
    file_y = FileField( "File Y" )
    label_x = StringField('Label X')
    label_y = StringField('Label Y')

    params = SelectMultipleField( "Param Selection", choices=[ (e.name, e.value) for e in ParamTypes ] )
    stats  = SelectMultipleField( "Statistic Selection", choices=[ (e.name, e.value) for e in param_stats.StatTypes ] )
    submit = SubmitField('Submit')

# Populate some model maintained by the flask application
modelDf = pandas.DataFrame()
nData = 100
modelDf[ 'c1_x' ] = range(nData)
modelDf[ 'c1_y' ] = [ x*x for x in range(nData) ]
modelDf[ 'c2_x' ] = range(nData)
modelDf[ 'c2_y' ] = [ 2*x for x in range(nData) ]

# Bokeh infrastructure
bokeh_lin_reg_app = Application(FunctionHandler(param_plotting.lin_reg_plot))
bokeh_app2 = Application(FunctionHandler(param_plotting.modify_doc2))

io_loop = IOLoop.current()

stat_type_2_plot_route = { param_stats.StatTypes.lin_reg.name : 'bk_lin_reg_app' }

server = Server({ f'/{stat_type_2_plot_route[param_stats.StatTypes.lin_reg.name]}': bokeh_lin_reg_app ,
                  '/bkapp2' : bokeh_app2 },
                 io_loop=io_loop, allow_websocket_origin=["localhost:8080"])
server.start()
#endregion

@flask_app.route('/', methods=['GET', "POST"] )
def index():
    """
    Main page where user submits all required input to conduct a csv to csv
    comparison analysis of common columns.
    """
    logger.debug("")

    session_info.init_session( session )
    form = CompareInputForm()

    if request.method == "POST" :
        if form.errors :
            logger.debug(form.errors)
        
        # Populate model with form data
        model = session_info.get_user_model(session)
        model.load_model( form )

        # Execute parameter comparison
        model.compare_parameters()

        return redirect( url_for('summary_page' ) )
    
    return render_template( 'index.html' , form=form )

@flask_app.route( '/summary', methods=["GET"])
def summary_page() :
    """
    The top level summary page where all found parameter result comparisons are presented
    to the user.
    """
    logger.debug("")
    model = session_info.get_user_model(session)
    return render_template( "summary_page.html" , model=model ,
                                                  stat_types=param_stats.StatTypes )

@flask_app.route( '/data/<table_type>', methods=["GET"])
def data_table_page( table_type ) :
    """
    Renders table presentation of data
    """
    logger.debug( f"table_type={table_type}" )
    model = session_info.get_user_model(session)

    # select table type's corresponding data
    if table_type == "x" :
        df = model._dfX
    elif table_type== "y" :
        df = model._dfY
    elif table_type == "merged" :
        df = model.dfMerged
    elif table_type == "param" :
        param = request.args["param"]
        logger.debug(f"param={param}")
        df = model.dfMerged[[ model.id_col , f"{param}_x", f"{param}_y"]]
    else :
        logger.debug()
        raise ValueError( f"Unrecognized table_type={table_type}" )
    
    return f"<pre>{df.to_string()}</pre>" # TODO replace with template

@flask_app.route( '/plot/<stat_type>', methods=["GET"])
def plot_page( stat_type ) :
    """
    Renders table presentation of data
    """
    logger.debug( f"stat_type={stat_type}" )
    param = request.args["param"]

    script = server_document( url=f'http://localhost:5006/{stat_type_2_plot_route[stat_type]}',
                              arguments={'param' : param ,
                                         'stat_type' : stat_type ,
                                         'session_id' : session[ session_info.session_id_key ] }
                            )

    return render_template('plot_page.html',
                           script=script ,
                           param=param ,
                           stat_type=param_stats.StatTypes[stat_type] )

@flask_app.route( '/app2/<colName>' , methods=['GET'] )
def bkapp2_page( colName ) :
    script = server_document( url='http://localhost:5006/bkapp2', arguments={'colName' : colName } )
    return render_template("embed.html", script=script)

if __name__ == '__main__':
    from tornado.httpserver import HTTPServer
    from tornado.wsgi import WSGIContainer
    from bokeh.util.browser import view

    launch_time_str = datetime.strftime( launch_time , '%Y-%m-%d_%H.%M.%S' )
    CommonLogging.setup_logger( os.getcwd() , launch_time_str , app_name )

    logger.info('Opening Flask app with embedded Bokeh application on http://localhost:8080/')

    # This uses Tornado to server the WSGI app that flask provides. Presumably the IOLoop
    # could also be started in a thread, and Flask could server its own app directly
    http_server = HTTPServer(WSGIContainer(flask_app))
    http_server.listen(8080)

    io_loop.add_callback(view, "http://localhost:8080/")
    io_loop.start()