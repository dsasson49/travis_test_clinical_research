import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from variables import ClinicalVariable
meds_variables=[]

#Medication object (inclusion)
ssri_snri =['citalopram', 'duloxetine', 'escitalopram', 'fluvoxamine', 'fluoxetine', 
            'milnacipran', 'levomilnacipran', 'paroxetine', 'sertraline', 'venlafaxine', 
            'desvenlafaxine', 'vilazodone', 'vortioxetine']

mdd_var=ClinicalVariable('ssri_snri')
mdd_var.add_subvariable(subvariable_name='ssri_snri',category='drug',value=ssri_snri)
mdd_var.add_constraint(['count',[2,42,730],'ssri_snri'])
mdd_var.add_constraint(['only_one', 30,'ssri_snri'])
meds_variables.append(mdd_var)

# psychiatric exclusions
exclusion_drugs=['ketamine', 'esketamine']
excl_var=ClinicalVariable('exclusion_drugs')
excl_var.add_subvariable(subvariable_name='exclusion_drugs',category='drug',value=exclusion_drugs)
meds_variables.append(excl_var)

"""
    finalize all variables. If no constraints specified for a subvariable, adds default constraint of count of 1 
    for that subvariable value(i.e. as long as that lab value/diagnosis/drug is seen, it will match the constraint).
    If constraint specified for a subvariable, does nothing
"""
for clinical_variable in meds_variables:
    clinical_variable.finalize_variable()