from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# -------------------------------
# Flask + CORS Setup
# -------------------------------
app = Flask(__name__)
CORS(app)

# -------------------------------
# Load model and feature list
# -------------------------------
calibrated_clf = joblib.load("calibrated_clf.joblib")
feat_cols = joblib.load("feat_cols.joblib")

# -------------------------------
# Routes
# -------------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        city = data.get("city", "Delhi")
        start_date = data.get("start_date", None)
        days = int(data.get("days", 7))

        today = datetime.today() if not start_date else datetime.strptime(start_date, "%Y-%m-%d")
        future_dates = pd.date_range(start=today + timedelta(days=1), periods=days)

        # Generate simple synthetic input (normally from NASA data)
        np.random.seed(42)
        X_future = pd.DataFrame({'DATE': future_dates})
        for col in feat_cols:
            if "T2M_MAX" in col:
                X_future[col] = np.random.normal(38, 3, size=days)
            elif "T2M_MIN" in col:
                X_future[col] = np.random.normal(26, 2, size=days)
            elif "RH2M" in col:
                X_future[col] = np.random.normal(45, 10, size=days)
            elif "WS10M" in col:
                X_future[col] = np.random.normal(2, 0.5, size=days)
            elif "ALLSKY_SFC_SW_DWN" in col:
                X_future[col] = np.random.normal(20, 5, size=days)
            elif "PRECTOTCORR" in col:
                X_future[col] = np.random.normal(0.1, 0.05, size=days)
            elif "Heat_Index" in col:
                X_future[col] = np.random.normal(40, 2, size=days)
            else:
                X_future[col] = np.random.normal(0, 1, size=days)

        # Reorder
        for col in feat_cols:
            if col not in X_future.columns:
                X_future[col] = 0
        X_future = X_future[feat_cols]

        # Predict
        y_future_prob = calibrated_clf.predict_proba(X_future)[:, 1]
        y_future_prob = pd.Series(y_future_prob).rolling(window=3, center=True, min_periods=1).mean().values
        y_future_prob = 0.05 + 0.9 * y_future_prob
        y_future_pred = (y_future_prob > 0.5).astype(int)

        # Risk category
        risk_levels = []
        for prob in y_future_prob:
            if prob > 0.8:
                risk_levels.append("Extreme Risk")
            elif 0.6 < prob <= 0.8:
                risk_levels.append("High Risk")
            elif 0.4 < prob <= 0.6:
                risk_levels.append("Moderate Risk")
            else:
                risk_levels.append("Low Risk")

        # Prepare results
        result_df = pd.DataFrame({
            "DATE": future_dates.strftime("%Y-%m-%d"),
            "Heatwave_Prob": y_future_prob,
            "Heatwave_Pred": y_future_pred,
            "Risk_Level": risk_levels
        })

        return jsonify({
            "city": city,
            "results": result_df.to_dict(orient="records")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
 from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
from fastapi.middleware.cors import CORSMiddleware

# Load saved model and features
model = joblib.load("models/calibrated_clf.joblib")
feat_cols = joblib.load("models/feat_cols.joblib")

app = FastAPI(title="Heatwave Predictor API")

# Allow frontend origin for CORS
origins = ["*"]  # For production, replace "*" with your frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Input schema
class PredictRequest(BaseModel):
    features: dict  # e.g., {"T2M_MAX":36.5, "RH2M":55.2, ...}

@app.post("/predict")
def predict(req: PredictRequest):
    # Validate keys
    missing = [col for col in feat_cols if col not in req.features]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing features: {missing}")

    # Create feature vector
    x = np.array([req.features[col] for col in feat_cols]).reshape(1, -1)
    prob = float(model.predict_proba(x)[:,1][0])
    pred = int(prob > 0.5)

    # Risk categorization
    if prob > 0.8:
        risk = "Extreme Risk"
    elif prob > 0.6:
        risk = "High Risk"
    elif prob > 0.4:
        risk = "Moderate Risk"
    else:
        risk = "Low Risk"

    return {"probability": prob, "prediction": pred, "risk_level": risk}
