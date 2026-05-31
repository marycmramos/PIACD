# Use Cases: Climate-Driven Energy Demand Analytics System

This document describes the main use cases of the system. Each use case represents a core interaction between users and the system, covering authentication, data ingestion, data processing, model training, prediction generation, and evaluation access.

The scope of all use cases is the Climate-Driven Energy Demand Analytics System.

---

# UC1 – User Registration

**Primary Actor:**  
User

**Level:**  
User Goal

**Stakeholders and Interests:**

- Users: want secure access to the system.
- System administrators: require controlled and identifiable users.
- Developers: require secure storage of credentials.

**Preconditions:**

- The user is not already registered in the system.

**Main Success Scenario:**

1. The user provides a username and password.
2. The system validates the input format and password length.
3. The user optionally provides an administrator registration token.
4. The system validates the administrator token.
5. The system hashes the password using bcrypt.
6. The system stores the new user credentials securely.
7. The system assigns the appropriate role:
   - Admin, if the token is valid
   - Standard user, otherwise
8. The system confirms successful registration.

**Extensions / Alternative Paths:**

2a. Invalid password format  
- The system rejects the password if it does not meet the minimum length requirement.

4a. Invalid administrator token  
- The system ignores administrator privileges.  

6a. Username already exists  
- The system informs the user that the username is already taken.

**Postconditions:**

- A new user account is securely stored, ensuring that the password is protected using cryptographic hashing.  
- The user can authenticate in the system.

---

# UC2 – User Authentication (Login)

**Primary Actor:**  
User

**Level:**  
User Goal

**Stakeholders and Interests:**

- Users: want secure and reliable access.
- System administrators: want secure authentication.
- Developers: require controlled access to protected endpoints.

**Preconditions:**

- The user is registered in the system.
- The user already has valid credentials.

**Main Success Scenario:**

1. The user enters username and password.
2. The system retrieves the stored user credentials.
3. The system verifies the password using bcrypt.
4. The system validates the user role and permissions.
5. The system grants access to the protected application areas.

**Extensions / Alternative Paths:**

3a. Invalid credentials  
- The system rejects authentication.  
- The user is informed that login failed.

2a. Username does not exist  
- The system denies authentication.

**Postconditions:**

- The user is authenticated successfully.
- The user can access authorized system functionalities according to their role.

---

# UC3 – Data Ingestion

**Primary Actor:**  
Authenticated Admin

**Level:**  
User Goal

**Stakeholders and Interests:**

- Administrators: want to update datasets.
- Researchers: require up-to-date energy and climate data.
- System developers: require reproducible data ingestion.

**Preconditions:**

- The administrator is authenticated.  
- External APIs are reachable.  
- Internet connection is available.

**Main Success Scenario:**

1. The administrator triggers the ingestion process.  
2. The system connects to the ENTSO-E Transparency Platform API.  
3. Electricity demand data is retrieved.  
4. The system connects to the Copernicus ERA5 Climate Data Store.  
5. Climate data is retrieved.  
6. The system stores the datasets in the raw data directory.  
7. The system logs the successful ingestion operation with timestamp and execution time.

**Extensions / Alternative Paths:**

2a. ENTSO-E API unavailable  
- The system logs the ingestion failure.  
- The ingestion process terminates safely.

4a. ERA5 API unavailable  
- The system logs the error and aborts the ingestion process.

**Postconditions:**

