# Clinical Research Workflow
Backend for conducting clinical research studies using the SDK and allowing for 1) definition and saving of variables, 2) definition and saving of cohorts using those variables, and 3) conducting of clinical studies using those variables


### Defining Variables
To build a cohort using variables defined in a standard way, we need to make a variable object that can hold multiple different subvariables of different variables types. The key types are:
* 'dx' - diagnostic codes
* 'drug' - medications
* 'proc' - procedure codes 
* 'lab' - laboratory fields
* 'vitals' - vital fields

Once these subvariable values are specified, we need to specify constraints that must be satisfied with these subvariables to positively indicate the concept represented by the ClinicalVariable. For example for the ClinicalVariable representing "diabetes" we could define the constraints as being:
1. 2 diagnosis codes within 365 days
2. The prescription of an anti-diabetic medication within 90 days of a diabetes diagnosis codes
3. An HbA1c value > 6.5

The code below illustrates some examples of adding constraints and building a variable object
```python
#Initialize variable
>>> diabetes_var=ClinicalVariable('diabetes')
#Add subvariable of diagnoses codes
>>> diabetes_var.add_subvariable(subvariable_name='diabetes_codes',category='dx',value=['E11.21','E11.22','E11.29','E11.34'])
#Add subvariable of drug names
>>> diabetes_var.add_subvariable(subvariable_name='diabetes_drugs',category='drug',value=['metformin','canigaflozin','sulfonylurea','singliptin'])
#Add subvariable of lab names
>>> diabetes_var.add_subvariable(subvariable_name='diabetes_lab',category='lab',value=['hba1c'])
#Add constraint that must see a diabetes drug 0 to 90 days after a diabetes code
>>> diabetes_var.add_constraint(['time',[0,90],'diabetes_drugs','diabetes_codes'])
#Add constraint that hba1c value msut be between 6.5 and 50
>>> diabetes_var.add_constraint(['threshold',[6.5,50],'diabetes_lab'])
#Add constraint that you must see two counts of diabetes codes with the second code 30 to 365 after the first
>>> diabetes_var.add_constraint(['count',[2,30,365],'diabetes_codes'])
#See subvariable you added in 
>>> diabetes_var.subvariable_to_dict('diabetes_codes')
Out:
{'name': 'diabetes_codes',
 'category': 'dx',
 'value': ['E11.21', 'E11.22', 'E11.29', 'E11.34']}
>>> diabetes_var.variable_to_dict()
Out:
{'name': 'diabetes',
 'subvariable_name': ['diabetes_codes', 'diabetes_drugs', 'diabetes_lab'],
 'category': ['dx', 'drug', 'lab'],
 'value': [['E11.21', 'E11.22', 'E11.29', 'E11.34'],
  ['metformin', 'canigaflozin', 'sulfonylurea', 'singliptin'],
  ['hba1c']],
 'constraint': [['time',
   [0, 90],
   ['metformin', 'canigaflozin', 'sulfonylurea', 'singliptin'],
   ['E11.21', 'E11.22', 'E11.29', 'E11.34']],
  ['threshold', [6.5, 50], ['hba1c']],
  ['count', [2, 30, 365], ['E11.21', 'E11.22', 'E11.29', 'E11.34']]]}
  ```

### Defining a Cohort (TBD)
Once variables are defined, you can use them to define a cohort. A cohort is made of 1 to many variable objects and a study window. 1 variable must be specified as the primary anchor around which the assessment window for other variables will be based. Each variable must be labeled as either 'inclusion', 'exclusion', or 'covariate' ('covariates' will not be used in cohort building, but later for analysis).

The code below shows the building of a cohort object
```python
TBD: workspace deleted notebook and remaking class
```

### Building a Cohort (TBD)
Once a cohort study window, anchor variable, and other variables are defined. The cohort object will have the ability to perform the necessary queries via the SDK and manipulation of returns to identify the nfer_pids that are appropriate for that query.

### Match a Cohort (TBD)
TBD

### Analyzing a Cohort (TBD)
By using a previously defined cohort, an outcome of interest, and an analysis type an analysis can be produced

## Kedro Overview

This is your new Kedro project, which was generated using `Kedro 0.17.3`.

Take a look at the [Kedro documentation](https://kedro.readthedocs.io) to get started.

## Rules and guidelines

In order to get the best out of the template:

* Don't remove any lines from the `.gitignore` file we provide
* Make sure your results can be reproduced by following a [data engineering convention](https://kedro.readthedocs.io/en/stable/12_faq/01_faq.html#what-is-data-engineering-convention)
* Don't commit data to your repository
* Don't commit any credentials or your local configuration to your repository. Keep all your credentials and local configuration in `conf/local/`

## How to install dependencies

Declare any dependencies in `src/requirements.txt` for `pip` installation and `src/environment.yml` for `conda` installation.

To install them, run:

```
kedro install
```

## How to run your Kedro pipeline

You can run your Kedro project with:

```
kedro run
```

## How to test your Kedro project

Have a look at the file `src/tests/test_run.py` for instructions on how to write your tests. You can run your tests as follows:

```
kedro test
```

To configure the coverage threshold, go to the `.coveragerc` file.

## Project dependencies

To generate or update the dependency requirements for your project:

```
kedro build-reqs
```

This will copy the contents of `src/requirements.txt` into a new file `src/requirements.in` which will be used as the source for `pip-compile`. You can see the output of the resolution by opening `src/requirements.txt`.

After this, if you'd like to update your project requirements, please update `src/requirements.in` and re-run `kedro build-reqs`.

[Further information about project dependencies](https://kedro.readthedocs.io/en/stable/04_kedro_project_setup/01_dependencies.html#project-specific-dependencies)

## How to work with Kedro and notebooks

> Note: Using `kedro jupyter` or `kedro ipython` to run your notebook provides these variables in scope: `context`, `catalog`, and `startup_error`.
>
> Jupyter, JupyterLab, and IPython are already included in the project requirements by default, so once you have run `kedro install` you will not need to take any extra steps before you use them.

### Jupyter
To use Jupyter notebooks in your Kedro project, you need to install Jupyter:

```
pip install jupyter
```

After installing Jupyter, you can start a local notebook server:

```
kedro jupyter notebook
```

### JupyterLab
To use JupyterLab, you need to install it:

```
pip install jupyterlab
```

You can also start JupyterLab:

```
kedro jupyter lab
```

### IPython
And if you want to run an IPython session:

```
kedro ipython
```

### How to convert notebook cells to nodes in a Kedro project
You can move notebook code over into a Kedro project structure using a mixture of [cell tagging](https://jupyter-notebook.readthedocs.io/en/stable/changelog.html#release-5-0-0) and Kedro CLI commands.

By adding the `node` tag to a cell and running the command below, the cell's source code will be copied over to a Python file within `src/<package_name>/nodes/`:

```
kedro jupyter convert <filepath_to_my_notebook>
```
> *Note:* The name of the Python file matches the name of the original notebook.

Alternatively, you may want to transform all your notebooks in one go. Run the following command to convert all notebook files found in the project root directory and under any of its sub-folders:

```
kedro jupyter convert --all
```

### How to ignore notebook output cells in `git`
To automatically strip out all output cell contents before committing to `git`, you can run `kedro activate-nbstripout`. This will add a hook in `.git/config` which will run `nbstripout` before anything is committed to `git`.

> *Note:* Your output cells will be retained locally.

## Package your Kedro project

[Further information about building project documentation and packaging your project](https://kedro.readthedocs.io/en/stable/03_tutorial/05_package_a_project.html)
