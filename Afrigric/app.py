import os
import shutil
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session, jsonify
from werkzeug.utils import secure_filename
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from PIL import Image
import joblib
import pandas as pd
from datetime import datetime
from translations import get_text, get_recommendations, TRANSLATIONS, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE
from weather_service import weather_service
from farming_assistant import farming_assistant
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


app = Flask(__name__)
app.secret_key = 'your_very_secure_secret_key_here'
app.config['SESSION_TYPE'] = 'filesystem'

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load models with error handling
try:
    disease_model = tf.keras.models.load_model('models/disease_model.keras')
    pest_model = tf.keras.models.load_model('models/pest_model.keras')
    nutrient_model = tf.keras.models.load_model('models/nutrient_model.keras')
    yield_model = joblib.load('models/xgboost_crop_yield_model.pkl')
    print("✅ All models loaded successfully!")
except Exception as e:
    print(f"❌ Error loading models: {str(e)}")
    # Handle model loading failure appropriately
    raise e

def get_current_language():
    """Get the current language from session or default"""
    return session.get('language', DEFAULT_LANGUAGE)

# Language switching route
@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in SUPPORTED_LANGUAGES:
        session['language'] = lang
    return redirect(request.referrer or url_for('home'))

# Weather API routes
@app.route('/api/weather/<location>')
def get_weather(location):
    """Get weather data for a location"""
    planting_date = request.args.get('planting_date')
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))

    print(f"Fetching weather data for: {location}")  # Debug log

    if planting_date:
        # Fetch historical weather data for growing period
        weather_data = weather_service.get_historical_weather_data(location, planting_date, end_date)
        print(f"Historical weather API response: {weather_data}")  # Debug log
    else:
        # Fetch current weather data
        weather_data = weather_service.get_weather_data(location)
        print(f"Current weather API response: {weather_data}")  # Debug log

    if weather_data['success']:
        return jsonify({
            'success': True,
            'data': weather_data
        })
    else:
        print(f"Weather API error: {weather_data['error']}")  # Debug log
        return jsonify({
            'success': False,
            'error': weather_data['error']
        }), 400

@app.route('/api/location_suggestions')
def location_suggestions():
    """Get location suggestions for autocomplete"""
    query = request.args.get('q', '')
    if not query or len(query) < 2:
        return jsonify([])

    suggestions = weather_service.get_location_suggestions(query)
    return jsonify(suggestions)

@app.route('/test_weather')
def test_weather():
    """Test weather functionality"""
    test_result = weather_service.get_weather_data('Lagos,Nigeria')
    return jsonify(test_result)

@app.route('/weather_test')
def weather_test_page():
    """Simple page to test weather functionality"""
    api_key = os.getenv('OPENWEATHER_API_KEY', '')
    api_key_status = len(api_key) > 0

    return render_template('debug_weather.html', api_key=api_key if api_key_status else None)

@app.route('/weather_debug')
def weather_debug():
    """Simple page to test weather functionality"""
    return f"""
    <h1>Weather Test Page</h1>
    <p>Testing weather API with Lagos, Nigeria:</p>
    <a href="/test_weather" target="_blank">Click here to test weather API</a>
    <br><br>
    <a href="/yield">Go to Yield Prediction</a>
    <br>
    <a href="/weather_test">Go to Debug Page</a>
    """


# Class mappings
DISEASE_MAPPING = {
    0: 'Blight', 
    1: 'Common_Rust', 
    2: 'Gray_Leaf_Spot', 
    3: 'Healthy'
}

PEST_MAPPING = {
    0: 'Ants', 
    1: 'Aphids', 
    2: 'Caterpillar', 
    3: 'Corn Worm', 
    4: 'Earwig', 
    5: 'Fall Armyworm', 
    6: 'Grasshopper', 
    7: 'Leaf Beetle', 
    8: 'Mole Cricket', 
    9: 'Red Spider', 
    10: 'Slug', 
    11: 'Snail', 
    12: 'Stem Borer', 
    13: 'Weevil'
}

NUTRIENT_MAPPING = {
    0: 'Healthy (No Deficiency)', 
    1: 'All Nutrients Deficient', 
    2: 'Potassium Deficiency', 
    3: 'Nitrogen Deficiency', 
    4: 'Phosphorus Deficiency', 
    5: 'Zinc Deficiency'
}

from recommendations import RECOMMENDATIONS

# Disease recommendations
RECOMMENDATIONS['Blight'] = {
        'description': 'Blight is a serious fungal disease that causes irregular brown or black spots on leaves, stems, and sometimes fruits. The spots often have a water-soaked appearance and may develop yellow halos. In severe cases, entire plants can wilt and die rapidly.',
        'solutions': [
            'Step 1: Immediate Action - Remove and destroy all infected plant parts. Burn them or bury them deep (at least 1 meter) away from your field.',
            'Step 2: Organic Treatment - Prepare neem oil spray: Mix 5ml (1 teaspoon) of pure neem oil with 1 liter of warm water. Add 2-3 drops of liquid soap as an emulsifier. Spray thoroughly on all plant surfaces, especially the undersides of leaves, every 7 days for 3 weeks.',
            'Step 3: Soil Treatment - Apply wood ash around the base of plants at a rate of 100g per plant. This raises soil pH and creates unfavorable conditions for the fungus.',
            'Step 4: Biological Control - Apply Trichoderma viride powder (available in agricultural stores) to the soil at 10g per plant mixed with compost.'
        ],
        'prevention': [
            'Crop Rotation: After harvesting, plant legumes (beans, peas) or cereals (wheat, barley) for at least 2 seasons before returning to maize.',
            'Spacing: Maintain 75cm between plants and 90cm between rows to ensure good air circulation.',
            'Variety Selection: Plant blight-resistant varieties like SC 403, SC 513, or DK 8031.',
            'Watering Technique: Always water at the base of plants in the early morning. Never wet the leaves.',
            'Sanitation: Clean all tools with 10% bleach solution after working with infected plants.'
        ],
        'monitoring': [
            'Inspect plants twice weekly during wet weather.',
            'Look for small, water-soaked spots on leaves, especially after rain. If you find any, mark the plant and begin treatment immediately as described above.',
            'Start by examining the lowest leaves on each plant, as blight infections usually begin there. If you see any signs, remove those leaves and dispose of them far from the field.',
        ]
    }
