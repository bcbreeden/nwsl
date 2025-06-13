# blog_loader.py
import os
import yaml

BLOG_DIR = "data/blog"

def load_blog_posts():
    posts = []
    for fname in os.listdir(BLOG_DIR):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(BLOG_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            if content.startswith('---'):
                _, frontmatter, body = content.split('---', 2)
                meta = yaml.safe_load(frontmatter)
                meta["body"] = body.strip()
                if not meta.get("draft", False):
                    posts.append(meta)
    posts.sort(key=lambda p: p["publish_date"], reverse=True)
    return posts

def get_post_by_slug(slug):
    for post in load_blog_posts():
        if post["slug"] == slug:
            return post
    return None
