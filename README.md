# RealEstateProject

Real Estate Price Prediction Project is a MLOps project which is used to predict the price of the house or the flat based on the features like area, number of bedrooms, number of bathrooms, etc. 

The dataset of more than 400,000 properties was collected from a real estate website in Vietnam. After cleaning the data, the dataset was reduced to 200,000 properties which are used to experiment with different machine learning models. After experimenting with different models and hyperparameters tuning, the XGBoost Regressor model was found to be the best model with the mean absolute error on the validation set of 2.83. The model was then deployed using BentoML and Docker. The users can use the model serving and get predictions through HTTP or gRPC requests.

## Architecture

1. Data collection:
- Data is collected from a real estate website in Vietnam.

2. Data pipeline:
- The data went through the data pipeline to be ingested, cleaned, and explored. 
- The data is then stored in the offline feature store.

3. Training pipeline:
- The data is retrieved from the offline feature store and then went through the pipeline to be transformed, validated, and split into training and validation sets. 
- The training set is then used to experiment with different machine learning models and hyperparameters tuning.
- The trained models are then got evaluated on the validation set and validated to be selected as the best model. The best model then got logged to the model registry.
- All the metadata of the training pipeline such as the metrics, hyperparameters, and artifacts are logged to the ML metadata store.

4. Model serving:
- The best model is then retrieved from the model registry and deployed through batch inference and online inference.
- The users can use the online inference to get predictions through HTTP or gRPC requests.
- The users can also use the batch inference to get predictions on a large number of data.

5. Monitoring:
- The logs from the data pipeline, training pipeline, and model serving are collected, stored, and visualized.
- The system metrics are also collected, stored, and visualized.
- The data drift is also monitored.

## Authors

- [@Thangphan0102](https://github.com/Thangphan0102)

## Tech Stack

**Source control management:** Git and GitHub

**Programming language:** Python

**Machine Learning libraries:** Pandas, Numpy, Scikit-learn, XGBoost

**Feature store:** Feast

**Experiment tracking, Model registry, ML metadata store:** MLflow

**Workflow orchestration:** Apache Airflow

**Monitoring:** Prometheus and Grafana

**Logging:** ELK stack

**CI/CD:** GitHub Actions

**Model serving:** BentoML and Docker

**Scrawling:** Scrapy and Redis