RECOMMENDATIONS['Common_Rust'] = {
        'description': 'Common rust appears as small, circular to elongated golden brown pustules primarily on leaves. The pustules break open to release powdery orange spores. Severe infections can cause premature leaf drop and reduced yields.',
        'solutions': [
            'Step 1: Early Treatment - At first sign of rust, mix 1 tablespoon of baking soda, 1 teaspoon of vegetable oil, and 1 liter of water. Add 3 drops of liquid soap. Spray every 5 days for 3 applications.',
            'Step 2: Sulfur Application - Dust plants with wettable sulfur powder (wear mask and gloves). Apply in early morning when dew is present for better adhesion.',
            'Step 3: Remove Severely Infected Leaves - Carefully prune and destroy leaves with more than 50% coverage.',
            'Step 4: Strengthen Plants - Apply foliar spray of seaweed extract (5ml per liter) weekly for 3 weeks to boost plant immunity.'
        ],
        'prevention': [
            'Plant early-maturing varieties that escape peak rust periods.',
            'Avoid excessive nitrogen fertilizer which promotes lush, susceptible growth.',
            'Ensure proper spacing (75cm between plants) for good air flow.',
            'Remove all crop debris after harvest as spores overwinter on plant material.',
            'Water plants in the morning so leaves dry quickly.'
        ],
        'monitoring': [
            'Every Friday, examine the upper surfaces of all maize leaves for small yellow spots. If you find any, record the location and begin the recommended rust treatment.',
            'Monitor lower leaf surfaces for developing pustules.',
            'Watch for orange powder when touching leaves - this indicates spore production.'
        ]
    }
RECOMMENDATIONS['Gray_Leaf_Spot'] = {
        'description': 'Gray leaf spot causes rectangular, tan to gray lesions bounded by leaf veins. Lesions may coalesce, causing large areas of dead tissue. Severe infections can lead to complete defoliation.',
        'solutions': [
            'Step 1: Immediate Action - Remove severely infected leaves (those with >5 lesions) and destroy by burning.',
            'Step 2: Fungicide Application - Prepare copper fungicide according to label (typically 5g per liter). Spray every 10 days during wet periods.',
            'Step 3: Boost Plant Health - Apply potassium-rich fertilizer (like wood ash) at 50g per plant to help leaves resist infection.',
            'Step 4: Organic Spray - Make garlic spray by blending 3 garlic bulbs with 1 liter water. Strain and add 5 drops of liquid soap. Spray every 7 days.'
        ],
        'prevention': [
            'Rotate with non-grass crops (legumes are ideal) for 2-3 years.',
            'Use resistant varieties like PHB 30D79 or SC 637.',
            'Avoid overhead irrigation - use drip irrigation if possible.',
            'Plow under crop residues immediately after harvest.',
            'Maintain soil pH between 6.0-6.5 through liming.'
        ],
        'monitoring': [
            'During periods of high humidity (especially after rain), inspect the lowest leaves on each plant for rectangular, tan to gray lesions. If found, remove and destroy those leaves immediately.',
            'Look for small, water-soaked spots that turn tan with dark borders.',
            'Monitor field edges where disease often starts first.'
        ]
    }
RECOMMENDATIONS['Healthy'] = {
        'description': 'Your plants show no signs of disease. Maintain good practices to keep them healthy!',
        'maintenance': [
            'Every Monday morning, carefully inspect all maize plants for any new spots, discoloration, or wilting. If you notice any unusual changes, immediately isolate affected plants and follow the recommended treatment steps above.',
            'Maintain proper spacing between plants for good air circulation.',
            'Water consistently, providing about 2.5cm of water per week.',
            'Apply balanced fertilizer (NPK 10-10-10) every 4-6 weeks during growing season.',
            'Keep area weed-free to reduce competition and pest habitats.'
        ]
    }

# Pest recommendations
RECOMMENDATIONS['Ants'] = {
        'description': 'Ants themselves don\'t damage maize directly, but they farm aphids and other sap-sucking insects, protecting them from predators in exchange for honeydew. Large ant populations can indicate other pest problems.',
        'solutions': [
            'Step 1: Disrupt Trails - Sprinkle diatomaceous earth or wood ash around plant bases to create barriers ants won\'t cross.',
            'Step 2: Bait Stations - Place borax-sugar bait (mix 1 part borax with 3 parts sugar and enough water to make syrup) in small containers near ant trails.',
            'Step 3: Boiling Water - Carefully pour boiling water into visible nest entrances in early morning when ants are less active.',
            'Step 4: Natural Repellent - Spray plants with citrus oil solution (10 drops orange oil per liter water) to disrupt scent trails.'
        ],
        'prevention': [
            'Keep fields free of debris where ants can nest.',
            'Control aphids and other honeydew-producing insects.',
            'Apply sticky barriers (like Tanglefoot) around base of plants if ants are climbing.',
            'Encourage natural predators like birds by providing perches near field.',
            'Plant mint or tansy around field edges as natural deterrents.'
        ],
        'monitoring': [
            'Twice a week, look for visible ant trails moving up and down maize stalks and across the soil surface. If you see ants, follow the trail to locate nests and apply the recommended ant control methods.',
            'Look for clusters of aphids or other sap-sucking insects being tended by ants.',
            'Monitor for small soil mounds indicating nest sites.'
        ]
    }
