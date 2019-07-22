#region imports
# BASE PYTHON
import logging

# THIRD PARTY
import pandas
#endregion

logger = logging.getLogger(__name__)

class Model() :
    def __init__(self) :
        logger.debug("")
        # Inputs
        self.file_name_x = ""
        self.file_name_y = ""
        self.label_x = ""
        self.label_y = ""
        self._dfX = None
        self._dfY = None
        self._dfMerged = None
        self._params = []
        self._stats = []
        self.id_col = ""

        # Outputs
        self.param_results = {}

    def load_model(self, form ) :
        """
        Loads the user's model instance with all relevant inputs from the html form
        """
        logger.debug("")
        self.id_col = form.id_col.data
        self.file_name_x = form.file_x.data.filename
        self.file_name_y = form.file_x.data.filename
        self._dfX = pandas.read_csv( form.file_x.raw_data[0] )
        self._dfY = pandas.read_csv( form.file_y.raw_data[0] )
        self._params = form.params.data
        self._stats = form.stats.data

        # Use filenames if no labels were explicitly given
        self.label_x = form.label_x.data if form.label_x.data else self.file_name_x
        self.label_y = form.label_y.data if form.label_y.data else self.file_name_y

    def compare_parameters(self) :
        """
        """
        logger.info("Compare Results...")
        self.merge_data()

    def merge_data(self) :
        """
        """
        logger.debug("")
        if self.id_col not in self._dfX :
            raise ValueError( f"id_col={self.id_col} not in X-input" )
        if self.id_col not in self._dfY :
            raise ValueError( f"id_col={self.id_col} not in Y-input" )

        self.dfMerged = self._dfX.merge( self._dfY ,  on=self.id_col )