- Raw energy data is stored in */data/raw/energy/*.  
- Raw climate data is stored in */data/raw/weather/*.

---

# UC4 – Data Cleaning and Alignment

**Primary Actor:**  
Authenticated Admin

**Level:**  
User Goal

**Stakeholders and Interests:**

- Data scientists: require consistent datasets.  
- System developers: require robust preprocessing pipelines.

**Preconditions:**

- Raw datasets are available.

**Main Success Scenario:**

1. The administrator triggers the cleaning process.  
2. The system loads the raw climate and energy datasets.  
3. The system detects missing timestamps and invalid records.  
4. The system normalizes time zones.  
5. The system aligns climate and electricity demand data.  
6. The cleaned dataset is saved in the processed data directory.  
7. The system logs the successful cleaning operation with timestamp.

**Extensions / Alternative Paths:**

3a. Missing values detected  
- The system handles missing data using predefined strategies.

2a. Raw data files missing  
- The system logs the error and terminates the process.

**Postconditions:**

- Cleaned datasets are stored in */data/processed/*.

---

# UC5 – Model Training and Evaluation

**Primary Actor:**  
Authenticated Admin

**Level:**  
User Goal

**Stakeholders and Interests:**

- Administrators: want to update models.  
- Analysts: want reliable predictive models.  
- Researchers: want model evaluation results.

**Preconditions:**

- The administrator is authenticated.  
- Processed datasets are available.

**Main Success Scenario:**

1. The administrator triggers model training.  
2. The system generates predictive features.  
3. The dataset is split using time-aware splitting.  
4. The system performs hyperparameter optimization using Grid Search.
5. The system selects the best-performing model configuration.
6. The Linear Regression model is trained.  
7. The Random Forest model is trained.  
8. The system evaluates the models using MAE, RMSE, and R².
9. The system generates residual analysis visualizations.
10. The system evaluates potential overfitting using train and test metrics.
11. The system calculates feature importance scores.
12. The system records execution performance metrics for each training stage.
13. The trained models and evaluation metrics are stored.   
14. The system logs the model training operation, including timestamp and execution time.

**Extensions / Alternative Paths:**

4a. Grid Search fails
- The system logs the error and aborts training.

6a. Model training error
- The system logs the failure and aborts the process.

**Postconditions:**

- Trained models are stored.  
- Evaluation metrics are saved.

---

# UC6 – Prediction Generation

**Primary Actor:**  
Authenticated User

**Level:**  
User Goal

**Stakeholders and Interests:**

- Energy analysts: want demand forecasts.  
- Researchers: want predictive insights.

**Preconditions:**

- The user is authenticated.  
- A trained model exists.

**Main Success Scenario:**

1. The user selects a prediction mode and model.
2. The user provides climate and temporal input data.
3. The user selects the energy context.
4. The system validates the input values.
5. The system generates the required predictive features.
6. The system loads the selected trained model.
7. The model produces electricity demand predictions.
8. The system returns the estimated electricity demand.
9. The system generates visualizations of predicted demand over time.
10. The prediction request is stored in the prediction history.

**Extensions / Alternative Paths:**

1a. Selected model unavailable
- The system loads the best available model automatically.

**Postconditions:**

- The predicted electricity demand is returned to the user.

---

# UC7 – View Model Evaluation Metrics

**Primary Actor:**  
Authenticated User

**Level:**  
User Goal

**Stakeholders and Interests:**

- Analysts: want to assess model performance.  
- Researchers: want insight into prediction quality.

**Preconditions:**

- The user is authenticated.  
- Model evaluation results exist.

**Main Success Scenario:**

1. The user requests model evaluation metrics.
2. The system retrieves stored evaluation results.
3. The system displays model comparison metrics.
4. The system displays residual analysis visualizations.
5. The system displays overfitting analysis results.
6. The system displays feature importance rankings.
7. The system displays execution performance metrics.

**Extensions / Alternative Paths:**

2a. Evaluation results not available  
- The system informs the user that no metrics are available.

**Postconditions:**

- Evaluation metrics are displayed to the user.

---

# UC8 – Model Configuration

**Primary Actor:**  
Authenticated Admin

**Level:**  
User Goal

**Stakeholders and Interests:**

- Administrators: want to control model behaviour.
- Data scientists: want to experiment with different model configurations.
- System developers: require flexible model tuning.

**Preconditions:**

- The administrator is authenticated.
- The system is operational.

**Main Success Scenario:**

1. The administrator requests the current model configuration.
2. The system retrieves the current training parameters.
3. The administrator modifies configuration parameters such as:
   - Random Forest number of estimators
   - Maximum tree depth
   - Feature selection options
   - Model selection
4. The system validates the provided configuration.
5. The system saves the updated configuration.
6. The system confirms the successful update.

**Postconditions:**

- Updated model configuration parameters are stored and will be applied during the next model training operation.

---

# UC9 – User Management

**Primary Actor:**  
Authenticated Admin

**Level:**  
User Goal

**Stakeholders and Interests:**

- Administrators: require control over system access.
- Users: require secure and reliable account management.
- System developers: require controlled role management.

**Preconditions:**

- The administrator is authenticated.

**Main Success Scenario:**

1. The administrator requests the list of registered users.
2. The system retrieves stored user accounts.
3. The administrator selects a user account.
4. The administrator performs an action such as:
   - Promote user to admin
   - Disable user account
   - Delete user account
5. The system validates the action.
6. The system updates the user data.
7. The system confirms the successful update.

**Extensions / Alternative Paths:**

5a. User not found  
- The system informs the administrator that the user does not exist.

**Postconditions:**

- User account information is updated accordingly.

---

# UC10 – Prediction History Access

**Primary Actor:**  
Authenticated User

**Level:**  
User Goal

**Stakeholders and Interests:**

- Analysts: want to review previous predictions.
- Researchers: want to analyze historical model outputs.

**Preconditions:**

- The user is authenticated.
- Prediction records exist.

**Main Success Scenario:**

1. The user requests prediction history.
2. The system retrieves stored prediction records.
3. The system returns the historical predictions including:
   - Input data
   - Predicted demand
   - Timestamp
   - Model version used.

**Extensions / Alternative Paths:**

2a. No prediction records available  
- The system informs the user that no prediction history exists.

**Postconditions:**

- Historical predictions are displayed to the user.

---

# UC11 – Execute Full Data Pipeline

**Primary Actor:**  
Authenticated Admin  

**Level:**  
User Goal  

**Stakeholders and Interests:**

- Administrators: want a simple way to execute the full workflow  
- Data scientists: require consistent and reproducible data processing  
- System developers: want automated and maintainable pipeline execution  

**Preconditions:**

- The administrator is authenticated  
- The system is operational  
- Required datasets or ingestion configuration are available  

**Main Success Scenario:**

1. The administrator triggers full pipeline execution  
2. The system optionally performs data ingestion  
3. The system executes data cleaning for energy and weather datasets  
4. The system performs dataset integration  
5. The system generates features  
6. The system trains machine learning models  
7. The system evaluates the models  
8. The system stores trained models, datasets, and results  
9. The system logs execution details (timestamp, duration, status)  

**Extensions / Alternative Paths:**

2a. Data ingestion disabled  
- The system skips ingestion and uses existing datasets  

3a. Cleaning failure  
- The system logs the error and terminates execution  

6a. Training skipped (existing configuration)  
- The system detects an existing model with the same configuration  
- Training is skipped to avoid redundant computation

**Postconditions:**

- All pipeline outputs (processed data, models, results) are stored  
- Execution logs are recorded for traceability  
- The system state is updated consistently  

---

# UC12 – Execute System Testing

**Primary Actor:**  
System / Developer (via CI or local execution)  

**Level:**  
Subfunction / System Goal  

**Stakeholders and Interests:**

- Developers: want to ensure system correctness  
- Administrators: want a reliable system  
- CI/CD pipeline: requires automated validation before deployment  

**Preconditions:**

- The system codebase is available  
- Test environment is properly configured  
- Required dependencies are installed  

**Main Success Scenario:**

1. The testing process is triggered (locally or via CI pipeline)  
2. The system executes unit tests for individual components  
3. The system executes integration tests for pipeline workflows  
4. The system validates API endpoints and authentication behavior  
5. The system verifies expected outputs and error handling  
6. The system reports test results (pass/fail)  
7. The system logs test execution details  

**Extensions / Alternative Paths:**

2a. Unit test failure  
- The system reports the failure and marks the build as failed  

3a. Integration test failure  
- The system logs inconsistencies and aborts validation  

4a. API test failure  
- The system reports incorrect responses or status codes  

**Postconditions:**

- Test results are available  
- System correctness is validated or failures are identified  
- CI pipeline status reflects test outcomes  

---

# UC13 – Dashboard Visualization Access

**Primary Actor:**  
Authenticated User

**Level:**  
User Goal

**Stakeholders and Interests:**

- Analysts: want an overview of system behaviour.
- Researchers: want to interpret demand patterns.
- Administrators: want monitoring capabilities.

**Preconditions:**

- The user is authenticated.
- Processed datasets and model outputs exist.

**Main Success Scenario:**

1. The user accesses the dashboard page.
2. The system retrieves processed energy and climate data.
3. The system retrieves best prediction results.
4. The system generates dashboard visualizations including:
   - Demand by hour of day
   - Seasonal demand behaviour
   - Last 24-hour real vs predicted demand
   - Model performance summaries
5. The system displays charts and summaries.

**Extensions / Alternative Paths:**

3a. Prediction results unavailable  
- The system displays available historical data only.

2a. Processed datasets unavailable  
- The system informs the user that dashboard data is unavailable.

**Postconditions:**

- The user obtains a visual overview of system behaviour and model performance.

---

# UC14 – Climate and Energy Relationship Analysis

**Primary Actor:**  
Authenticated User

**Level:**  
User Goal

**Stakeholders and Interests:**

- Researchers: want to understand climate impact on energy demand.
- Analysts: want to identify seasonal and weather-driven behaviour.

**Preconditions:**

- Processed datasets are available.
- The user is authenticated.

**Main Success Scenario:**

1. The user accesses the data analysis section.
2. The system retrieves climate and electricity demand data.
3. The system generates comparative visualizations between:
   - Climate variables
   - Electricity demand
4. The system generates correlation and relationship visualizations.
5. The user analyzes seasonal and climate-driven demand patterns.

**Extensions / Alternative Paths:**

2a. Data unavailable  
- The system informs the user that analysis data is unavailable.

**Postconditions:**

- Climate-demand relationships are visualized and available for interpretation.

---

# UC15 – Extreme Climate Alert Analysis

**Primary Actor:**  
Authenticated User

**Level:**  
User Goal

**Stakeholders and Interests:**

- Analysts: want to identify extreme weather events.
- Researchers: want to study climate impact scenarios.

**Preconditions:**

- Processed climate data exists.
- The user is authenticated.

**Main Success Scenario:**

1. The user accesses the alert analysis section.
2. The user defines threshold values for climate variables.
3. The system analyzes historical climate records.
4. The system identifies periods exceeding the thresholds.
5. The system displays the number of affected hours and related statistics.

**Postconditions:**

- Extreme climate scenarios are identified and visualized.

---

# UC16 – Execution Log Visualization

**Primary Actor:**  
Authenticated Admin

**Level:**  
User Goal

**Stakeholders and Interests:**

- Administrators: want execution traceability.
- Developers: want debugging and monitoring capabilities.

**Preconditions:**

- The administrator is authenticated.
- System logs exist.

**Main Success Scenario:**

1. The administrator accesses the execution logs section.
2. The system retrieves stored execution logs.
3. The system displays:
   - Pipeline execution logs
   - Authentication logs
   - Training logs
   - Performance timing logs
4. The administrator reviews execution history and system behaviour.

**Postconditions:**

- System execution information is available for monitoring and debugging.

---

# UC17 – Real-Time Prediction Visualization

**Primary Actor:**  
Authenticated User

**Level:**  
User Goal

**Stakeholders and Interests:**

- Analysts: want visual interpretation of predictions.
- Researchers: want temporal forecast analysis.

**Preconditions:**

- The user is authenticated.
- A trained model exists.

**Main Success Scenario:**

1. The user requests a real-time prediction visualization using climate and temporal input features.
2. The system retrieves prediction results.
3. The system generates temporal demand forecast charts.
4. The system displays estimated load evolution throughout the day.
5. The user analyzes forecast behaviour visually.

**Postconditions:**

- Prediction results are visually displayed to the user.

---

# UC18 – Execute Partial Pipeline Components

**Primary Actor:**  
Authenticated Admin

**Level:**  
User Goal

**Stakeholders and Interests:**

- Administrators: want flexible execution of specific pipeline stages.
- Developers: want modular and maintainable pipeline execution.
- Data scientists: want to rerun specific processing stages without executing the full pipeline.

**Preconditions:**

- The administrator is authenticated.
- The system is operational.

**Main Success Scenario:**

1. The administrator accesses the pipeline management section.
2. The administrator selects a specific pipeline component to execute:
   - Data ingestion
   - Data cleaning
   - Feature engineering
   - Model training
   - Model evaluation
3. The system validates the execution dependencies.
4. The system verifies that all required previous stages were completed successfully.
5. The selected pipeline component is executed.
6. The system stores the generated outputs.
7. The system logs execution details including timestamp, duration, and status.
8. The system confirms successful execution.

**Extensions / Alternative Paths:**

3a. Required dependencies missing  
- The system prevents execution of the selected component.  
- The system informs the administrator which previous stages must be executed first.

5a. Component execution failure  
- The system logs the error and terminates execution safely.

2a. Invalid pipeline selection  
- The system rejects the request.

**Postconditions:**

- The selected pipeline stage is executed successfully.
- Outputs and execution logs are updated accordingly.