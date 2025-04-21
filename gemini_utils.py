import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

genai.configure(api_key=GEMINI_API_KEY)

def get_gemini_model():
    """Get the Gemini model for text generation"""
    return genai.GenerativeModel('gemini-2.0-flash')

def improve_text(text):
    """
    Analyze and improve text using Gemini API.
    
    Args:
        text: Full text
        
    Returns:
        Improved text
    """
    model = get_gemini_model()
    
    prompt = f"""
        You will receive a text at the end of this prompt.

        Revise the text to improve clarity, conciseness, professionalism and scientific rigor, 
        while maintaining the original meaning. Ensure correct grammar, appropriate word choice, and smooth flow. Do not add new information.

        For Spanish texts, use formal vocabulary and phrasing typical of Chilean Spanish. 
        Avoid slang or informal expressions, but strictly preserve Chilean Spanish localisms and standard vocabulary. 
        Do not replace words that are common and accepted in formal Chilean Spanish with terms from other Spanish-speaking regions. 
        For example, retain words such as 'auto', 'papa', 'maní', and 'palta', 
        as these are standard in Chile and should not be changed to 'carro', 'patata', 'cacahuete', or 'aguacate' respectively.

        For English texts, prefer US English.
        For German texts, prefer German from Germany.

        The intended output is the revised text in the same language as the original. 
        If the text includes some foreign words, leave them there, as it was probably intended that way.

        The text will be pasted below the hyphens:
        --------
        {text}
        """

    try:
        response = model.generate_content(prompt)
        improved_text = response.text.strip()
        
        # If the response is empty or an error occurred, keep the original
        if not improved_text:
            improved_text = text
    except Exception as e:
        print(f"Error improving text: {e}")
        # In case of error, keep the original text

    return improved_text