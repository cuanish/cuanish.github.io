#!/bin/bash

# Script to update tech news index.html with new HTML files
# Usage: ./update_news.sh [directory]

mv html/*html news/

# Set default directory to current working directory if not provided
TECH_DIR="${1:-$(pwd)}"

# Check if we're in the right directory structure
if [[ ! -d "$TECH_DIR/news" ]]; then
    echo "❌ Error: news directory not found in $TECH_DIR"
    echo "Usage: $0 [path_to_github_pages_directory]"
    echo "Example: $0 /path/to/cuanish.github.io"
    exit 1
fi

INDEX_FILE="$TECH_DIR/news/index.html"
TECH_NEWS_DIR="$TECH_DIR/news"

# Check if index.html exists
if [[ ! -f "$INDEX_FILE" ]]; then
    echo "❌ Error: $INDEX_FILE not found"
    exit 1
fi

echo "📁 Scanning for new tech news HTML files in $TECH_NEWS_DIR..."

# Find all HTML files that match news patterns
html_files=($(find "$TECH_NEWS_DIR" -name "tech_news_*.html" -o -name "tech_news_security_*.html" -o -name "linux_news_*.html" -o -name "robotics_news_*.html" -o -name "security_news_*.html" -o -name "combined_news_*.html" | sort -r))

if [[ ${#html_files[@]} -eq 0 ]]; then
    echo "ℹ️  No tech news HTML files found"
    exit 0
fi

echo "📄 Found ${#html_files[@]} HTML file(s)"

# Create a backup of the current index.html
backup_file="$INDEX_FILE.backup.$(date +%Y%m%d_%H%M%S)"
cp "$INDEX_FILE" "$backup_file"
echo "💾 Created backup: $backup_file"

# Set environment variables for Python script
export INDEX_FILE="$INDEX_FILE"
export HTML_FILES=$(printf '%s\n' "${html_files[@]}")

# Run the Python script with the new format
python3 << 'EOF'
import re
import sys
import os
from datetime import datetime

def get_section_info(filename):
    """Determine section, display name, and date from filename"""
    if filename.startswith('combined_news_'):
        return None  # Skip combined files
    
    patterns = {
        r'^tech_news_(\d{8})_\d{6}\.html$': ('tech', 'Technology Updates'),
        r'^(security_news_|tech_news_security_)(\d{8})_\d{6}\.html$': ('security', 'Security Updates'),
        r'^robotics_news_(\d{8})_\d{6}\.html$': ('robotics', 'Robotics Updates'),
        r'^linux_news_(\d{8})_\d{6}\.html$': ('linux', 'Linux Updates'),
    }
    
    for pattern, (section, display_name) in patterns.items():
        match = re.match(pattern, filename)
        if match:
            # Extract date from the appropriate group
            date_str = match.group(2) if len(match.groups()) > 1 else match.group(1)
            # Convert YYYYMMDD to "Month DD, YYYY" format
            date_obj = datetime.strptime(date_str, '%Y%m%d')
            formatted_date = date_obj.strftime('%B %d, %Y')
            return section, display_name, formatted_date
    
    return None

def extract_existing_entries(content, section):
    """Extract existing filenames from a section"""
    # Find the section's ul content
    pattern = rf'<div class="section-content" id="{section}-content">.*?<ul class="news-list">(.*?)</ul>'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return set()
    
    section_content = match.group(1)
    # Find all href links in this section
    href_pattern = r'href="[^"]*/([\w_]+\.html)"'
    existing_files = set(re.findall(href_pattern, section_content))
    return existing_files

def insert_entries_in_section(content, section, new_entries):
    """Insert new entries at the top of the specified section's ul list"""
    if not new_entries:
        return content
    
    # Find the ul tag within the specific section
    section_pattern = rf'(<div class="section-content" id="{section}-content">.*?<ul class="news-list">)'
    
    def replace_func(match):
        return match.group(1) + '\n' + '\n'.join(new_entries)
    
    updated_content = re.sub(section_pattern, replace_func, content, flags=re.DOTALL)
    return updated_content

# Main execution
index_file = os.environ.get('INDEX_FILE')
html_files_str = os.environ.get('HTML_FILES')

if not index_file or not html_files_str:
    print('Error: Missing environment variables')
    sys.exit(1)

html_files = html_files_str.strip().split('\n') if html_files_str.strip() else []

try:
    with open(index_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
except Exception as e:
    print(f'Error reading {index_file}: {e}')
    sys.exit(1)

new_entries_by_section = {'tech': [], 'security': [], 'robotics': [], 'linux': []}
existing_entries_by_section = {}

for section in new_entries_by_section.keys():
    existing_entries_by_section[section] = extract_existing_entries(html_content, section)

new_entries_added = 0
processed_files = []

for html_file in html_files:
    if not html_file.strip():
        continue
        
    filename = os.path.basename(html_file.strip())
    section_info = get_section_info(filename)
    
    if not section_info:
        print(f'⭐️ Skipping {filename} (combined file or unknown format)')
        continue
    
    section, display_name, formatted_date = section_info
    
    if filename in existing_entries_by_section[section]:
        print(f'⭐️ Skipping {filename} (already in {section} section)')
        continue
    
    # Create new entry matching the current HTML format
    entry = f'''                        <li>
                            <a href="https://cuanish.github.io/news/{filename}" target="_blank">
                                <span>{display_name}</span>
                                <div>
                                    <span class="news-date">{formatted_date}</span>
                                    <i class="fas fa-external-link-alt news-arrow"></i>
                                </div>
                            </a>
                        </li>'''
    
    new_entries_by_section[section].insert(0, entry)  # Insert at beginning for newest first
    
    processed_files.append(f'{display_name} ({formatted_date}) -> {section}')
    new_entries_added += 1

# Update HTML content for each section with new entries
updated_content = html_content
for section, entries in new_entries_by_section.items():
    if entries:
        print(f'📄 Updating {section} section with {len(entries)} new entries...')
        updated_content = insert_entries_in_section(updated_content, section, entries)

if new_entries_added > 0:
    try:
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f'✅ Successfully updated {index_file}')
    except Exception as e:
        print(f'Error writing to {index_file}: {e}')
        sys.exit(1)
        
    print('🆕 New entries added:')
    for entry in processed_files:
        print(f'   • {entry}')
else:
    print('ℹ️  No new entries to add')

print(f'📊 Total new entries added: {new_entries_added}')
EOF

# Check if the Python script succeeded
if [ $? -eq 0 ]; then
    echo ""
    echo "📊 Summary:"
    echo "   • Processed HTML files: ${#html_files[@]}"
    echo "   • Backup saved: $backup_file"
    
    # Optional: Show git status if we're in a git repo
    if git rev-parse --git-dir > /dev/null 2>&1; then
        echo ""
        echo "📋 Git status:"
        git status --porcelain "$INDEX_FILE"
        echo ""
        echo "🚀 To commit changes:"
        echo "   git add $INDEX_FILE"
        echo "   git commit -m 'Update tech news index with new entries'"
        echo "   git push"
    fi
    
    echo ""
    echo "🎉 Update complete! Check your website to see the new entries."
else
    echo "❌ Failed to update HTML file"
    echo "💾 Restoring from backup..."
    mv "$backup_file" "$INDEX_FILE"
    exit 1
fi
