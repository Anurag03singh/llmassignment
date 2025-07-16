import praw
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

def fetch_user_content(username, limit=50):
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT")
    )

    posts = []
    comments = []
    profile = {}
    try:
        user = reddit.redditor(username)
        user._fetch()  # Force fetch to populate all fields
        if getattr(user, "is_suspended", False):
            profile = {"error": "User is suspended.", "is_suspended": True}
            return {"profile": profile, "content": []}
        profile = {
            "name": user.name,
            "created_utc": user.created_utc,
            "created_date": datetime.utcfromtimestamp(user.created_utc).strftime('%Y-%m-%d') if user.created_utc else None,
            "icon_img": getattr(user, "icon_img", None),
            "comment_karma": getattr(user, "comment_karma", None),
            "link_karma": getattr(user, "link_karma", None),
            "is_employee": getattr(user, "is_employee", None),
            "is_mod": getattr(user, "is_mod", None),
            "is_gold": getattr(user, "is_gold", None),
            "has_verified_email": getattr(user, "has_verified_email", None),
            "subreddit": getattr(user, "subreddit", None),
            "is_suspended": getattr(user, "is_suspended", False),
        }
        for post in user.submissions.new(limit=limit):
            posts.append(f"[POST] {post.title}: {post.selftext}")
        for comment in user.comments.new(limit=limit):
            comments.append(f"[COMMENT] {comment.body}")
    except praw.exceptions.RedditAPIException as e:
        profile = {"error": f"Reddit API error: {e}"}
    except praw.exceptions.PRAWException as e:
        profile = {"error": f"PRAW error: {e}"}
    except Exception as e:
        if "404" in str(e) or "NotFound" in str(e):
            profile = {"error": "User does not exist or is deleted."}
        else:
            profile = {"error": str(e)}
    return {"profile": profile, "content": posts + comments}