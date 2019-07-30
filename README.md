# DataApp--ParamCompare
A simple Flask application demonstrating data navigation and comparison capabilities between two data sources.


# Running the app
The main entry point for the app is found in `data_app.py` and can be ran by simply invoking that file from the command line

    python data_app.py
    
Shortly after running the app the default browser will launch with a new tab where the app first renders the inputs page webform. This will all be running under a localhost context at port 8080. At this point the user can select any two csv files which have column headers in common and each with a sample ID column identified by the ID text field of the web form.

There are two sample csv files (`1.x.csv, 1.y.csv`) under the `/test/test_data/` folder which can be used to demonstrate with.
