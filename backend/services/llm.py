from openai import OpenAI
import os
import json
from typing import List, Dict, Any, Optional

# Initialize DeepSeek Client
# DeepSeek API uses the OpenAI SDK structure
def get_llm_client():
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY environment variable not set")
    
    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

SYSTEM_PROMPT = """
You are an expert legal AI assistant for licensed lawyers.
Your goal is to analyze legal documents and provide structured, professional outputs.

RULES:
1. You are an assistant, not a judge. Do not fabricate cases or statutes.
2. Output STRICTLY JSON. No markdown, no conversational filler.
3. Follow the JSON schema provided for each task type exactly.
4. If a field is unknown, use null.
5. Be precise, professional, and conservative in risk assessment.

RESPONSE FORMAT:
{
  "status": "ok" | "input_error" | "refused",
  "task_type": "summary" | "issue_spotting" | "clause_extraction" | "draft_document" | "checklist",
  "jurisdiction": "string | null",
  "summary": "string (high level summary of the result)",
  "outputs": { ... task specific object ... },
  "issues": ["string (list of potential problems or uncertainties)"]
}
"""

async def run_legal_task(task_type: str, docs: List[Dict[str, Any]], instructions: str = None, jurisdiction: str = None) -> Dict[str, Any]:
    client = get_llm_client()
    
    # Prepare context from documents
    doc_context = ""
    for doc in docs:
        doc_context += f"--- DOCUMENT START: {doc.get('filename')} ---\n"
        for page in doc.get('pages', []):
            doc_context += f"[Page {page.get('page_number')}]\n{page.get('raw_text')}\n"
        doc_context += f"--- DOCUMENT END ---\n\n"

    # Construct the specific prompt based on task
    user_prompt = f"""
    TASK: {task_type}
    JURISDICTION: {jurisdiction or "Not specified"}
    INSTRUCTIONS: {instructions or "None"}
    
    DOCUMENTS:
    {doc_context}
    
    Perform the task and return the JSON response.
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat", # or deepseek-coder, check API docs. Usually deepseek-chat is best for general text.
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={ "type": "json_object" },
            temperature=0.2 # Low temperature for factual/legal accuracy
        )
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from LLM")
            
        # Parse JSON
        try:
            result = json.loads(content)
            return result
        except json.JSONDecodeError:
            # Simple retry logic could go here (ask LLM to fix JSON)
            # For MVP, just return error
            return {
                "status": "error",
                "task_type": task_type,
                "summary": "Failed to parse LLM response as JSON",
                "outputs": {},
                "issues": ["Invalid JSON output from model"]
            }
            
    except Exception as e:
        return {
            "status": "error",
            "task_type": task_type,
            "summary": f"LLM Error: {str(e)}",
            "outputs": {},
            "issues": [str(e)]
        }
