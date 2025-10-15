import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Load ML model and feature columns
try:
    clf = joblib.load('calibrated_clf.joblib')
    feat_cols = joblib.load('feat_cols.joblib')
    print("✅ ML Model loaded successfully")
    print(f"📊 Features expected: {len(feat_cols)}")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    clf = None
    feat_cols = None

# City coordinates for reference
CITIES = {
    "Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946},
    "Bangalore": {"lat": 12.9716, "lon": 77.5946},
    "Chandigarh": {"lat": 30.7333, "lon": 76.7794}
}

def create_features(df):
    """Create time-based and lag features for the model"""
    df['DATE'] = pd.to_datetime(df['DATE'])
    
    # Time-based features
    df['Month'] = df['DATE'].dt.month
    df['Day'] = df['DATE'].dt.day
    df['DayOfYear'] = df['DATE'].dt.dayofyear
    df['Year'] = df['DATE'].dt.year
    
    # Seasonal features (cyclical encoding)
    df['sin_day'] = np.sin(2 * np.pi * df['DayOfYear'] / 365.25)
    df['cos_day'] = np.cos(2 * np.pi * df['DayOfYear'] / 365.25)
    
    # Add lag features (using mean historical values for prediction)
    # In production, you'd want historical data from a database
    df['TMAX_lag1'] = 35.0  # Default summer temperature
    df['TMAX_lag7'] = 34.5
    df['TMAX_lag14'] = 34.0
    
    return df

def predict_heatwave(city, start_date, days):
    """Make heatwave predictions for given city and date range"""
    if clf is None or feat_cols is None:
        return {"error": "Model not loaded. Check if calibrated_clf.joblib and feat_cols.joblib exist."}
    
    # Validate city
    if city not in CITIES:
        return {"error": f"City '{city}' not found. Available cities: {', '.join(CITIES.keys())}"}
    
    # Parse start date or use today
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            start = datetime.now()
    else:
        start = datetime.now()
    
    # Generate date range
    try:
        days = int(days)
        if days < 1 or days > 15:
            days = 7
    except:
        days = 7
    
    dates = [start + timedelta(days=i) for i in range(days)]
    
    # Create DataFrame with dates
    df = pd.DataFrame({'DATE': dates})
    
    # Add city info
    df['CITY'] = city
    
    # Create features
    df = create_features(df)
    
    # Add base temperature estimate (seasonal)
    # This is a simple model - in production you'd query actual weather data
    month_temps = {
        1: 20, 2: 23, 3: 28, 4: 35, 5: 40, 6: 38,
        7: 35, 8: 33, 9: 33, 10: 30, 11: 25, 12: 21
    }
    df['TMAX'] = df['Month'].map(month_temps)
    
    # Adjust for city (some cities are hotter)
    city_adjustments = {
        "Delhi": 2, "Mumbai": -1, "Kolkata": 1,
        "Chennai": 0, "Bengaluru": -3, "Bangalore": -3, "Chandigarh": 1
    }
    df['TMAX'] += city_adjustments.get(city, 0)
    
    # Ensure all required features are present
    for col in feat_cols:
        if col not in df.columns:
            df[col] = 0
    
    # Select features in correct order
    try:
        X = df[feat_cols]
    except KeyError as e:
        return {"error": f"Missing feature: {str(e)}. Check your model's feature requirements."}
    
    # Make predictions
    try:
        probs = clf.predict_proba(X)[:, 1]
        preds = clf.predict(X)
    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}
    
    # Create results
    results = []
    for i, date in enumerate(dates):
        prob = float(probs[i])
        pred = int(preds[i])
        
        # Determine risk level
        if prob >= 0.8:
            risk = "🔴 Extreme"
        elif prob >= 0.6:
            risk = "🟠 High"
        elif prob >= 0.4:
            risk = "🟡 Moderate"
        elif prob >= 0.2:
            risk = "🟢 Low"
        else:
            risk = "⚪ Very Low"
        
        results.append({
            "DATE": date.strftime("%Y-%m-%d"),
            "Heatwave_Prob": round(prob, 3),
            "Heatwave_Pred": pred,
            "Risk_Level": risk
        })
    
    return {
        "city": city,
        "start_date": start.strftime("%Y-%m-%d"),
        "days": days,
        "results": results
    }

@app.route("/")
def index():
    """Serve the main page"""
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    """Handle prediction requests"""
    try:
        data = request.get_json()
        city = data.get("city", "Delhi")
        start_date = data.get("start_date", "")
        days = data.get("days", 7)
        
        result = predict_heatwave(city, start_date, days)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model_loaded": clf is not None,
        "features_count": len(feat_cols) if feat_cols else 0
    })

@app.route("/cities")
def get_cities():
    """Get available cities"""
    return jsonify(list(CITIES.keys()))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Flask server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