RECOMMENDATIONS['Aphids'] = {
        'description': 'Aphids are small, soft-bodied insects that cluster on undersides of leaves and stems, sucking plant sap. They excrete sticky honeydew and can transmit viral diseases. Heavy infestations cause leaf curling and stunted growth.',
        'solutions': [
            'Step 1: Strong Water Spray - Use a strong jet of water to dislodge aphids from plants. Do this in early morning so plants dry quickly.',
            'Step 2: Soap Spray - Mix 1 tablespoon of pure liquid soap (not detergent) with 1 liter water. Spray directly on aphids every 2-3 days for 2 weeks.',
            'Step 3: Neem Oil Treatment - Apply neem oil solution (5ml neem oil + 1 liter water + few drops soap) every 7 days for 3 applications.',
            'Step 4: Introduce Beneficial Insects - Release ladybugs or lacewings (available from garden suppliers) at dusk near infestations.'
        ],
        'prevention': [
            'Plant companion crops like nasturtiums or garlic that repel aphids.',
            'Use reflective mulches (aluminum foil) to confuse flying aphids.',
            'Avoid excess nitrogen fertilizer which promotes tender growth aphids prefer.',
            'Encourage natural predators by planting small-flowered plants like alyssum.',
            'Remove weeds that can serve as alternate hosts.'
        ],
        'monitoring': [
            'Every Wednesday, turn over the newest maize leaves and look closely for clusters of small, soft-bodied aphids. If you find any, start the water spray or soap spray treatment immediately.',
            'Look for sticky honeydew on leaves or ants tending aphids.',
            'Watch for distorted or curled new growth.'
        ]
    }
RECOMMENDATIONS['Caterpillar'] = {
        'description': 'Caterpillars are the larval stage of moths and butterflies that chew on leaves, stems, and sometimes ears of corn. Different species cause different damage patterns from ragged leaf edges to completely skeletonized leaves.',
        'solutions': [
            'Step 1: Hand Picking - Inspect plants daily and hand-pick caterpillars (wear gloves for hairy species). Drop into soapy water.',
            'Step 2: Bt Spray - Apply Bacillus thuringiensis (Bt) according to label, typically 5g per liter. Spray in evening when caterpillars are active.',
            'Step 3: Natural Spray - Make hot pepper spray by steeping 2 chopped hot peppers in 1 liter hot water overnight. Strain and add 1 teaspoon soap. Spray affected plants.',
            'Step 4: Beneficial Nematodes - Apply Steinernema carpocapsae nematodes to soil for soil-dwelling caterpillars.'
        ],
        'prevention': [
            'Use floating row covers to prevent moths from laying eggs.',
            'Plant trap crops like sunflowers to attract pests away from maize.',
            'Encourage natural predators like birds, wasps, and spiders.',
            'Practice crop rotation to disrupt life cycles.',
            'Till soil after harvest to expose overwintering pupae.'
        ],
        'monitoring': [
            'Inspect all maize plants at sunrise and sunset, when caterpillars are most active. Look for chewed leaves or visible caterpillars, and remove them by hand if found.',
            'Look for frass (caterpillar droppings) on leaves as an early sign.',
            'Use pheromone traps to monitor adult moth populations.'
        ]
    }
RECOMMENDATIONS['Corn Worm'] = {
        'description': 'Corn worms (corn earworms) are destructive caterpillars that feed on developing ears, entering through the silk channel. They cause direct yield loss and promote fungal infections in damaged ears.',
        'solutions': [
            'Step 1: Silk Treatment - Apply 5 drops of mineral oil mixed with Bt (Bacillus thuringiensis) to corn silks when they begin to brown.',
            'Step 2: Manual Removal - For small plantings, check ears weekly and remove any worms found at the tip.',
            'Step 3: Botanical Insecticide - Apply neem oil (5ml per liter) directly to silks every 5 days during silking period.',
            'Step 4: Trichogramma Wasps - Release these tiny parasitic wasps that attack worm eggs (available from biological control suppliers).'
        ],
        'prevention': [
            'Plant early-maturing varieties to avoid peak pest periods.',
            'Use tight-husked varieties that are harder for worms to enter.',
            'Practice deep plowing after harvest to destroy overwintering pupae.',
            'Install pheromone traps to monitor moth flights and time treatments.',
            'Remove and destroy infested ears immediately.'
        ],
        'monitoring': [
            'During the pollination period, examine corn silks every morning for small, white worm eggs. If eggs are present, apply mineral oil and Bt mixture as described in the solutions.',
            'Inspect ear tips weekly for feeding damage or frass.',
            'Use blacklight traps to monitor adult moth activity.'
        ]
    }
RECOMMENDATIONS['Fall Armyworm'] = {
        'description': 'Fall armyworm is a highly destructive pest that feeds in large groups, skeletonizing leaves and sometimes cutting young plants. They are most active in warm conditions and can completely defoliate fields rapidly.',
        'solutions': [
            'Step 1: Early Detection - Handpick and destroy egg masses (fuzzy white patches) and young larvae.',
            'Step 2: Bt Application - Spray Bacillus thuringiensis var. kurstaki (5g per liter) in late afternoon when larvae are feeding.',
            'Step 3: Spinosad Treatment - Apply spinosad-based insecticide (follow label rates) as a last resort for severe infestations.',
            'Step 4: Push-Pull Strategy - Plant desmodium between rows and napier grass around perimeter to repel and trap armyworms.'
        ],
        'prevention': [
            'Plant early to avoid peak armyworm periods.',
            'Encourage natural enemies like parasitic wasps and birds.',
            'Use resistant varieties where available.',
            'Practice field sanitation to remove alternate hosts.',
            'Intercrop with repellent plants like garlic or onions.'
        ],
        'monitoring': [
            'Every Saturday, inspect the underside of maize leaves for fuzzy white egg masses. If you find any, remove them by hand and destroy them away from the field.',
            'Look for window-paned leaves (translucent patches where tissue has been eaten).',
            'Use pheromone traps to detect adult moth flights.'
        ]
    }

