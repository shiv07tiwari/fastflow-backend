import asyncio

from nodes.base_node import BaseNode, NodeType, BaseNodeInput, InputType
from services.youtube_scraper import fetch_youtube_comments


class YouTubeCommentsRetriever(BaseNode):

    def __init__(self, **kwargs):
        if kwargs:
            super().__init__(**kwargs)
        else:
            inputs = [
                BaseNodeInput("video_id", InputType.COMMON, "text", is_required=True),
                BaseNodeInput("max_results", InputType.INTERNAL_ONLY, "text"),
            ]
            super().__init__(
                id='yt_comments',
                name="YouTube Comments Retriever",
                icon_url="https://cdn-icons-png.flaticon.com/512/174/174883.png",
                description="Scrape comments from YouTube videos",
                node_type=NodeType.AI.value,
                is_active=True,
                inputs=inputs,
                outputs=["comment_authors", "comment_texts", "comment_likes", "comment_dates"],
                **kwargs
            )

    async def execute(self, input: dict) -> list:
        video_id = input.get("video_id", '')
        
        try:
            max_results = int(input.get("max_results", 100))
        except Exception:
            max_results = 100

        if not isinstance(video_id, list):
            video_id = [video_id]

        response = []
        for vid in video_id:
            promise = asyncio.to_thread(fetch_youtube_comments, vid, max_results)
            response.append(promise)

        response = await asyncio.gather(*response)

        final_response = []
        for comments in response:
            comment_authors = "\n".join([comment['author'] for comment in comments])
            comment_texts = "<sep>".join([comment['text'] for comment in comments])
            comment_likes = "\n".join([str(comment['likes']) for comment in comments])
            comment_dates = "\n".join([comment['published_at'] for comment in comments])
            
            final_response.append({
                "comment_authors": comment_authors,
                "comment_texts": comment_texts,
                "comment_likes": comment_likes,
                "comment_dates": comment_dates
            })

        return final_response
