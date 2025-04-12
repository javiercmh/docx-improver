import docx
import re # Import the regular expression module
from docx.shared import RGBColor

def extract_text_from_docx(file_path):
    """
    Extract text content from a DOCX file.
    Returns the full text as a single string.
    """
    try:
        doc = docx.Document(file_path)
        paragraphs_text = [para.text for para in doc.paragraphs if para.text.strip()]
        return '\n'.join(paragraphs_text)
    except Exception as e:
        print(f"Error reading DOCX file {file_path}: {e}")
        raise # Re-raise the exception to be handled upstream

def create_improved_docx(improved_text, output_path):
    """
    Create a new DOCX file by parsing the improved text with Gemini markup
    (~~deleted~~**inserted**) and applying formatting.
    """
    doc = docx.Document()
    changes_count = 0 # Initialize changes count

    # Add a title
    title = doc.add_heading('Improved Document', 0)
    title.alignment = 1  # Center alignment

    # Add a brief explanation
    explanation = doc.add_paragraph()
    explanation.add_run('This document has been improved by Gemini AI. ').bold = True
    explanation.add_run('Deletions are shown in ').bold = True
    red_text = explanation.add_run('red strikethrough')
    red_text.font.color.rgb = RGBColor(255, 0, 0)
    red_text.font.strike = True
    red_text.bold = True
    explanation.add_run(', and additions are shown in ').bold = True
    blue_text = explanation.add_run('blue bold') # Changed from underline for clarity, adjust as needed
    blue_text.font.color.rgb = RGBColor(0, 0, 255)
    blue_text.bold = True
    explanation.add_run('.').bold = True

    # Add a separator
    doc.add_paragraph('─' * 50)

    # Regex to find the Gemini markup: ~~deleted~~**inserted**
    # It captures the deleted part (group 1) and the inserted part (group 2)
    pattern = re.compile(r'~~\s*(.*?)\s*~~\s*\*\*\s*(.*?)\s*\*\*')

    # Process the improved text paragraph by paragraph (split by newline)
    # This assumes Gemini preserves paragraph breaks reasonably well.
    original_paragraphs_count = 0 # Count paragraphs processed
    for paragraph_text in improved_text.split('\n'):
        if not paragraph_text.strip(): # Handle potentially empty lines
            continue

        original_paragraphs_count += 1
        para = doc.add_paragraph()
        last_end = 0 # Keep track of the end position of the last match

        print(f"Processing paragraph: {paragraph_text}")
        # Find all matches in the current paragraph text
        matches = list(pattern.finditer(paragraph_text))
        print(f"Matches found: {len(matches)}")
        if not matches:
            # No changes in this paragraph, add as is
            para.add_run(paragraph_text)
        else:
            # Process text segments and changes
            for match in matches:
                start, end = match.span()
                deleted_text = match.group(1)
                inserted_text = match.group(2)
                changes_count += 1 # Count each replacement as one change

                # Add the text before the current match
                if start > last_end:
                    para.add_run(paragraph_text[last_end:start])

                # Add the deleted text with strikethrough and red color
                if deleted_text: # Only add if there was deleted text
                    del_run = para.add_run(deleted_text)
                    del_run.font.strike = True
                    del_run.font.color.rgb = RGBColor(255, 0, 0)

                # Add the inserted text with bold and blue color
                if inserted_text: # Only add if there was inserted text
                    ins_run = para.add_run(inserted_text)
                    ins_run.font.bold = True
                    ins_run.font.color.rgb = RGBColor(0, 0, 255)

                last_end = end # Update the position for the next segment

            # Add any remaining text after the last match
            if last_end < len(paragraph_text):
                para.add_run(paragraph_text[last_end:])

    # Add a summary at the end
    doc.add_paragraph('─' * 50)
    summary = doc.add_paragraph()
    summary.add_run(f'Summary: Gemini AI suggested {changes_count} changes across {original_paragraphs_count} processed paragraphs.').bold = True

    # Save the document
    try:
        doc.save(output_path)
        return changes_count, original_paragraphs_count
    except Exception as e:
        print(f"Error saving DOCX file {output_path}: {e}")
        raise # Re-raise the exception


if __name__ == "__main__":
    import os
    filepath = "uploads/052647b5-186e-4fc0-8697-7c6426907e5a_documento.docx"
    original_text = extract_text_from_docx(filepath)
    improved_text = """El sol salió anoche y iluminó toda la oscuridad. Los pájaros ladraban alegremente mientras los gatos volaban por el cielo azul. Era un día tan tranquilo que hasta el ruido ensordecedor era silencioso. Decidí desayunar una cena de tres platos antes de irme a dormir al trabajo de la mañana.
Mi coche nuevo es más viejo que mi abuelo, pero aún así tiene menos kilómetros porque nunca lo he conducido. Ayer fui a la tienda de la esquina que está a cinco horas en coche y compré leche cuadrada y pan líquido. El dependiente me dijo que eran artículos muy populares y que siempre se agotaban rápidamente, especialmente los plátanos verdes maduros.
Si llueve, entonces el suelo estará seco. Hoy no está lloviendo, por lo tanto, el suelo está mojado. Esta es una conclusión lógica y evidente para cualquiera con un poco de sentido común. Además, todos sabemos que los peces viven en los árboles y los pájaros nadan en el océano, es biología básica.
Ayer vi un fantasma invisible que era completamente transparente, excepto por sus brillantes colores fosforescentes. Me dijo que venía del futuro pasado y que el agua hierve a cero grados. Fue una conversación muy normal y para nada extraña. Después, el fantasma se materializó en una estatua de piedra que flotaba en el aire.
El sol ~~salió anoche~~ **se puso anoche** e iluminó toda la oscuridad. Los pájaros ~~ladraban~~ **cantaban** alegremente mientras los gatos ~~volaban~~ **corrían** por el cielo azul. Era un día tan tranquilo que hasta el ruido ~~ensordecedor~~ **intenso** era silencioso. Decidí desayunar una cena de tres platos antes de ~~irme a dormir al~~ **ir al** trabajo de la mañana.

Mi coche nuevo es más viejo que mi abuelo, pero aún así tiene menos kilómetros porque nunca lo he conducido. Ayer fui a la tienda de la esquina que está a cinco horas en coche y compré leche cuadrada y pan líquido. El dependiente me dijo que eran artículos muy populares y que siempre se agotaban rápidamente, especialmente los plátanos verdes maduros.

Si llueve, entonces el suelo estará seco. Hoy no está lloviendo, por lo tanto, el suelo está mojado. Esta es una conclusión lógica y evidente para cualquiera con un poco de sentido común. Además, todos sabemos que los peces viven en los árboles y los pájaros nadan en el océano, es biología básica.

Ayer vi un fantasma invisible que era completamente transparente, excepto por sus brillantes colores fosforescentes. Me dijo que venía del futuro pasado y que el agua hierve a cero grados. Fue una conversación muy normal y ~~para nada extraña~~ **nada extraña**. Después, el fantasma se materializó en una estatua de piedra que flotaba en el aire."""
    
    output_path = "processed/improved_document.docx"
    
    try:
        changes_count = create_improved_docx(improved_text, output_path)
    except Exception as e:
        print(f"An error occurred during the test: {e}")
        
    print("Direct test finished.")