# Nutrient deficiency recommendations
RECOMMENDATIONS['Nitrogen Deficiency'] = {
        'description': 'Nitrogen deficiency shows as uniform yellowing (chlorosis) of older leaves starting from the tip progressing toward the stem. Plants are stunted with spindly stalks and poor ear development.',
        'solutions': [
            'Step 1: Quick Fix - Apply foliar spray of urea (10g per liter water) in early morning or late afternoon.',
            'Step 2: Soil Amendment - Side-dress with composted manure (2kg per plant) or chemical fertilizer (15g ammonium sulfate per plant).',
            'Step 3: Green Manure - Plant and incorporate nitrogen-fixing cover crops like cowpea or clover between seasons.',
            'Step 4: Long-Term Solution - Apply 100g of neem cake per plant every 3 months to slowly release nitrogen.'
        ],
        'prevention': [
            'Conduct soil test before planting to determine nitrogen needs.',
            'Use split applications - apply 1/3 at planting, 1/3 at knee-high stage, 1/3 at tasseling.',
            'Maintain proper soil pH (6.0-6.5) for optimal nitrogen availability.',
            'Practice crop rotation with legumes to naturally replenish nitrogen.',
            'Use organic mulches that decompose to release nitrogen slowly.'
        ],
        'monitoring': [
            'Every Tuesday, inspect the lowest leaves of each maize plant for yellowing that starts at the tips. If yellowing is observed, apply a foliar urea spray as described in the solutions.',
            'Monitor plant growth rate - nitrogen-deficient plants grow slower.',
            'Watch for poor ear development and small ears.'
        ]
    }
RECOMMENDATIONS['Phosphorus Deficiency'] = {
        'description': 'Phosphorus deficiency causes stunted plants with dark green or purplish older leaves. Roots are poorly developed and plants mature slowly. Ears may be poorly filled with irregular kernel patterns.',
        'solutions': [
            'Step 1: Immediate Treatment - Apply foliar spray of 5% superphosphate solution (50g per liter) every 10 days for 3 applications.',
            'Step 2: Soil Application - Mix 50g of rock phosphate or bone meal per plant into top 10cm of soil.',
            'Step 3: Organic Matter - Incorporate compost high in phosphorus (like mushroom compost) at 3kg per square meter.',
            'Step 4: Microbial Boost - Apply phosphorus-solubilizing bacteria (PSB) inoculant to help release bound phosphorus.'
        ],
        'prevention': [
            'Apply phosphorus at planting as it doesn\'t move well in soil.',
            'Maintain soil pH between 6.0-7.0 for best phosphorus availability.',
            'Use band application of fertilizer near roots rather than broadcasting.',
            'Add mycorrhizal fungi to help plants access phosphorus.',
            'Avoid overwatering which can leach phosphorus from root zone.'
        ],
        'monitoring': [
            'Look for purple tint on lower leaves and leaf margins.',
            'Check for poor root development when pulling weeds.',
            'Monitor plant height compared to expected growth stage.'
        ]
    }
RECOMMENDATIONS['Potassium Deficiency'] = {
        'description': 'Potassium deficiency appears as yellowing and browning (necrosis) along leaf margins starting with older leaves. Stalks are weak and prone to lodging. Ears may have poorly filled tips.',
        'solutions': [
            'Step 1: Quick Correction - Spray potassium sulfate (10g per liter) on leaves in early morning.',
            'Step 2: Soil Amendment - Apply wood ash (100g per plant) or muriate of potash (20g per plant) around base.',
            'Step 3: Organic Options - Bury banana peels or compost rich in fruit wastes near plants.',
            'Step 4: Long-Term Fix - Grow and incorporate potassium-accumulating cover crops like comfrey.'
        ],
        'prevention': [
            'Conduct regular soil tests to monitor potassium levels.',
            'Apply potassium in split doses - half at planting, half at knee-high stage.',
            'Maintain proper calcium levels as imbalance affects potassium uptake.',
            'Use composted vegetable matter regularly to replenish potassium.',
            'Avoid excessive nitrogen which can worsen potassium deficiency.'
        ],
        'monitoring': [
            'On Thursdays, examine the oldest leaves on each plant for yellow or brown edges that progress inward. If you see this, apply potassium sulfate spray as described above.',
            'Monitor stalk strength - potassium-deficient stalks bend easily.',
            'Watch for poor grain filling at ear tips.'
        ]
    }
RECOMMENDATIONS['Zinc Deficiency'] = {
        'description': 'Zinc deficiency causes broad white to yellow bands between leaf veins while veins remain green (interveinal chlorosis). Plants are stunted with shortened internodes, producing a rosette appearance.',
        'solutions': [
            'Step 1: Foliar Spray - Apply zinc sulfate heptahydrate (5g per liter) with a few drops of vinegar to help absorption.',
            'Step 2: Soil Application - Mix 10g of zinc sulfate per plant into topsoil or apply zinc-enriched manure.',
            'Step 3: Seed Treatment - For future plantings, soak seeds in 0.1% zinc sulfate solution for 12 hours before planting.',
            'Step 4: Organic Sources - Apply compost made from zinc-rich materials like seafood waste or certain weeds.'
        ],
        'prevention': [
            'Maintain soil pH between 6.0-7.0 as zinc becomes less available at higher pH.',
            'Use balanced fertilizers as excess phosphorus can induce zinc deficiency.',
            'Practice crop rotation with non-cereal crops to break deficiency cycles.',
            'Incorporate organic matter to improve zinc retention in soil.',
            'Avoid overliming which can tie up zinc.'
        ],
        'monitoring': [
            'When new leaves emerge, look for broad white or yellow stripes between the veins. If you notice this, apply zinc sulfate foliar spray as recommended.',
            'Check for shortened internodes giving plants a bushy appearance.',
            'Monitor plant height compared to expected growth stage.'
        ]
    }
