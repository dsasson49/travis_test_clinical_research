# -*- coding: utf-8 -*-
import numpy as np
from nferx_sdk.data_sources import RecordsAPIWrapper
from nferx_sdk.utils.query import *
from variables import *
from cohorts import *
import time
import datetime

rec = RecordsAPIWrapper()

def create_cohort(clinical_cohort):
    '''
    Creates cohort from clinical cohort object

    Parameters
    ----------
    clinical_cohort : Clinical Cohort object
    Returns
    -------
    cohort: list of patients that belong to the cohort

    '''
    df_from_variable = []
    study_window = [convert_to_unix(element) for element in clinical_cohort.study_window]
    for variable in clinical_cohort.clinical_variable:
        df_from_constraint = []
        for item in list(variable.constraint.items()):
            for constraint in item[1]:
                df = create_query_from_constraint(variable.name, variable, constraint, item[0], study_window)
                df_from_constraint.append(df)
        df_from_variable.append(find_intersection(inclusion_or = df_from_constraint))
    inclusion_variable = []
    exclusion_variable = []
    for counter, df in enumerate(df_from_variable):
        if clinical_cohort.variable_category[counter] == "inclusion":
            inclusion_variable.append(df)
        elif clinical_cohort.variable_category[counter] == "exclusion":
            exclusion_variable.append(df)
    return find_intersection(inclusion_and = inclusion_variable, exclusion = exclusion_variable, is_df = False)

def create_query_from_constraint(disease_name, variable, variable_constraint, constraint_type, study_window):
    '''
    Creates a dataframe from a variable constrain

    Parameters
    ----------
    disease_name : str
        Name of disease.
    variable : clinical variable
        clinical variable object.
    variable_constraint : constraint (example: [[2, 0, 365], mdd_codes])
        Variable constraint defining a cohort
    constraint_type : str
        "count", "time", ...
    study_window : list
        study window in unix (ie. [121212122, 1212121334])

    Returns
    -------
    Dataframe of cohort defined by constraint

    '''
    category_to_col_head = {"drug": "meds_drugs", "dx": "diagnosis_code"}
    if constraint_type == "time":
        cohort = rec.makeCohort(disease_name, cohortSpecifier = query_sdk(disease_name, [get_code_type(variable_constraint[1]), get_code_type(variable_constraint[2])], [variable_constraint[1], variable_constraint[2]], study_window))
    if constraint_type == "count":
        cohort = rec.makeCohort(disease_name, cohortSpecifier = query_sdk(disease_name, [get_code_type(variable_constraint[1])], [variable_constraint[1]], study_window))
    cohort_df = pd.DataFrame()
    columns = ['patient_id','timestamp', "diagnosis_code", "meds_drugs"]
    cohort.initDump(cohortProjector=columns)
    ii = 0
    while cohort.advanceDF():
        ii+=1
        df = cohort.getDF() # Gets a new chunk each time called
        cohort_df = cohort_df.append(df)
    sorted_df=cohort_df.sort_values(by=['patient_id','timestamp'])
    if constraint_type == "time":
        event_col_head = [category_to_col_head[variable.get_subvariable_dict_from_list(variable_constraint[1])['category']], category_to_col_head[diabetes.get_subvariable_dict_from_list(variable_constraint[2])['category']]]
        return events_occur_multiple(sorted_df, event_col_head, [variable_constraint[1], variable_constraint[2]], True, variable_constraint[0][0], variable_constraint[0][1])
    if constraint_type == "count":
        event_col_head = [category_to_col_head[variable.get_subvariable_dict_from_list(variable_constraint[1])['category']] for ii in range(variable_constraint[0][0])]
        event_criteria = [variable_constraint[1] for ii in range(variable_constraint[0][0])]
        return events_occur_multiple(sorted_df, event_col_head, event_criteria, False, variable_constraint[0][1], variable_constraint[0][2])

