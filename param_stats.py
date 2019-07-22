#region imports
# BASE PYTHON
from enum import Enum
import logging

# THIRD PARTY
from scipy import stats
#endregion

logger = logging.getLogger(__name__)

class StatTypes(Enum) :
    lin_reg = "Linear Regression"
    bias = "Bias Plot"
    t_test = "t-Test"


def linear_regression( param , x , y ) :
    """
    Calculates the linear regression (least squares fit) between the
    data x and y
    """
    logger.debug(f"param={param}")
    slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)

    lin_reg_result = { 'slope'    : slope, 
                       'intercept': intercept,
                       'r_value'  : r_value,
                       'p_value'  : p_value,
                       'std_err'  : std_err } 

    return lin_reg_result

def students_t_test( param , x , y ) :
    """
    Calculates the students t-test between the data x and y
    """
    logger.debug(f"param={param}")
    t_stat, p_val = stats.ttest_ind(x, y, equal_var=False)

    t_test_result = { 't_stat' : t_stat ,
                      'p_val'  : p_val  }
    return t_test_result