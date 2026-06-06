import re

with open('/Users/dhruv/.gemini/antigravity/scratch/portfolio/index.html', 'r') as f:
    html = f.read()

# Add aria-hidden to decorative SVGs
html = html.replace('<svg viewBox="0 0 16 16">', '<svg viewBox="0 0 16 16" aria-hidden="true">')
html = html.replace('<svg viewBox="0 0 16 16" fill="currentColor">', '<svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">')

# Add aria-hidden to project icons
html = re.sub(r'<span class="project-icon">(.+?)</span>', r'<span class="project-icon" aria-hidden="true">\1</span>', html)

# Add aria-labels to project links
def add_label(match):
    full_match = match.group(0)
    href = match.group(1)
    if "JusticeQueue" in href:
        label = "View JusticeQueue Source Code"
    elif "justicequeuelive" in href:
        label = "View JusticeQueue Live Demo"
    elif "Aura" in href:
        label = "View Aura Source Code"
    elif "aurasys" in href:
        label = "View Aura Live Demo"
    elif "FlowBoard" in href:
        label = "View FlowBoard Source Code"
    elif "ReviewAgent" in href:
        label = "View PRBeliefs Source Code"
    elif "prbeliefs" in href:
        label = "View PRBeliefs on GitHub Marketplace"
    elif "Disaster-Relief" in href:
        label = "View Disaster Relief Tracker Source Code"
    else:
        return full_match
    return full_match.replace('class="project-link"', f'aria-label="{label}" class="project-link"')

html = re.sub(r'<a href="([^"]+)" class="project-link" target="_blank" rel="noopener">', add_label, html)

# Also fix the Resume link in the footer
html = html.replace('<a href="Resume.pdf" target="_blank" rel="noopener" class="contact-link">Resume ↗</a>', '<a href="Resume.pdf" target="_blank" rel="noopener" aria-label="Download Dhruva Aher Resume PDF" class="contact-link">Resume ↗</a>')

with open('/Users/dhruv/.gemini/antigravity/scratch/portfolio/index.html', 'w') as f:
    f.write(html)

print("done")
