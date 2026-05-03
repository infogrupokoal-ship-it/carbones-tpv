import os
import glob
import re

def migrate_tailwind_cdn():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(project_root, 'static')
    html_files = glob.glob(os.path.join(static_dir, '*.html'))
    html_files.extend(glob.glob(os.path.join(project_root, '*.html')))

    count = 0
    pattern = re.compile(r'^[ \t]*<script\s+src=["\']https://cdn\.tailwindcss\.com["\']></script>\s*$', re.MULTILINE)
    for file_path in html_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content, num_subs = pattern.subn('    <link rel="stylesheet" href="/static/css/tailwind.css">\n', content)
        if num_subs > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            count += 1
            
    print(f"✅ Migrated {count} HTML files to use local tailwind.css")

if __name__ == '__main__':
    migrate_tailwind_cdn()
