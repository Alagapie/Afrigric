# Weather Integration Setup Guide

## 🌤️ AfriGric Weather Integration

This guide will help you set up the weather integration feature for accurate yield predictions.

## Prerequisites

1. **OpenWeatherMap API Key**: Get a free API key from [OpenWeatherMap](https://openweathermap.org/api)
2. **Python Dependencies**: Install required packages

## Setup Instructions

### 1. Get OpenWeatherMap API Key

1. Visit [https://openweathermap.org/api](https://openweathermap.org/api)
2. Click "Sign Up" and create a free account
3. Verify your email address
4. Go to "API Keys" tab in your dashboard
5. Copy your API key (it looks like: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5`)

### 2. Configure API Key

1. Open the `.env` file in your project root
2. Replace the placeholder with your actual API key:

```env
OPENWEATHER_API_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5
```

**Example of what your .env file should look like:**
```env
OPENWEATHER_API_KEY=550e8400e29b0414e2c31d8d
```

### 3. Test Your API Key

1. Visit: `http://localhost:5000/weather_test` (after starting the app)
2. Click "Test Weather API with Lagos"
3. You should see weather data instead of an error

### 4. Use Weather Integration

1. Start the Flask application:
```bash
python app.py
```

2. Navigate to the Yield Prediction page (`/yield`)
3. Enable "Use Real Weather Data"
4. Select a city from the dropdown (e.g., "Kano")
5. Watch the weather data auto-fill the form fields!

## Troubleshooting

### If you get "401 Unauthorized" error:

1. **Check your .env file** - Make sure it contains your real API key
2. **API Key Format** - Should be 32 characters, letters and numbers only
3. **Test the key** - Use the debug page at `/weather_test`
4. **Wait for activation** - New API keys might take a few minutes to activate

### Example working .env file:
```env
OPENWEATHER_API_KEY=550e8400e29b0414e2c31d8d
```

### Free API Limits:
- 60 calls per minute
- 1,000,000 calls per month
- Perfect for development and small applications!

## Features

### ✅ Smart Weather Auto-Fill
- Automatically fills temperature and rainfall fields
- Visual indicators when data is loaded
- Real-time weather conditions display

### ✅ Professional Form Design
- Clean, organized layout
- Dropdown for crop selection
- Improved field labels and placeholders

### ✅ Multilingual Support
- Weather terms translated in all 4 languages
- Location input supports local languages
- Error messages in user's preferred language

### ✅ Error Handling
- Graceful fallback if API is unavailable
- User-friendly error messages
- Loading states and progress indicators

## API Limits (Free Tier)

- **60 calls per minute**
- **1,000,000 calls per month**
- **Current weather and 5-day forecast**

This is more than enough for most applications!

## Troubleshooting

### Common Issues:

1. **API Key Error**: Make sure your API key is correctly added to `.env`
2. **Location Not Found**: Try different city names or add country codes
3. **Network Issues**: Check your internet connection
4. **Rate Limits**: Wait a minute if you hit the API limit

### Test Commands:

```bash
# Test weather API directly
curl "https://api.openweathermap.org/data/2.5/weather?q=Lagos&appid=YOUR_API_KEY&units=metric"
```

## Usage Examples

### For Lagos, Nigeria:
- Location input: "Lagos, Nigeria"
- Auto-fills: Current temperature and rainfall data

### For Kano, Nigeria:
- Location input: "Kano"
- Auto-fills: Local weather conditions

### For Abuja, Nigeria:
- Location input: "Abuja"
- Auto-fills: Capital city weather data

## Benefits

1. **Accurate Predictions**: Real weather data improves yield accuracy
2. **User-Friendly**: No need for farmers to guess weather conditions
3. **Real-Time**: Always up-to-date weather information
4. **Local**: Weather data specific to farming location
5. **Professional**: Clean, modern interface with great UX

## Support

If you encounter any issues:

1. Check the Flask application logs
2. Verify your API key is working
3. Test with different locations
4. Ensure all dependencies are installed

The weather integration will significantly improve the accuracy of your yield predictions! 🌦️