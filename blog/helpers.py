from google.generativeai.types import HarmCategory, HarmBlockThreshold, BlockedReason

from ai_blog.gemini import ai_model

from .constants import MAX_COMMENT_LENGTH


def get_ai_response(content):
    limit = int(MAX_COMMENT_LENGTH / 2)
    return ai_model.generate_content(f'Reply to this comment using less than {limit} symbols: {content}').text

def ai_verify_safety(content):
    response = ai_model.generate_content(
        f'Is this text save to public: {content}',
        safety_settings= {
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE
        }
    )

    if response.candidates[0].finish_reason == BlockedReason.SAFETY:
        return False
    return True