RECOMMENDATIONS['All Nutrients Deficient'] = {
        'description': 'Your plants show multiple deficiency symptoms indicating general nutrient starvation. This often results from poor soil fertility, improper pH, or excessive leaching from heavy rains.',
        'solutions': [
            'Step 1: Balanced Fertilizer - Apply complete NPK fertilizer (10-10-10) at 30g per plant, watered in well.',
            'Step 2: Compost Tea - Brew compost tea by soaking 1kg compost in 10 liters water for 3 days. Dilute 1:10 and apply to soil.',
            'Step 3: Foliar Feeding - Spray seaweed extract (5ml per liter) every 10 days for quick nutrient uptake.',
            'Step 4: Soil Testing - Conduct proper soil test to identify specific deficiencies and amend accordingly.'
        ],
        'prevention': [
            'Implement regular crop rotation with legumes and cover crops.',
            'Apply well-composted manure annually at 5kg per square meter.',
            'Maintain proper soil pH (6.0-6.5 for maize) for nutrient availability.',
            'Use mulch to prevent nutrient leaching during heavy rains.',
            'Consider terrace farming or contour planting if erosion is an issue.'
        ],
        'monitoring': [
            'Every week, systematically inspect all parts of each maize plant for signs of multiple deficiencies (yellowing, stunting, poor development). If you observe these, apply a balanced NPK fertilizer and follow the solutions above.',
            'Monitor growth rate compared to expected stages.',
            'Watch for general yellowing, stunting, and poor development.'
        ]
    }
RECOMMENDATIONS['Healthy (No Deficiency)'] = {
    'description': 'Your plants show no signs of nutrient deficiency. Maintain good nutrient management practices to keep them healthy!',
    'solutions': [
        'Continue regular soil testing to monitor nutrient levels and ensure balanced fertility.',
        'Apply balanced NPK fertilizers (10-10-10) as needed based on soil test recommendations.',
        'Incorporate organic amendments like compost or manure to maintain long-term soil health.'
    ],
    'prevention': [
        'Conduct soil tests every 2-3 years before planting season.',
        'Practice crop rotation with legumes to naturally replenish soil nutrients.',
        'Apply well-composted organic matter annually at 5kg per square meter.',
        'Maintain proper soil pH (6.0-6.5) for optimal nutrient availability.',
        'Use mulch to prevent nutrient leaching during heavy rains.'
    ],
    'monitoring': [
        'Every week, inspect plants for any signs of nutrient stress (yellowing, stunting, poor growth).',
        'Monitor plant growth rate compared to expected stages.',
        'Keep records of fertilizer applications and plant responses.',
        'Watch for general yellowing, stunting, or poor development as early warning signs.'
    ]
}


