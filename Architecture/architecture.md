# Architectural Style: Climate-Driven Energy Demand Analytics System

The system follows a Client–Server architecture implemented through a REST API and internally structured using a Layered Architecture.

This design separates the user interface from the backend services responsible for data processing and machine learning operations.

The architecture was selected to ensure:

- separation of concerns
- maintainability
- scalability
- testability
- clear responsibility boundaries between components

The system integrates user interaction, authentication, data processing, and machine learning modeling into a coherent architecture.

---

# AS1 – Architectural Patterns

## Streamlit-Based Client–Server Architecture

The system adopts a Streamlit-based client–server architecture where:

- the client interface is implemented using Streamlit
- the backend processing layer is composed of Python services responsible for:
  - authentication
  - data processing
  - machine learning prediction
  - model validation
  - visualization generation

Communication between the user interface and the processing components occurs internally within the Streamlit application runtime.

The application integrates:

- interactive dashboards
- real-time prediction services
- historical analytics
- model validation workflows
- CSV/JSON data visualization

Advantages of this architecture include:

- simplified deployment and maintenance
- fast integration between UI and machine learning components
- reduced communication overhead
- rapid prototyping and experimentation
- centralized application management

---

## Layered Architecture

The system follows a layered architecture pattern where functionality is divided into logical and independent layers.

Each layer interacts only with adjacent layers to maintain:

- low coupling
- high cohesion
- modularity
- maintainability

The layers implemented in the system are:

1. Presentation Layer (Streamlit Pages and UI Components)

2. Session & Authentication Layer
   - user authentication
   - session state management
   - role-based access control

3. Application Service Layer
   - prediction orchestration
   - validation workflows
   - metric computation
   - dashboard coordination

4. Data Processing Layer
   - feature engineering
   - temporal transformations
   - data filtering
   - preprocessing pipelines

5. Machine Learning Layer
   - Random Forest model
   - Linear Regression model
   - inference services
   - model evaluation

6. Persistence Layer
   - JSON prediction storage
   - serialized model storage (.pkl)
   - dataset access
   - configuration files

---

## Architectural Characteristics

The architecture was designed to support:

- modular development
- independent model experimentation
- real-time forecasting
- historical prediction analysis
- extensibility for future ML models
- interactive analytical visualization

The modular organization also facilitates:

- debugging
- testing
- future migration to external APIs or cloud services
- scalability of the analytical components

---

# AS2 – System Architecture Overview

The Streamlit application centralizes both frontend interaction and backend processing inside a unified Python environment.

Users interact with the graphical interface to:

- configure prediction scenarios
- visualize historical demand behaviour
- validate model performance
- compare predictions against real values
- export analytical results

The Data Processing Layer is responsible for transforming temporal and climatic variables into machine learning features used during inference and validation.

The Machine Learning Layer executes prediction workflows using trained models, including:

- Linear Regression
- Random Forest Regressor

The modular separation between interface, processing, modeling, and persistence layers ensures:

- maintainability
- extensibility
- scalability
- simplified debugging
- independent model experimentation

---

## AS3.1 Presentation Layer (Streamlit Client)

The user interface is implemented using Streamlit.

The Streamlit application acts as the main presentation layer of the system, providing an interactive web-based interface for users to access all analytical and machine learning functionalities.

User interactions within the Streamlit interface trigger internal application workflows rather than direct backend API calls, since both frontend and backend logic are integrated within the same Python-based application.

Examples of user-driven actions include:

- selecting prediction models (Random Forest / Linear Regression)
- configuring real-time forecasting scenarios
- filtering historical data
- executing model validation
- visualizing metrics and performance results
- exporting datasets and predictions

---

### Streamlit Implementation Details

The Streamlit application is designed as a modular multi-page system, where each page represents a specific functional component of the platform.

The main sections include:

- Authentication (login/logout system)
- Dashboard (global analytics and visualization)
- Real-time prediction interface
- Historical prediction analysis
- Model metrics and evaluation
- Administrative panel (admin-only features)

After authentication, user session state is maintained using Streamlit session management, allowing role-based access control (e.g., admin vs standard user).

Each interaction in the interface triggers internal function calls that:

- load trained models
- process input features
- generate predictions
- compute evaluation metrics
- render visual outputs (Plotly charts, tables, and metrics)

Responses are not exchanged via HTTP in a separate backend, but instead are processed directly within the Streamlit runtime environment and displayed dynamically.

This architecture ensures:

- fast response time
- simplified deployment (single application)
- tight integration between UI and machine learning logic
- reduced system complexity compared to a distributed API-based architecture

---

## AS3.2 Authentication Layer

Authentication is currently managed directly within the Streamlit application layer.

The authentication-related logic is located in:

*/src/utils/user_manager.py*

User credentials are stored in a JSON file located in:

*/src/utils/users.json*

### Password Security

Passwords are processed using bcrypt hashing before being stored.

