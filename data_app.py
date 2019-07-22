#region imports
# BASE PYTHON
from datetime import datetime
from enum import Enum
import logging
import os

# THIRD PARTY
from flask import Flask, jsonify, redirect, render_template, request, url_for
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
#endregion

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
    file_x = FileField( "File X" )
    file_y = FileField( "File Y" )
    name_x = StringField('Source X')
    name_y = StringField('Source Y')

    params = SelectMultipleField( "Param Selection", choices=[ (e.name, e.value) for e in ParamTypes ] )
    submit = SubmitField('Submit')

# Populate some model maintained by the flask application
modelDf = pandas.DataFrame()
nData = 100
modelDf[ 'c1_x' ] = range(nData)
modelDf[ 'c1_y' ] = [ x*x for x in range(nData) ]
modelDf[ 'c2_x' ] = range(nData)
modelDf[ 'c2_y' ] = [ 2*x for x in range(nData) ]

# Bokeh infrastructure
bokeh_app1 = Application(FunctionHandler(param_plotting.modify_doc1))
bokeh_app2 = Application(FunctionHandler(param_plotting.modify_doc2))

io_loop = IOLoop.current()

server = Server({'/bkapp1': bokeh_app1 ,
                 '/bkapp2' : bokeh_app2 },
                 io_loop=io_loop, allow_websocket_origin=["localhost:8080"])
server.start()
#endregion

@flask_app.route('/', methods=['GET', "POST"] )
def index():
    form = CompareInputForm()

    if request.method == "POST" :
        if form.errors :
            logger.debug(form.errors)
        # form.validate_on_submit()
        return redirect( url_for('summary_page') )

    
    return render_template( 'index.html' , form=form )

@flask_app.route( '/summary', methods=["GET"])
def summary_page() :
    return "Summary Page"

@flask_app.route( '/app1/<colName>' , methods=['GET'] )
def bkapp1_page( colName ) :
    script = server_document( url='http://localhost:5006/bkapp1' , arguments={'colName' : colName } )
    return render_template("embed.html", script=script)

@flask_app.route( '/app2/<colName>' , methods=['GET'] )
def bkapp2_page( colName ) :
    script = server_document( url='http://localhost:5006/bkapp2', arguments={'colName' : colName } )
    return render_template("embed.html", script=script)

@flask_app.route('/sendModelData/<colName>' , methods=['GET'] )
def sendModelData( colName ) :
    x = modelDf[ colName + "_x" ].tolist()
    y = modelDf[ colName + "_y" ].tolist()
    return jsonify( x=x , y=y )

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