RECOMMENDATIONS['Earwig'] = {
    'description': 'Earwigs are nocturnal insects that can feed on maize seedlings and soft plant tissues, causing irregular holes and damage.',
    'solutions': [
        'Inspect plants at night with a flashlight to spot and remove earwigs by hand.',
        'Place rolled-up damp newspapers or cardboard tubes near plants in the evening; collect and destroy earwigs hiding inside each morning.',
        'Apply diatomaceous earth around plant bases to deter earwigs.',
        'Encourage natural predators such as birds and toads.'
    ],
    'prevention': [
        'Remove plant debris and mulch where earwigs can hide.',
        'Avoid overwatering and keep the area around plants dry.',
        'Seal cracks and crevices in nearby structures.'
    ],
    'monitoring': [
        'Check traps and plant bases every morning for earwig activity.',
        'Record any increases in earwig numbers or plant damage.'
    ]
}
RECOMMENDATIONS['Grasshopper'] = {
    'description': 'Grasshoppers chew on maize leaves, stems, and sometimes ears, causing ragged holes and defoliation. Large infestations can severely reduce yield.',
    'solutions': [
        'Handpick grasshoppers early in the morning when they are less active.',
        'Apply neem oil spray (5ml per liter of water) to affected plants every 7 days.',
        'Use floating row covers to protect young maize seedlings.',
        'Encourage natural predators such as birds and chickens.',
        'For severe infestations, apply approved biological insecticides (e.g., Nosema locustae spores) following label instructions.'
    ],
    'prevention': [
        'Keep field edges mowed and free of tall weeds where grasshoppers lay eggs.',
        'Rotate crops and avoid planting maize next to grassland or fallow fields.',
        'Plant trap crops (e.g., sunflowers) to attract grasshoppers away from maize.'
    ],
    'monitoring': [
        'Inspect maize plants and field edges twice a week for grasshopper presence.',
        'Look for chewed leaves and droppings as early signs of infestation.'
    ]
}
RECOMMENDATIONS['Leaf Beetle'] = {
    'description': 'Leaf beetles feed on maize leaves, creating small, round holes and sometimes skeletonizing the foliage.',
    'solutions': [
        'Handpick beetles and larvae from plants and destroy them.',
        'Apply neem oil or insecticidal soap to affected leaves every 5-7 days.',
        'Introduce beneficial insects such as ladybugs and lacewings.',
        'Remove and destroy heavily infested leaves.'
    ],
    'prevention': [
        'Remove weeds and plant debris that can harbor beetles.',
        'Rotate crops to break the beetle life cycle.',
        'Use reflective mulches to deter beetles from landing on plants.'
    ],
    'monitoring': [
        'Check the undersides of leaves weekly for beetles and larvae.',
        'Monitor for new holes or skeletonized areas on leaves.'
    ]
}
RECOMMENDATIONS['Mole Cricket'] = {
    'description': 'Mole crickets tunnel through soil, damaging maize roots and seedlings, which can cause wilting and stunted growth.',
    'solutions': [
        'Flood infested areas with water and a few drops of dish soap to force mole crickets to the surface for removal.',
        'Apply beneficial nematodes (Steinernema spp.) to soil to control mole cricket larvae.',
        'Till soil before planting to expose and destroy eggs and larvae.'
    ],
    'prevention': [
        'Maintain well-drained soil and avoid overwatering.',
        'Remove grassy weeds and plant debris where mole crickets hide.',
        'Encourage natural predators such as birds.'
    ],
    'monitoring': [
        'Inspect soil and roots of young maize plants weekly for signs of tunneling or wilting.',
        'Look for raised soil ridges or holes near plant bases.'
    ]
}
RECOMMENDATIONS['Red Spider'] = {
    'description': 'Red spider mites are tiny pests that feed on maize leaves, causing yellow stippling, webbing, and leaf drop.',
    'solutions': [
        'Spray affected plants with a strong jet of water to dislodge mites.',
        'Apply insecticidal soap or neem oil to the undersides of leaves every 5 days.',
        'Remove and destroy heavily infested leaves.',
        'Increase humidity around plants if possible, as mites thrive in dry conditions.'
    ],
    'prevention': [
        'Keep plants well-watered and avoid drought stress.',
        'Remove weeds and plant debris that can harbor mites.',
        'Encourage natural predators such as predatory mites and ladybugs.'
    ],
    'monitoring': [
        'Inspect the undersides of leaves twice a week for mites and webbing.',
        'Look for yellow spots or stippling as early signs of infestation.'
    ]
}
RECOMMENDATIONS['Slug'] = {
    'description': 'Slugs feed on maize seedlings and leaves, leaving irregular holes and silvery slime trails.',
    'solutions': [
        'Handpick slugs in the evening or early morning and destroy them.',
        'Set out shallow dishes of beer as traps to attract and drown slugs.',
        'Apply diatomaceous earth or crushed eggshells around plant bases to deter slugs.',
        'Use iron phosphate slug baits if needed, following label instructions.'
    ],
    'prevention': [
        'Remove mulch, plant debris, and weeds where slugs hide.',
        'Water plants in the morning to keep soil surface dry overnight.',
        'Encourage natural predators such as birds, toads, and ground beetles.'
    ],
    'monitoring': [
        'Check for slime trails and feeding damage on seedlings and leaves every few days.',
        'Inspect traps and plant bases regularly for slug activity.'
    ]
}
RECOMMENDATIONS['Snail'] = {
    'description': 'Snails feed on maize seedlings and leaves, causing ragged holes and leaving slime trails.',
    'solutions': [
        'Handpick snails in the evening or after rain and destroy them.',
        'Set out boards or tiles as shelters; collect and remove snails hiding underneath each morning.',
        'Apply copper tape or diatomaceous earth around plant bases to deter snails.',
        'Use iron phosphate snail baits if needed, following label instructions.'
    ],
    'prevention': [
        'Remove plant debris, mulch, and weeds where snails hide.',
        'Water plants in the morning to reduce overnight moisture.',
        'Encourage natural predators such as birds and toads.'
    ],
    'monitoring': [
        'Inspect seedlings and leaves for holes and slime trails every few days.',
        'Check shelters and plant bases for snails regularly.'
    ]
}
RECOMMENDATIONS['Stem Borer'] = {
    'description': 'Stem borers are larvae that tunnel into maize stems, causing dead hearts, stunted growth, and reduced yield.',
    'solutions': [
        'Cut and destroy infested stems below the borer entry point.',
        'Apply neem oil or Bacillus thuringiensis (Bt) to the base of stems and leaf whorls.',
        'Remove and destroy crop residues after harvest to eliminate overwintering larvae.',
        'Encourage natural enemies such as parasitic wasps.'
    ],
    'prevention': [
        'Rotate maize with non-host crops to break the borer life cycle.',
        'Plant resistant maize varieties if available.',
        'Avoid late planting, which increases borer risk.'
    ],
    'monitoring': [
        'Inspect stems and leaf whorls weekly for entry holes, frass, or wilting.',
        'Check for dead hearts and stunted plants as signs of infestation.'
    ]
}
RECOMMENDATIONS['Weevil'] = {
    'description': 'Weevils are small beetles that can damage maize both in the field and in storage, boring into kernels and stems.',
    'solutions': [
        'Handpick adult weevils from plants and destroy them.',
        'Harvest maize promptly and dry thoroughly before storage.',
        'Store maize in airtight containers or bags with natural repellents (e.g., dried neem leaves).',
        'Use approved insecticides for severe field infestations, following label instructions.'
    ],
    'prevention': [
        'Clean storage areas and containers before use.',
        'Rotate crops and avoid continuous maize planting.',
        'Remove and destroy crop residues after harvest.'
    ],
    'monitoring': [
        'Inspect plants and stored maize regularly for weevils or damage.',
        'Check for small holes in kernels and stems as early signs of infestation.'
    ]
}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clear_upload_folder():
    """Completely clear the upload folder"""
    folder = app.config['UPLOAD_FOLDER']
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

def preprocess_image(img_path, target_size=(224, 224)):
    """Improved image preprocessing with error handling"""
    try:
        # Read image
        img = Image.open(img_path)
        
        # Convert to RGB if not already
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        # Resize and preprocess
        img = img.resize(target_size)
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0
        
        return img_array
    except Exception as e:
        print(f"Error preprocessing image: {str(e)}")
        raise

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def home():
    clear_upload_folder()
    lang = get_current_language()
    translations = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    return render_template('index.html', translations=translations, current_lang=lang)