This ensures that plaintext passwords are never stored in the system.

---

### Session-Based Authentication

Authentication is handled through Streamlit session state management.

The authentication flow is as follows:

1. The user submits credentials through the login form.
2. The application validates the credentials using the authentication utility.
3. If authentication succeeds, the authenticated user object is stored in `st.session_state["user"]`
4. The user is redirected to the protected application pages.
5. Subsequent pages verify the existence of the authenticated session before granting access.

---

### User Roles

The system defines two user roles.

#### Authenticated User

Standard users can:

- request predictions
- view model evaluation metrics
- explore processed datasets

#### Authenticated Admin

Administrators can additionally:

- trigger data ingestion
- execute the cleaning pipeline
- run feature engineering
- train models
- manage users

Administrative privileges are assigned during account creation through an optional administrator token.

To register as an administrator, the user must provide a valid admin token in the **"Admin Token"** field during the sign-up process.

### Authentication Logging

All authentication attempts are logged with timestamps for monitoring and auditing purposes.

### Current Authentication Architecture

The current authentication architecture follows a session-based structure:

    Streamlit App
        ↓
    user_manager.py
        ↓
    users.json

This structure provides a lightweight and modular authentication system while allowing future architectural improvements without major changes to the application flow.

---

## AS3.3 Application Service Layer

The application service layer coordinates interactions between the Streamlit interface and the internal system modules.

Rather than using API endpoints, the application relies on direct function calls imported from local modules.

Responsibilities include:

- orchestrating pipeline execution
- triggering model training
- loading trained models
- generating predictions
- coordinating interactions between modules
- isolating business logic from the user interface layer

This layer prevents the Streamlit interface from directly interacting with low-level processing components.

Instead, the UI communicates with dedicated service and utility modules responsible for handling the application's core operations.

---

### Architectural Separation

The system follows a modular architecture where the presentation layer remains separated from the processing logic.

The Streamlit interface is responsible only for:

- collecting user input
- triggering application actions
- displaying results and visualizations

Core functionalities such as:

- data ingestion
- preprocessing
- feature engineering
- model training
- prediction generation

are implemented in independent modules and imported when required.

---

### Current Interaction Structure

The current application flow follows this structure:

    Streamlit Interface
            ↓
    Service / Utility Modules
            ↓
    ML Pipelines and Processing Components
            ↓
    Models / Data / Outputs

This structure improves maintainability, readability, and modularity while reducing coupling between the user interface and the system logic.

---

## AS3.4 Data Ingestion Layer

The ingestion module retrieves external datasets from:

- **ENTSO-E** electricity demand data
- **ERA5 (Copernicus)** climate data

Raw datasets are stored without modification in:

