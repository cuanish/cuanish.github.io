import os
import re

# Define the directory to process
TECH_WRITEUPS_DIR = "tech-writeups"

# CSS to add or update
NEW_CSS = """
        .terminal-content {
            padding: 20px 30px;
        }

        .terminal-content ol {
            margin-left: 15px;
        }

        .terminal-content ol li {
            margin-bottom: 10px;
        }

        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            h1 {
                font-size: 1.8em;
                margin-bottom: 15px;
            }

            h2, h3 {
                margin-bottom: 8px;
            }

            hr {
                margin: 8px 0 15px 0;
            }

            .terminal-content {
                padding: 15px 20px;
            }

            .terminal-content table {
                font-size: 0.9em;
            }

            .terminal-content ol {
                margin-left: 10px;
            }
        }
"""

def update_css_in_file(file_path):
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Check for <ol> tags
        if re.search(r'<ol\b[^>]*>', content, re.IGNORECASE):
            print(f"Found <ol> tags in {file_path}")

        # Find the <style> section
        style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
        if not style_match:
            print(f"No <style> section found in {file_path}. Skipping.")
            return

        style_content = style_match.group(1)
        style_start, style_end = style_match.span()

        # Check if .terminal-content padding already exists
        if '.terminal-content {' in style_content:
            # Update padding
            new_style_content = re.sub(
                r'\.terminal-content\s*\{([^}]*)\}',
                r'.terminal-content {\1    padding: 20px 30px;\n}',
                style_content,
                flags=re.DOTALL
            )
        else:
            new_style_content = style_content + '\n' + '.terminal-content {\n    padding: 20px 30px;\n}\n'

        # Check if .terminal-content ol already exists
        if '.terminal-content ol {' not in new_style_content:
            new_style_content += '\n        .terminal-content ol {\n            margin-left: 15px;\n        }\n'

        # Check if .terminal-content ol li already exists
        if '.terminal-content ol li {' not in new_style_content:
            new_style_content += '\n        .terminal-content ol li {\n            margin-bottom: 10px;\n        }\n'

        # Check if @media (max-width: 768px) exists
        media_match = re.search(r'@media \(max-width: 768px\) \{([^}]*)\}', new_style_content, re.DOTALL)
        if media_match:
            media_content = media_match.group(1)
            # Update or add .terminal-content padding and ol margin in media query
            if '.terminal-content {' in media_content:
                new_media_content = re.sub(
                    r'\.terminal-content\s*\{([^}]*)\}',
                    r'.terminal-content {\1    padding: 15px 20px;\n}',
                    media_content,
                    flags=re.DOTALL
                )
            else:
                new_media_content = media_content + '\n            .terminal-content {\n                padding: 15px 20px;\n            }\n'

            if '.terminal-content ol {' not in media_content:
                new_media_content += '\n            .terminal-content ol {\n                margin-left: 10px;\n            }\n'

            new_style_content = re.sub(
                r'@media \(max-width: 768px\) \{([^}]*)\}',
                f'@media (max-width: 768px) {{{new_media_content}}}',
                new_style_content,
                flags=re.DOTALL
            )
        else:
            # Add the entire media query if it doesn't exist
            new_style_content = new_style_content.rstrip() + '\n' + NEW_CSS

        # Reconstruct the file content with updated <style> section
        new_content = content[:style_start] + f'<style>{new_style_content}</style>' + content[style_end:]

        # Write the updated content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"Updated CSS in {file_path}")

    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")

def main():
    # Walk through technical-writeups directory
    for root, _, files in os.walk(TECH_WRITEUPS_DIR):
        for file in files:
            if file == "index.html":
                file_path = os.path.join(root, file)
                print(f"Processing {file_path}")
                update_css_in_file(file_path)

if __name__ == "__main__":
    main()