def query_sdk(disease_name, events, event_criteria, study_window):
    '''
    Queries SDK to form preliminary temporally unfiltered cohort. 
    
    Inputs:
    disease_name (str): the name of the disease. Can be used to get diagnostic codes if necessary
    events (list): list of event types ("diagnosis", "medication")
    event_criteria (list of lists): list of lists of criteria (diagnostic codes or medication names)
    study_window (list): [start of study in unix, end of study in unix]
    
    Outputs:
    cohort (dataframe): Dataframe of the patients that fulfill the criteria. Will be filtered further by temoral criterial.
    '''
    if len(events) == 1:
        query = andQuery(create_query(events[0], event_criteria[0]), rangeQuery("timestamp", study_window[0], study_window[1]))
        
    if len(events) == 2:
        query = andQuery(orQuery(create_query(events[0], event_criteria[0]), create_query(events[1], event_criteria[1])), rangeQuery("timestamp", study_window[0], study_window[1]))
    
    if len(events) == 3:
        query = andQuery(orQuery(create_query(events[0], event_criteria[0]), create_query(events[1], event_criteria[1]), create_query(events[2], event_criteria[2])), rangeQuery("timestamp", study_window[0], study_window[1]))
        
    return query

def create_query(event, event_criteria):
    if event == "diagnosis":
        return inQuery("diagnosis_code", event_criteria)
    if event == "medication":
        drug_list = event_criteria
        #drug_list = []
        #for drug in event_criteria:
           # drug_list += list(rec.getSynonyms(drug)['name'])
        return inQuery("meds_drugs", drug_list)
    
def get_code_type(codes):
    '''
    Returns "medication" or "diagnosis" given list of codes
    input:
    codes (lst): list of codes
    '''
    if len(codes):
        if codes[0].isalpha():
            return "medication"
        else:
            return "diagnosis"
    else:
        return ""
    
def events_occur_multiple(sorted_df_pre_filt, event_col_head, event_criteria, order_matters, minimum_gap, max_gap):
    """
    Filters sorted df to only include patients that fulfill some temporal criterium (has x medication within 6 months of y diagnosis). 
    Inputs:
    sorted_df_pre_filt (df): Dataframe of patients queried for either of the criteria (has a dx code or a medication within study window) sorted by timestamp and patient id
    event_col_head (lst): list of column headers that the function should use to filter
    event_criteria (lst of lst): list of criterial for each column header. (ie. list of diagnosis codes and a list of medications)
    """
    occurs_multiple = pd.DataFrame()
    patient_id_lst = sorted(set(list(sorted_df_pre_filt['patient_id'])))
    for patient in patient_id_lst:
        temp_df = sorted_df_pre_filt[sorted_df_pre_filt['patient_id']==patient]
        temp_df_lst_by_criteria = [temp_df[temp_df[event_col_head[ii]].isin(event_criteria[ii])] for ii in range(len(event_col_head))]
        if order_matters:
            include = is_included_order(temp_df_lst_by_criteria, minimum_gap, max_gap)
        else:
            include = is_included_not_order(temp_df_lst_by_criteria, minimum_gap, max_gap)
        if include:
            occurs_multiple = occurs_multiple.append(temp_df)
    return occurs_multiple

def is_included_order(temp_df_lst, min_gap, max_gap):
    '''
    Suboordinate function of events_occur_multiple. The order of events does
    not matter
    '''
    lst_of_timestamps = sorted(set(list(temp_df_lst[0]['timestamp'])))
    lst_of_time_intervals = [[[time, time + min_gap * 24 * 60 * 60], [time, time + max_gap * 24 * 60 * 60]] for time in lst_of_timestamps]
    for time_int in lst_of_time_intervals:
        columns_in_interval_check = [False for ii in range(len(temp_df_lst[1:]))]
        for counter, df in enumerate(temp_df_lst[1:]):
            in_interval, next_event_timestamp = is_in_interval(df, time_int)
            if in_interval:
                columns_in_interval_check[counter] = True
                time_int[0][0] = next_event_timestamp
                time_int[1][0] = next_event_timestamp
        if False not in columns_in_interval_check:
            return True
    return False
                

