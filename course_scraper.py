import re
import json
from bs4 import BeautifulSoup

def extract_markdown_table(text, header_anchor="## Evaluation"):
    lines = text.splitlines()
    inside_table = False
    table_lines = []

    for i, line in enumerate(lines):
        if header_anchor.lower() in line.lower():
            for j in range(i + 1, len(lines)):
                l = lines[j].strip()
                if l.startswith("|") and "|" in l:
                    inside_table = True
                    table_lines.append(l)
                elif inside_table and not l.startswith("|"):
                    break
            break

    if not table_lines:
        return []

    headers = [h.strip() for h in table_lines[0].strip().split("|") if h.strip()]
    data_rows = table_lines[2:]

    table_data = []
    for row in data_rows:
        cols = [c.strip() for c in row.strip().split("|") if c.strip()]
        if len(cols) == len(headers):
            table_data.append(dict(zip(headers, cols)))
    return table_data

def parse_markdown_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        md = f.read()

    result = {}

    # Title
    title_match = re.search(r"# (.+)", md)
    result["title"] = title_match.group(1).strip() if title_match else "Untitled"

    # Course intro (first paragraph before any <details>)
    intro_match = re.search(r"# .+?\n\n(.*?)\n<details>", md, re.DOTALL)
    result["course_intro"] = intro_match.group(1).strip() if intro_match else ""

    # Course link
    link_match = re.search(r"\[(Tools in Data Science.*?)\]\((https?://.*?)\)", md)
    if link_match:
        result["course_link"] = {"text": link_match.group(1), "url": link_match.group(2)}

    # <details> sections
    details = []
    for m in re.finditer(r"<details>\s*<summary><strong>(.*?)</strong></summary>\s*(.*?)</details>", md, re.DOTALL):
        heading = m.group(1).strip()
        content = BeautifulSoup(m.group(2).strip(), "html.parser").get_text().strip()
        details.append({"heading": heading, "content": content})
    result["details_sections"] = details

    # Modules (numbered markdown links)
    module_pattern = re.compile(r"\d+\.\s+\*\*\[(.+?)\]\((.+?)\)\*\*.*?\*\*(.+?)\*\*", re.DOTALL)
    modules = []
    for m in module_pattern.finditer(md):
        modules.append({
            "title": m.group(1).strip(),
            "link": m.group(2).strip(),
            "purpose": m.group(3).strip()
        })
    result["modules"] = modules

    # Evaluation table
    result["grading_table"] = extract_markdown_table(md)

    # Live session Zoom links
    zoom_links = re.findall(r"https://.*?\.zoom\.us/j/\S+", md)
    result["live_session_links"] = list(set(zoom_links))

    # Instructor/TA section
    ta_section = re.search(r"### Faculty & TA Team\s+(.*?)\n\n", md, re.DOTALL)
    result["instructors"] = ta_section.group(1).strip() if ta_section else ""

    # Misc links (discourse, github, google docs, etc.)
    all_links = re.findall(r"\[(.*?)\]\((https?://.*?)\)", md)
    misc = [{"text": text, "url": url} for text, url in all_links if "iitm.ac.in" in url or "github.com" in url or "google.com" in url]
    result["misc_links"] = misc

    return result

def main():
    input_file = "coursecontent.md"
    output_file = "coursecontent_structured.json"

    data = parse_markdown_file(input_file)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Structured content saved to: {output_file}")

if __name__ == "__main__":
    main()
