import os
import json
from glob import glob

def load_discourse_chunks(discourse_dir):
    chunks = []
    files = glob(os.path.join(discourse_dir, "*.json"))

    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        title = data.get("title", "")
        url = data.get("url", "")
        posts = data.get("post_stream", {}).get("posts", [])

        if not posts:
            continue

        question = posts[0].get("cooked", "").replace("\n", " ").strip()
        replies = [p.get("cooked", "").replace("\n", " ").strip() for p in posts[1:] if p.get("cooked")]

        answer = " ".join(replies[:3])  # Take top 3 replies only

        chunks.append({
            "source": "discourse",
            "title": title,
            "url": url,
            "content": f"Q: {question}\nA: {answer}"
        })

    return chunks


def load_course_chunks(course_json_path):
    with open(course_json_path, "r", encoding="utf-8") as f:
        course = json.load(f)

    chunks = []

    # Modules
    for mod in course.get("modules", []):
        chunks.append({
            "source": "coursecontent",
            "title": f"Module: {mod['title']}",
            "content": f"{mod['title']} teaches how to {mod['purpose']}. Refer: {mod['link']}"
        })

    # Details sections (like: “This course is quite hard”)
    for section in course.get("details_sections", []):
        chunks.append({
            "source": "coursecontent",
            "title": f"Note: {section['heading']}",
            "content": section["content"]
        })

    # Evaluation table
    for row in course.get("grading_table", []):
        week = row.get("Week", "Unknown")
        row_content = ", ".join([f"{k}: {v}" for k, v in row.items()])
        chunks.append({
            "source": "coursecontent",
            "title": f"Evaluation - Week {week}",
            "content": row_content
        })

    return chunks


def main():
    discourse_dir = "discourse_data"
    coursecontent_path = "coursecontent_structured.json"
    output_path = "knowledge_chunks.jsonl"

    chunks = load_discourse_chunks(discourse_dir)
    chunks += load_course_chunks(coursecontent_path)

    with open(output_path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            json.dump(chunk, f, ensure_ascii=False)
            f.write("\n")

    print(f"✅ Extracted {len(chunks)} knowledge chunks to {output_path}")

if __name__ == "__main__":
    main()
