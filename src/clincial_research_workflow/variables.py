class ClinicalVariable():
    """
    A class used to hold medication, lab, and diagnosis variables that can be used to define
    an outcome or disease state.

    Attributes
    ----------
    name : str
        Name of variable object
    sub_var_name : str
        Name of sub-variables that compose the variable object
    category : list of str
        List of variable category strings of values 'drug', 'dx', 'proc', or 'lab'
    value: list of str
        list of values to query (e.g. drug names, lab names, diagnosis codes, or procedure codes)
    constraint: list of lists
        list of constraint parameters of format that is dependent on constraint type. Key parameter for cohort building

    """

    def __init__(self, name, subvariable_name=None, category=None, value=None):
        """
        Parameters
        ----------
        name : str
            Name of variable object
        subvariable_name : str
            Name of subvariables that compose the variable object
        category : list of str
            List of variable category strings of values 'drug', 'dx', 'proc', 'vital' or 'lab'
        value: list of str
            list of values to query (e.g. drug names, lab names, diagnosis codes, or procedure codes)
        """
        self.name = name
        self.subvariable_name = subvariable_name
        self.category = category
        self.value = value
        self.constraint = {}

    def add_subvariable(self, subvariable_name, category, value):
        """
        Add a subvariable (e.g. list of diagnosis codes, drugs, labs) to the variable object
        """
        if self.subvariable_name:
            self.subvariable_name += [subvariable_name]
        else:
            self.subvariable_name = [subvariable_name]
        if self.category:
            self.category += [category]
        else:
            self.category = [category]
        if self.value:
            self.value += [value]
        else:
            self.value = [value]

    def add_constraint(self, constraint):
        """
        Add a constraint to the variable object specifying a relationship between a variable
        and other variables or itself

        Paramaters
        ----------
        constraint: list
            A specially formatted list whose formatting depends on the constraint type ('time','count','threshold')
                - 'time' > ['time',[<days since dependee variable min>,<days since dependee variable max>], <dependent variable name>, <dependee variable name>]
                - 'count' > ['count',[<number occurences>,<min days since first occurrence>,<max days since first occurrence>], <subvariable name>]
                - 'threshold' > ['threshold',[<min_threshold>,<max_threshold>],<subvariable name>]
                - 'only_one' > ['only_one', <interval_days>, <subvariable name>]
        """
        constraint_type = constraint[0]
        if constraint_type == 'time':
            dependent_variable = constraint[-2]
            dependee_variable = constraint[-1]
            dependent_index = self.subvariable_name.index(dependent_variable)
            dependee_index = self.subvariable_name.index(dependee_variable)
            constraint[-2] = self.value[dependent_index]
            constraint[-1] = self.value[dependee_index]
        if constraint_type in ['threshold', 'count']:
            threshold_variable = constraint[-1]
            threshold_index = self.subvariable_name.index(threshold_variable)
            constraint[-1] = self.value[threshold_index]
        if constraint_type == 'only_one':
            onlyone_variable = constraint[-1]
            onlyone_index = self.subvariable_name.index(onlyone_variable)
            constraint[-1] = self.value[onlyone_index]
        if constraint_type in self.constraint.keys():
            self.constraint[constraint_type] += [constraint[1:]]
        else:
            self.constraint[constraint_type] = [constraint[1:]]

    def subvariable_to_dict(self, subvariable_name):
        """
        Returns dictionary of
        """
        try:
            subvariable_index = self.subvariable_name.index(subvariable_name)
            subvariable_attributes = {'name': subvariable_name, 'category': self.category[subvariable_index],
                                      'value': self.value[subvariable_index]}
            return subvariable_attributes
        except:
            print("Input subvariable_name not found")
            raise

    def variable_to_dict(self):
        """
        Returns dictionary containing ClinicalObject attribute values
        """
        variable_dict = {
            'name': self.name,
            'subvariable_name': self.subvariable_name,
            'category': self.category,
            'value': self.value,
            'constraint': self.constraint
        }
        return variable_dict
    
    def get_subvariable_dict_from_list(self, codes):
        '''
        Returns dictionary of the subvariable from a list of codes within 
        the subvariable's constraint

        '''
        subvariable_index = self.value.index(codes)
        return self.subvariable_to_dict(self.subvariable_name[subvariable_index])

    def finalize_variable(self):
        """
        Generates default constraints where appropriate and makes explicit links between interconnected constraints.
        Should only be called after all individual constraints have been added
        """
        # variables for which there has been a constraint
        constrained_values = []
        for constraint_type in self.constraint:
            for constraint in self.constraint[constraint_type]:
                if constraint_type in ['threshold', 'count', 'only_one']:
                    constraint_value = constraint[-1]
                    constrained_values.append(constraint_value)
                elif constraint_type == 'time':
                    constraint_values = constraint[-2:]
                    constrained_values += constraint_values
        # compare constrained values to all populated values
        unconstrained_values = [value for value in self.value if value not in constrained_values]

        # TODO: make sure constraint interpreter knows 1,0,0 is a special case of just making sure a matching value is seen
        for value in unconstrained_values:
            if 'count' in self.constraint.keys():
                self.constraint['count'].append([[1, 0, 0], value])
            else:
                self.constraint['count'] = [[1, 0, 0], value]
                # default is a single variable count if not otherswise stated
        for value in unconstrained_values:
            self.constraint

        ##TODO: if variable is seen in multiple constraints, link those constraints to create a special super constraint of some sort