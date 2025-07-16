import os

# Only import OpenAI and llama_cpp if needed

def load_model(llm_backend=None):
    if llm_backend is None:
        llm_backend = os.getenv("LLM_BACKEND", "openai")
    if llm_backend == "local":
        from llama_cpp import Llama
        model_path = "./models/mistral-7b-instruct-v0.1.Q4_0.gguf"
        llm = Llama(
            model_path=model_path,
            n_ctx=2048,
            chat_format="mistral-instruct"
        )
        return llm
    elif llm_backend == "openai":
        # No model object needed for OpenAI
        return None
    elif llm_backend == "gemini":
        import google.generativeai as genai
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set in environment.")
        genai.configure(api_key=api_key)
        # Use the most capable available Gemini model for text generation
        model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
        return model
    else:
        raise ValueError(f"Unknown llm_backend: {llm_backend}")

def estimate_token_count(text):
    return len(text) // 4

def generate_persona(content, model, username="Unknown", profile=None, persona_template=None, llm_backend=None):
    if llm_backend is None:
        llm_backend = os.getenv("LLM_BACKEND", "openai")
    profile_md = ""
    if profile:
        profile_md = "\nProfile Metadata:\n"
        for k, v in profile.items():
            if k == "subreddit" and isinstance(v, dict):
                profile_md += f"  - subreddit: {v.get('title', '')} | {v.get('public_description', '')}\n"
            else:
                profile_md += f"  - {k}: {v}\n"
    if persona_template:
        persona_format = persona_template
    else:
        persona_format = '''\n1. Name: Use the Reddit username as the name (e.g., "u/spez").\n2. Age, Occupation, Status, Location, Tier, Archetype: Leave these fields blank or as “Unknown” unless something is inferred from posts.\n3. Core Traits: Practical, Spontaneous, Adaptable, Active — mark presence if referenced in the Reddit content.\n4. Motivations: Evaluate and rate (1–5 bars or levels) the following:\n   - Convenience\n   - Wellness\n     - Speed\n   - Preferences\n   - Comfort\n   - Dietary Needs\n\n5. Personality: Rate user on:\n   - Introvert vs. Extrovert\n   - Intuition vs. Sensing\n   - Feeling vs. Thinking\n   - Perceiving vs. Judging\n\n6. Behaviour & Habits: Bullet list of inferred routines or behavioral patterns (with citation from posts/comments).\n\n7. Frustrations: Bullet list of complaints, pain points, or negative experiences mentioned (with citation).\n\n8. Goals & Needs: Bullet list of goals or desires from the user's posts/comments (with citation).\n\nFormat this all into a clear Markdown text block with labeled sections.\n'''
    static_prompt = f"""
You are an expert in user persona analysis.
Analyze the following Reddit posts/comments and profile metadata for user u/{username} and generate a persona in this Markdown format:
{persona_format}
{profile_md}
Reddit content:
"""
    max_tokens = 2048
    static_tokens = estimate_token_count(static_prompt)
    reserved_output_tokens = 1024
    available_tokens = max_tokens - static_tokens - reserved_output_tokens
    included_content = []
    used_tokens = 0
    for entry in content:
        entry_tokens = estimate_token_count(entry + "\n")
        if used_tokens + entry_tokens > available_tokens:
            break
        included_content.append(entry)
        used_tokens += entry_tokens
    truncated = len(included_content) < len(content)
    if truncated:
        print(f"⚠️  Truncated Reddit content to fit model context window. Only {len(included_content)} of {len(content)} items included.")
    prompt = static_prompt + "\n".join(included_content)
    if llm_backend == "local":
        output = model(
            prompt=prompt,
            max_tokens=1024,
            stop=["</s>"]
        )
        return output["choices"][0]["text"].strip()
    elif llm_backend == "openai":
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    elif llm_backend == "gemini":
        response = model.generate_content(prompt)
        return response.text.strip()
    else:
        raise ValueError(f"Unknown llm_backend: {llm_backend}")