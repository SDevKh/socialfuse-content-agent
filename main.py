
import os
import random
import requests
from groq import Groq

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

themes = [
    "Building in Public",
    "Creator Pain Points",
    "Toxic Comments",
    "AI",
    "Marketing",
    "Product Updates",
    "Founder Lessons"
]

theme = random.choice(themes)

prompt = f"""
You are the founder of SocialFuse, an AI-powered Instagram comment moderation SaaS.

Generate ONE X post under 280 characters.

Theme: {theme}

Requirements:
- Human sounding
- No hashtags
- No emojis
- Slightly opinionated
- Valuable or thought-provoking
- Don't sound like marketing

Return only the post.
"""

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}]
)

post = response.choices[0].message.content.strip()

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

data = {
    "parent": {"database_id": DATABASE_ID},
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
        "Theme": {
            "select": {
                "name": theme
            }
        }
    }
}

r = requests.post(
    "https://api.notion.com/v1/pages",
    headers=headers,
    json=data
)
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

    results = response.json()["results"]

    posts = []

    for page in results:
        try:
            title = page["properties"]["X Post"]["title"][0]["text"]["content"]
            posts.append(title)
        except:
            pass

    return "\n".join(posts)

print(r.text)
