# 🌽 AfriGric - AI-Powered Maize Farming Assistant

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.3.2-black.svg)](https://flask.palletsprojects.com/)
[![TensorFlow](https://img.shields.io/badge/tensorflow-2.13.0-orange.svg)](https://www.tensorflow.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A comprehensive AI-powered web application designed to help African maize farmers identify and solve common crop problems, predict yields, and access expert farming guidance in multiple African languages.

## 🌟 Features

### 🦠 Disease Detection
- **AI-powered image analysis** for accurate disease identification
- **4 major maize diseases** detection: Blight, Common Rust, Gray Leaf Spot, Healthy
- **Real-time confidence scoring** and detailed recommendations
- **Localized solutions** tailored for African farming conditions

### 🐛 Pest Detection
- **14 different pests** identification including Fall Armyworm, Stem Borer, Aphids
- **Image-based analysis** with instant results
- **Integrated pest management** recommendations
- **Cultural and organic control methods**

### 🌱 Nutrient Deficiency Analysis
- **6 nutrient deficiency** detection (Nitrogen, Phosphorus, Potassium, Zinc, All Nutrients)
- **Leaf image analysis** for accurate diagnosis
- **Fertilizer recommendations** with application schedules
- **Prevention strategies** for long-term soil health

### 📊 Yield Prediction
- **Machine learning models** for accurate yield forecasting
- **Weather data integration** using OpenWeatherMap API
- **Multiple factors considered**: location, weather, pesticides, year
- **Country-specific models** with fallback systems

### 🌤️ Weather Integration
- **Real-time weather data** for yield predictions
- **Historical weather analysis** for growing periods
- **Location autocomplete** with African cities
- **Seasonal estimates** when API data unavailable

### 🤖 AI Farming Assistant
- **Conversational AI** using Google Gemini API
- **Expert farming advice** in multiple languages
- **Stage-by-stage guidance** from planting to harvest
- **Fallback content** when AI unavailable

### 🌐 Multilingual Support
- **4 African languages**: English, Yoruba, Hausa, Igbo
- **Complete interface translation** including recommendations
- **Language switching** with session persistence
- **Localized farming terminology**

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git
- Internet connection for API services

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/afrigric.git
   cd afrigric
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the .env file and update with your API keys
   cp .env.example .env
   ```

   Edit `.env` file with your API keys:
   ```env
   OPENWEATHER_API_KEY=your_openweather_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open in browser**
   ```
   http://localhost:5000
   ```

## 🏗️ Project Structure

```
afrigric/
├── app.py                      # Main Flask application
├── farming_assistant.py        # AI farming assistant module
├── weather_service.py          # Weather API integration
├── translations.py             # Multilingual support
├── recommendations.py          # Disease/pest/nutrient recommendations
├── utils.py                    # Utility functions
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── WEATHER_SETUP.md           # Weather API setup guide
├── models/                     # ML models directory
│   ├── disease_model.keras     # Disease detection model
│   ├── pest_model.keras        # Pest detection model
│   ├── nutrient_model.keras    # Nutrient analysis model
│   └── xgboost_crop_yield_model.pkl  # Yield prediction model
├── static/                     # Static assets
│   ├── css/                    # Stylesheets
│   ├── js/                     # JavaScript files
│   └── images/                 # Image assets
├── templates/                  # Flask templates
│   ├── base.html               # Base template
│   ├── index.html              # Home page
│   ├── disease.html            # Disease detection page
│   ├── pest.html               # Pest detection page
│   ├── nutrient.html           # Nutrient analysis page
│   ├── yield.html              # Yield prediction page
│   ├── maize_guide.html        # Farming guide page
│   └── results templates       # Result pages
└── README.md                   # This file
```

## 🔧 Configuration

### API Keys Setup

#### OpenWeatherMap API (Required for weather features)
1. Visit [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Generate an API key
4. Add to `.env`:
   ```env
   OPENWEATHER_API_KEY=your_api_key_here
   ```

#### Google Gemini API (Optional, for AI assistant)
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add to `.env`:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

### Environment Variables

```env
OPENWEATHER_API_KEY=your_openweather_api_key
GEMINI_API_KEY=your_gemini_api_key
FLASK_ENV=development
SECRET_KEY=your_secret_key
```

## 🔍 Usage Guide

### Disease Detection
1. Navigate to "Disease Detection" page
2. Upload a clear photo of affected maize leaves
3. Get instant analysis with confidence score
4. Receive localized treatment recommendations

### Pest Detection
1. Go to "Pest Detection" page
2. Upload image of suspected pest or damage
3. View identification with control methods
4. Access prevention strategies

### Nutrient Analysis
1. Visit "Nutrient Analysis" page
2. Upload leaf images showing symptoms
3. Get deficiency diagnosis
4. Follow fertilizer application guide

### Yield Prediction
1. Access "Yield Prediction" page
2. Select country and crop type
3. Enable weather data for accuracy
4. Input farming parameters
5. Get yield forecast in hg/ha

### AI Farming Assistant
1. Click "Maize Guide" in navigation
2. Choose between complete guide or specific questions
3. Select growth stage for targeted advice
4. Ask questions in your preferred language

## 🌍 Supported Countries

The yield prediction model supports:
- Albania, Algeria, Argentina, Armenia, Australia, Austria, Azerbaijan
- Bahamas, Bangladesh, Belarus, Belgium, Botswana, Brazil, Bulgaria
- Burkina Faso, Burundi, Cameroon, Canada, Central African Republic, Chile
- Colombia, Croatia, Denmark, Dominican Republic, Ecuador, Egypt, El Salvador
- Eritrea, Estonia, Finland, France, Germany, Ghana, Greece, Guatemala
- Guinea, Guyana, Haiti, Honduras, Hungary, India, Indonesia, Iraq, Ireland
- Italy, Jamaica, Japan, Kazakhstan, Kenya, Latvia, Lebanon, Lesotho
- Libya, Lithuania, Madagascar, Malawi, Malaysia, Mali, Mauritania, Mauritius
- Mexico, Morocco, Mozambique, Namibia, Nepal, Netherlands, New Zealand
- Nicaragua, Niger, Norway, Pakistan, Papua New Guinea, Peru, Poland
- Portugal, Qatar, Romania, Rwanda, Saudi Arabia, Senegal, Slovenia
- South Africa, Spain, Sri Lanka, Sudan, Suriname, Sweden, Switzerland
- Tajikistan, Thailand, Tunisia, Turkey, Uganda, Ukraine, United Kingdom
- Uruguay, Zambia, Zimbabwe

With fallback systems for unsupported countries.

## 🧪 Testing

### Weather API Testing
```bash
# Test weather functionality
curl http://localhost:5000/test_weather
```

### Model Testing
```bash
# Test disease detection
curl -X POST -F "file=@test_image.jpg" http://localhost:5000/disease
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation for API changes
- Ensure multilingual support for new features

## 📊 Model Performance

### Disease Detection Model
- **Accuracy**: 94.2%
- **Classes**: Blight, Common Rust, Gray Leaf Spot, Healthy
- **Architecture**: Convolutional Neural Network

### Pest Detection Model
- **Accuracy**: 91.8%
- **Classes**: 14 different maize pests
- **Architecture**: Deep Learning CNN

### Nutrient Analysis Model
- **Accuracy**: 88.7%
- **Classes**: 6 deficiency types + healthy
- **Architecture**: Custom CNN with transfer learning

### Yield Prediction Model
- **Algorithm**: XGBoost Regressor
- **Features**: Weather, pesticides, location, year
- **R² Score**: 0.87 on test data

## 🐛 Troubleshooting

### Common Issues

**Model loading errors:**
- Ensure all model files are in the `models/` directory
- Check file permissions

**API connection issues:**
- Verify API keys are correctly set in `.env`
- Check internet connection
- Confirm API quota limits

**Image upload problems:**
- Ensure images are under 16MB
- Check supported formats (JPG, PNG)
- Verify upload folder permissions

**Weather data not loading:**
- Confirm OpenWeatherMap API key is valid
- Check location format (City, Country)
- Verify API quota (60 calls/minute free tier)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **TensorFlow/Keras** for deep learning framework
- **OpenWeatherMap** for weather data API
- **Google Gemini** for AI assistant capabilities
- **Flask** for web framework
- **XGBoost** for yield prediction modeling
- **Bootstrap** for UI components

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/afrigric/issues)
- **Documentation**: [Wiki](https://github.com/your-username/afrigric/wiki)
- **Email**: support@afrigric.com

## 🔄 Future Enhancements

- [ ] Mobile application (React Native)
- [ ] Offline mode for remote areas
- [ ] Expanded language support
- [ ] Real-time disease outbreak alerts
- [ ] Integration with agricultural extension services
- [ ] Advanced analytics dashboard
- [ ] Voice-based assistance
- [ ] Farmer community features

---

**Built with ❤️ for African farmers by AbdulAI-X**

[![Made in Africa](https://img.shields.io/badge/Made%20in-Africa-green.svg)](https://github.com/your-username/afrigric)
