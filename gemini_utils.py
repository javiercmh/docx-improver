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

def analyze_and_improve_text(text):
    """
    Analyze and improve text using Gemini API.
    
    Args:
        text: Full text
        
    Returns:
        Improved text
    """
    model = get_gemini_model()
    
    prompt = f"""Please refine the following text for clarity, conciseness, and professionalism, ensuring a business-oriented style suitable for either United States English or Chilean Spanish, depending on the language of the source document. Ensure accurate grammar and spelling, improved word choice, and enhanced flow, while preserving the original meaning and avoiding the addition of new information.

When refining Spanish text, **prioritize formal vocabulary and phrasing commonly understood and used in a professional context in Chile.** Specifically, replace words that are common in other Spanish-speaking regions but less so or not used in Chile with their formal Chilean equivalents (e.g., replace "aguacate" with "palta," "coche" with "auto," "caña" [for small beer] with "cerveza pequeña," "guay" with "excelente" or "positivo," "piso" with "departamento," etc.). Avoid informal or slang terms.

Similarly, when refining English text, prioritize formal vocabulary and phrasing common in the United States over other regional variations, avoiding slang or overly casual language.

Return only one revised text in the same language as the original, clearly indicating all changes made using the following convention:

* **Typographical errors:** Enclose the incorrect word in double tildes (~~) and immediately follow it with the corrected word in bold (**). For example: ~~imajinan~~**imaginan** or ~~teh~~**the**.
* **Word choice and conciseness improvements (including regional vocabulary replacements):** Enclose the original word(s) in double tildes (~~) and immediately follow it with the improved word(s) in bold (**). For example: ~~es la monda~~**es atractiva** or ~~aguacates~~**paltas** or ~~uses its legs to~~**jumps**.
* **Grammatical corrections (excluding typos and word choice):** Indicate the change directly within the word if possible (e.g., ofrese**r**, jump**s**). If the change involves adding or removing words for grammatical correctness, use the double tilde and bold convention as described above.

Text to improve: <input>{text}</input>"""

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