*/data/raw/weather/*
*/data/raw/energy/*

The ingestion process can be triggered via the API by an administrator.

Errors during ingestion are logged and handled gracefully.

---

## AS3.5 Data Cleaning and Alignment Layer

This module performs preprocessing operations including:

- timezone alignment
- missing timestamp handling
- validation of required columns
- removal of corrupted records
- merging climate and energy datasets

The code for this component is located in:

*/src/cleaning/*

Processed datasets are stored in:

*/data/processed/*

Validation checks prevent pipeline failures due to incomplete data.

---

### Energy Dataset Cleaning

The energy dataset is processed through a structured cleaning pipeline designed to ensure temporal consistency, data integrity, and compatibility with climate data for subsequent merging.

The cleaning process is implemented as a sequence of transformations applied in a fail-fast manner, where invalid states interrupt execution to preserve data reliability.

---

#### Data Loading and Initial Validation

The dataset is loaded from a CSV file, using the first column as the index.

A validation step ensures that:

- the dataset is successfully loaded  
- the dataset is not empty  

If the dataset is empty or cannot be loaded, execution is interrupted.

---

#### Datetime Index Conversion

The original index is converted into a datetime format to enable time-based operations.

This step ensures:

- compatibility with resampling operations  
- correct temporal ordering  

Errors during conversion are logged and propagated.

---

#### Column Standardization

The column `"Actual Load"` is renamed to `"load"` to enforce a consistent naming convention across the system.

A validation step ensures that:

- the required `"load"` column exists after transformation  

If the column is missing, execution is stopped.

---

#### Timestamp Normalization

The datetime index is reset and transformed into an explicit `"timestamp"` column.

This ensures:

- compatibility with other datasets  
- consistency with merging operations  

A validation check guarantees that the timestamp column is correctly created.

---

#### Duplicate Handling and Sorting

Duplicate records based on the `"timestamp"` column are removed.

The dataset is then sorted in ascending chronological order to ensure:

- temporal consistency  
- correct sequencing for time-based analysis  

---

#### Timezone Alignment

All timestamps are converted to UTC format.

This step is critical to:

- ensure alignment with weather data  
- avoid inconsistencies caused by timezone differences  

---

#### Temporal Resampling

The dataset is resampled to an hourly frequency using mean aggregation.

This ensures:

- uniform temporal granularity  
- compatibility with the weather dataset  

---

#### Missing Value Monitoring

Missing values are not immediately removed or imputed.

Instead:

- missing value counts are computed  
- results are logged for monitoring and analysis  

This approach preserves transparency regarding data quality.

---

#### Final Validation and Formatting

A final validation ensures that:

- the `"load"` column exists in the processed dataset  

Values are rounded to two decimal places to:

- standardize numerical precision  
- reduce unnecessary variability  

---

#### Data Persistence

The cleaned dataset is stored in the processed data directory:

*/data/processed/*

During this step:

- the final number of rows is logged  
- successful execution is recorded  

---

#### Summary

The energy data cleaning pipeline ensures:

- consistent timestamp formatting  
- standardized column naming  
- removal of duplicates  
- timezone normalization to UTC  
- hourly temporal alignment  
- validation of required data fields  
- full traceability through logging  

This prepares the dataset for integration with climate data in the merging stage.

---

### Weather Dataset Cleaning and Preparation

The weather dataset requires a multi-stage preprocessing pipeline due to its structure, format, and distribution across multiple files.

Unlike the energy dataset, climate data is provided as multiple compressed NetCDF files, each representing different variables and time periods. The system processes these files through a sequence of extraction, organization, merging, and cleaning steps.

---

#### Data Extraction from Compressed Files

Weather data is initially stored as compressed files containing NetCDF (`.nc`) datasets.

The extraction process:

- validates whether files are ZIP archives  
- extracts only `.nc` files  
- renames extracted files to preserve source traceability  
- ignores corrupted or invalid files  

This step ensures that all usable NetCDF files are available for further processing.

---

#### Organization by Variable

After extraction, the system processes a large number of NetCDF files (monthly data across multiple variables).

Files are grouped based on their variable type, identified through filename patterns:

- accumulated values (`acc`)  
- average values (`avg`)  
- instantaneous values (`inst`)  
- maximum values (`max`)  

For each group:

- NetCDF files are loaded using `xarray`  
- datasets are converted into tabular format (DataFrame)  
- data is aggregated by timestamp (`valid_time`) using mean values  
- monthly data is concatenated into a single yearly dataset  

This results in four structured CSV files, each representing one variable category across the full year.

---

#### Intermediate Data Persistence

Each variable-specific dataset is stored as an individual CSV file:

*/data/raw/weather/weather_2025_<variable>.csv*

This step reduces complexity and allows modular processing of large datasets.

Temporary NetCDF files are removed after processing to optimize storage usage.

---

#### Merging Weather Variables

The four variable-specific datasets are merged into a single unified dataset.

This process includes:

- loading all variable datasets  
- validating the presence of required columns (`valid_time`)  
- removing irrelevant metadata columns (e.g., `number`, `expver`)  
- removing duplicated spatial columns (latitude, longitude)  

The datasets are merged using an inner join on the `valid_time` column to ensure:

- temporal alignment across all variables  
- consistency of observations  

The result is a consolidated weather dataset containing all relevant climate features.

---

#### Time Handling and Standardization

The merged dataset is processed to standardize time representation:

- the time column (`valid_time`) is converted to datetime format  
- timestamps are aligned to UTC  

This ensures compatibility with the energy dataset and supports time-based analysis.

---

#### Spatial Aggregation

Weather data originally contains multiple spatial points (grid-based measurements).

To align with energy data:

- all spatial points are aggregated per timestamp using mean values  

This produces a single representative value per variable and timestamp.

---

#### Unit Conversion

Climate variables are converted into standard and interpretable units:

- temperature variables (Kelvin → Celsius)  
- precipitation variables (meters → millimeters)  

This ensures consistency and interpretability for modeling.

---

#### Feature Derivation (Wind Speed)

Wind speed is computed from its vector components:

- horizontal wind (`u10`)  
- vertical wind (`v10`)  

These are combined into a single feature:

- `wind_speed`  

After computation, the original components are removed to reduce redundancy.

---

#### Column Standardization

Columns are renamed to consistent and descriptive names:

- `valid_time` → `timestamp`  
- `t2m` → `temperature`  
- `mx2t` → `temp_max`  
- `mn2t` → `temp_min`  
- `tp` → `total_precipitation`  
- `cp` → `convective_precipitation`  
- `ssrd` → `solar_radiation`  

This ensures alignment with the rest of the system and improves readability.

---

#### Final Validation and Sorting

The dataset is validated to ensure:

- presence of the timestamp column  
- correct chronological ordering  

The dataset is sorted by timestamp, and missing values are logged for monitoring purposes.

---

#### Final Formatting and Storage

All numerical values are rounded to a fixed precision.

The final cleaned dataset is stored in:

*/data/processed/weather_2025_clean.csv*

