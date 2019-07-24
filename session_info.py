#region imports
# BASE PYTHON
import logging
import uuid

# USER DEFINED
from Model import Model
#endregion

"""
Module dedicated to maintaining the user's session state for this flask app
"""

logger = logging.getLogger(__name__)

session_id_key = 'session_id'
user_sessions = {}


def init_session(session) :
    """
    Initializes the current user's session to map to a fresh Model instance.
    """
    
    if session_id_key not in session :
        logger.info("New user session")
        session[ session_id_key ] = str(uuid.uuid4())

    user_sessions[ session[ session_id_key ] ] = Model()

def get_user_model_from_key( session_id ) :
    """
    Retrieves the current user's model instance given their current session ID
    """
    return user_sessions[ session_id ]

def get_user_model(session) :
    """
    Retrieves the current user's model instance given their current flask session
    """
    return user_sessions[ session[ session_id_key ] ]