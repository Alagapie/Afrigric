import os
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FarmingAssistant:
    def __init__(self):
        # Check for API key
        api_key = os.getenv('GEMINI_API_KEY', '').strip()

        if not api_key or api_key == '' or api_key == 'AIzaSyB9Q8w8k8Q8w8k8Q8w8k8Q8w8k8Q8w8k8Q8w8k' or len(api_key) < 20:
            print("⚠️  Gemini API key not configured properly. Using fallback content only.")
            self.api_available = False
            self.llm = None
            self.conversation = None
        else:
            try:
                # Configure Gemini API (following working Streamlit pattern)
                genai.configure(api_key=api_key)

                # Set generation configuration (matching working example)
                generation_config = {
                    "temperature": 0.8,
                    "top_k": 40,
                    "top_p": 0.8,
                    "max_output_tokens": 2048,
                }

                # Initialize Gemini model directly (following working pattern)
                self.model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash-lite",
                    generation_config=generation_config
                )

                # Test the API with a simple request
                try:
                    test_response = self.model.generate_content("Hello, Gemini API test")
                    print("✅ Gemini API test successful")
                except Exception as test_e:
                    print(f"⚠️  Gemini API test failed: {str(test_e)}")
                    # Continue anyway, might work for actual requests

                # Initialize LangChain with Gemini for conversational features
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    temperature=0.8,
                    top_k=40,
                    top_p=0.8,
                    google_api_key=api_key,
                    request_timeout=30,
                    max_retries=2
                )

                # Create conversation memory
                self.memory = ConversationBufferMemory()

                # Initialize conversation chain
                self.conversation = ConversationChain(
                    llm=self.llm,
                    memory=self.memory,
                    verbose=False
                )

                self.api_available = True
                print("✅ Gemini API initialized successfully with proper configuration")

            except Exception as e:
                print(f"❌ Failed to initialize Gemini API: {str(e)}")
                self.api_available = False
                self.model = None
                self.llm = None
                self.conversation = None

    def get_language_instruction(self, lang_code):
        """Get language instruction for AI prompts"""
        language_instructions = {
            'en': 'You MUST respond ONLY in English. Do not use any other language. All your responses must be in English.',
            'yo': 'You MUST respond ONLY in Yoruba language. Do not use any other language. All your responses must be in Yoruba.',
            'ha': 'You MUST respond ONLY in Hausa language. Do not use any other language. All your responses must be in Hausa.',
            'ig': 'You MUST respond ONLY in Igbo language. Do not use any other language. All your responses must be in Igbo.'
        }
        return language_instructions.get(lang_code, 'You MUST respond ONLY in English. Do not use any other language. All your responses must be in English.')

    def get_maize_guidance(self, stage=None, question=None, language='en'):
        """Get comprehensive maize farming guidance"""

        if question:
            # Handle specific user questions
            return self._answer_question(question, language)
        elif stage:
            # Provide guidance for specific growth stages
            return self._get_stage_guidance(stage, language)
        else:
            # Provide complete maize farming guide
            return self._get_complete_guide(language)

    def _get_complete_guide(self, language='en'):
        """Get complete maize farming guide from planting to harvest"""

        # Check if API is available
        if not self.api_available or not self.model:
            return {
                'success': False,
                'error': 'Gemini API not configured. Please set GEMINI_API_KEY in .env file.',
                'fallback_content': self._get_fallback_guide(language)
            }

        language_instruction = self.get_language_instruction(language)

        prompt = f"""
        You are an expert agricultural extension officer specializing in maize farming.
        {language_instruction}

        IMPORTANT: You must follow these language rules strictly:
        - Respond only in the specified language above
        - Do not mix languages or use any other language
        - Use appropriate terminology and expressions for the target language
        - Maintain the same level of detail and structure regardless of language

        Provide a comprehensive, step-by-step guide for maize farming from beginning to end.
        Make it practical, easy to understand, and suitable for smallholder farmers in developing countries.

        Structure your response with clear sections and practical tips. Include:
        1. Land preparation
        2. Seed selection and planting
        3. Fertilizer application
        4. Weed management
        5. Pest and disease control
        6. Irrigation (if applicable)
        7. Harvesting
        8. Post-harvest handling
        9. Common mistakes to avoid

        Use simple language and include approximate timelines, quantities, and costs where relevant.
        Keep the response under 2000 words.
        """

        try:
            # Use direct Gemini API (following working Streamlit pattern)
            response = self.model.generate_content(prompt)
            return {
                'success': True,
                'content': response.text,
                'type': 'complete_guide'
            }
        except Exception as e:
            error_msg = str(e).lower()
            if 'timeout' in error_msg or 'connection' in error_msg or 'network' in error_msg:
                user_friendly_error = 'Connection timeout. Check your internet connection and try again.'
            elif 'quota' in error_msg or 'rate limit' in error_msg:
                user_friendly_error = 'API quota exceeded. Please try again later.'
            elif 'invalid' in error_msg or 'unauthorized' in error_msg:
                user_friendly_error = 'API key issue. Please check your GEMINI_API_KEY configuration.'
            else:
                user_friendly_error = f'AI service temporarily unavailable: {str(e)}'

            return {
                'success': False,
                'error': user_friendly_error,
                'fallback_content': self._get_fallback_guide(language)
            }

    def _get_stage_guidance(self, stage, language='en'):
        """Get guidance for specific maize growth stages"""

        # Check if API is available
        if not self.api_available or not self.model:
            return {
                'success': False,
                'error': 'Gemini API not configured. Please set GEMINI_API_KEY in .env file.',
                'stage': stage,
                'fallback_content': self._get_stage_fallback(stage, language)
            }

        language_instruction = self.get_language_instruction(language)

        stage_prompts = {
            'land_preparation': "Provide detailed guidance on land preparation for maize farming",
            'planting': "Guide on proper maize planting techniques, spacing, and timing",
            'fertilizer': "Explain maize fertilizer requirements and application schedules",
            'weed_control': "Describe effective weed management strategies for maize",
            'pest_control': "Cover common maize pests and integrated pest management",
            'disease_control': "Explain maize disease identification and treatment",
            'irrigation': "Guide on maize watering requirements and irrigation methods",
            'harvesting': "Explain when and how to harvest maize properly",
            'post_harvest': "Cover maize storage, processing, and marketing"
        }

        prompt = f"""
        You are an agricultural expert. {language_instruction}

        IMPORTANT: You must follow these language rules strictly:
        - Respond only in the specified language above
        - Do not mix languages or use any other language
        - Use appropriate terminology and expressions for the target language
        - Maintain the same level of detail and structure regardless of language

        Provide detailed, practical guidance for the {stage} stage of maize farming.
        Make it specific, actionable, and suitable for smallholder farmers.

        Focus on:
        - Best practices and techniques
        - Common mistakes to avoid
        - Signs of problems to watch for
        - Approximate costs and timelines
        - Local adaptation tips for African farming conditions

        Keep the response under 1500 words.
        Stage: {stage}
        Guidance needed: {stage_prompts.get(stage, 'General maize farming guidance')}
        """

        try:
            # Use direct Gemini API (following working Streamlit pattern)
            response = self.model.generate_content(prompt)
            return {
                'success': True,
                'content': response.text,
                'type': 'stage_guide',
                'stage': stage
            }
        except Exception as e:
            error_msg = str(e).lower()
            if 'timeout' in error_msg or 'connection' in error_msg or 'network' in error_msg:
                user_friendly_error = 'Connection timeout. Check your internet connection and try again.'
            elif 'quota' in error_msg or 'rate limit' in error_msg:
                user_friendly_error = 'API quota exceeded. Please try again later.'
            elif 'invalid' in error_msg or 'unauthorized' in error_msg:
                user_friendly_error = 'API key issue. Please check your GEMINI_API_KEY configuration.'
            else:
                user_friendly_error = f'AI service temporarily unavailable: {str(e)}'

            return {
                'success': False,
                'error': user_friendly_error,
                'stage': stage,
                'fallback_content': self._get_stage_fallback(stage, language)
            }

    def _answer_question(self, question, language='en'):
        """Answer specific farming questions using conversational AI"""

        # Check if API is available
        if not self.api_available or not self.model:
            return {
                'success': False,
                'error': 'Gemini API not configured. Please set GEMINI_API_KEY in .env file.',
                'question': question,
                'fallback_content': self._get_question_fallback(question, language)
            }

        language_instruction = self.get_language_instruction(language)

        context_prompt = f"""
        You are a knowledgeable agricultural extension officer helping maize farmers.
        {language_instruction}

        IMPORTANT: You must follow these language rules strictly:
        - Respond only in the specified language above
        - Do not mix languages or use any other language
        - Use appropriate terminology and expressions for the target language
        - Maintain the same level of detail and structure regardless of language

        Answer the farmer's question: "{question}"

        Guidelines:
        - Be practical and specific
        - Use simple, clear language
        - Include local context where relevant (Africa-focused)
        - Suggest affordable, accessible solutions
        - If recommending products, suggest local alternatives
        - Include preventive measures
        - Mention when to seek professional help

        Keep the response under 1000 words.
        Provide actionable advice based on proven agricultural practices.
        """

        try:
            # Use direct Gemini API (following working Streamlit pattern)
            response = self.model.generate_content(context_prompt)
            return {
                'success': True,
                'content': response.text,
                'type': 'question_answer',
                'question': question
            }
        except Exception as e:
            error_msg = str(e).lower()
            if 'timeout' in error_msg or 'connection' in error_msg or 'network' in error_msg:
                user_friendly_error = 'Connection timeout. Check your internet connection and try again.'
            elif 'quota' in error_msg or 'rate limit' in error_msg:
                user_friendly_error = 'API quota exceeded. Please try again later.'
            elif 'invalid' in error_msg or 'unauthorized' in error_msg:
                user_friendly_error = 'API key issue. Please check your GEMINI_API_KEY configuration.'
            else:
                user_friendly_error = f'AI service temporarily unavailable: {str(e)}'

            return {
                'success': False,
                'error': user_friendly_error,
                'question': question,
                'fallback_content': self._get_question_fallback(question, language)
            }

    def _get_fallback_guide(self, language='en'):
        """Fallback maize guide if AI fails"""

        if language == 'ha':
            return """
# Jagorar Noman Masara Cikakke

## 1. Shirye-shiryen ƙasa
- Tsaftace ƙasa daga ciyawa da ragowar amfanin gona
- Fasa ko juyar da ƙasa zuwa zurfin 15-20 cm
- Bar ƙasa ta huta na tsawon makonni 2-3 kafin shuka
- Gwada pH na ƙasa (matsayi mafi kyau: 5.5-7.0) da ingancin ƙasa

## 2. Zaɓin iri & Shuka
- Zaɓi iri masu inganci da juriya ga cututtuka
- Shuka a lokacin damina (Maris-Mayu a Najeriya)
- Tazara: 75cm tsakanin layuka, 25cm tsakanin tsire-tsire
- Shuka iri 2-3 a kowane rami, bar 1 bayan sun fito
- Zurfin shuka: 3-5 cm

## 3. Amfani da Taki
- Yi amfani da NPK 15:15:15 lokacin shuka (50kg kowace eka)
- Kara urea bayan makonni 4-6 (25kg kowace eka)
- Yi amfani da taki lokacin tsire-tsire sun kai gwiwa
- Yi ruwa sosai bayan amfani da taki

## 4. Sarrafa Ciyawa
- Yi waƙa ta farko: makonni 2-3 bayan shuka
- Ta biyu: makonni 6-8 bayan shuka
- Yi amfani da lauje ko cire ciyawa da hannu
- Sa mulch don rage ciyawa

## 5. Sarrafa Kwari & Cututtuka
- Duba gonar akai-akai don kwari (soja, masu huda ganga)
- Yi amfani da maganin neem don kwari masu laushi
- Cire da ƙone tsire-tsiren da suka kamu da cuta
- Yi jujjuyawar amfanin gona

## 6. Ban Ruwa
- Masara na bukatar ruwa 500-800mm a lokacin girma
- Yi ruwa duk bayan kwanaki 7-10 idan ba ruwa
- Guji ruwa mai yawa da ke jawo toshewar ƙasa
- Lokaci mafi kyau: safiya ko yamma

## 7. Girbi
- Girba idan ganyen masara sun bushe (kwanaki 90-120 daga shuka)
- Yanke tsire-tsire daga ƙasa
- Bar masara ta bushe a fili na makonni 2-3
- Fara fitar da hatsi idan danshi ya kai 12-15%

## 8. Bayan Girbi
- Ajiye a wuri mai tsabta, bushe, da iska
- Yi amfani da kwantena masu rufewa don hana kwari
- Ware da tantance don samun farashi mai kyau
- Yi la’akari da sayarwa ga kungiyoyi ko masu siye kai tsaye

## Kurakurai da a guje wa su
- Shuka da wuri ko da jinkiri
- Yin taki da yawa ko kadan
- Rashin sarrafa ciyawa yadda ya kamata
- Rashin lura da kwari
- Ajiya mara kyau da ke jawo asara
"""
        else:
            return """
# Complete Maize Farming Guide

## 1. Land Preparation
- Clear the land of weeds and previous crop residues
- Plow or till the soil to a depth of 15-20 cm
- Allow 2-3 weeks for soil to settle before planting
- Test soil pH (ideal: 5.5-7.0) and fertility

## 2. Seed Selection & Planting
- Choose certified, disease-resistant maize varieties
- Plant during rainy season (March-May in Nigeria)
- Spacing: 75cm between rows, 25cm between plants
- Plant 2-3 seeds per hole, thin to 1 after germination
- Planting depth: 3-5 cm

## 3. Fertilizer Application
- Apply NPK 15:15:15 at planting (50kg per acre)
- Top-dress with urea after 4-6 weeks (25kg per acre)
- Apply when plants are knee-high
- Water in fertilizers well

## 4. Weed Management
- First weeding: 2-3 weeks after planting
- Second weeding: 6-8 weeks after planting
- Use hoe or manual weeding
- Apply mulch to suppress weeds

## 5. Pest & Disease Control
- Monitor regularly for pests (armyworm, stalk borer)
- Use neem spray for soft-bodied insects
- Remove and destroy diseased plants
- Practice crop rotation

## 6. Irrigation
- Maize needs 500-800mm water during growing season
- Water every 7-10 days if no rain
- Avoid waterlogging
- Best time: early morning or evening

## 7. Harvesting
- Harvest when husks are dry (90-120 days from planting)
- Cut stalks at ground level
- Dry cobs in field for 2-3 weeks
- Shell when moisture content is 12-15%

## 8. Post-Harvest
- Store in clean, dry, well-ventilated place
- Use airtight containers to prevent pests
- Sort and grade for better market prices
- Consider selling to cooperatives or direct buyers

## Common Mistakes to Avoid
- Planting too early or too late
- Over-fertilizing or under-fertilizing
- Poor weed control
- Inadequate pest monitoring
- Improper storage leading to losses
"""

    def _get_stage_fallback(self, stage, language='en'):
        """Get fallback content for specific farming stages"""

        hausa_fallbacks = {
            'land_preparation': """
## Shirye-shiryen ƙasa don Masara
- Tsaftace duk ciyawa da ragowar amfanin gona
- Fasa ƙasa zuwa zurfin 15-20cm
- Fasa manyan ƙwarya na ƙasa
- Bar ƙasa ta huta na makonni 2-3 kafin shuka
- Gwada pH na ƙasa idan zai yiwu (5.5-7.0)
- Kara taki ko kashin dabbobi idan ƙasa ba ta da kyau
""",
            'planting': """
## Jagorar Shuka Masara
- Shuka a farkon damina (Maris-Mayu)
- Yi amfani da iri masu juriya ga cututtuka
- Shuka iri 2-3 a kowane rami, zurfi 3-5cm
- Tazara: 75cm tsakanin layuka, 25cm tsakanin tsire-tsire
- Bar tsiro 1 a kowane rami bayan sun fito
- Shuka a cikin rukuni don samun kyakkyawan pollination
""",
            'fertilizer': """
## Amfani da Taki
- Yi amfani da NPK 15:15:15 lokacin shuka (50kg kowace eka)
- Kara urea bayan makonni 4-6 (25kg kowace eka)
- Yi taki lokacin tsire-tsire sun kai gwiwa
- Yi ruwa bayan amfani da taki
- Gwada ƙasa akai-akai don guje wa yin taki da yawa
""",
            'weed_control': """
## Sarrafa Ciyawa
- Waƙa ta farko: makonni 2-3 bayan shuka
- Ta biyu: makonni 6-8 bayan shuka
- Yi amfani da lauje ko cire ciyawa da hannu
- Sa mulch a kusa da tsire-tsire
- Kada a bar ciyawa ta yi furanni
- Yi waƙa da safe lokacin tsire-tsire suna da ƙarfi
""",
            'pest_control': """
## Sarrafa Kwari
- Duba tsire-tsire kullum don alamun kwari
- Yi amfani da maganin neem don kwari masu laushi
- Cire da hannu kwari kamar soja da masu huda ganga
- Yi jujjuyawar amfanin gona don karya zagayowar kwari
- Kawo kwari masu amfani kamar ladybug
- Cire da ƙone tsire-tsiren da suka kamu sosai
""",
            'irrigation': """
## Jagorar Ban Ruwa
- Yi ruwa duk bayan kwanaki 7-10 a lokacin fari
- Masara na bukatar ruwa 500-800mm a lokacin girma
- Yi ruwa da safe ko yamma
- Guji ruwa mai yawa da ke jawo toshewar ƙasa
- Yi amfani da furrow ko drip irrigation idan zai yiwu
- Duba danshin ƙasa akai-akai
"""
        }

        english_fallbacks = {
            'land_preparation': """
## Land Preparation for Maize
- Clear all weeds and old crop debris
- Plow the soil to 15-20cm depth
- Break up large soil clumps
- Wait 2-3 weeks before planting to let soil settle
- Test soil pH if possible (should be 5.5-7.0)
- Add organic matter if soil is poor
""",
            'planting': """
## Maize Planting Guide
- Plant during early rainy season (March-May)
- Use certified seeds resistant to local diseases
- Plant 2-3 seeds per hole, 3-5cm deep
- Space holes 75cm apart in rows, 25cm between rows
- Thin to 1 plant per hole after germination
- Plant in blocks rather than single rows for better pollination
""",
            'fertilizer': """
## Fertilizer Application
- Apply NPK 15:15:15 at planting (50kg per acre)
- Side-dress with urea 4-6 weeks after planting (25kg per acre)
- Apply fertilizers when plants are knee-high
- Water immediately after applying fertilizers
- Test soil regularly to avoid over-fertilization
""",
            'weed_control': """
## Weed Management
- First weeding: 2-3 weeks after planting
- Second weeding: 6-8 weeks after planting
- Use hand hoeing or manual weeding
- Apply organic mulch around plants
- Never let weeds flower and produce seeds
- Weed early in the morning when plants are turgid
""",
            'pest_control': """
## Pest Control
- Monitor plants daily for pest signs
- Use neem oil spray for aphids and mites
- Hand-pick caterpillars and armyworms
- Practice crop rotation to break pest cycles
- Introduce beneficial insects like ladybugs
- Remove and burn heavily infested plants
""",
            'irrigation': """
## Irrigation Guide
- Water every 7-10 days during dry spells
- Provide 500-800mm water during growing season
- Water early morning or late evening
- Avoid waterlogging which causes root rot
- Use furrows or drip irrigation if possible
- Monitor soil moisture regularly
"""
        }

        if language == 'ha':
            return hausa_fallbacks.get(stage, "Ba a samu jagorar wannan mataki a Hausa ba.")
        else:
            return english_fallbacks.get(stage, "General maize farming guidance not available offline.")

    def _get_question_fallback(self, question, language='en'):
        """Get fallback answer for questions"""
        question_lower = question.lower()

        if language == 'ha':
            if 'weed' in question_lower or 'weeding' in question_lower or 'ciyawa' in question_lower:
                return """
## Shawarwari kan Ciyawa:
- Yi waƙa na farko makonni 2-3 bayan shuka, na biyu makonni 6-8 bayan shuka
- Yi amfani da lauje don guje wa lalata tushen masara
- Cire ciyawa kafin su fara fure don hana yaduwa
- Sa mulch a kusa da tsire-tsire don rage ciyawa
- Yi waƙa da safe lokacin tsire-tsire suna da ƙarfi
"""
            elif 'pest' in question_lower or 'insect' in question_lower or 'kwari' in question_lower:
                return """
## Shawarwari kan Kwari:
- Duba tsire-tsire kullum don alamun kwari
- Yi amfani da maganin neem don kwari masu laushi
- Cire da hannu manyan kwari kamar soja da masu huda ganga
- Yi jujjuyawar amfanin gona don karya zagayowar kwari
- Cire da ƙone sassan tsire-tsiren da suka kamu sosai
"""
            elif 'fertilizer' in question_lower or 'fertiliser' in question_lower or 'taki' in question_lower:
                return """
## Shawarwari kan Taki:
- Yi amfani da NPK 15:15:15 lokacin shuka (50kg kowace eka)
- Kara urea a matsayin taki bayan makonni 4-6 bayan shuka
- Yi ruwa bayan amfani da taki
- Gwada ƙasa don sanin irin taki da ake bukata
- Guji yin taki da yawa da ke iya ƙone tsire-tsire
"""
            else:
                return """
## Shawarwari na Gaba ɗaya:
- Duba amfanin gona kullum don canje-canje
- Rubuta kwanan wata da duk abin da aka yi a gona
- Kiyaye tazara tsakanin tsire-tsire don samun iska
- Yi ruwa akai-akai amma guji ruwa mai yawa
- Tuntubi jami’in noman ƙasa don ƙarin shawarwari
"""
        else:
            if 'weed' in question_lower or 'weeding' in question_lower:
                return """
## Weeding Advice:
- Weed 2-3 weeks after planting and again at 6-8 weeks
- Use hand hoeing to avoid damaging maize roots
- Remove weeds before they flower to prevent seed production
- Apply mulch around plants to suppress weed growth
- Weed early morning when plants are strong
"""
            elif 'pest' in question_lower or 'insect' in question_lower:
                return """
## Pest Control Advice:
- Check plants daily for signs of pests
- Use neem oil spray for soft-bodied insects
- Hand-pick large caterpillars and beetles
- Practice crop rotation to break pest life cycles
- Remove and destroy heavily infested plant parts
"""
            elif 'fertilizer' in question_lower or 'fertiliser' in question_lower:
                return """
## Fertilizer Advice:
- Apply NPK 15:15:15 at planting (50kg per acre)
- Add urea as top-dressing 4-6 weeks after planting
- Water immediately after applying fertilizers
- Test soil to determine specific nutrient needs
- Avoid over-fertilization which can burn plants
"""
            else:
                return """
## General Farming Advice:
- Monitor your crops daily for any changes
- Keep good records of planting dates and treatments
- Maintain proper plant spacing for good air circulation
- Water consistently but avoid waterlogging
- Consult local agricultural extension officers for specific advice
"""

# Global instance
farming_assistant = FarmingAssistant()