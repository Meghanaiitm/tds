import io
import contextlib
import traceback
import base64
import requests
import pandas as pd
import matplotlib
# Force non-interactive backend to stop GUI warnings
matplotlib.use('Agg') 
import matplotlib.pyplot as plt

# Global memory
REPL_CONTEXT = {}

def execute_python(code: str):
    output_buffer = io.StringIO()
    plt.clf()

    try:
        # Create a session with a browser-like User-Agent
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

        local_env = REPL_CONTEXT
        local_env.update({
            "pd": pd,
            "plt": plt,
            "requests": session, # OVERRIDE requests with our safe session
            "io": io
        })

        with contextlib.redirect_stdout(output_buffer):
            exec(code, {}, local_env)
            
        result = output_buffer.getvalue().strip()
        
        if plt.get_fignums():
            img_buf = io.BytesIO()
            plt.savefig(img_buf, format='png')
            img_buf.seek(0)
            image_data = base64.b64encode(img_buf.read()).decode('utf-8')
            result += f"\n[IMAGE_GENERATED: {image_data}]"
            plt.clf()

        if not result:
            return "[Code executed successfully, but produced no output. Did you forget to print()?]"
            
        return result

    except Exception:
        return f"Execution Error:\n{traceback.format_exc()}"