---

#### Summary

The weather data pipeline ensures:

- extraction of NetCDF data from compressed sources  
- grouping and consolidation of monthly datasets  
- merging of multiple climate variables  
- spatial aggregation into time-based observations  
- unit standardization and feature derivation  
- consistent timestamp formatting (UTC)  
- removal of redundant and irrelevant data  
- validation and logging for reliability  

This process transforms complex raw climate data into a structured dataset suitable for integration with energy demand data.

---

### Dataset Integration (Energy + Weather)

After both datasets are individually cleaned and standardized, the system performs a final integration step to combine energy demand data with climate variables.

This step is essential to enable machine learning models to capture relationships between weather conditions and electricity consumption.

---

#### Input Validation

Both datasets are first validated to ensure:

- they are successfully loaded  
- they are not empty  
- they contain the required `"timestamp"` column  

If any validation fails, execution is interrupted to prevent invalid merges.

---

#### Timestamp Alignment

Although both datasets are previously converted to UTC, an additional normalization step is applied:

- timestamps are converted to datetime format  
- timezone information is removed (`tz_localize(None)`)  

This ensures exact matching between datasets during the merge operation.

---

#### Dataset Merging

The integration is performed using an inner join on the `"timestamp"` column:

- energy dataset (target variable: load)  
- weather dataset (climate features)  

This guarantees:

- perfect temporal alignment  
- only shared timestamps are retained  

A validation step ensures that the resulting dataset is not empty.

---

#### Post-Merge Cleaning

After merging, the dataset is refined by:

- removing unnecessary or redundant columns (e.g., spatial metadata)  
- sorting records chronologically by timestamp  

This ensures a clean and consistent structure for downstream processing.

---

#### Data Persistence

The final merged dataset is stored in:

*/data/processed/dataset_merged.csv*

Logging captures:

- dataset shape after merge  
- successful execution  

---

#### Pipeline Integration

All steps described in the weather and energy preprocessing workflows - including:

- weather extraction and organization  
- weather merging and cleaning  
- energy cleaning  
- final dataset integration  

are orchestrated through a unified pipeline.

This design ensures that:

- the entire process can be executed with a single command  
- intermediate scripts do not need to be run manually  
- execution is consistent and reproducible  

The pipeline coordinates all stages sequentially, handling dependencies between components and ensuring that each step receives correctly processed input data.

---

#### Summary

The dataset integration process ensures:

- strict validation of input datasets  
- consistent timestamp formatting  
- accurate temporal alignment  
- combination of energy demand with climate variables  
- removal of redundant information  
- full automation through pipeline orchestration  

This results in a final dataset ready for feature engineering and machine learning modeling.

---

## AS3.6 Feature Engineering Module

The feature engineering component generates predictive variables used by the models.

The implementation is located in:

*/src/features/*

Current features include:

- hour of day
- day of week
- month
- cyclic features such as hours of the day and days of the week
- lagged demand features for 1h, 24h (a day) and 168h (a week)
- rolling features like temperature and load of the day
- climatic features such as temperature range, if its likely to be happening a cold or heatwave and if there is any anomaly in the temperature. There is always a feature for the hours during the day only (between 7am and 7pm), the differentiation between the current load and the load from 1 hour before
- interaction between temperature and hour of the day 

These features capture temporal patterns and climate effects on electricity demand.

---

## AS3.7 – Modeling Component

The system implements two predictive models for electricity demand forecasting and we also implement a Naive baseline to compare if there is indeed an improvement.

### Lag of 1 hour (Naive Baseline)

**Lag of 1 hour** is used as our naive baseline, providing a default value against which we can compare our models. We assume that the energy consumption in the current hour is the same as in the previous hour, representing a minimal benchmark.

---

### Linear Regression (ML Baseline)

**Linear Regression** is used as a baseline due to its simplicity and interpretability.

It establishes a performance benchmark for the machine learning system.

---

### Random Forest Regressor

A **Random Forest Regressor** is implemented to capture nonlinear relationships between climate variables and electricity demand.

The model considers interactions between:

- temperature
- solar radiation
- wind conditions

Advantages include:

- ability to model nonlinear relationships
- robustness to noisy data
- reduced overfitting through ensemble learning

---

### Model Configuration and Training

The parameters of each model are stored in `utils/model_config.json` and these can be adjusted by an **Authenticated Admin**. After running the file `training_models.py`, a folder named **models** will be generated, where the trained models will be stored as well as the split sections of the code for both this step and the next one, in format *.pkl*.
(Note: this approach was adopted to mitigate issues related to inconsistent data splitting between training and testing phases.)

If the desired configuration has already been requested by a previous admin user, the system avoids redundant computation by skipping the training process rather than re-executing the code. This is achieved by generating a unique hash for each configuration and comparing it with those stored from previous experiments.

---

### Model Evaluation

The evaluation phase is performed after training and aims to assess the performance and generalization capability of the developed models. The evaluation pipeline loads the previously saved train/test splits and trained models from the directory `data/models/`, ensuring full consistency between the training and testing stages.

The dataset used for evaluation is loaded from `data/processed/features.csv`, and the same preprocessing step (removal of the first 168 samples) is applied to maintain alignment with the training phase.

A naive baseline is first established using a **1-hour lag approach**, where the predicted value corresponds to the observed value from the previous hour (`lag_1h`). This baseline serves as a minimum benchmark against which the machine learning models are compared.

The following evaluation metrics are reported:

- **Mean Absolute Error (MAE)**
- **Root Mean Squared Error (RMSE)**
- **R² Score**

Both **Linear Regression** and **Random Forest** models, loaded from `data/models/lr_model.pkl` and `data/models/rf_model.pkl`, are evaluated on the test set. Their results are directly compared with the baseline. Additionally, an improvement metric is computed based on the difference in MAE relative to the baseline.

To further analyze model behavior, a **residual analysis** is conducted using the Random Forest predictions. Summary statistics such as mean, standard deviation, minimum, and maximum residual values are computed and stored. The full residuals are also saved to `data/results/residuals_<run_id>.json` for further inspection.

An **overfitting analysis** is performed by comparing model performance on both training and test sets. This allows for the identification of potential overfitting by analyzing discrepancies between training and testing errors.

Furthermore, **feature importance** is extracted from the Random Forest model, providing insight into the relative contribution of each feature in the prediction process.

All evaluation outputs are stored in the directory `data/results/`, including:

- Detailed results (`results_<run_id>.json`)
- Residuals (`residuals_<run_id>.json`)
- Test set predictions for visualization (`test_predictions.json`)

Additionally, a summary of each experiment is appended to `data/experiments/experiments.json`, including the configuration hash, timestamp, and key performance indicators. This enables experiment tracking and comparison across different model configurations.

Finally, a simple decision rule is applied: if at least one model outperforms the baseline (in terms of MAE), it is considered a meaningful improvement; otherwise, the models are deemed not to provide added predictive value over the naive approach.

---

### Model Persistence Strategy

Trained models and intermediate datasets are stored in:

`data/models/`

This includes:

- Trained models (`lr_model.pkl`, `rf_model.pkl`)
- Train/test splits (`X_train.pkl`, `X_test.pkl`, `y_train.pkl`, `y_test.pkl`)
- Corresponding timestamps (`ts_train.pkl`, `ts_test.pkl`)

Persistence is handled using **serialization via Joblib**, which is suitable for both simple and complex models.

#### Linear Regression Persistence

The Linear Regression model is stored as a serialized object (`lr_model.pkl`) using Joblib. Although the model internally consists of coefficients and an intercept, saving the full object ensures consistency and simplifies loading during evaluation and inference.

#### Random Forest Persistence

Due to the complexity of ensemble tree structures, the Random Forest model is also stored using Joblib serialization (`rf_model.pkl`).

This approach guarantees:

- Integrity of the trained model  
- Portability across different environments  
- Efficient loading for inference and evaluation

---

### Model Selection and Hyperparameter Optimization

To improve predictive performance and ensure an informed model selection process, the system performs hyperparameter optimization using `GridSearchCV`.

The optimization process evaluates multiple configurations for each machine learning model using time-series cross-validation (`TimeSeriesSplit`), ensuring that temporal data ordering is preserved during validation.

The following models are currently optimized:

- Linear Regression
- Random Forest Regressor

For each model, multiple hyperparameter combinations are tested and evaluated using Mean Absolute Error (MAE) as the primary scoring metric.

After the optimization process:

1. The best hyperparameters for each model are identified.
2. Both optimized models are evaluated on the test dataset.
3. Performance metrics are computed, including:
   - MAE
   - RMSE
   - R² Score
4. The best-performing model is automatically selected.
5. The trained models and optimization results are stored locally and the optimization results are saved in:

*/data/models/best_params.json*

The trained models are exported as serialized `.pkl` files for later use by the application.

---

### Model Visualization in the Application

The application loads the stored optimization results and displays the best-performing model directly within the Streamlit interface.

This allows users and administrators to:

- inspect the selected model
- review evaluation metrics
- compare model performance
- visualize the model chosen during the optimization phase

This approach ensures transparency in the model selection process while supporting reproducibility and maintainability.

---

# AS4 – System Workflows

## Model Management Workflow (Admin)

1. The administrator logs into the Streamlit application.
2. The administrator accesses the model management interface.
3. Previously trained models, stored metrics, and optimization results are loaded from local storage.
4. The administrator can:
   - inspect existing model performance
   - compare evaluation metrics
   - modify selected model parameters
   - execute model retraining
   - trigger the complete processing pipeline
   - execute individual pipeline stages separately

The available pipeline stages include:

