import os

# Directory containing the HTML files
root_dir = 'tech-writeups'

# Old and new back link URLs
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
                
                # Check if the old link exists
                if old_link in content:
                    # Replace the old link with the new link
                    updated_content = content.replace(old_link, new_link)
                    
                    # Write the updated content back to the file
                    with open(html_file, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    print(f'Updated back link in {html_file}')
                else:
                    print(f'Skipped {html_file}: old back link not found')
            except Exception as e:
                print(f'Failed to update {html_file}: {e}')
        else:
            print(f'Skipped {subdir_path}: no index.html found')
