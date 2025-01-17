import pickle

import uvicorn
from fastapi import FastAPI
from sqlalchemy import create_engine

from features_collector.feature_collector_manager import FeatureCollectorManager
from features_collector.input.feature_collector_bank_input import FeatureCollectorBankInput
from features_collector.postgres.points_dao import PointsDao
from ml.predictor import Predictor
from utils.feature_transformer_for_ml import FeatureTransformerForMl

app = FastAPI()

DB_URL = "postgresql://postgres:abc@db:5432/points"
engine = create_engine(DB_URL)
points_dao = PointsDao(engine)

with open("ml/models/atm_best.pkl", "rb") as f:
    model = pickle.load(f)
feature_collector_manager = FeatureCollectorManager(points_dao)
predictor = Predictor(model)


@app.get("/predict-bank-quality")
def predict(lat: float, long: float):
    feature_collector_bank_input = FeatureCollectorBankInput(latitude=lat, longitude=long)
    feature_collector_bank_output = feature_collector_manager.collect_features(feature_collector_bank_input)

    bank_row_dataframe = FeatureTransformerForMl.transform(feature_collector_bank_output)
    quality = predictor.predict(bank_row_dataframe)

    return {"quality": quality[0]}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