@app.route('/disease', methods=['GET', 'POST'])
def disease_detection():
    clear_upload_folder()
    
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        # Check if file is empty
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        # Validate file
        if file and allowed_file(file.filename):
            try:
                # Secure filename and save
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                # Save file
                file.save(filepath)
                
                # Verify file was saved
                if not os.path.exists(filepath):
                    flash('Error saving file', 'error')
                    return redirect(request.url)
                
                # Preprocess and predict
                processed_img = preprocess_image(filepath)
                prediction = disease_model.predict(processed_img)
                predicted_class = np.argmax(prediction)
                confidence = np.max(prediction) * 100
                problem = DISEASE_MAPPING[predicted_class]
                
                # Get translated recommendations
                lang = get_current_language()
                recommendations = get_recommendations(problem, lang)
                
                lang = get_current_language()
                translations = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
                return render_template('disease_results.html',
                                    problem_type=get_text('disease', lang),
                                    problem_name=problem,
                                    confidence=f"{confidence:.2f}%",
                                    image_path=filename,
                                    translations=translations,
                                    current_lang=lang,
                                    description=recommendations.get('description', ''),
                                    solutions=recommendations.get('solutions', []),
                                    prevention=recommendations.get('prevention', []),
                                    monitoring=recommendations.get('monitoring', []))
                
            except Exception as e:
                flash(f'Error processing image: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Allowed file types are png, jpg, jpeg', 'error')
            return redirect(request.url)
    
    lang = get_current_language()
    translations = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    return render_template('disease.html', translations=translations, current_lang=lang)
@app.route('/yield', methods=['GET', 'POST'])
def yield_prediction():
    lang = get_current_language()
    translations = TRANSLATIONS.get(lang, TRANSLATIONS['en'])

    if request.method == 'POST':
        try:
            # Check if weather data should be fetched
            use_weather = request.form.get('use_weather') == 'on'
            location = request.form.get('location', '').strip()
            planting_date = request.form.get('planting_date', '').strip()

            if use_weather and location:
                # Fetch weather data for the growing period
                if planting_date:
                    from datetime import datetime, timedelta
                    # Calculate growing period (assume harvest is current date for now)
                    today = datetime.now().strftime('%Y-%m-%d')
                    weather_data = weather_service.get_historical_weather_data(location, planting_date, today)
                else:
                    weather_data = weather_service.get_weather_data(location)

                if weather_data['success']:
                    rainfall = weather_data['avg_rainfall']
                    temperature = weather_data['avg_temperature']
                    flash(get_text('weather_updated', lang), 'success')
                else:
                    flash(get_text('weather_error', lang), 'error')
                    rainfall = float(request.form['rainfall'])
                    temperature = float(request.form['temperature'])
            else:
                rainfall = float(request.form['rainfall'])
                temperature = float(request.form['temperature'])
            # Handle unknown countries by using similar country proxies
            selected_country = request.form['Area']

            # Known countries in the dataset (based on typical crop yield datasets)
            known_countries = [
                'Albania', 'Algeria', 'Argentina', 'Armenia', 'Australia', 'Austria', 'Azerbaijan',
                'Bahamas', 'Bangladesh', 'Belarus', 'Belgium', 'Botswana', 'Brazil', 'Bulgaria',
                'Burkina Faso', 'Burundi', 'Cameroon', 'Canada', 'Central African Republic', 'Chile',
                'Colombia', 'Croatia', 'Denmark', 'Dominican Republic', 'Ecuador', 'Egypt', 'El Salvador',
                'Eritrea', 'Estonia', 'Finland', 'France', 'Germany', 'Ghana', 'Greece', 'Guatemala',
                'Guinea', 'Guyana', 'Haiti', 'Honduras', 'Hungary', 'India', 'Indonesia', 'Iraq', 'Ireland',
                'Italy', 'Jamaica', 'Japan', 'Kazakhstan', 'Kenya', 'Latvia', 'Lebanon', 'Lesotho',
                'Libya', 'Lithuania', 'Madagascar', 'Malawi', 'Malaysia', 'Mali', 'Mauritania', 'Mauritius',
                'Mexico', 'Morocco', 'Mozambique', 'Namibia', 'Nepal', 'Netherlands', 'New Zealand',
                'Nicaragua', 'Niger', 'Norway', 'Pakistan', 'Papua New Guinea', 'Peru', 'Poland',
                'Portugal', 'Qatar', 'Romania', 'Rwanda', 'Saudi Arabia', 'Senegal', 'Slovenia',
                'South Africa', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Sweden', 'Switzerland',
                'Tajikistan', 'Thailand', 'Tunisia', 'Turkey', 'Uganda', 'Ukraine', 'United Kingdom',
                'Uruguay', 'Zambia', 'Zimbabwe'
            ]

            # Country mapping for unknown countries (use similar climates/geography)
            country_fallbacks = {
                'Nigeria': 'Ghana',  # Similar West African climate
                'Ethiopia': 'Kenya',  # Similar East African climate
                'Tanzania': 'Kenya',  # Similar climate
                'Congo': 'Cameroon',  # Similar Central African climate
                'Ivory Coast': 'Ghana',  # Similar West African climate
                'Senegal': 'Mali',  # Similar Sahel climate
                'Chad': 'Niger',  # Similar Sahel climate
                'Mali': 'Niger',  # Both Sahel region
                'Benin': 'Ghana',  # Similar Gulf of Guinea climate
                'Togo': 'Ghana',  # Similar climate
                'Sierra Leone': 'Guinea',  # Similar West African climate
                'Liberia': 'Guinea',  # Similar climate
                'Gambia': 'Senegal',  # Similar climate
                'Guinea-Bissau': 'Guinea',  # Similar climate
                'Cape Verde': 'Senegal',  # Similar climate
                'Somalia': 'Kenya',  # Similar East African climate
                'Djibouti': 'Eritrea',  # Similar climate
                'Comoros': 'Madagascar',  # Similar island climate
                'Seychelles': 'Mauritius',  # Similar island climate
                'Equatorial Guinea': 'Cameroon',  # Similar climate
                'Gabon': 'Cameroon',  # Similar climate
                'Angola': 'Zambia',  # Similar Southern African climate
                'Namibia': 'Botswana',  # Similar Southern African climate
                'Swaziland': 'South Africa',  # Similar climate
                'Lesotho': 'South Africa',  # Similar climate
                'Zimbabwe': 'Zambia',  # Similar climate
                'Mozambique': 'Malawi',  # Similar climate
            }

            # Determine which country to use for prediction
            if selected_country in known_countries:
                country_for_model = selected_country
                session['original_country'] = selected_country
                session['fallback_country'] = None
                flash(f'Using data for {selected_country}', 'info')
            elif selected_country in country_fallbacks:
                fallback_country = country_fallbacks[selected_country]
                country_for_model = fallback_country
                session['original_country'] = selected_country
                session['fallback_country'] = fallback_country
            else:
                # Default fallback for completely unknown countries
                country_for_model = 'Nigeria'  # Default African country
                session['original_country'] = selected_country
                session['fallback_country'] = 'Nigeria'

            data = {
                'Area': country_for_model,  # Use the mapped country for the model
                'Item': request.form['Item'],
                'Year': int(request.form['Year']),
                'average_rain_fall_mm_per_year': rainfall,
                'pesticides_tonnes': float(request.form['pesticides']),
                'avg_temp': temperature
            }

            input_df = pd.DataFrame([data])
            prediction = yield_model.predict(input_df)[0]

            return render_template('yield_results.html',
                                  prediction=round(prediction, 2),
                                  weather_data=weather_data if use_weather and location and weather_data.get('success') else None,
                                  translations=translations,
                                  current_lang=lang,
                                  planting_date=planting_date,
                                  **data)

        except Exception as e:
            flash(f'Error making prediction: {str(e)}', 'error')
            return redirect(url_for('yield_prediction'))

    return render_template('yield.html', translations=translations, current_lang=lang)
