import json

def verify_grounding(question, chunks, answer, client):
    """
    Role: Source Matcher
    Checks if every part of the answer can be traced back to the chunks.
    """
    context = "\n\n".join([f"Chunk {i}: {c['text']}" for i, c in enumerate(chunks)])
    
    prompt = f"""
    You are a Source Matcher. Your only job is to check if the provided answer is strictly 
    supported by the chunks.

    CHUNKS:
    {context}

    ANSWER:
    {answer}

    TASK:
    Identify any sentence in the ANSWER that is NOT supported by the CHUNKS.
    Return JSON only:
    {{
        "grounded": true/false,
        "unsupported_claims": ["claim 1", "claim 2"],
        "reasoning": "string"
    }}
    """
    
    res = client.chat.completions.create(
        model="xiaomi/mimo-v2-flash:free",
        messages=[{"role": "user", "content": prompt}],
        response_format={ "type": "json_object" }
    )
    return json.loads(res.choices[0].message.content)