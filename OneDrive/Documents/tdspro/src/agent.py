import json
import requests
import re
from browser import fetch_page_content
from llm import chat_with_llm
from tools import execute_python, REPL_CONTEXT

SYSTEM_PROMPT = """
You are an autonomous data science agent.
1. Understand the goal from the PAGE CONTENT.
2. Use `run_python` to scrape data, analyze CSVs, or calculate answers.
3. ALWAYS `print()` the results of your python code so you can see them.
4. Once you have the answer, use `submit`.

PYTHON VARIABLES AVAILABLE:
- `requests` (Use this for HTTP GET/POST)
- `pd` (Pandas)
- `plt` (Matplotlib)
- `io` (Input/Output)

RULES:
- Do NOT use `web_request`, `scrape_url`, or `beautifulsoup` (unless you import bs4).
- The text on the page usually contains the submission URL (e.g., /submit). FIND IT.
- The output of `run_python` is what you `print()`.

FORMAT: JSON ONLY.
{ "thought": "...", "action": "run_python", "code": "import pandas as pd\n..." }
or
{ "thought": "...", "action": "submit", "answer": "...", "submission_url": "..." }
"""

def extract_json(text):
    """Helper to find JSON object inside LLM response"""
    try:
        # Find string between first { and last }
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(text)
    except:
        raise ValueError("No valid JSON found")

def solve_task(start_url, email, secret):
    current_url = start_url
    
    # Limit max levels to avoid infinite loops
    max_levels = 5
    level_count = 0
    
    while current_url and level_count < max_levels:
        level_count += 1
        print(f"\n🌍 STARTING LEVEL {level_count}: {current_url}")
        
        REPL_CONTEXT.clear()
        history = [SYSTEM_PROMPT]
        
        try:
            page_content = fetch_page_content(current_url)
        except Exception as e:
            return {"error": f"Browser failed: {e}"}
            
        history.append(f"PAGE CONTENT for {current_url}:\n{page_content}")
        
        level_solved = False
        
        for step in range(15): 
            print(f"--- Step {step + 1} ---")
            
            try:
                llm_response = chat_with_llm(history)
                plan = extract_json(llm_response)
            except Exception as e:
                print(f"❌ JSON Error: {e}")
                history.append(f"System: Your response was not valid JSON. Error: {str(e)}. Try again.")
                continue
                
            print(f"🤖 Thought: {plan.get('thought')}")
            action = plan.get('action')
            
            if action == "run_python":
                print("⚡ Executing Python...")
                res = execute_python(plan.get('code'))
                
                # Truncate output if it's too long to save tokens
                display_out = res if len(res) < 500 else res[:500] + "...(truncated)"
                print(f"   Output: {display_out}") 
                history.append(f"PYTHON OUTPUT:\n{res}")
                
            elif action == "submit":
                payload = {
                    "email": email,
                    "secret": secret,
                    "url": current_url,
                    "answer": plan.get('answer')
                }
                
                # Trust the LLM's URL, default to standard if missing
                target = plan.get('submission_url')
                if not target:
                    target = "[https://tds-llm-analysis.s-anand.net/submit](https://tds-llm-analysis.s-anand.net/submit)"
                
                print(f"🚀 Submitting to {target}: {payload}")
                
                try:
                    r = requests.post(target, json=payload, timeout=30)
                    try:
                        resp = r.json()
                    except:
                        # If server returns 500 HTML
                        error_msg = f"Server returned non-JSON: {r.status_code}"
                        print(f"❌ {error_msg}")
                        history.append(f"System: {error_msg}")
                        continue

                    print(f"✅ Server: {resp}")
                    
                    if resp.get("correct"):
                        next_url = resp.get("url")
                        if next_url:
                            print(f"⏩ Moving to next level: {next_url}")
                            current_url = next_url
                            level_solved = True
                            break 
                        else:
                            print("🎉 Quiz Completed Successfully!")
                            return resp
                    else:
                        error = f"Submission rejected: {resp.get('reason')}"
                        print(f"❌ {error}")
                        history.append(f"System: The server said your answer was WRONG. Reason: {resp.get('reason')}. Try a different approach.")
                        
                except Exception as e:
                    print(f"❌ Submit Network Failed: {e}")
                    history.append(f"System: Network error during submit: {e}")
                    
        if not level_solved:
            return {"error": f"Failed to solve {current_url} in 15 steps"}
            
    return {"status": "Quiz Completed"}