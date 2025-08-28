import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========================================================
# TOOL LIST + CATEGORY MAPPING
# ========================================================
tool_categories = {
    # --- LLMs & Chatbots ---
    "ChatGPT": "LLMs & Chatbots",
    "Claude": "LLMs & Chatbots",
    "Gemini": "LLMs & Chatbots",
    "Grok": "LLMs & Chatbots",
    "Perplexity": "LLMs & Chatbots",
    "Mistral": "LLMs & Chatbots",
    "LLaMA": "LLMs & Chatbots",
    "Command R+": "LLMs & Chatbots",
    "Open Assistant": "LLMs & Chatbots",
    "Anthropic": "LLMs & Chatbots",
    "Pi AI": "LLMs & Chatbots",

    # --- Open Source Models ---
    "Falcon": "Open Source Models",
    "Dolly": "Open Source Models",
    "StableLM": "Open Source Models",
    "Vicuna": "Open Source Models",
    "Alpaca": "Open Source Models",
    "Orca": "Open Source Models",
    "Mixtral": "Open Source Models",
    "Phi": "Open Source Models",
    "DeepSeek": "Open Source Models",

    # --- Image/Video/Audio Generation ---
    "Stable Diffusion": "Image/Video/Audio Generation",
    "DALL-E": "Image/Video/Audio Generation",
    "MidJourney": "Image/Video/Audio Generation",
    "Runway": "Image/Video/Audio Generation",
    "Leonardo AI": "Image/Video/Audio Generation",
    "Pika Labs": "Image/Video/Audio Generation",
    "Gen-2 Runway": "Image/Video/Audio Generation",
    "Kaiber": "Image/Video/Audio Generation",
    "Synthesia": "Image/Video/Audio Generation",
    "Scenario": "Image/Video/Audio Generation",

    # --- Speech/Audio ---
    "Whisper": "Speech/Audio",
    "ElevenLabs": "Speech/Audio",
    "Hugging Face Audio": "Speech/Audio",
    "Descript": "Speech/Audio",
    "Play.ht": "Speech/Audio",

    # --- Vector Databases ---
    "Pinecone": "Vector Databases",
    "Weaviate": "Vector Databases",
    "Chroma": "Vector Databases",
    "Milvus": "Vector Databases",
    "Vespa": "Vector Databases",
    "Redis Vector": "Vector Databases",
    "Qdrant": "Vector Databases",

    # --- Frameworks & Libraries ---
    "LangChain": "Frameworks & Libraries",
    "LlamaIndex": "Frameworks & Libraries",
    "Haystack": "Frameworks & Libraries",
    "DSPy": "Frameworks & Libraries",
    "Transformers": "Frameworks & Libraries",
    "Diffusers": "Frameworks & Libraries",
    "OpenVINO": "Frameworks & Libraries",
    "DeepSpeed": "Frameworks & Libraries",
    "Accelerate": "Frameworks & Libraries",

    # --- MLOps & Orchestration ---
    "MLflow": "MLOps & Orchestration",
    "Weights & Biases": "MLOps & Orchestration",
    "ClearML": "MLOps & Orchestration",
    "Kubeflow": "MLOps & Orchestration",
    "Prefect": "MLOps & Orchestration",
    "Airflow": "MLOps & Orchestration",
    "Ray": "MLOps & Orchestration",
    "Flyte": "MLOps & Orchestration",

    # --- Cloud AI Platforms ---
    "Azure AI": "Cloud AI Platforms",
    "AWS Bedrock": "Cloud AI Platforms",
    "Google Vertex AI": "Cloud AI Platforms",
    "Cohere": "Cloud AI Platforms",
    "AI21 Labs": "Cloud AI Platforms",

    # --- Code Generation ---
    "Copilot": "Code Generation",
    "CodeWhisperer": "Code Generation",
    "Tabnine": "Code Generation",
    "Replit AI": "Code Generation",

    # --- Productivity / Agents ---
    "AutoGPT": "Productivity / Agents",
    "BabyAGI": "Productivity / Agents",
    "CrewAI": "Productivity / Agents",
    "Langroid": "Productivity / Agents",
    "Voyager": "Productivity / Agents",
    "Devin AI": "Productivity / Agents",
}

# Extract tool list directly from keys
tools = list(tool_categories.keys())


# ========================================================
# WEEKLY WINDOWS
# ========================================================
def get_weeks(num_weeks=4):
    today = datetime.today().date()
    weeks = []
    start_week = today - timedelta(days=today.weekday())
    for i in range(num_weeks):
        ws = start_week - timedelta(weeks=i)
        we = ws + timedelta(days=6)
        weeks.append((ws, we))
    return list(reversed(weeks))


# ========================================================
# STACKOVERFLOW (Simulated)
# ========================================================
def so_get_mentions(tool, start_date, end_date):
    return abs(hash(tool + str(start_date) + str(end_date))) % 200

