#region imports
import logging
import logging.handlers
import os
import sys
#endregion

MAJOR_DIV = "=" * 325
MINOR_DIV = '-' * 180

root_logger = logging.getLogger()

def setup_logger( output_directory , launch_time , app_name ) :
    """ 
    Sets up the debug log file and streamhandler for console output to the root logger
    which allows arbitrary project wide loggers to propagate their log messages for the
    root logger to take care of.

    Parameters
    ----------
    output_directory : str
        The output directory where debug logs will be written to disk under the LOGS subdirectory.
    launch_time : str
        The time which the application was launched
    app_name : str
        The name of the application requesting logging resources, will makeup part of the
        debug log filename.
    """

    # Guard Clause: enforce single setup through application lifetime.
    if root_logger.handlers :
        root_logger.debug( "debug logger already configured.")
        return

    # Create LOGS subfolder if it doesn't already exist
    logs_subdir = os.path.join( output_directory , "LOGS")
    if not os.path.exists( logs_subdir ) :
        os.makedirs( logs_subdir )

    # Change root logger's level from warning to widest level in order to direct
    # logging propagation from any module up to root logger
    root_logger.setLevel( logging.DEBUG )

    # Add filehandler for debug log
    log_file_path = os.path.join( logs_subdir , f"{launch_time}__DEBUG_LOG--{app_name}.log" )
    max_log_size = 5e+7 # 50 MB roll
    file_handler = logging.handlers.RotatingFileHandler( log_file_path , maxBytes=max_log_size , backupCount=10 )
    file_handler.setLevel( logging.DEBUG )
    debug_formatter = logging.Formatter("%(asctime)s - %(threadName)s [%(levelname)s] %(module)s.%(funcName)s  %(message)s")
    file_handler.setFormatter( debug_formatter )
    root_logger.addHandler( file_handler )

    # Add stream output handler for status updates visible at the console
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel( logging.INFO )
    info_formatter = logging.Formatter( "%(message)s" )
    stream_handler.setFormatter( info_formatter )
    root_logger.addHandler( stream_handler )

    # Open debug log
    root_logger.debug( f"Application '{app_name}' launched at {launch_time}" )

def unhandled_exc_logger( exc_type , exc_value , exc_traceback ):
    """
    Callback for sys module's excepthook to record any unhandled exceptions
    into the debug log for failure analysis of the soon to crash application
    """
    root_logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = unhandled_exc_logger