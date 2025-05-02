## EazyML Responsible-AI: Augmented Intelligence
![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)  ![PyPI package](https://img.shields.io/badge/pypi%20package-0.0.60-brightgreen) ![Code Style](https://img.shields.io/badge/code%20style-black-black)

![EazyML](https://github.com/EazyML/eazyml-docs/raw/refs/heads/master/EazyML_logo.png)

A collection of APIs from EazyML family to discover patterns, generate insights, or mine rules from your datasets. Each discovered pattern is expressed as a set of conditions on feature variables - each with a trust-score to reflect confidence in the insight, allowing you to analyze and apply these insights to your data. Ideal for pattern recognition, interpretable AI, and augmented intelligence workflows.

### Features
- **Pattern Mining**: Discover meaningful rules from the  datasets.
- **Insight Generation**: Generate high-value insights with associated trust scores.
- **Application of Rules**: Apply discovered patterns to datasets for further analysis.

Ideal for use cases like interpretability, training data analysis, and building solutions with augmented intelligence.

## Installation
To use the augmented intelligence, ensure you have Python installed on your system.
### User installation
The easiest way to install this package for augmented intelligence is using pip:
```bash
pip install -U eazyml-insight
```
### Dependencies
This package requires:
- werkzeug
- unidecode
- pandas
- scikit-learn
- nltk
- pyyaml
- requests

## Usage
Here's an example of how you can use the APIs from this package.

#### Imports
```python
from eazyml_insight import ez_init, ez_insight, ez_validate
```

#### Initialize and Read Data
```
# Initialize the EazyML automl library.
_ = ez_init()

# Define training data (Replace with the correct data path).
train_data_path = "path_to_your_training_data.csv"
```

#### Fetch Insights
```
# Define the outcome (target variable)
outcome = "target"  # Replace with your target variable name

# Customize options for fetching insights
insight_options = {"data_source": "parquet"}

# Call the EazyML APIs to fetch the insights
insight_response = ez_insight(train_data_path, outcome, options=insight_options)

# insight_response is a dictionary object with following keys.
# print(insight_response.keys())
# dict_keys(['success', 'message', 'insights'])

# the insight_response object contains insights/patterns that you can explore to integrate in your augmented intelligence workflows.

```

#### Use Insights to Validate
```
# Define test data.
test_data_path = "path_to_your_test_data.csv"

# Define the insights (response from ez_insight)
insights = insight_response['insights']

# Choose the record_number for validation. The default value is 1 if no value is provided.
validate_options = {"record_number": [1, 2, 3]}

# Call the EazyML function to validate
validate_response = ez_validate(train_data_path, outcome, insights, test_data_path, options=validate_options)

# validate response is a dictionary object with following keys.
# print(validate_response.keys())
# dict_keys(['success', 'message', 'validations', 'validation_filter'])

# the validate_response object contains validation metrics on the insights provided by ez_insight, along with the filtered data from the test data for the given record number in the insights.

```
You can find more information in the [documentation](https://eazyml.readthedocs.io/en/latest/packages/eazyml_insight.html).


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
