import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

def improve_text(text):
    """
    Analyze and improve text using Gemini API.
    
    Args:
        text: Full text
        
    Returns:
        Improved text
    """
    logger.info("Improving text using Gemini API")
    model = genai.GenerativeModel('gemini-2.0-flash')
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
        logger.error(f"Error improving text: {e}")
        # In case of error, keep the original text
        improved_text = text

    return improved_text

if __name__ == "__main__":
    # Test the improve_text function with a sample text
    sample_text = """This is a sampae text not very weill wrotten. I t contain errors and the flow is not good.
    It would be very nice to fix those problems so that in the end the documentis is more clearer and professionaller.
"""
    improved_text = improve_text(sample_text)
    print("Original Text:", sample_text)
    print("Improved Text:", improved_text)