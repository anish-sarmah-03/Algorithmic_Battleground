import subprocess
import tempfile
import os
import sys

def run_code_in_sandbox(language, code, expected_input=""):
    try:
        if language == "python":
            # 1. Create a temporary .py file on your server (your PC)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code)
                filename = f.name
            
            # 2. Run the file locally using your own Python installation
            # sys.executable ensures it uses the exact Python version running Flask
            result = subprocess.run(
                [sys.executable, filename], 
                input=expected_input,
                text=True,
                capture_output=True,
                timeout=5 # Kills the code after 5 seconds to prevent infinite loops
            )
            
            # 3. Clean up the temp file
            os.remove(filename) 

            # 4. Check for crashes (Syntax errors, out of bounds, etc.)
            if result.returncode != 0:
                return {
                    "status": "Runtime Error", 
                    "stdout": result.stdout, 
                    "stderr": result.stderr
                }
            
            # 5. Clean Execution!
            return {
                "status": "Accepted", 
                "stdout": result.stdout, 
                "stderr": ""
            }
            
        elif language == "c++":
            # WARNING: This requires g++ (MinGW) to be installed and added to your Windows PATH
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False, encoding='utf-8') as f:
                f.write(code)
                source_file = f.name
            
            exe_file = source_file.replace('.cpp', '.exe')
            
            # Compile
            compile_process = subprocess.run(['g++', source_file, '-o', exe_file], text=True, capture_output=True)
            if compile_process.returncode != 0:
                os.remove(source_file)
                return {"status": "Compile Error", "compile_output": compile_process.stderr}
            
            # Run
            run_process = subprocess.run([exe_file], input=expected_input, text=True, capture_output=True, timeout=5)
            
            # Cleanup
            os.remove(source_file)
            if os.path.exists(exe_file):
                os.remove(exe_file)
                
            if run_process.returncode != 0:
                return {"status": "Runtime Error", "stdout": run_process.stdout, "stderr": run_process.stderr}
            return {"status": "Accepted", "stdout": run_process.stdout, "stderr": ""}
            
        else:
            return {"status": "API Error", "stderr": f"Local executor does not support {language} yet."}

    except subprocess.TimeoutExpired:
        return {"status": "Time Limit Exceeded", "stderr": "Code execution took too long (Infinite Loop?)"}
    except Exception as e:
        return {"status": "Engine Error", "stderr": str(e)}