def is_included_not_order(temp_df_lst, min_gap, max_gap):
    '''
    Suboordinate function of events_occur_multiple. The order of events does
    not matter.
    '''
    lengths_of_dfs = [len(df) for df in temp_df_lst]
    start_idx = lengths_of_dfs.index(min(lengths_of_dfs))
    start_df = temp_df_lst[start_idx]
    remaining_dfs = temp_df_lst[0:start_idx] + temp_df_lst[start_idx+1:]
    lst_of_timestamps = sorted(set(list(start_df['timestamp'])))
    lst_of_time_intervals = [[[time - min_gap * 24 * 60 * 60, time + min_gap * 24 * 60 * 60], [time - max_gap * 24 * 60 * 60, time + max_gap * 24 * 60 * 60]] for time in lst_of_timestamps]
    for time_int in lst_of_time_intervals:
        columns_in_interval_check = [False for ii in range(len(remaining_dfs))]
        for counter, df in enumerate(remaining_dfs):
            if is_in_interval(df, time_int)[0]:
                columns_in_interval_check[counter] = True
        if False not in columns_in_interval_check:
            return True
    return False

def is_in_interval(df, time_int):
    '''
    Checks whether there exists a timestamp within a dataframe within a given
    time interval (interva: [anchor - maxgap: anchor - mingap, anchor + mingap: anchor + maxgap])

    '''
    for timestamp in sorted(set(list(df['timestamp']))):
        if is_between(timestamp, time_int[1]) and not is_between(timestamp, time_int[0]):
            return [True, timestamp]
    return [False, None]

def is_between(timestamp, gap):
    '''
    Checks whether timestamp is within an interval (interval: [x:y])

    '''
    if gap[0] == gap[1]:
        return False
    
    if timestamp>=gap[0] and timestamp<=gap[1]:
        return True
    else:
        return False
    
def find_intersection(inclusion_or = [], inclusion_and = [], exclusion = [], is_df = True):
    '''
    Finds different intersections between patients from different cohorts depending
    on whether they are demed inclusion_or inclusion_and or exclusion criteria.
    Use inclusion_or for constraints within a variable.
    Use inclusion_and for cohorts built from different variables

    Parameters
    ----------
    inclusion_or : list, optional
        List of dataframes or lists of patients
    inclusion_and : list, optional
         List of dataframes or lists of patients
    exclusion : list, optional
        List of dataframes or lists of patients
    is_df : boolean, optional
        True if the arguments are lists of dataframes. False if lists of lists

    Returns
    -------
    patient_cohort : list
        List of patients that form clinical cohort 

    '''
    if is_df:
        patient_cohort = []
        for inclusion_cohort in inclusion_or:
            if len(inclusion_cohort):
                patient_cohort += list(inclusion_cohort['patient_id'])
        patient_cohort = sorted(set(patient_cohort))

        for inclusion_cohort in inclusion_and:
            if len(inclusion_cohort):
                patient_cohort = list(set(patient_cohort) & set(inclusion_cohort['patient_id']))

        for exclusion_cohort in exclusion:
            if len(exclusion_cohort):
                patient_cohort = list(np.setdiff1d(patient_cohort, list(exclusion_cohort['patient_id'])))
    else:
        patient_cohort = []
        
        for inclusion_cohort in inclusion_or:
            patient_cohort += inclusion_cohort
        patient_cohort = sorted(set(patient_cohort))

        for inclusion_cohort in inclusion_and:
            patient_cohort = list(set(patient_cohort) & set(inclusion_cohort))

        for exclusion_cohort in exclusion:
            patient_cohort = list(np.setdiff1d(patient_cohort, exclusion_cohort))

    return patient_cohort

def convert_to_unix(date):
    '''
    Time in yyyyymmdd to unix
    '''
    return time.mktime(datetime.datetime.strptime(str(date), "%Y%m%d").timetuple())


