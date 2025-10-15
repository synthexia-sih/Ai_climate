# ☀️ AI Heatwave Forecast Dashboard

A Flask-based web application that predicts heatwave occurrences in Indian cities using machine learning models trained on 15 years of NASA weather data.

## 🌟 Features

- **Interactive Map**: Visual representation of Indian cities with Leaflet.js
- **ML Predictions**: Heatwave probability predictions using LightGBM model
- **Risk Assessment**: Color-coded risk levels (Extreme, High, Moderate, Low, Very Low)
- **Date Range Selection**: Predict up to 15 days in advance
- **Responsive Design**: Modern UI with Tailwind CSS and glassmorphism effects
- **Real-time Updates**: Dynamic predictions based on selected parameters

## 🏗️ Project Structure

```
heatwave-dashboard/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment configuration
├── calibrated_clf.joblib # ML model file (you need to add this)
├── feat_cols.joblib      # Feature columns file (you need to add this)
├── templates/
│   └── index.html        # Main dashboard template
├── static/
│   ├── style.css         # Custom CSS styles
│   └── main.js           # Frontend JavaScript
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Your ML model files: `calibrated_clf.joblib` and `feat_cols.joblib`

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd heatwave-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your ML model files**
   - Place `calibrated_clf.joblib` in the root directory
   - Place `feat_cols.joblib` in the root directory

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   - Navigate to `http://localhost:5000`

## 🌐 Deployment

### Render.com Deployment

1. **Connect your GitHub repository to Render**
2. **The `render.yaml` file will automatically configure:**
   - Python 3.9.16 environment
   - Automatic dependency installation
   - Gunicorn WSGI server
   - Environment variables

3. **Add your model files to the repository:**
   ```bash
   git add calibrated_clf.joblib feat_cols.joblib
   git commit -m "Add ML model files"
   git push
   ```

### Other Platforms

For other platforms (Heroku, Railway, etc.), ensure:
- Set `PORT` environment variable
- Use `gunicorn --bind 0.0.0.0:$PORT app:app` as start command
- Include all dependencies in `requirements.txt`

## 🔧 API Endpoints

### GET `/`
- Serves the main dashboard page

### POST `/predict`
- **Request Body:**
  ```json
  {
    "city": "Delhi",
    "start_date": "2024-01-15",
    "days": 7
  }
  ```
- **Response:**
  ```json
  {
    "city": "Delhi",
    "start_date": "2024-01-15",
    "days": 7,
    "results": [
      {
        "DATE": "2024-01-16",
        "Heatwave_Prob": 0.75,
        "Heatwave_Pred": 1,
        "Risk_Level": "🟠 High"
      }
    ]
  }
  ```

### GET `/health`
- Health check endpoint
- Returns model status and feature count

### GET `/cities`
- Returns list of available cities

## 🎯 Supported Cities

- Delhi
- Mumbai
- Kolkata
- Chennai
- Bengaluru
- Chandigarh

## 🧠 Machine Learning Model

The application uses a LightGBM classifier trained on:
- 15 years of NASA weather data
- Seasonal features and lag variables
- Temperature threshold: 40°C for heatwave definition

### Risk Levels
- 🔴 **Extreme Risk**: Probability ≥ 80%
- 🟠 **High Risk**: Probability 60-79%
- 🟡 **Moderate Risk**: Probability 40-59%
- 🟢 **Low Risk**: Probability 20-39%
- ⚪ **Very Low Risk**: Probability < 20%

## 🛠️ Customization

### Adding New Cities

1. **Update `CITIES` dictionary in `app.py`:**
   ```python
   CITIES = {
       "NewCity": {"lat": 12.3456, "lon": 78.9012},
       # ... existing cities
   }
   ```

2. **Add city option in `templates/index.html`:**
   ```html
   <option>NewCity</option>
   ```

3. **Update city coordinates in `static/main.js`:**
   ```javascript
   const cities = {
       "NewCity": [12.3456, 78.9012],
       // ... existing cities
   };
   ```

### Modifying Risk Thresholds

Edit the risk level logic in `app.py`:
```python
if prob >= 0.8:
    risk = "🔴 Extreme"
elif prob >= 0.6:
    risk = "🟠 High"
# ... modify as needed
```

## 🐛 Troubleshooting

### Common Issues

1. **Model files not found**
   - Ensure `calibrated_clf.joblib` and `feat_cols.joblib` are in the root directory
   - Check file permissions

2. **CORS errors**
   - Flask-CORS is configured to allow all origins
   - For production, restrict to your domain

3. **Prediction errors**
   - Check that all required features are present in the model
   - Verify feature column names match exactly

4. **Map not loading**
   - Check internet connection for Leaflet.js CDN
   - Verify browser console for JavaScript errors

## 📝 License

This project is open source. Feel free to modify and distribute.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review the API documentation
- Open an issue on GitHub
