## EazyML Responsible-AI: Modeling
![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)  ![PyPI package](https://img.shields.io/badge/pypi%20package-0.0.74-brightgreen) ![Code Style](https://img.shields.io/badge/code%20style-black-black)

![EazyML](https://github.com/EazyML/eazyml-docs/raw/refs/heads/master/EazyML_logo.png)

`eazyml-automl` is a comprehensive python package designed to simplify machine learning workflows for data scientists, engineers, and developers. With **AutoML capabilities**, EazyML enables automated feature selection, model training, hyperparameter optimization, and cross-validation, all with minimal code. The package trains multiple models in the background, rank orders them by performance metrics, and recommends the best model for your use case.

### Features
- **Global Feature Importance**: Get insights into the most impactful features influencing the target variable.
- **Confidence Scoring**: Enhance predictive reliability of your models with confidence scores.
- **Hyperparameter Tuning**: Enhance performance of your predictive operations with optimal models.

`eazyml-automl` is perfect for users looking to streamline the development and operationalization of robust and efficient machine learning models.

## Installation
### User installation
The easiest way to install EazyML modeling is using pip:
```bash
pip install -U eazyml-automl
```
### Dependencies
EazyML Modeling requires :
- werkzeug
- unidecode
- pandas
- scikit-learn
- nltk
- pyyaml
- requests

## Usage
Initialize and train predictive models on the given training data. Perform predictions on the given test data. Customize training and inference using options parameter. Please refer to the APIs documentation and boilerplate notebooks for details.

#### Imports
```python
import pandas as pd
import joblib
from eazyml import ez_init, ez_build_model, ez_predict
```

#### Initialize and Read Data
```
# Initialize the EazyML automl library.
_ = ez_init()

# Load training data (Replace with the correct data path).
train_data_path = "path_to_your_training_data.csv"
train_data = pd.read_csv(train_data_path)
```

#### Train and Save Model
```
# Define the outcome (target variable)
outcome = "target"  # Replace with your target variable name

# Customize options for building models
build_options = {"model_type": "predictive"}

# Call EazyML APIs to train models
build_response = ez_build_model(train_data, outcome, options=build_options)

# build_response is a dictionary object with following keys.
# print(build_response.keys())
# dict_keys(['success', 'message', 'model_performance', 'global_importance', 'model_info'])

# Save the response for later use (e.g., for predictions with ez_predict).
build_model_response_path = 'model_response.joblib'
joblib.dump(build_response, build_model_response_path)

```

#### Use Saved Model to Predict
```
# Load test data.
test_data_path = "path_to_your_test_data.csv"
test_data = pd.read_csv(test_data_path)

# This shows how to use a saved model, but you might as well use the build_response object directly in case you have both build and predict operations in the same notebook for your experiments.
build_model_response_path = 'model_response.joblib'
build_model_response = joblib.load(build_model_response_path)
model_info = build_model_response["model_info"]

# Choose the model for prediction from the key "model_performance" in the build_model_response object above. The default model is the top-performing model if no value is provided.
pred_options = {"model": "Random Forest with Information Gain"}

# Call the eazyml function to predict
pred_response = ez_predict(test_data, model_info, options=pred_options)

# prediction response is a dictionary object with following keys.
# print(pred_response.keys())
# dict_keys(['success', 'message', 'pred_df'])

```
You can find more information in the [documentation](https://eazyml.readthedocs.io/en/latest/packages/eazyml_model.html).


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