def fetch_stackoverflow(weeks):
    data = []
    for week_start, week_end in weeks:
        for tool in tools:
            count = so_get_mentions(tool, str(week_start), str(week_end))
            data.append({
                "tool_name": tool,
                "category": tool_categories.get(tool, "Other"),
                "platform": "StackOverflow",
                "start_week": str(week_start),
                "end_week": str(week_end),
                "popularity_score": count
            })
    return pd.DataFrame(data)


# ========================================================
# HACKERNEWS
# ========================================================
def hn_get_mentions(tool, start_date, end_date):
    base_url = "https://hn.algolia.com/api/v1/search"
    page = 0
    num_stories = total_points = total_comments = 0

    while True:
        params = {
            "query": tool,
            "tags": "story",
            "hitsPerPage": 1000,
            "page": page,
            "numericFilters": f"created_at_i>{int(datetime.combine(start_date, datetime.min.time()).timestamp())},created_at_i<{int(datetime.combine(end_date, datetime.max.time()).timestamp())}"
        }
        response = requests.get(base_url, params=params, verify=False)
        if response.status_code != 200:
            break
        data = response.json()
        hits = data.get("hits", [])
        if not hits:
            break
        num_stories += len(hits)
        total_points += sum(hit.get("points", 0) for hit in hits)
        total_comments += sum(hit.get("num_comments", 0) for hit in hits)
        if page >= data.get("nbPages", 0) - 1:
            break
        page += 1
        time.sleep(0.5)
    return num_stories + total_points + total_comments

def fetch_hackernews(weeks):
    data = []
    for week_start, week_end in weeks:
        for tool in tools:
            score = hn_get_mentions(tool, week_start, week_end)
            data.append({
                "tool_name": tool,
                "category": tool_categories.get(tool, "Other"),
                "platform": "HackerNews",
                "start_week": str(week_start),
                "end_week": str(week_end),
                "popularity_score": score
            })
    return pd.DataFrame(data)


# ========================================================
# GITHUB
# ========================================================
GITHUB_API_URL = "https://api.github.com/search/repositories"
TOKEN = ""  # insert GitHub token if needed

def fetch_github_tools(limit=50, topic="llm"):
    headers = {"Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    params = {"q": f"topic:{topic}", "sort": "stars", "order": "desc", "per_page": limit}
    response = requests.get(GITHUB_API_URL, headers=headers, params=params, verify=False)
    response.raise_for_status()
    data = response.json()
    repos = []
    for repo in data.get("items", []):
        repos.append([repo["name"], repo["stargazers_count"]])
    return repos

def fetch_github(weeks, limit=50, topic="llm"):
    all_data = []
    repos = fetch_github_tools(limit=limit, topic=topic)
    for week_start, week_end in weeks:
        for name, stars in repos:
            all_data.append({
                "tool_name": name,
                "category": tool_categories.get(name, "Other"),
                "platform": "GitHub",
                "start_week": str(week_start),
                "end_week": str(week_end),
                "popularity_score": stars
            })
    return pd.DataFrame(all_data)


# ========================================================
# PRODUCT HUNT (Simulated)
# ========================================================
def ph_get_likes(tool, start_date, end_date):
    return abs(hash("PH" + tool + str(start_date) + str(end_date))) % 150

def fetch_producthunt(weeks):
    data = []
    for week_start, week_end in weeks:
        for tool in tools:
            likes = ph_get_likes(tool, str(week_start), str(week_end))
            data.append({
                "tool_name": tool,
                "category": tool_categories.get(tool, "Other"),
                "platform": "ProductHunt",
                "start_week": str(week_start),
                "end_week": str(week_end),
                "popularity_score": likes
            })
    return pd.DataFrame(data)


# ========================================================
# YOUTUBE (Simulated)
# ========================================================
def yt_get_views(tool, start_date, end_date):
    return abs(hash("YT" + tool + str(start_date) + str(end_date))) % 1_000_000

def fetch_youtube(weeks):
    data = []
    for week_start, week_end in weeks:
        for tool in tools:
            views = yt_get_views(tool, str(week_start), str(week_end))
            data.append({
                "tool_name": tool,
                "category": tool_categories.get(tool, "Other"),
                "platform": "YouTube",
                "start_week": str(week_start),
                "end_week": str(week_end),
                "popularity_score": views
            })
    return pd.DataFrame(data)


# ========================================================
# RUN ALL + MERGE
# ========================================================
def run_all():
    weeks = get_weeks(4)

    df_so = fetch_stackoverflow(weeks)
    print("✅ StackOverflow done")

    df_hn = fetch_hackernews(weeks)
    print("✅ HackerNews done")

    df_gh = fetch_github(weeks)
    print("✅ GitHub done")

    df_ph = fetch_producthunt(weeks)
    print("✅ ProductHunt done")

    df_yt = fetch_youtube(weeks)
    print("✅ YouTube done")

    final_df = pd.concat([df_so, df_hn, df_gh, df_ph, df_yt], ignore_index=True)
    final_df.to_csv("combined_trends.csv", index=False)
    print("🎯 All platforms merged into combined_trends.csv with category column added")

if __name__ == "__main__":
    run_all()
