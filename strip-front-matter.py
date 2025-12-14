import os
import re

# Directory containing the HTML files
root_dir = 'tech-writeups'

# Regex pattern to match the front matter (flexible for whitespace)
front_matter_pattern = r'^\s*---\s*\n\s*layout:\s*none\s*\n\s*---\s*\n'

# Old and new back link URLs (for optional back link update)
old_link = '<a href="https://archie-linux.github.io/technical-writeups" class="back-link">← Back</a>'
new_link = '<a href="https://archie-linux.github.io/tech-writeups" class="back-link">← Back</a>'

# Iterate through subdirectories
for subdir in os.listdir(root_dir):
    subdir_path = os.path.join(root_dir, subdir)
    if os.path.isdir(subdir_path) and subdir != 'backup':
        html_file = os.path.join(subdir_path, 'index.html')
        if os.path.exists(html_file):
            try:
                # Read the HTML file
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Track changes
                updated = False
                
                # Check and remove front matter
                if re.search(front_matter_pattern, content):
                    content = re.sub(front_matter_pattern, '', content, count=1)
                    updated = True
                    print(f'Removed front matter from {html_file}')
                else:
                    print(f'Skipped {html_file}: front matter not found')
                
                # Check and update back link
                if old_link in content:
                    content = content.replace(old_link, new_link)
                    updated = True
                    print(f'Updated back link in {html_file}')
                else:
                    print(f'Skipped {html_file}: old back link not found')
                
                # Write updated content back if changes were made
                if updated:
                    with open(html_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f'Saved updated {html_file}')
                else:
                    print(f'No changes needed for {html_file}')
            except Exception as e:
                print(f'Failed to process {html_file}: {e}')
        else:
            print(f'Skipped {subdir_path}: no index.html found')
