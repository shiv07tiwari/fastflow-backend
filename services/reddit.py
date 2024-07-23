import os
from datetime import datetime

import pandas as pd
import praw


class RedditService:

    def __init__(self):
        try:
            self.client = reddit = praw.Reddit(
                client_id=os.getenv("REDDIT_CLIENT_ID", None),
                client_secret=os.getenv("REDDIT_CLIENT_SECRET", None),
                password=os.getenv("REDDIT_PASSWORD", None),
                username=os.getenv("REDDIT_USERNAME", None),
                user_agent=os.getenv("REDDIT_USER_AGENT", None),
            )
            print(reddit.user.me())
        except Exception as e:
            print("Error creating Reddit client: ", e)
            self.client = None

    def fetch_subreddit_posts(self, subreddit_name, post_limit=10):

        if not self.client:
            return pd.DataFrame()

        subreddit = self.client.subreddit(subreddit_name)

        # Fetch hot posts
        posts = []
        for post in subreddit.hot(limit=post_limit):
            posts.append([
                post.title,
                post.score,
                post.id,
                post.subreddit,
                post.url,
                post.num_comments,
                post.selftext,
                datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S')
            ])

        # Create a DataFrame
        df = pd.DataFrame(posts,
                          columns=['title', 'score', 'id', 'subreddit', 'url', 'num_comments', 'body', 'created'])
        return df

    async def search_reddit(self, query, subreddit_name=None, post_limit=10):

        if not self.client:
            return pd.DataFrame()

        if subreddit_name:
            subreddit = self.client.subreddit(subreddit_name)
            search_results = subreddit.search(query, limit=post_limit)
        else:
            search_results = self.client.subreddit("all").search(query, limit=post_limit)

        posts = []
        for post in search_results:
            posts.append([
                post.title,
                post.score,
                post.id,
                post.subreddit.display_name,
                post.url,
                post.num_comments,
                post.selftext,
                datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S')
            ])

        # Create a DataFrame
        df = pd.DataFrame(posts,
                          columns=['title', 'score', 'id', 'subreddit', 'url', 'num_comments', 'body', 'created'])
        # Return only the body of the post

        return df