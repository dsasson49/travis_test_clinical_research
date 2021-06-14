# https://github.com/lumenbiomics/clinical-research/issues/4


class ClinicalCohort:
    """
    A class to hold ClinicalVariables, study window, and temporal information to build a study cohort

    Attributes
    ----------
    name : str
        Name of cohort
    study_window: list of int
        Date range fromw which to extract cohort of format [YYYYMMDD,YYYYMMDD]
    clinical_variable: list of ClinicalVariable
        list of ClinicalVariable objects
    variable_category: list of str
        Categories of ClinicalVariables in study. Options are 'inclusion', 'exclusion','exposure', 'outcome', and 'covariate'
    assessment_window: list of list of int/float/boolean
        List of lists of assessment window for each variable of format [int,int] where applicable. FALSE if not applicable
        Ex: any history of cancer = check for cancer variable from -infinity to cohort entry date
    washout_window: list of list of int/float/boolean
        List of lists of washout window for each variable of format [int,int] where applicable. FALSE if not applicable
        Ex: patient considered part of drug cohort until 7 days after stopping drug
    temporal_anchor: list of str/ClinicalVariable
        Anchoring of each variable in study. Options are 'primary' for primary anchor, 'secondary', or ClinicalVariable to which
        a variables assessment window is anchored
        Ex: drug exposure = primary, drug stoppage = secondary
    primary_anchor_specified: booelan
        Boolean indicating if primary anchor has been specified, which if true alters the cohort building and analysis process

    """

    def __init__(
        self,
        name,
        study_window,
        clinical_variable=None,
        variable_category=None,
        assessment_window=False,
        washout_window=False,
        temporal_anchor=False,
    ):

        self.name = name
        self.study_window = study_window
        self.clinical_variable = clinical_variable
        self.variable_category = variable_category
        self.assessment_window = assessment_window
        self.washout_window = washout_window
        self.temporal_anchor = temporal_anchor
        self.primary_anchor_specified = False

    def add_clinical_variable(
        self,
        clinical_variable,
        variable_category,
        temporal_anchor=False,
        assessment_window=False,
        washout_window=False,
    ):
        """
        Add a subvariable (e.g. list of diagnosis codes, drugs, labs) to the variable object
        """
        if self.clinical_variable:
            self.clinical_variable += [clinical_variable]
        else:
            self.clinical_variable = [clinical_variable]

        if self.variable_category:
            self.variable_category += [variable_category]
        else:
            self.variable_category = [variable_category]

        if self.temporal_anchor:
            self.temporal_anchor += [temporal_anchor]
        else:
            self.temporal_anchor = [temporal_anchor]
        if self.assessment_window:
            self.assessment_window += [assessment_window]
        else:
            self.assessment_window = [assessment_window]
        if self.washout_window:
            self.washout_window += [washout_window]
        else:
            self.washout_window = [washout_window]

        # Check if this is a primary anchor
        if temporal_anchor == "primary":
            self.primary_anchor_specified = True

    # I am pretty sure constraints will need to be checked be reasoning over SDK return as its query function is not advanced enough for these besides the
    # default constraint of count = 1 (i.e. any occurence)
    def check_count_constraint(constraint):
        pass

    def check_temporal_constraint(constraint):
        pass

    def check_threshold_constraint(constraint):
        pass

    def build_cohort(self):
        """
        TODO:
            1. Check if there is a primary anchor
                a. If primary anchor / exposure base all assessment windows around that
                b. If not use assessment windows starting on first patient encounter in EHR that meets any inclusion criteria
            2. Get constraints from 'inclusion' ClinicalVariables and build cohort
                a. Each of these will likely require a mixture of querying the SDK and taking in and manipulating a returned dataframe
                b. Within a ClinicalVariable, each constratint should be evaluated as OR (e.g. diabetes is positive if 2x diagnosis code OR hba1c > 6.5)
                c. Between ClinicalVariables, constraints should be evaulated as AND (e.g. diabetes.constraints AND depression.constraints if both are inclusion criteria)
            3. Get constraints from 'exclusion' ClinicalVariables and build cohort
            4. Subtract exclusion cohort from inclusion cohrot to create final cohort
            5. Covariates and outcome variables should be saved for use in analysis but don't change cohort building

        Returns
        -------
        nfer_cohort : list of str
            list of nfer_pids that match the inclusion/exclusion criteria
        """
        pass

    def build_cohort_funnel(self):
        """
        TODO
        Shows the cohort attrition as each inclusion/exclusion criteria is applied so user can decide which restrictions
        if any they may need to loosen to increase their N

        Returns
        -------
        attrition_list : dict of dict
            Lists of lists of format {variable_category: {variable_name: cohort count after applied}}
        """
        pass