- Data Ingestion
- Data Cleaning
- Feature Engineering
- Model Training
- Model Evaluation
- Prediction Generation

5. Updated results are stored locally in */data/experiments/experiments.json* and displayed in the Streamlit dashboard.

---

## Prediction and Dashboard Workflow (User)

1. The user logs into the system.
2. The Streamlit application loads:
   - the best trained model
   - stored evaluation metrics
   - processed datasets
   - prediction outputs
   - optimization results

3. The user can:
   - request predictions
   - explore processed datasets
   - visualize model evaluation metrics
   - inspect the selected best-performing model

4. When a prediction is requested:
   - the trained model is loaded from local storage
   - the required features are generated
   - the prediction is computed and displayed in the interface

Prediction responses are designed to execute with low latency to provide near real-time interaction within the dashboard.

---

# AS5 – Repository Structure

project/
│
├── Architecture/
├── data/
│   ├── processed/
│   └── raw/
│       ├── energy/
│       └── weather/
│   └── experiments/
│   └── models/
│   └── results/
│
├── logs/
├── Requirements/
├── src/
│   ├── auth/
│   ├── cleaning/
│   ├── features/
│   ├── ingestion/
│   ├── models/
│   ├── pipeline/
│   ├── streamlit/
│       └── pages/
│   └── utils/
│
├── testing/
├── .env
├── .gitignore
├── .gitkeep
├── .gitlab-ci.yml
└── README.md

---

# AS6 – Quality Attributes

Quality attributes are evaluated following ISO/IEC 25010 scenarios.

---

## Performance

The system is designed to ensure efficient execution of data processing and prediction tasks through systematic performance monitoring and optimization strategies.

### Performance Measurement

Execution time is measured for all major components of the data pipeline, including:

- Data ingestion  
- Data cleaning  
- Data merging  
- Feature engineering  

Execution times are automatically recorded in `logs/performance.log`, enabling persistent tracking across runs.

---

### Pipeline Performance

The full pipeline includes data ingestion as its initial stage. However, ingestion is disabled by default due to its high execution cost:

- Weather ingestion (~1.5 hours) is commented out  
- Energy ingestion (~15 seconds) can be executed when required  

Instead, previously collected datasets are reused from local storage to improve efficiency.

A typical pipeline execution (without ingestion) produces:

- Energy cleaning: ~0.69 s  
- Weather cleaning: ~12.28 s  
- Data merge: ~0.07 s  
- Feature engineering: ~0.01 s  
- Total pipeline time: ~13.21 s  

The weather processing stage is the most computationally expensive due to dataset size and complexity.

---

### Prediction Performance

For the machine learning component:

- Model training time is measured during execution  
- Prediction latency is minimized during inference  

Target requirement:

- Prediction response time: **< 1 second**

This is achieved by performing all preprocessing offline and restricting runtime operations to model inference only.

---

### Performance Monitoring Strategy

Performance is continuously monitored through:

- stage-level execution time measurement  
- total pipeline execution time tracking  
- persistent logging in `logs/performance.log`  

Each pipeline stage is individually timed, enabling:

- identification of bottlenecks  
- comparison across executions  
- targeted optimization of expensive operations  

This ensures full observability of system performance.

---

### Summary

Performance is ensured through:

- measurement of execution time for each pipeline stage  
- tracking total pipeline execution time  
- persistent logging of performance metrics  
- stage-level monitoring for bottleneck detection  
- avoidance of repeated ingestion of large datasets  
- optimization for fast prediction response (< 1 second)

---

## Reliability

The system follows a reliability-oriented design based on validation, fail-fast execution, and centralized logging.

---

### Failure Handling Strategy

The system adopts a **fail-fast approach**, where:

- invalid inputs immediately interrupt execution  
- incomplete or corrupted datasets are not processed  
- errors are logged and lead to controlled termination  

This approach prioritizes **data integrity over partial execution**, preventing silent failures and inconsistent outputs.

The system does not implement graceful degradation, since processing incomplete or inconsistent data could compromise model correctness.

---

### Input Validation

Validation is performed at multiple stages:

- verification of input file existence before execution  
- validation of non-empty datasets  
- verification of required columns before transformations  
- validation of API credentials during ingestion  

These checks ensure that all processing stages operate on valid and consistent data.

---

### Exception Handling

All major components are protected with structured exception handling:

- ingestion handles API and file-related errors  
- cleaning and transformation steps handle data inconsistencies  
- the pipeline includes a global try/except block  

Errors are logged with descriptive messages and propagated to avoid silent failures.

---

### Logging Strategy

A centralized logging system ensures traceability and debugging capability:

- all components log to `logs/reliability.log`

Each log entry includes:

- timestamp  
- severity level (INFO, WARNING, ERROR)  
- descriptive message  

The system logs:

- execution steps  
- validation checks  
- missing values  
- errors and failures  
- pipeline start and completion  

This enables full traceability of system execution.

