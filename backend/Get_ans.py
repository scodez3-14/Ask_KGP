import json, os
from openai import OpenAI
from dotenv import load_dotenv
from ask_wiki import ask_question

# Import experts
from MoE.Source_master import verify_grounding
from MoE.hallucinate_hunter import detect_hallucinations
from MoE.logic_expert import audit_logic

load_dotenv()
ai_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

def get_verified_answer(question, chunks):

    # Create a highly structured context for the LLM
    context_list = []
    for i, c in enumerate(chunks):
        structured_chunk = (
            f"--- START CHUNK [{i}] ---\n"
            f"WIKI PAGE: {c.get('page', 'N/A')}\n"
            f"SECTION: {c.get('title', 'N/A')}\n"
            f"SOURCE URL: {c.get('source', 'N/A')}\n"
            f"CONTENT:\n{c['text']}\n"
            f"--- END CHUNK [{i}] ---"
        )
        context_list.append(structured_chunk)

    context_text = "\n\n".join(context_list)
    print(context_text)

    # Prompt the LLM with clear instructions
    prompt = f"""
CONTEXT:
{context_text}

QUESTION: {question}

INSTRUCTIONS:
1. Answer the question based ONLY on the context.
2. Every piece of context has 'Source tag exmp->"source": "https://wiki.metakgp.org/w/AGV"'.
   You can assume society name from the URL after '/w/'.
3. Use the 'Source/Title' to confirm WHICH society the information belongs to.
4. Be bold but accurate. If the data is there, provide it.
5. ID of the chunk you used to form this answer.
6. If unsure, say 'I do not have enough info'.

RESPONSE FORMAT (JSON):
{{
    "answer": "Your detailed answer here...",
    "chunk_id": [5]
}}
"""

    gen_res = ai_client.chat.completions.create(
        model="xiaomi/mimo-v2-flash:free",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    raw_output = json.loads(gen_res.choices[0].message.content)
    answer = raw_output.get("answer")
    cited_ids = raw_output.get("chunk_id", [])

    # Filter chunks to ONLY those cited by the AI
    cited_chunks = [chunks[i] for i in cited_ids if i < len(chunks)]

    # If no chunks were cited, we consider it a failure early
    if not cited_chunks:
        return answer, {"status": "HALLUCINATED", "reason": "No sources cited"}, chunks

    g_check = verify_grounding(question, cited_chunks, answer, ai_client)
    h_check = detect_hallucinations(cited_chunks, answer, ai_client)
    l_check = audit_logic(cited_chunks, answer, ai_client)

    is_failed = (
        not g_check.get("grounded", True)
        or h_check.get("hallucinations_found", False)
        or not l_check.get("logic_valid", True)
    )

    status = "HALLUCINATED" if is_failed else "VERIFIED"

    return answer, {
        "status": status,
        "cited_ids": cited_ids,
        "details": {"g": g_check, "h": h_check, "l": l_check}
    }, cited_chunks


def ask_kgp_with_rerun(question):
    """The Rerun Loop: Expands search if experts fail the first attempt."""

    # ATTEMPT 1: Normal Search (10 chunks)
    print("🔍 Attempting first search...")
    chunks = ask_question(question, 10)

    answer, audit, cited_chunks = get_verified_answer(question, chunks)

    if audit["status"] == "HALLUCINATED":
        print("⚠️ Hallucination detected. Rerunning with 10 chunks...")
        chunks = ask_question(question, 10)
        answer, audit, cited_chunks = get_verified_answer(question, chunks)

    return answer, audit, cited_chunks


if __name__ == "__main__":
    print("Welcome to MetaKGP QA System")