@app.route('/pest', methods=['GET', 'POST'])
def pest_detection():
    clear_upload_folder()
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                processed_img = preprocess_image(filepath)
                prediction = pest_model.predict(processed_img)
                predicted_class = np.argmax(prediction)
                confidence = np.max(prediction) * 100
                problem = PEST_MAPPING[predicted_class]
                
                # Get translated recommendations
                lang = get_current_language()
                recommendations = get_recommendations(problem, lang)

                translations = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
                return render_template('pest_results.html',
                                    problem_type=get_text('pests', lang),
                                    problem_name=problem,
                                    confidence=f"{confidence:.2f}%",
                                    image_path=filename,
                                    translations=translations,
                                    current_lang=lang,
                                    description=recommendations.get('description', ''),
                                    solutions=recommendations.get('solutions', []),
                                    prevention=recommendations.get('prevention', []),
                                    monitoring=recommendations.get('monitoring', []))
            
            except Exception as e:
                flash(f'Error processing image: {str(e)}', 'error')
                return redirect(request.url)
    
    lang = get_current_language()
    translations = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    return render_template('pest.html', translations=translations, current_lang=lang)

@app.route('/nutrient', methods=['GET', 'POST'])
def nutrient_detection():
    clear_upload_folder()
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                processed_img = preprocess_image(filepath)
                prediction = nutrient_model.predict(processed_img)
                predicted_class = np.argmax(prediction)
                confidence = np.max(prediction) * 100
                problem = NUTRIENT_MAPPING[predicted_class]
                
                # Get translated recommendations
                lang = get_current_language()
                recommendations = get_recommendations(problem, lang)

                translations = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
                return render_template('nutrient_results.html',
                                    problem_type=get_text('nutrients', lang),
                                    problem_name=problem,
                                    confidence=f"{confidence:.2f}%",
                                    image_path=filename,
                                    translations=translations,
                                    current_lang=lang,
                                    description=recommendations.get('description', ''),
                                    solutions=recommendations.get('solutions', []),
                                    prevention=recommendations.get('prevention', []),
                                    monitoring=recommendations.get('monitoring', []))
            
            except Exception as e:
                flash(f'Error processing image: {str(e)}', 'error')
                return redirect(request.url)
    
    lang = get_current_language()
    translations = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    return render_template('nutrient.html', translations=translations, current_lang=lang)

# Maize Guidance Routes
@app.route('/maize-guide')
def maize_guide():
    """Main maize guidance page"""
    lang = get_current_language()
    translations = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    print(f"[DEBUG] /maize-guide: lang={lang}, complete_guide={translations.get('complete_guide')}, stage_by_stage={translations.get('stage_by_stage')}, ask_assistant={translations.get('ask_assistant')}")
    return render_template('maize_guide.html', translations=translations, current_lang=lang)

@app.route('/api/maize-guidance', methods=['POST'])
def get_maize_guidance():
    """API endpoint for maize guidance"""
    try:
        data = request.get_json()
        stage = data.get('stage')
        question = data.get('question')
        language = get_current_language()
    
        # Allow requests where both are null/None - this will trigger complete guide
        guidance = farming_assistant.get_maize_guidance(stage=stage, question=question, language=language)

        if guidance['success']:
            return jsonify({
                'success': True,
                'content': guidance['content'],
                'type': guidance['type'],
                'stage': guidance.get('stage'),
                'question': guidance.get('question')
            })
        else:
            # Return fallback content if available, otherwise return error
            if guidance.get('fallback_content'):
                return jsonify({
                    'success': True,  # Still success because we have fallback
                    'content': guidance['fallback_content'],
                    'type': 'fallback',
                    'stage': guidance.get('stage'),
                    'question': guidance.get('question'),
                    'note': guidance['error']
                })
            else:
                return jsonify({
                    'success': False,
                    'error': guidance['error']
                }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)