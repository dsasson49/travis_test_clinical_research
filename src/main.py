
# execute this script from /Users/christopherpoptic/clinical_research_workflow'

# from src import utils
#from src.utils import util
from src.utils.util import initialize_credentials
initialize_credentials()

from notebooks.chris.make_cohorts import get_filtered_patients
df = get_filtered_patients()
