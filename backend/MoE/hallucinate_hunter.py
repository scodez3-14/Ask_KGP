import json

def detect_hallucinations(chunks, answer, client):
    """
    Role: Hallucination Hunter
    Specifically hunts for 'Invented Entities' (Names, Dates, Stats).
    """
    context = "\n".join([c['text'] for c in chunks])
    
    prompt = f"""
    You are a Hallucination Hunter. Compare the Entities in the Answer vs the Context.
    
    CONTEXT: {context}
    ANSWER: {answer}

    Find any names, dates, or numbers in the Answer that do NOT appear in the Context.
    Return JSON:
    {{
        "hallucinations_found": true/false,
        "invented_details": ["name X", "date Y"],
        "severity": "high/low"
    }}
    """
    
    res = client.chat.completions.create(
        model="xiaomi/mimo-v2-flash:free",
        messages=[{"role": "user", "content": prompt}],
        response_format={ "type": "json_object" }
    )
    return json.loads(res.choices[0].message.content)