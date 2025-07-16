import re
from reddit_scraper import fetch_user_content
from llm_persona_generator import load_model, generate_persona
import os

def extract_username(user_input):
    # Accepts either a username or a profile URL
    user_input = user_input.strip()
    # Regex for Reddit profile URL
    match = re.match(r"https?://(www\.)?reddit\.com/user/([A-Za-z0-9_-]+)/?", user_input)
    if match:
        return match.group(2)
    # If just a username (with or without u/ prefix)
    if user_input.startswith("u/"):
        return user_input[2:]
    return user_input

def check_citations(persona_text):
    # Check for citation markers in key sections
    issues = []
    sections = [
        ("Behaviour & Habits", r"## Behaviour & Habits(.*?)(##|$)", True),
        ("Frustrations", r"## Frustrations(.*?)(##|$)", True),
        ("Goals & Needs", r"## Goals & Needs(.*?)(##|$)", True),
    ]
    for section, pattern, must_have in sections:
        match = re.search(pattern, persona_text, re.DOTALL | re.IGNORECASE)
        if match:
            section_text = match.group(1)
            if must_have and not re.search(r"\[(POST|COMMENT)\]", section_text):
                issues.append(f"No citations found in section: {section}")
    return issues

def main():
    user_input = input("Enter Reddit username or profile URL: ").strip()
    username = extract_username(user_input)
    try:
        limit = int(input("How many posts/comments to fetch? [default 50]: ") or 50)
    except ValueError:
        limit = 50
    template_path = input("Optional: Path to persona template file (press Enter to use default): ").strip()
    persona_template = None
    if template_path:
        try:
            with open(template_path, "r", encoding="utf-8") as tf:
                persona_template = tf.read()
        except Exception as e:
            print(f"Could not read template file: {e}. Using default template.")
            persona_template = None
    result = fetch_user_content(username, limit=limit)

    profile = result.get("profile")
    content = result.get("content")

    # Improved error handling
    if not content or (profile and profile.get("is_suspended")):
        if profile and profile.get("is_suspended"):
            print("This user is suspended.")
        elif profile and profile.get("error"):
            print(f"Error fetching user: {profile['error']}")
        else:
            print("No content found.")
        return

    model = load_model()
    persona = generate_persona(content, model, username=username, profile=profile, persona_template=persona_template)

    # Post-process for missing citations
    citation_issues = check_citations(persona)
    if citation_issues:
        print("\n⚠️  Citation issues detected:")
        for issue in citation_issues:
            print("-", issue)

    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/{username}_persona.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(persona)

    print(f"\n✅ Persona saved to {output_path}")

if __name__ == "__main__":
    main()
