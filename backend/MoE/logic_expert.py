import json

def audit_logic(chunks, answer, client):
    """
    Role: Logic Expert
    Checks if the relationship logic in the answer follows from the chunks.
    """
    context = "\n".join([c['text'] for c in chunks])
    
    prompt = f"""
    You are a Logic Expert. Audit the relationships described in the answer.
    
    CONTEXT: {context}
    ANSWER: {answer}

    Does the conclusion in the answer follow logically from the premises in the context?
    Example Error: Context says 'A works for B', but Answer says 'B works for A'.
    
    Return JSON:
    {{
        "logic_valid": true/false,
        "fallacies": ["description of logical error"],
        "confidence_score": 0.0-1.0
    }}
    """
    
    res = client.chat.completions.create(
        model="xiaomi/mimo-v2-flash:free",
        messages=[{"role": "user", "content": prompt}],
        response_format={ "type": "json_object" }
    )
    return json.loads(res.choices[0].message.content)