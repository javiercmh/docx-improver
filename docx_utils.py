import re
import docx
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
    (~~deleted~~**inserted**, **added**, word**suffix**) and applying formatting.
    """
    doc = docx.Document()
    changes_count = 0 # Initialize changes count
    original_paragraphs_count = 0 # Count paragraphs processed

    # --- Document Header ---
    title = doc.add_heading('Improved Document', 0)
    title.alignment = 1  # Center alignment
    explanation = doc.add_paragraph()
    explanation.add_run('This document has been improved by Gemini AI. ').bold = True
    explanation.add_run('Deletions are shown in ').bold = True
    red_text = explanation.add_run('red strikethrough')
    red_text.font.color.rgb = RGBColor(255, 0, 0)
    red_text.font.strike = True
    red_text.bold = True
    explanation.add_run(', and additions/corrections are shown in ').bold = True # Updated text
    blue_text = explanation.add_run('blue bold')
    blue_text.font.color.rgb = RGBColor(0, 0, 255)
    blue_text.bold = True
    explanation.add_run('.').bold = True
    doc.add_paragraph('─' * 50) # Separator

    # --- Regex Patterns ---
    delete_insert_pattern = r'~~\s*(?P<deleted>.*?)\s*~~\s*\*\*\s*(?P<inserted>.*?)\s*\*\*'
    bold_pattern = r'\*\*(?P<bolded>.*?)\*\*'
    inline_bold_pattern = r'(?P<wordbase>\w+)\*\*(?P<suffix>\w+)\*\*'  # example: word**suffix**

    # Combine patterns - Order can matter if patterns overlap significantly.
    combined_pattern_regex = f"({delete_insert_pattern})|({bold_pattern})|({inline_bold_pattern})"
    pattern = re.compile(combined_pattern_regex)

    # --- Process Paragraphs ---
    for paragraph_text in improved_text.split('\n'):
        if not paragraph_text.strip(): # Handle potentially empty lines
            # Add blank paragraph for spacing if needed (and not at the start)
            if original_paragraphs_count > 0:
                doc.add_paragraph()
            continue # Skip processing this empty line

        original_paragraphs_count += 1
        para = doc.add_paragraph()
        last_end = 0 # Keep track of the end position of the last match
        matches = list(pattern.finditer(paragraph_text))

        if not matches:
            # No changes in this paragraph, add as is
            para.add_run(paragraph_text)
        else:
            # Process text segments and changes
            for match in matches:
                start, end = match.span()
                # Add the text before the current match
                if start > last_end:
                    preceding_text = paragraph_text[last_end:start]
                    para.add_run(preceding_text)

                # --- Check named groups to determine formatting ---
                deleted_text = match.group('deleted')
                inserted_text = match.group('inserted')
                bolded_text = match.group('bolded')
                wordbase_text = match.group('wordbase')
                suffix_text = match.group('suffix')

                # --- Apply formatting based on which group matched ---
                if deleted_text is not None or inserted_text is not None:
                    # It's a delete/insert match
                    changes_count += 1
                    if deleted_text:
                        del_run = para.add_run(deleted_text)
                        del_run.font.strike = True
                        del_run.font.color.rgb = RGBColor(255, 0, 0)
                    if inserted_text:
                        ins_run = para.add_run(inserted_text)
                        ins_run.font.bold = True
                        ins_run.font.color.rgb = RGBColor(0, 0, 255)

                elif bolded_text is not None:
                    # It's a standalone bold pattern match (an addition)
                    changes_count += 1
                    bold_run = para.add_run(bolded_text)
                    bold_run.font.bold = True
                    bold_run.font.color.rgb = RGBColor(0, 0, 255) # Use blue bold

                elif wordbase_text is not None and suffix_text is not None:
                    # It's an inline bold pattern match (e.g., word**suffix**)
                    changes_count += 1
                    # Add the base part normally
                    para.add_run(wordbase_text)
                    # Add the suffix part with formatting
                    suffix_run = para.add_run(suffix_text)
                    suffix_run.font.bold = True
                    suffix_run.font.color.rgb = RGBColor(0, 0, 255) # Use blue bold
                last_end = end # Update the position for the next segment

            # Add any remaining text after the last match
            if last_end < len(paragraph_text):
                remaining_text = paragraph_text[last_end:]
                para.add_run(remaining_text)

    # --- Document Footer ---
    doc.add_paragraph('─' * 50)
    summary = doc.add_paragraph()
    summary.add_run(f'Summary: Gemini AI suggested {changes_count} changes across {original_paragraphs_count} processed paragraphs.').bold = True

    # --- Save Document ---
    try:
        doc.save(output_path)
        # Return counts for potential use in the Flask app
        return changes_count, original_paragraphs_count
    except Exception as e:
        print(f"Error saving DOCX file {output_path}: {e}")
        raise # Re-raise the exception


# --- Updated Test Block ---
if __name__ == "__main__":
    import os
    print("Running docx_utils directly for testing...")

    # Define a sample text with all markup types
    sample_improved_text = """Propuesta de Negocio: **Comercialización de Paltas y Cervezas Pequeñas**
Estimados Señores: Les presentamos una **oportunidad de negocio** que es ~~la monda~~**sumamente atractiva**. ¿Se ~~imajinan~~**imaginan** poder ofrese**r** a sus clientes?

El sol ~~salió anoche~~ **se puso anoche** e iluminó toda la oscuridad. Los pájaros ~~ladraban~~ **cantaban** alegremente mientras los gatos ~~volaban~~ **corrían** por el cielo azul. Era un día tan tranquilo que hasta el ruido ~~ensordecedor~~ **intenso** era silencioso. Decidí desayunar una cena de tres platos antes de ~~irme a dormir al~~ **ir al** trabajo de la mañana.

Ayer vi un fantasma invisible que era completamente transparente, excepto por sus brillantes colores fosforescentes. Me dijo que venía del futuro pasado y que el agua hierve a cero grados. Fue una conversación muy normal y ~~para nada extraña~~ **nada extraña**. Después, el fantasma se materializó en una estatua de piedra que flotaba en el aire.

This show**s** an inline English correction. It also ~~demonstrates~~**shows** a block change."""

    # Define where to save the test output file
    test_output_filename = "processed/direct_test_output_all_formats.docx"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_output_path = os.path.join(script_dir, test_output_filename)

    # Call the function to create the document
    try:
        # Capture the return values even in the test
        num_changes, num_paras = create_improved_docx(sample_improved_text, test_output_path)
        print(f"Test document created at: {test_output_path}")
        print(f"Detected {num_changes} changes across {num_paras} paragraphs.")
    except Exception as e:
        print(f"An error occurred during the test: {e}")

    print("Direct test finished.")
# --- End of the test block ---