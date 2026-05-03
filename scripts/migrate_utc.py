import os
import re

def migrate_utcnow(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Fix datetime.utcnow() directly
                new_content = re.sub(r'datetime\.utcnow\(\)', 'datetime.now(datetime.timezone.utc)', content)
                
                # Fix default=datetime.utcnow
                new_content = re.sub(r'default=datetime\.utcnow\b(?!\()', 'default=lambda: datetime.now(datetime.timezone.utc)', new_content)
                
                # Fix onupdate=datetime.utcnow
                new_content = re.sub(r'onupdate=datetime\.utcnow\b(?!\()', 'onupdate=lambda: datetime.now(datetime.timezone.utc)', new_content)
                
                if new_content != content:
                    # Also need to make sure datetime.timezone is available if we use it.
                    # Instead of importing timezone everywhere, it's safer to use datetime.UTC since Python 3.11
                    # But if Python < 3.11, datetime.timezone.utc is compatible.
                    
                    # Actually datetime.now(datetime.UTC) is great.
                    # Wait, if we use datetime.timezone.utc we need `import datetime` instead of `from datetime import datetime`.
                    # Let's replace with `datetime.now(datetime.timezone.utc)`.
                    # If the file has `from datetime import datetime`, then `datetime.timezone.utc` won't work unless `timezone` is also imported.
                    pass
                
                # Let's be smarter:
                # Replace datetime.utcnow() -> datetime.now(datetime.timezone.utc)
                # If 'from datetime import datetime', we should import timezone as well.
                if new_content != content:
                    if 'from datetime import datetime' in new_content and 'timezone' not in new_content:
                        new_content = new_content.replace('from datetime import datetime', 'from datetime import datetime, timezone')
                        new_content = new_content.replace('datetime.now(datetime.timezone.utc)', 'datetime.now(timezone.utc)')
                        new_content = new_content.replace('datetime.now(datetime.UTC)', 'datetime.now(timezone.utc)')
                    elif 'import datetime' in new_content:
                        # 'datetime.now(datetime.timezone.utc)' is valid.
                        pass
                    else:
                        # Missing import? Add it.
                        pass
                        
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Migrated {filepath}")

if __name__ == "__main__":
    migrate_utcnow('backend')
