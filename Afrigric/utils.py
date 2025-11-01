from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib
import os

app = Flask(__name__)

# Load the trained pipeline
model_path = 'xgboost_crop_yield_model.pkl'
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found at {model_path}")
pipeline = joblib.load(model_path)

@app.route('/')
def home():
    return render_template('inde.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get form data
        data = {
            'Area': request.form['Area'],
            'Item': request.form['Item'],
            'Year': int(request.form['Year']),
            'average_rain_fall_mm_per_year': float(request.form['rainfall']),
            'pesticides_tonnes': float(request.form['pesticides']),
            'avg_temp': float(request.form['temperature'])
        }
        
        # Convert to DataFrame for prediction
        input_df = pd.DataFrame([data])
        
        # Make prediction
        prediction = pipeline.predict(input_df)[0]
        
        return render_template('inde.html', 
                             prediction_text=f'Predicted Yield: {prediction:,.2f} hg/ha',
                             show_result=True)
    
    except Exception as e:
        return render_template('inde.html', 
                             prediction_text=f'Error: {str(e)}',
                             show_result=True)

@app.route('/predict_api', methods=['POST'])
def predict_api():
    try:
        data = request.get_json(force=True)
        input_df = pd.DataFrame([data])
        prediction = pipeline.predict(input_df)[0]
        return jsonify({'prediction': prediction})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)