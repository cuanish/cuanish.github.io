import os
import markdown
import yaml
import re
import shutil

# HTML template with updated hacker theme and Highlight.js
HTML_TEMPLATE = '''
---
layout: none
---
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anish - {title}</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/monokai.min.css">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            background: #1e1e2e;
            color: #e0e0e0;
            font-family: 'Courier New', monospace;
            line-height: 1.6;
            overflow-x: hidden;
        }}

        .matrix-bg {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            opacity: 0.05;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}

        .back-link {{
            color: #5bc0de;
            text-decoration: none;
            padding: 10px;
            display: block;
            transition: all 0.3s ease;
            margin-bottom: 20px;
            font-size: 1.1em;
        }}

        .back-link:hover {{
            color: #ff6b6b;
            text-shadow: 0 0 5px rgba(255, 107, 107, 0.5);
        }}

        .terminal-window {{
            background: #2a2a3a;
            border: 2px solid #5bc0de;
            border-radius: 10px;
            margin: 20px 0;
            box-shadow: 0 0 15px rgba(91, 192, 222, 0.2);
        }}

        .terminal-header {{
            background: #3a3a4a;
            padding: 10px;
            border-bottom: 1px solid #5bc0de;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .terminal-dots {{
            display: flex;
            gap: 5px;
        }}

        .dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }}

        .dot.red {{ background: #ff5f56; }}
        .dot.yellow {{ background: #ffbd2e; }}
        .dot.green {{ background: #27ca3f; }}

        .terminal-title {{
            color: #a0a0a0;
            font-size: 14px;
        }}

        .terminal-content {{
            padding: 20px;
        }}

        .terminal-content pre {{
            background: #1e1e2e;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }}

        .terminal-content code {{
            font-family: 'Courier New', monospace;
        }}

        .terminal-content table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        .terminal-content th, .terminal-content td {{
            border: 1px solid #5bc0de;
            padding: 10px;
            text-align: left;
        }}

        .terminal-content th {{
            background: #3a3a4a;
            color: #e0e0e0;
        }}

        .terminal-content td {{
            background: #2a2a3a;
        }}

        .prompt {{
            color: #5bc0de;
            margin-bottom: 10px;
        }}

        .command {{
            color: #ff6b6b;
        }}

        h1 {{
            color: #e0e0e0;
            font-weight: normal;
            text-shadow: 0 0 5px rgba(91, 192, 222, 0.3);
            font-size: 2.2em;
            text-align: center;
            margin-bottom: 20px;
        }}

        h2, h3 {{
            color: #e0e0e0;
            font-weight: normal;
            margin-bottom: 10px;
        }}

        hr {{
            border: 0;
            border-top: 1px solid #5bc0de;
            margin: 10px 0 20px 0;
            opacity: 0.5;
        }}

        @keyframes glow {{
            from {{ text-shadow: 0 0 5px rgba(91, 192, 222, 0.3); }}
            to {{ text-shadow: 0 0 10px rgba(91, 192, 222, 0.5); }}
        }}

        .footer {{
            text-align: center;
            padding: 20px;
            border-top: 1px solid #5bc0de;
            margin-top: 50px;
            color: #a0a0a0;
        }}

        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            
            h1 {{
                font-size: 1.8em;
                margin-bottom: 15px;
            }}

            h2, h3 {{
                margin-bottom: 8px;
            }}

            hr {{
                margin: 8px 0 15px 0;
            }}

            .terminal-content table {{
                font-size: 0.9em;
            }}
        }}

        .matrix-char {{
            position: absolute;
            color: #5bc0de;
            font-family: monospace;
            font-size: 14px;
            animation: matrix-fall linear infinite;
        }}

        @keyframes matrix-fall {{
            0% {{ opacity: 1; transform: translateY(-100vh); }}
            100% {{ opacity: 0; transform: translateY(100vh); }}
        }}
    </style>
</head>
<body>
    <canvas class="matrix-bg" id="matrixCanvas"></canvas>

    <div class="container">
        <a href="https://archie-linux.github.io/technical-writeups" class="back-link">← Back</a>
        
        <h1>{title}</h1>
        <hr>

        <div class="terminal-window">
            <div class="terminal-header">
                <div class="terminal-dots">
                    <div class="dot red"></div>
                    <div class="dot yellow"></div>
                    <div class="dot green"></div>
                </div>
                <div class="terminal-title">~/technical-writeups/{subdir}/index.sh</div>
            </div>
            <div class="terminal-content">
                {content_html}
            </div>
        </div>

        <div class="footer">
            <div class="prompt">root@writeup:~$ <span class="command">echo "End of transmission"</span></div>
            <p>&copy; 2025 Anish. All rights reserved.</p>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            // Initialize Highlight.js
            hljs.highlightAll();

            const canvas = document.getElementById('matrixCanvas');
            if (!canvas) {{
                console.error('Canvas element not found');
                return;
            }}
            const ctx = canvas.getContext('2d');
            if (!ctx) {{
                console.error('Canvas context not available');
                return;
            }}

            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;

            const chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()_+-=[]{{}}|;:,.<>?';
            const charArray = chars.split('');
            const fontSize = 14;
            const columns = Math.floor(canvas.width / fontSize);
            const drops = Array(columns).fill(1);

            function draw() {{
                ctx.fillStyle = 'rgba(30, 30, 46, 0.04)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = '#5bc0de';
                ctx.font = `${{fontSize}}px monospace`;

                for (let i = 0; i < drops.length; i++) {{
                    const text = charArray[Math.floor(Math.random() * charArray.length)];
                    ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                    if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {{
                        drops[i] = 0;
                    }}
                    drops[i]++;
                }}
            }}

            setInterval(draw, 35);

            window.addEventListener('resize', () => {{
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            }});
        }});
    </script>
</body>
</html>
'''

