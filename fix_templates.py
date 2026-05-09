import os
import re

base_path = r"c:\Users\Asus\OneDrive - Higher Education Commission\Desktop\testApp\jobPortal\recruiter\templates\recruiter"
files = [
    "add_skill.html", "all_jobs_created.html", "application_detail.html", 
    "applications_for_job.html", "companyForm.html", "dashboard.html", 
    "jobForm.html", "job_detail.html", "log_in.html", 
    "representative_profile.html", "sign_up.html"
]

base_html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %} {% endblock %}</title>
    {% block style %} {% endblock %}
</head>
<body>
    {% block content %}
    {% endblock %}
</body>
</html>"""

with open(os.path.join(base_path, "base.html"), "w", encoding="utf-8") as f:
    f.write(base_html_content)

for filename in files:
    filepath = os.path.join(base_path, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract title
    title_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else filename.replace('.html', '').replace('_', ' ').title()

    # Extract style
    style_match = re.search(r"<style>(.*?)</style>", content, re.IGNORECASE | re.DOTALL)
    style = style_match.group(1).strip() if style_match else ""

    # Extract body content
    body_match = re.search(r"<body>(.*?)</body>", content, re.IGNORECASE | re.DOTALL)
    if body_match:
        body = body_match.group(1).strip()
    else:
        # For files like add_skill.html which might not have body tags
        # Just strip doctype, html, head
        body = re.sub(r"<!DOCTYPE html>|<html.*?>|</html>|<head>.*?</head>|<body>|</body>", "", content, flags=re.IGNORECASE | re.DOTALL).strip()

    new_content = '{% extends "recruiter/base.html" %}\n\n'
    new_content += '{% block title %} ' + title + ' {% endblock %}\n\n'
    
    if style:
        new_content += '{% block style %}\n<style>\n' + style + '\n</style>\n{% endblock %}\n\n'
        
    new_content += '{% block content %}\n\n' + body + '\n\n{% endblock %}\n'
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
        
print("Done")
