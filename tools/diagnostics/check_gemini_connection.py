import os
import sys
import json
from dotenv import load_dotenv

def check_gemini():
    print("--- QUANTUM GEMINI DIAGNOSTIC v1.0 ---")
    
    # Try to load .env from current dir or project root
    load_dotenv()
    
    results = {
        "ok": False,
        "provider": "gemini",
        "env_var_used": "none",
        "key_present": False,
        "key_suffix": "none",
        "model": os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
        "error_type": "NONE",
        "raw_error_summary": "Initial state",
        "recommendation": "Check API keys"
    }
    
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    var_name = "GEMINI_API_KEY" if os.getenv("GEMINI_API_KEY") else "GOOGLE_API_KEY" if os.getenv("GOOGLE_API_KEY") else "none"
    
    if not api_key:
        results["error_type"] = "VARIABLE_MISSING"
        results["raw_error_summary"] = "No GEMINI_API_KEY or GOOGLE_API_KEY found in environment."
        results["recommendation"] = "Set GEMINI_API_KEY in your .env file or environment variables."
        return results

    results["key_present"] = True
    results["env_var_used"] = var_name
    results["key_suffix"] = api_key[-4:] if len(api_key) > 4 else "****"
    
    try:
        import google.generativeai as genai
    except ImportError:
        results["error_type"] = "LIBRERIA_MISSING"
        results["raw_error_summary"] = "google-generativeai library not installed."
        results["recommendation"] = "Run: pip install -q -U google-generativeai"
        return results

    try:
        genai.configure(api_key=api_key)
        
        print("\n--- AVAILABLE MODELS ---")
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f" - {m.name}")
                available_models.append(m.name)
        
        if results["model"] not in available_models and f"models/{results['model']}" not in available_models:
             # Try to find a fallback automatically
             candidates = [m for m in available_models if "flash" in m.lower()]
             if candidates:
                 print(f"WARN: Requested model '{results['model']}' not found. Suggestion: {candidates[0]}")
             else:
                 print(f"WARN: Requested model '{results['model']}' not found in available list.")

        model = genai.GenerativeModel(results["model"])
        
        # Short test prompt
        response = model.generate_content("Ping", generation_config={"max_output_tokens": 10})
        
        if response.text:
            results["ok"] = True
            results["raw_error_summary"] = "Connection successful."
            results["recommendation"] = "System operational."
    except Exception as e:
        err_msg = str(e)
        results["raw_error_summary"] = err_msg
        
        if "API_KEY_INVALID" in err_msg or "400" in err_msg:
            results["error_type"] = "CLAVE_INVALIDA"
            results["recommendation"] = "Verify the API Key in Google AI Studio. It might be expired or revoked."
        elif "quota" in err_msg.lower() or "429" in err_msg:
            results["error_type"] = "CUOTA_EXCEDIDA"
            results["recommendation"] = "Rate limit reached. Upgrade to Tier 1 or wait for reset."
        elif "billing" in err_msg.lower():
            results["error_type"] = "BILLING_REQUIRED"
            results["recommendation"] = "Enable billing in Google Cloud Console for this project."
        elif "model not found" in err_msg.lower() or "invalid model" in err_msg.lower():
            results["error_type"] = "MODELO_INVALIDO"
            results["recommendation"] = f"The model '{results['model']}' is not available for this key. Try 'gemini-1.5-flash'."
        else:
            results["error_type"] = "RED_O_GENERICO"
            results["recommendation"] = "Check internet connection or Google API status."

    return results

if __name__ == "__main__":
    diag_result = check_gemini()
    print(json.dumps(diag_result, indent=4))
    
    if diag_result["ok"]:
        sys.exit(0)
    else:
        sys.exit(1)
