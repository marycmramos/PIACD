# Climate-Driven Energy Demand Analytics System

An AI-driven analytics platform for electricity demand forecasting using climate and energy consumption data. The system integrates automated data ingestion, preprocessing pipelines, machine learning forecasting models and interactive visualizations to support energy demand analysis and decision-making.

## Overview

The project combines climate and electricity consumption data from public European sources to predict future energy demand. It provides tools for data ingestion, preprocessing, model training, prediction generation, model evaluation and visualization through a user-friendly web interface.

## Features

- User authentication and role-based access control
- Automated data ingestion from:
  - ENTSO-E Transparency Platform
  - Copernicus ERA5 Climate Data Store
- Data cleaning and alignment pipelines
- Feature engineering and preprocessing
- Machine Learning forecasting models:
  - Linear Regression
  - Random Forest
- Hyperparameter optimization with Grid Search
- Model evaluation using:
  - MAE
  - RMSE
  - R² Score
- Residual and overfitting analysis
- Interactive dashboards and visualizations
- Prediction history management
- Execution logs and monitoring
- CI/CD and automated testing

## System Architecture

The system follows a layered architecture composed of:

- Presentation Layer (Streamlit)
- Authentication & Authorization Layer
- Data Ingestion Layer
- Data Processing Layer
- Feature Engineering Layer
- Machine Learning Layer
- Prediction Services
- Visualization Layer
- Monitoring & Logging Layer

## Machine Learning Pipeline

1. Data Ingestion
2. Data Cleaning
3. Dataset Integration
4. Feature Engineering
5. Model Training
6. Hyperparameter Optimization
7. Model Evaluation
8. Prediction Generation
9. Visualization and Monitoring

## Technologies

### Machine Learning & Data Science
- Python
- Scikit-learn
- Pandas
- NumPy
- Joblib

### Climate & Energy Data
- ENTSO-E API
- ERA5 Climate Data
- Xarray
- NetCDF

### Web Application
- Streamlit

### DevOps & Quality Assurance
- Git
- GitLab CI/CD
- Unit Testing
- Integration Testing

### Security
- Bcrypt Password Hashing
- Role-Based Access Control (RBAC)

## Main Use Cases

### User Management
- User Registration
- User Authentication
- Role Management

### Data Operations
- Data Ingestion
- Data Cleaning and Alignment
- Feature Engineering

### Machine Learning
- Model Training
- Model Evaluation
- Hyperparameter Optimization
- Prediction Generation

### Analytics & Visualization
- Dashboard Visualization
- Climate-Energy Relationship Analysis
- Real-Time Prediction Visualization
- Extreme Climate Alert Analysis

### Administration
- Pipeline Execution
- Execution Logs
- System Testing

## Results

The platform enables:

- Climate-aware electricity demand forecasting
- Comparative evaluation of forecasting models
- Analysis of climate impacts on energy consumption
- Interactive visualization of predictions and model performance
- Reproducible end-to-end machine learning workflows

## Authors

Developed as part of the BSc in Artificial Intelligence and Data Science at the University of Coimbra.

## License

This project was developed for academic purposes.
