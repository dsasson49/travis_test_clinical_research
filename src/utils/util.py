import os
from pathlib import Path
import logging
import logging.config


BASE_DIR = Path("/Users/christopherpoptic/clinical_research_workflow")
# DEFAULT_LEVEL = logging.INFO
# LOGGING_FORMAT = '%(asctime)s %(levelname)s:%(message)s'


def initialize_credentials():
    """
    Call this function to load your NFERENCE_USER and NFERENCE_TOKEN credentials
    from thte credentials.yml file so you can make API calls with the SDK.

    """

    # import credentials
    # https://kedro.readthedocs.io/en/stable/04_kedro_project_setup/02_configuration.html
    from kedro.config import ConfigLoader

    # conf_paths = ["../conf/base", "../conf/local"]
    conf_paths = [Path(BASE_DIR, "conf/local")]
    print(f"conf_paths are:  {conf_paths}")

    print
    conf_loader = ConfigLoader(conf_paths)
    credentials = conf_loader.get("credentials*", "credentials*/**")

    # Environment setup
    os.environ["X_NFER_BASEURL"] = "https://preview.nferx.com"
    os.environ["NFERENCE_USER"] = credentials["nfer_access_key"]  # "yash@nference.net"
    os.environ["NFERENCE_TOKEN"] = credentials["nfer_secret_key"]  # "<api_token>"

    print("Loaded credentials.  Nference SDK ready to use.\n")
