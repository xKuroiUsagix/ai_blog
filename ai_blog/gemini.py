import google.generativeai as genai

from ai_blog.settings import GEMINI_API_KEY, GEMINI_MODEL_NAME


genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel(model_name=GEMINI_MODEL_NAME)
