## EazyML Responsible-AI: XAI
![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)  ![PyPI package](https://img.shields.io/badge/pypi%20package-0.0.88-brightgreen) ![Code Style](https://img.shields.io/badge/code%20style-black-black)

![EazyML](https://github.com/EazyML/eazyml-docs/raw/refs/heads/master/EazyML_logo.png)

`eazyml-xai` is a python package designed to make machine learning predictions more transparent and interpretable. It provides human-readable explanations for predictions.

### Features
- **Local Feature Importance**: Get insights into the most impactful features influencing the predicted target variable.
- **Explanations**: Explains the reason behind the predicted target variable.
- **Explainability Score**: Enhance the reliability of explanations with an explainability score.

`eazyml-xai` is a key tool for building trust in AI systems by providing clear, actionable explanations.

## Installation
To use the explainable ai, ensure you have Python installed on your system.
### User installation
The easiest way to install EazyML Explainable AI is using pip:
```bash
pip install -U eazyml-xai
```
### Dependencies
This package requires:
- pandas
- scikit-learn
- werkzeug
- Unidecode
- pydot
- numpy
- pyyaml
- xgboost

## Usage
### Example 1 - Fetching explanations with the EazyML model.

#### Imports
```python
from eazyml_xai import ez_init, ez_explain
```

#### Initialize and Read Data
```
# Initialize the EazyML automl library.
_ = ez_init()

# Load training data (Replace with the correct data path).
train_data_path = "path_to_your_training_data.csv"
train = pd.read_csv(train_data_path)

# Load test data (Replace with the correct data path).
test_data_path = "path_to_your_test_data.csv"
test = pd.read_csv(test_data_path)
```

#### Fetch Explanations
```
# Define the outcome (target variable)
outcome = "target"  # Replace with your target variable name

# Build EazyML predictive models
build_options = {'model_type': 'predictive'}
build_resp = ez_build_model(train, outcome=outcome, options=build_options)

# Use model_info from ez_build_model response
model_info = build_resp["model_info"]

# Customize options for fetching explanations
xai_options = {"record_number": [1, 2, 3]}

# To fetch the explanations
xai_response = ez_explain(train, outcome, test_data_path, model_info, options=xai_options)

# xai_response is a dictionary object with following keys.
# print (xai_response.keys())
# dict_keys(['success', 'message', 'explanations'])

# reponse object contains a dictionary with explanations for the user specified record numbers. 

```

### Example 2 - Fetching explanations with your model and EazyML preprocessing.

#### Imports
```python
from eazyml_xai import ez_init, ez_explain, create_onehot_encoded_features, ez_get_data_type
```

#### Initialize and Read Data
```
# Initialize the EazyML automl library.
_ = ez_init()

# Load training data (Replace with the correct data path).
train_data_path = "path_to_your_training_data.csv"
train = pd.read_csv(train_data_path)

# Define input features (X) and target variable (y)
y = train[outcome]
X = train.drop(outcome, axis=1)

# Load test data (Replace with the correct data path).
test_data_path = "path_to_your_test_data.csv"
test = pd.read_csv(test_data_path)
```

#### Fetch Explanations
```
# Define the outcome (target variable)
outcome = "target"  # Replace with your target variable name

# Get data type of features
type_df = ez_get_data_type(train, outcome)

# List of categorical columns
cat_list = type_df[type_df['Data Type'] == 'categorical']['Variable Name'].tolist()
cat_list = [ele for ele in cat_list if ele != outcome]

# Create one-hot encoded features
train = create_onehot_encoded_features(train, cat_list)

# Define your model object (replace with any model of your choice)
model_info = <YourModelClass>(<parameters>)  # e.g., RandomForestClassifier(), LogisticRegression(), etc.

# Train your model object
model_info.fit(X, y)

# Customize options for fetching explanations
xai_options = {"record_number": [1, 2, 3]}

# To fetch the explanations
xai_response = ez_explain(train, outcome, test_data_path, model_info, options=xai_options)

# xai_response is a dictionary object with following keys.
# print (xai_response.keys())
# dict_keys(['success', 'message', 'explanations'])

# reponse object contains a dictionary with explanations for the user specified record numbers. 

```

### Example 3 - Fetching explanations with your model and preprocessing.

#### Imports
```python
from eazyml_xai import ez_init, ez_explain
```

#### Initialize and Read Data
```
# Initialize the EazyML automl library.
_ = ez_init()

# Load training data (Replace with the correct data path).
train_data_path = "path_to_your_training_data.csv"
train = pd.read_csv(train_data_path)

# Define input features (X) and target variable (y)
y = train[outcome]
X = train.drop(outcome, axis=1)

# Load test data (Replace with the correct data path).
test_data_path = "path_to_your_test_data.csv"
test = pd.read_csv(test_data_path)
```

#### Fetch Explanations
```
# Define the outcome (target variable)
outcome = "target"  # Replace with your target variable name

# Implement your preprocessing steps within a custom preprocessor class and define it
# (Replace <YourPreprocessorClass> with the specific preprocessor class you're using)
preprocessor = <YourPreprocessorClass>(<parameters>)  # Example: StandardScaler(), CustomPreprocessor()

# Fit the preprocessor on your dataset
preprocessor.fit(X, y)

# Define your model object (replace with any model of your choice)
model_info = <YourModelClass>(<parameters>)  # e.g., RandomForestClassifier(), LogisticRegression(), etc.

# Train your model object
model_info.fit(X, y)

# Customize options for fetching explanations
xai_options = {"record_number": [1, 2, 3], "preprocessor", preprocessor}

# To fetch the explanations
xai_response = ez_explain(train_data_path, outcome, test_data_path, model_info, options=xai_options)

# xai_response is a dictionary object with following keys.
# print (xai_response.keys())
# dict_keys(['success', 'message', 'explanations'])

# reponse object contains a dictionary with explanations for the user specified record numbers. 

```
You can find more information in the [documentation](https://eazyml.readthedocs.io/en/latest/packages/eazyml_xai.html).


## Useful links, other packages from EazyML family
- [Documentation](https://docs.eazyml.com)
- [Homepage](https://eazyml.com)
- If you have questions or would like to discuss a use case, please contact us [here](https://eazyml.com/trust-in-ai)
- Here are the other packages from EazyML suite:

    - [eazyml-automl](https://pypi.org/project/eazyml-automl/): eazyml-automl provides a suite of APIs for training, optimizing and validating machine learning models with built-in AutoML capabilities, hyperparameter tuning, and cross-validation.
    - [eazyml-data-quality](https://pypi.org/project/eazyml-data-quality/): eazyml-data-quality provides APIs for comprehensive data quality assessment, including bias detection, outlier identification, and drift analysis for both data and models.
    - [eazyml-counterfactual](https://pypi.org/project/eazyml-counterfactual/): eazyml-counterfactual provides APIs for optimal prescriptive analytics, counterfactual explanations, and actionable insights to optimize predictive outcomes to align with your objectives.
    - [eazyml-insight](https://pypi.org/project/eazyml-insight/): eazyml-insight provides APIs to discover patterns, generate insights, and mine rules from your datasets.
    - [eazyml-xai](https://pypi.org/project/eazyml-xai/): eazyml-xai provides APIs for explainable AI (XAI), offering human-readable explanations, feature importance, and predictive reasoning.
    - [eazyml-xai-image](https://pypi.org/project/eazyml-xai-image/): eazyml-xai-image provides APIs for image explainable AI (XAI).

## License
This project is licensed under the [Proprietary License](https://github.com/EazyML/eazyml-docs/blob/master/LICENSE).

---

Maintained by [EazyML](https://eazyml.com)  
© 2025 EazyML. All rights reserved.