---

### Idempotency and Robustness

The ingestion process is designed to be idempotent:

- existing files are not re-downloaded  
- repeated executions do not duplicate data  

External API failures are detected and logged.

Although retry mechanisms are not currently implemented, the architecture allows their integration to improve robustness.

---

### Reproducibility

The system ensures reproducibility through:

- deterministic pipeline execution  
- consistent data processing order  
- configuration via environment variables  

Given the same inputs, the system produces identical outputs.

---

### Summary

Reliability is achieved through:

- fail-fast execution  
- strong input validation  
- centralized logging  
- structured exception handling  
- reproducible processing  

---
## Security

Security refers to the system’s ability to prevent unauthorized access while ensuring that legitimate users can securely interact with protected functionalities, such as model training, prediction generation, and data management.

The system enforces security across multiple architectural layers, particularly the API Layer, Authentication Layer, and User Management Module, ensuring controlled access to all critical operations.

### Security Properties

The system addresses the following security properties:

- Confidentiality: user credentials and authentication tokens are protected from unauthorized access
- Integrity: system data, models, and operations cannot be altered by unauthorized users
- Authentication (Assurance): users must prove their identity before accessing the system
- Authorization: role-based access control restricts sensitive operations
- Auditing: system activity is logged to enable traceability
- Availability: authenticated users can access system services reliably

### Security Mechanisms and Architectural Mapping

Security is implemented through multiple coordinated components:

### Authentication Layer:

    - Handles user login
    - Verifies credentials using bcrypt
    - Generates JWT tokens
    - Validates tokens for protected endpoints

### User Management Module

- Handles user registration and user administration
- Stores user credentials securely in the persistence layer
- Enforces password policies (minimum length)

### Authorization Control

Enforces role-based access:
 - User → prediction and metrics
 - Admin → ingestion, cleaning, training, configuration
Restricted endpoints validate user roles before execution

### Secure Storage (Persistence Layer)

- Passwords stored as bcrypt hashes in users.json
- No plaintext credentials are stored
- Prediction history and system data are separated by type

### Configuration Security

- Sensitive values (users, tokens, secrets) are stored in environment variables
- .env file is excluded from version control

### Auditing and Logging

The system logs:

- login attempts
- user management actions
- model execution actions

Each log includes:

- timestamp
- username
- action performed

---

### Security Scenarios (ISO/IEC 25010)

#### Scenario 1 – Unauthorized Access to Protected Pages

- Source: Unauthenticated user
- Stimulus: Attempts to access restricted application pages without logging in
- Environment: Normal system operation
- Artifact: Streamlit Authentication Layer
- Response:
    - Access is denied
    - User is redirected to the login page
    - No protected content is displayed
- Response Measure:
    - 100% of unauthorized access attempts are blocked
    - No sensitive information is exposed

---

#### Scenario 2 – Invalid Login Attempt

- Source: User
- Stimulus: Incorrect username or password submitted
- Environment: Normal operation
- Artifact: Authentication Layer
- Response:
    - Authentication is denied
    - Generic error message is displayed
- Response Measure:
    - No internal system details are exposed
    - All failed attempts are recorded

---

#### Scenario 3 – Secure User Registration

- Source: New user
- Stimulus: Creates a new account
- Environment: Normal operation
- Artifact: User Management Module
- Response:
    - Password is hashed using bcrypt before storage
    - User credentials are stored securely
- Response Measure:
    - No plaintext passwords are stored in the system

---

#### Scenario 4 – Invalid Admin Token During Registration

- Source: New user
- Stimulus: Attempts to register as administrator using an invalid admin token
- Environment: Normal operation
- Artifact: Registration Validation Layer
- Response:
    - Registration as administrator is denied
    - User receives an error message
- Response Measure:
    - Only users with a valid admin token can obtain administrative privileges

---

#### Scenario 5 – Access to Stored Model Results

- Source: Authenticated user
- Stimulus: Requests access to model metrics and prediction results
- Environment: Normal operation
- Artifact: Dashboard Visualization Layer
- Response:
    - Stored results are loaded and displayed
    - Only authenticated users can access the app pages
- Response Measure:
    - No page data is accessible without authentication

---

#### Scenario 6 – Session Validation After Logout

- Source: Authenticated user
- Stimulus: Logs out and attempts to revisit protected pages
- Environment: Normal operation
- Artifact: Session Management Layer
- Response:
    - Session is cleared
    - Access to protected pages is denied
- Response Measure:
    - Previous authenticated sessions become invalid immediately after logout

---

#### Scenario 7 – Protection of Stored Credentials

- Source: Internal system storage
- Stimulus: Credentials are written to persistent storage
- Environment: Normal operation
- Artifact: Persistence Layer
- Response:
    - Passwords are stored only as bcrypt hashes
    - Sensitive authentication data is never stored in plaintext
- Response Measure:
    - 100% of stored passwords are encrypted using bcrypt hashing

