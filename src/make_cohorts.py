import pandas as pd
from datetime import datetime

from nferx_sdk.data_sources import RecordsAPIWrapper, ClinicalTrialsAPIWrapper
from nferx_sdk.utils.query import inQuery, andQuery


# Set the NFERENCE_USER and NFERENCE_TOKEN access keys
from utils.util import initialize_credentials

initialize_credentials()

# initialize_credentials()

DISEASE_NAME = "CML"
START_TIMESTAMP = 74863940
END_TIMESTAMP = 46581720
NUM_MONTHS = 3
UNIT_NAME = "months"

drugs = [
    "venlafaxine",
    "Sertraline",
    "Paroxetine",
    "milnacipran",
    "levomilnacipran",
    "Fluvoxamine",
    "Fluoxetine",
    "Escitalopram",
    "duloxetine",
    "Desvenlafaxine",
    "Citalopram",
]

rec = RecordsAPIWrapper()
cml_codes_list = rec.getDiagnosticCodesFromDisease(DISEASE_NAME)


def get_filtered_patients(
    icd_code_list: list = cml_codes_list,
    num_months: int = NUM_MONTHS,
    occurrence_count: int = 2,
    medication_query: str = None,
) -> pd.DataFrame:
    """Given a list of ICD codes, a temporal window (start and end timestamps), an occurrence count,
    return list of patient_IDs and timestamps

    Args:
        icd_code_list (list): [description]
        start_timestamp (datetime): [description]
        end_timestamp (datetime): [description]
        occurrence_count (int): Minimum numnber of occurrences for one of the ICD codes to occur.  Default is 2.
        medication_query (str): (optional): default None

    Returns:
        df: Cohort list of Patient IDs matching the filtering criteria specified via arguments.
    """

    # (Optional) get the medications query
    meds_query = inQuery(
        [
            "medication_generic_name",
            "order_description",
            "med_generic",
            "order_drugs",
            "meds_drugs",
            "med_generic",
            "med_name_description",
            "med_generic_name_description",
        ],
        drugs,
    )
    codes_query = inQuery("diagnosis_code", icd_code_list)
    query = andQuery(meds_query, codes_query)

    cohort1 = rec.makeCohort(
        cohortName="cohort_name_here",
        cohortSpecifier=query,
        timeWindow=num_months,
        unit=UNIT_NAME,
    )

    cohort1.initDump(
        cohortProjector=[
            "patient_id",
            "timestamp",
            "diagnosis_code",
            "meds_drugs",
            "disease",
        ]
    )

    if cohort1.advanceDF():
        df = cohort1.getDF()
        # display(df)

    return df


if __name__ == "__main__":
    print("Running get_filtered_patients().  Stand by...\n")
    cohort_df = get_filtered_patients()
    print("Finished running get_filtered_patients() function.\n")
    print(cohort_df.shape)
