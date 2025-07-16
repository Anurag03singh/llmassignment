# Reddit Persona Generator

## Overview
This project generates detailed user personas by analyzing Reddit user activity (posts and comments). It leverages Large Language Models (LLMs) to synthesize a persona profile from Reddit data. The codebase is designed to run both locally (using open-source models) and via web APIs (OpenAI, Gemini), but is primarily focused on local execution for privacy, cost, and flexibility.

## Features
- Scrapes Reddit user posts and comments using PRAW
- Generates a structured persona profile in Markdown format
- Supports multiple LLM backends:
  - **Local**: Mistral 7B Instruct (via llama-cpp-python)
  - OpenAI GPT (if API key provided)
  - Google Gemini (if API key provided)
- Outputs persona files to the `output/` directory

## Local Model Focus
While the codebase can be configured to use OpenAI or Gemini APIs, it is optimized for local inference using the **Mistral 7B Instruct** model. This approach ensures:
- No data leaves your machine
- No API costs or rate limits
- Full control over the model and inference

## Why Not Deployed Yet?
Deployment (especially with OpenAI APIs) was taking significant time due to API rate limits, quota management, and the need for robust error handling. For this reason, the project is currently intended for local use. Web deployment can be added in the future as API handling is improved.

## Requirements
- Python 3.9+
- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python)
- [praw](https://praw.readthedocs.io/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- (Optional) [google-generativeai](https://pypi.org/project/google-generativeai/) for Gemini
- (Optional) [openai](https://pypi.org/project/openai/) for OpenAI
- Mistral 7B Instruct model file (`mistral-7b-instruct-v0.1.Q4_0.gguf`) in `./models/`

## Setup
1. **Clone the repository**
2. **Install dependencies:**
   ```bash
   python3 -m pip install -r requirements.txt
   ```
3. **Download the Mistral 7B Instruct model** and place it in the `models/` directory:
   - [Get the model here](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1-GGUF)
   - Place as `./models/mistral-7b-instruct-v0.1.Q4_0.gguf`
4. **Set up your Reddit API credentials:**
   - Create a `.env` file in the project root:
     ```
     REDDIT_CLIENT_ID=your_client_id
     REDDIT_CLIENT_SECRET=your_client_secret
     REDDIT_USER_AGENT=your_user_agent
     ```
5. **(Optional) Add OpenAI or Gemini API keys to `.env` if you want to use those backends.**
6. **Create the output directory:**
   ```bash
   mkdir -p output
   ```

## Usage
### Local (Recommended)
```bash
export LLM_BACKEND=local
python3 main.py
```
- Enter the Reddit username or profile URL when prompted.
- The persona will be saved in the `output/` directory.

### Web API (Optional)
- To use OpenAI or Gemini, set `LLM_BACKEND=openai` or `LLM_BACKEND=gemini` and provide the appropriate API key in your `.env` file.

## Code Style
It is recommended to follow [PEP-8 guidelines](https://peps.python.org/pep-0008/) for all Python code in this project.

## Notes
- The project is currently not deployed as a web service due to the time required to robustly handle OpenAI API quotas and errors.
- Local inference is the primary, most robust mode.
- Contributions and improvements are welcome! 