---

### Limitations

Despite the implemented mechanisms, the system presents some limitations that should be acknowledged:

- Communication is handled within a simplified architecture without enforced HTTPS in the current setup
- No token expiration or refresh mechanism is implemented for session management
- No rate limiting or brute-force protection is present for authentication endpoints
- User data is stored in JSON files instead of a relational database or dedicated identity service
- No multi-factor authentication is available for enhanced security

These limitations are acceptable within the academic scope of the project and reflect design choices aimed at prioritising simplicity, clarity, and ease of implementation over production-level security and scalability requirements.

---

# AS7 – Architectural Rationale

The system adopts a combined Client–Server and Layered Architecture in order to balance simplicity, modularity, and scalability.

The separation of the Streamlit application (presentation layer) from the internal processing components ensures that:

- the user interface remains lightweight and focused on interaction and visualization
- machine learning and data processing logic are isolated from the UI
- system components are easier to maintain and extend
- new features can be added without affecting the overall structure of the application

The layered design further improves the internal organization of the system by separating responsibilities into distinct functional levels, such as authentication, data processing, and model inference.

This separation enhances:

- maintainability, by isolating changes to specific layers
- testability, by allowing individual components to be validated independently
- readability, by clearly defining the role of each system module

Overall, the combination of these architectural patterns ensures a structured, modular, and extensible system suitable for machine learning-driven applications.

---

# AS8 – Testing Strategy

## Testing Approach

The system adopts an automated testing strategy using **pytest** to ensure correctness, robustness, and reliability across all system components.

All tests are organized in a dedicated `/Testing/` directory, following a modular structure aligned with the system’s layered architecture.

Testing covers both:

- successful execution paths
- failure and edge-case scenarios

This ensures that the system behaves correctly under both normal and unexpected conditions.

---

## Testing Levels

The system includes multiple levels of testing:

- **Unit Tests**: validate individual functions such as data cleaning, feature engineering, model training, and evaluation
- **Integration Tests**: validate interactions between multiple components across the full machine learning pipeline


This layered testing approach ensures both component-level correctness and overall system consistency.

---

## Testing Scope by Layer

Testing is directly aligned with the system architecture, ensuring that each layer is independently validated.

---

### Authentication Layer

Tested through:

- `test_user_manager`

Validates:

- password hashing and verification (bcrypt)
- user authentication logic
- role-based access control
- invalid login handling

---

### Data Pipeline Layer

Tested through:

- `test_ingest_energy`
- `test_ingest_weather`
- `test_extraction_weather`
- `test_merge_data`
- `test_merge_weather`
- `test_clean_energy`
- `test_clean_weather`
- `test_organize_weather`
- `test_dataset_features`
- `test_clean_energy`
- `test_clean_weather`

Validates:

- correct ingestion of energy and weather datasets
- handling of missing or inconsistent data
- correct merging of datasets
- data cleaning robustness
- dataset structure consistency

---

### Feature Engineering Layer

Tested through:

- `test_feature_engineering`
- `test_dataset_features`

Validates:

- correct generation of engineered features
- consistency of transformations across datasets
- presence and correctness of required model inputs

---

### Modeling Layer

Tested through:

- `test_train_models`
- `test_evaluate_models`
- `test_grid_search`

Validates:

- correct model training execution
- hyperparameter optimization (Grid Search)
- evaluation metrics (MAE, RMSE, R²)
- comparison between models (Linear Regression vs Random Forest)

---

### Integration Testing

A full pipeline integration test is implemented through:

- `test_integrate_pipeline`

Validates:

- end-to-end execution of the system pipeline
- interaction between ingestion, cleaning, feature engineering, and modeling
- overall system stability and reproducibility

---

## Failure Testing

The system includes explicit failure scenario testing to ensure robustness.

Tested scenarios include:

- missing input files
- corrupted datasets
- invalid or inconsistent data formats
- unauthorized user access attempts

These tests ensure:

- fail-fast behavior
- proper error handling
- prevention of silent failures
- system stability under incorrect inputs

---

## Continuous Integration

The system integrates automated testing using **CI/CD pipelines (GitLab CI or equivalent)**.

On each commit:

- dependencies are installed automatically
- the full test suite is executed using `pytest`
- the build fails if any test does not pass

This guarantees continuous validation of system correctness.

---

## Coverage Strategy

The testing strategy focuses on critical system components:

- data ingestion and preprocessing
- feature engineering logic
- machine learning training and evaluation
- authentication and user management
- full pipeline integration
- failure and edge-case handling

---

## Testing and Quality Attributes

The testing framework directly supports key software quality attributes:

- **Reliability:** ensures correct system behavior under normal and failure conditions
- **Maintainability:** allows independent validation of modular components
- **Robustness:** verifies system response to invalid or unexpected inputs
- **Reproducibility:** ensures consistent results across executions