# Function to parse front matter and content from md file
def parse_md_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Split front matter and body
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content
    front_matter = yaml.safe_load(parts[1])
    body = parts[2].strip()
    return front_matter, body

# Function to add <hr> after headings in HTML
def add_hr_after_headings(html_content):
    # Add <hr> after </h1>, </h2>, </h3>
    html_content = re.sub(r'(</h[1-3]>)', r'\1<hr>', html_content)
    return html_content

# Main script
root_dir = 'technical-writeups'
backup_dir = os.path.join(root_dir, 'backup')

# Create backup directory if it doesn't exist
if not os.path.exists(backup_dir):
    os.makedirs(backup_dir)

for subdir in os.listdir(root_dir):
    subdir_path = os.path.join(root_dir, subdir)
    if os.path.isdir(subdir_path) and subdir != 'backup':
        md_file = os.path.join(subdir_path, 'index.md')
        if os.path.exists(md_file):
            # Parse Markdown file
            front_matter, md_content = parse_md_file(md_file)
            title = front_matter.get('title', subdir.replace('-', ' ').title())
            # Convert Markdown to HTML with extensions
            content_html = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'codehilite'])
            # Add <hr> after headings
            content_html = add_hr_after_headings(content_html)
            # Generate HTML
            html = HTML_TEMPLATE.format(title=title, subdir=subdir, content_html=content_html)
            # Write to index.html
            html_file = os.path.join(subdir_path, 'index.html')
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f'Converted {md_file} to {html_file}')
            # Move index.md to backup folder
            backup_subdir = os.path.join(backup_dir, subdir)
            if not os.path.exists(backup_subdir):
                os.makedirs(backup_subdir)
            backup_md_file = os.path.join(backup_subdir, 'index.md')
            try:
                shutil.move(md_file, backup_md_file)
                print(f'Moved {md_file} to {backup_md_file}')
            except Exception as e:
                print(f'Failed to move {md_file} to {backup_md_file}: {e}')
