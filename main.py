
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

    return posts
    previous_posts = get_previous_posts()
    previous_posts_text = "\n".join(previous_posts)
```python
theme = random.choice(themes)
previous_posts = get_previous_posts()

prompt = f"""
You are the founder of SocialFuse.

Theme:
{theme}

Here are my previous posts:

{previous_posts}

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

for _ in range(3):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        candidate = response.choices[0].message.content.strip()

        # Prevent exact duplicates
        if candidate not in previous_posts:
            post = candidate
            break

    except Exception as e:
        print(e)

if post is None:
    raise Exception("Failed to generate a unique post after 3 attempts.")
```
print(r.text)
