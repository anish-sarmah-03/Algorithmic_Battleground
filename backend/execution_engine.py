import requests

def run_code_in_sandbox(language_name, source_code, expected_input):
   
    url = "https://emkc.org/api/v2/piston/execute"
    
    piston_langs = {
        'C++': 'cpp',
        'Java': 'java',
        'Python': 'python'
    }
    
    lang = piston_langs.get(language_name, 'python')
    
    payload = {
        "language": lang,
        "version": "*", 
        "files": [
            {
                "content": source_code
            }
        ],
        "stdin": expected_input
    }
    
    try:
        response = requests.post(url, json=payload)
        result = response.json()
        
        if 'compile' in result and result['compile']['code'] != 0:
            return {
                "status": "Compilation Error",
                "compile_output": result['compile']['output'],
                "stdout": None,
                "stderr": None
            }
            
        run_result = result.get('run', {})
        
        if run_result.get('signal') == 'SIGKILL':
            status_desc = "Time Limit Exceeded"
        elif run_result.get('code') != 0:
            status_desc = "Runtime Error"
        else:
            status_desc = "Accepted" 
            
        return {
            "status": status_desc,
            "stdout": run_result.get('stdout', '').strip(),
            "stderr": run_result.get('stderr', '').strip(),
            "compile_output": None
        }
        
    except Exception as e:
        return {"status": "Internal Server Error", "error": str(e)}