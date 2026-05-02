import os
import re

def audit_links():
    static_dir = "static"
    html_files = [f for f in os.listdir(static_dir) if f.endswith(".html")]
    
    print(f"--- Auditing {len(html_files)} HTML files in {static_dir} ---")
    
    for html in html_files:
        path = os.path.join(static_dir, html)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Find all /static/ links
        links = re.findall(r'href=["\'](/static/[^"\']+)["\']', content)
        links += re.findall(r'src=["\'](/static/[^"\']+)["\']', content)
        
        missing = []
        for link in links:
            local_path = link.lstrip("/")
            if not os.path.exists(local_path):
                missing.append(link)
                
        if missing:
            print(f"[ERROR] {html}: Missing {len(missing)} files: {missing}")
        else:
            print(f"[OK] {html}: All links OK.")

if __name__ == "__main__":
    audit_links()
