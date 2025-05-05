# Gooder AI Package

This package provides a streamlined way to ~evaluate~ valuate machine learning models on the **Gooder AI platform**. It exports a simple yet powerful function, **`valuate_model`**, which is designed to work with **scikit-learn-like models** and:

- **Authenticates** users with [Gooder.ai](https://latest.gooder.ai).  
- **Validates and uploads** model configuration and dataset for secure storage and processing.
- **Creates or updates** a shared "view" on [Gooder.ai](https://latest.gooder.ai), allowing users to interactively visualize and analyze their model performance.

## Installation
Install the package using pip:

```bash
pip install gooder_ai
```

## Usage

Here's an example invocation of the `valuate_model` function:

```python
import numpy as np
from some_ml_library import SomeModel  # Replace with an actual ML model library
import asyncio

# Define a dummy scikit-learn-like model
class DummyModel:
    def predict_proba(self, X):
        return np.random.rand(len(X), 2)  # Simulate probabilities for 2 classes
    
    classes_ = np.array([0, 1])  # Define class labels

# Instantiate the model
model = DummyModel()

# Create dummy dataset
x_data = np.random.rand(100, 5)  # 100 samples, 5 features
y = np.random.randint(0, 2, 100)  # Binary classification labels (0 or 1)

# Authentication credentials (optional)
auth_credentials = {
    "email": "user@example.com",
    "password": "securepassword123"
}

# Configuration dictionary
config = {
    "param1": "value1",
    "param2": "value2"
}

# View metadata
view_meta = {
    "mode": "public",
    "dataset_name": "test_dataset"
}

# Column names (optional)
column_names = {
    "dataset_column_names": ["feature1", "feature2", "feature3", "feature4", "feature5"],
    "score_column_names": ["prob_class_0", "prob_class_1"],
    "dependent_variable_name": "target"
}

# AWS variables (optional)
aws_variables = {
    "api_url": "https://api.gooder.ai",
    "bucket_name": "gooder-ai-bucket"
}

# Model names (optional)
model_names = ["model1", "model2"]

# Run the async function
output = asyncio.run(valuate_model(
    models=[model],
    x_data=x_data,
    y=y,
    auth_credentials=auth_credentials,
    config=config,
    view_meta=view_meta,
    model_names=model_names,
    column_names=column_names,
    aws_variables=aws_variables,
    max_size_uploaded_data=10,  # Limit uploaded data to 10MB
    max_size_saved_data=1000     # Limit saved data to 1000MB
))

print(output)  # Output: {'view_id': 'some-id', 'view_url': 'https://gooder.ai/some-id'}
```

## Function Parameters

### `valuate_model(**kwargs)`
The `valuate_model` function takes the following input arguments:

1. **`models: list[ScikitModel]`**  
   - Machine learning models that follow the `ScikitModel` protocol.  
   - It must have a scoring function (e.g., `predict_proba`), which is used to generate probability scores for classification.  
   - It must also have a `classes_` attribute, representing the possible target classes.

2. **`x_data: ndarray | DataFrame | list[str | int | float] | spmatrix`**  
   - A dataset containing the input features for evaluation.  
   - This is the dataset that will be fed into the model for prediction.

3. **`y: ndarray | DataFrame | list[str | int | float] | spmatrix`**  
   - A dataset representing the true target values (labels) corresponding to `x_data`.  
   - This helps in validating model performance.

4. **`auth_credentials: Credentials`**  
   - A dictionary with user authentication details for the Gooder AI platform.  
   - Structure:
     ```python
     {
         "email": str,  # User's email
         "password": str  # User's password
     }
     ```
   - These credentials are used for authentication to upload the dataset and configuration. It is optional if `upload_data_to_gooder = False` and `upload_config_to_gooder = False`.

5. **`config: dict`**  
   - A dictionary containing model configuration settings.  
   - This is validated against Gooder AI's schema before being uploaded.

6. **`view_meta: ViewMeta`**  
   - A dictionary containing metadata about the "view" (shared result visualization) being created or updated.  
   - Structure:
     ```python
     {
         "mode": Optional["public" | "protected" | "private"],  # Access control
         "view_id": Optional[str],  # ID of an existing view (if updating)
         "dataset_name": Optional[str]  # Name of the dataset (defaults to timestamp)
     }
     ```
   - If `view_id` is provided, an existing view is updated; otherwise, a new one is created.

7. **`column_names: ColumnNames = {}`** *(optional)*  
   - A dictionary specifying the column names for the dataset and scores.  
   - Structure:
     ```python
     {
         "dataset_column_names": Optional[list[str]],  # Feature names
         "score_column_names": Optional[list[str]],  # Column names for model scores
         "dependent_variable_name": Optional[str]  # Name of the target variable
     }
     ```

8. **`included_columns: list[str] = []`** *(optional)*  
   - A list of names specifying which columns to include in the dataset before visualizing the scores on the Gooder platform.  

9. **`aws_variables: AWSVariables = {}`** *(optional)*  
   - A dictionary containing AWS-related variables. 
   - Used for authentication and file uploads.
   - Structure:
     ```python
     {
         "api_url": Optional[str],
         "app_client_id": Optional[str],
         "identity_pool_id": Optional[str],
         "user_pool_id": Optional[str],
         "bucket_name": Optional[str],
         "base_url": Optional[str],
         "validation_api_url": Optional[str]
     }
     ```
   - Defaults to global values if not provided.

10. **`model_names: list[str]`**
   - This property is used to label the score columns in the output dataset and configuration.
   - If not provided default names are generated based on model class names.
   - Example: For a model that outputs binary classification scores, a column named "model1_score, model2_score" will be created.

11. **`max_size_uploaded_data: int = 10`** *(optional)* 
   - Defines the maximum allowed memory size (in megabytes, MB) for the combined dataset when uploading to Gooder AI.
   - Before uploading, the function calculates the memory usage of the full dataset.
   - If the dataset exceeds this threshold and `upload_data_to_gooder` is `True`, the operation is aborted and an exception is raised.
   - This is a safety limit to prevent large uploads that could impact performance or exceed platform limits.
   - Default value is 10MB, which is suitable for most use cases.
   - Increase this value if you need to work with larger datasets, but be aware of potential performance implications.

12. **`max_size_saved_data: int = 1000`** *(optional)* 
   - Defines the maximum allowed memory size (in megabytes, MB) for the combined dataset when saving locally.
   - Before saving, the function calculates the memory usage of the full dataset.
   - If the dataset exceeds this threshold and `upload_data_to_gooder` is `False`, the operation is aborted and an exception is raised.
   - This is a safety limit to prevent excessively large local files that could impact system performance.
   - Default value is 1000MB (approximately 1GB), which allows for much larger local datasets compared to uploads.
   - Increase this value if you need to work with very large datasets locally, but be aware of system memory constraints.

### Summary
- The function takes a **scikit-learn model**, **dataset**, **user credentials**, and **configuration details**.
- It authenticates with the Gooder AI platform, validates the config, and **uploads the dataset**.
- Then, it either **creates a new shared view or updates an existing one**.
- Finally, it **returns the view ID and URL**, allowing users to access model evaluation results.

## Config

# Chart Definition Configuration Example

Given below is an example chart/dashboard configuration for the Gooder AI app:

```typescript
const config = {
  "activeFilter": null, // Optional: ID of the active filter (default: null)
  "customChartLayoutMap": {
    "xl": [ // Layout for extra-large screens
      {
        "i": "d292c59c-e1f6-4f7e-ac53-525b7b6e6a56", // Chart ID
        "x": 0, // X position (grid units)
        "y": 0, // Y position (grid units)
        "w": 11, // Width (grid units)
        "h": 9, // Height (grid units)
        "moved": false, // Optional: Whether the item has been moved (default: false)
        "static": false // Optional: Whether the item is static (default: false)
      },
      // ... other xl layouts
    ],
    "lg": [ // Layout for large screens
      // ... similar structure as xl
    ],
    "md": [ // Layout for medium screens
      // ... similar structure as xl
    ],
    "sm": [ // Layout for small screens
      {
        "i": "2db67e79-3c40-40c5-ae42-7d426fa37597", // Chart ID
        "x": 0,
        "y": 36,
        "w": 12,
        "h": 12
      }
    ],
    "xs": [ // Layout for extra-small screens
      // ... similar structure as sm
    ]
  },
  "customCharts": [
    {
      "id": "74a92600-9334-4e57-afe5-2dbb61526547", // Required: Unique chart ID (UUID)
      "dataInitializationCode": "data init script", // Required: Script to initialize chart data
      "metricCalculationCode": "data calculate script", // Required: Script to calculate metrics
      "metric": "Num responses", // Required: Metric name (displayed on Y-axis)
      "title": "Response deciles", // Optional: Chart title (default: null)
      "resolution": 10, // Required: Number of data points/bins
      "unit": "none", // Required: Y-axis unit (from UnitTypes enum)
      "decimalPlaces": 2, // Optional: Decimal precision (default: 2)
      "minRange": 0, // Required: Minimum zoom range (0-100)
      "maxRange": 100, // Required: Maximum zoom range (0-100)
      "seriesType": "bar", // Required: Chart type (line/bar from SeriesTypes)
      "showRangeSlider": false, // Optional: Shows zoom slider on dashboard (default: false)
      "showInDashboard": true, // Required: Display chart on dashboard
      "showInMetricTable": true, // Required: Show metric in the table
      "showBaseline": false, // Optional: Display baseline (default: false)
      "description": null, // Optional: Chart description (default: null)
      "aspectRatio": null, // Optional: Aspect ratio (default: null)
      "scaleMetric": true, // Optional: Scale Y-axis with projected population (default: true)
      "suppressBar": true, // Optional: Hide the first bar for bar series (default: false)
      "suppressXAxisLabel": true, // Optional: Hide X-axis labels (default: false)
      "showThreshold": true, // Optional: Show threshold line (default: false)
      "reverseXAxis": false, // Optional: Reverse X-axis for bar series (default: false)
      "aiPrompt": null, // Optional: Custom AI prompt (default: null)
      "highlightType": "none", // Optional: Highlight type (from HighlightType, default: "none")
      "optimizeResolution": false // Optional: Optimize resolution (default: true)
    }
  ],
  "datasetID": "", // Optional: Dataset ID (format: dataset_name/Sheet1)
  "dependentVariable": "TARGET", // Required: Dependent variable column name
  "filters": null, // Optional: Array of rule IDs (default: null)
  "isOffline": false, // Optional: Offline mode toggle (default: false)
  "numberOfRowsSentInAIPrompt": 10, // Optional: Rows sent to AI (default: 10)
  "percentTreated": null, // Optional: Current % treated value (default: null)
  "positivePolarityValues": ["1"], // Required: Positive values of dependent variable
  "projectedPopulation": null, // Optional: Population scaling value (default: null)
  "rules": [ // Optional: Array of rules (default: null)
    {
      "id": "29a827d4-35ac-410e-9a31-45203dc1bb18", // Required: Rule ID (UUID)
      "value": "abcd", // Required: Value (string/number/boolean/array)
      "operator": ">" // Required: Operator (from Operators enum)
    }
  ],
  "scores": [
    {
      "fieldName": "P (TARGET=1) Min", // Required: Model field name
      "fieldLabel": "Model 3", // Optional: Display name (default: fieldName)
      "sortOrder": "desc" // Optional: Sorting (asc/desc, default: "desc")
    }
  ],
  "showFiltersOnDashboard": false, // Optional: Show filter controls (default: false)
  "sliderAssociations": [
    {
      "sliderID": "29a827d4-35ac-410e-9a31-45203dc1bb18", // Required: Slider ID
      "uswID": "d292c59c-e1f6-4f7e-ac53-525b7b6e6a56", // Required: Chart ID
      "showInDashboard": false // Optional: Show slider on dashboard (default: false)
    }
  ],
  "sliders": [
    {
      "id": "29a827d4-35ac-410e-9a31-45203dc1bb18", // Required: Slider ID (UUID)
      "name": "Cost of contact", // Required: Slider name
      "description": null, // Optional: Description (default: null)
      "min": 0, // Required: Minimum value
      "max": 100, // Required: Maximum value
      "value": 10, // Required: Current value
      "label": "coc" // Optional: Display label (default: null)
    }
  ],
  "title": "Targeted Marketing", // Optional: Dashboard title (default: null)
  "variableSelectors": null, // Optional: Variable aliases (default: null)
  "version": "2.3", // Optional: Config version (latest: 2.3, default: 1.0)
  "xAxisName": "Percent treated" // Optional: X-axis label (default: "Percent treated")
};
```

## **Common Issues**
1. **Mismatch in column names:** Ensure that the number of column names matches the dataset shape.  
2. **Invalid model type:** Ensure that the model conforms to the `ScikitModel` interface and implements a scoring function e.g `predict_proba` method.  
3. **Authentication failure:** Double-check credentials and the Gooder AI endpoint URL.
4. **Dataset size limits:** If you encounter size-related errors, adjust the `max_size_uploaded_data` or `max_size_saved_data` parameters.
5. **Model naming issues:** Ensure that the `model_names` list has the same length as the `models` list to avoid default naming.


## Loading specific configs: 
```python 
from gooder_ai.configs import load_starter_config

config = load_starter_config()
```

This config can be used to create view

## Sample Notebooks
[Running valuate_model on fraud detection models](https://drive.google.com/uc?export=download&id=1c3o2z7sTVB2rD-cm5xdtj-BiRE9vmC-m
)