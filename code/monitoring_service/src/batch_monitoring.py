from evidently.pipeline.column_mapping import ColumnMapping
from evidently.metric_preset import DataDriftPreset, RegressionPreset
from evidently.report import Report
import requests

from utils import *

logger = Log(AppConst.BATCH_MONITORING).log
AppPath()


def make_prediction(df: pd.DataFrame) -> pd.DataFrame:
    # Start
    logger.info("Started: Making prediction...")
    
    # Create request
    features = df.drop(columns=["price"]).to_dict(orient="records")
    request = {
        "request_id": "uuid-1",
        "properties": features
    }
    
    # Make request
    response = requests.post(url=Config.INFERENCE_SERVICE_URL, json=request)
    
    # Assign prediction
    prediction = response.json()["prediction"]
    
    # End
    logger.info("Finished: Making prediction...")
    
    return prediction


class BatchReports:
    DATASET_NAME = "properties"
    DATETIME_COL = ""
    NUMERICAL_COLS = ["area", "length", "width", "num_bedrooms", "num_bathrooms"]
    CATEGORICAL_COLS = []
    TARGET_COL = "price"
    PREDICTION_COL = "prediction"
    
    def __init__(self) -> None:
        # Data
        self.reference_data = read_parquet(AppPath.REFERENCE_PQ)
        self.production_data = read_parquet(AppPath.PRODUCTION_PQ)
        
        # Column mapping
        self.column_mapping = ColumnMapping(
            target=self.TARGET_COL,
            prediction=self.PREDICTION_COL,
            numerical_features=self.NUMERICAL_COLS,
            categorical_features=self.CATEGORICAL_COLS,
            datetime=self.DATETIME_COL,
        )
        
        # Reports
        self.data_report = Report(
            metrics=[
                DataDriftPreset(),
            ]
        )
        self.model_report = Report(
            metrics=[
                RegressionPreset(),
            ]
        )
        
    def run_prediction(self):
        self.production_data["prediction"] = make_prediction(self.production_data)
        self.reference_data["prediction"] = make_prediction(self.reference_data)
        
    def run_report(self):
        logger.info("Started: Running reports...")
        self.data_report.run(
            reference_data=self.reference_data,
            current_data=self.production_data,
            column_mapping=self.column_mapping,
        )
        self.model_report.run(
            reference_data=self.reference_data,
            current_data=self.production_data,
            column_mapping=self.column_mapping,
        )
        logger.info("Finished: Running reports...")
        
    def save_report(self):
        logger.info("Started: Saving reports...")
        self.data_report.save_html(AppPath.DATA_REPORT_HTML)
        self.model_report.save_html(AppPath.MODEL_REPORT_HTML)
        inspect_dir(AppPath.ARTIFACTS_DIR)
        logger.info("Finished: Saving reports...")
        

def main():
    # Start
    logger.info("Started: Batch monitoring...")
    
    # Init
    batch_report = BatchReports()
    
    # Run prediction
    batch_report.run_prediction()
    
    # Run reports
    batch_report.run_report()
    
    # Save reports
    batch_report.save_report()
    
    # End
    logger.info("Finished: Batch monitoring...")
    
    
if __name__ == "__main__":
    main()