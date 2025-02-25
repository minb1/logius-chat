def create_prompt(query, context, chat_history=""):
    """
    Create a prompt for the LLM by combining the user query with retrieved context and chat history.
    
    Args:
        query (str): The user's original query
        context (str): The context retrieved from similar documents
        chat_history (str): The formatted chat history
        
    Returns:
        str: The formatted prompt
    """
    prompt = f"""
Beantwoord de volgende vraag op basis van de verstrekte context.
Geef een zo volledig en nauwkeurig mogelijk antwoord. 
Let op technische details.

{chat_history}

**Vraag:** {query}

**Context:** {context}

Antwoord in het Nederlands.
"""
    return prompt 