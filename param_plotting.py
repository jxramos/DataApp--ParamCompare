"""
Module dedicated to encapsulating all the data plotting functionality for the app
"""

#region imports
# BASE PYTHON
import requests

# THIRD PARTY
from bokeh.layouts  import column
from bokeh.models   import AjaxDataSource,ColumnDataSource
from bokeh.plotting import figure
#endregion


#region BOKEH SOURCE
def modify_doc1(doc):
    # get colum name from query string
    args      = doc.session_context.request.arguments
    paramName = str( args['colName'][0].decode('utf-8') )

    # get model data from Flask
    url    = "http://localhost:8080/sendModelData/%s" % paramName 
    source = AjaxDataSource( data            = dict( x=[] , y=[] ) ,
                            data_url         = url       ,
                            polling_interval = 5000      ,
                            mode             = 'replace' ,
                            method           = 'GET'     )
    # plot the model data
    plot = figure( )
    plot.circle( 'x' , 'y' , source=source , size=2 )
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