```python
import os
import random
import requests
from groq import Groq

# Environment variables
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Groq client
client = Groq(api_key=GROQ_API_KEY)

# Themes
themes = [
    "Building in Public",
    "Creator Pain Points",
    "Toxic Comments",
    "AI",
    "Marketing",
    "Product Updates",
    "Founder Lessons"
]


def get_previous_posts():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    response = requests.post(
        url,
        headers=headers,
        json={
            "page_size": 20,
            "sorts": [
                {
                    "timestamp": "created_time",
                    "direction": "descending"
                }
            ]
        }
    )

    response.raise_for_status()

    results = response.json()["results"]

    posts = []

    for page in results:
        try:
            title = page["properties"]["X Post"]["title"][0]["text"]["content"]
            posts.append(title)
        except:
            pass

    return posts


# Get previous posts
previous_posts = get_previous_posts()
previous_posts_text = "\n".join(previous_posts)

# Choose a theme
theme = random.choice(themes)

# Prompt
prompt = f"""
You are the founder of SocialFuse.

Theme:
{theme}

Here are my previous posts:

{previous_posts_text}

Write ONE X post under 280 characters.

Requirements:
- Human sounding
- Slightly opinionated
- Share lessons, struggles, observations or contrarian thoughts
- Don't sell
- Avoid repeating previous ideas
- Avoid generic AI clichés
- No hashtags
- No emojis
- Occasionally ask a question

Return only the post.
"""

post = None

# Retry up to 3 times
for _ in range(3):
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b"
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        candidate = response.choices[0].message.content.strip()

        # Avoid exact duplicates
        if candidate.strip() not in [p.strip() for p in previous_posts]:
            post = candidate
            break

    except Exception as e:
        print(f"Groq Error: {e}")

if post is None:
    raise Exception("Failed to generate a unique post after 3 attempts.")

# Save to Notion
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

data = {
    "parent": {
        "database_id": DATABASE_ID
    },
    "properties": {
        "X Post": {
            "title": [
                {
                    "text": {
                        "content": post
                    }
                }
            ]
        },

    }
}

response = requests.post(
    "https://api.notion.com/v1/pages",
    headers=headers,
    json=data
)

print(response.status_code)
print(response.text)
response.raise_for_status()

print("Successfully added post to Notion.")
print(post)
```


