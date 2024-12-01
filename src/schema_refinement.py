import google.generativeai as genai

# Set your Gemini API key
genai.configure(api_key="AIzaSyCtwToVA60UQpJpa1BrHHGxxoxcoSNBBbM")

def refine_schema(entities, relationships):
    """Refine the schema using Google's Gemini API."""
    prompt = f"""
    Detected Entities: {entities}
    Detected Relationships: {relationships}
    Please suggest improvements or additions to the schema.
    """
    
    # Generating content using Gemini model
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    
    # Returning the refined schema as a response
    return response.text
