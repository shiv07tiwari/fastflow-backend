import asyncio

from nodes.base_node import BaseNode, NodeType, BaseNodeInput, InputType
from services.reddit import RedditService


class RedditBotNode(BaseNode):

    def __init__(self, **kwargs):
        if kwargs:
            super().__init__(**kwargs)
        else:
            inputs = [
                BaseNodeInput("query", InputType.COMMON, "text", is_required=True),
                BaseNodeInput("subreddit", InputType.COMMON, "text"),
                BaseNodeInput("post_limit", InputType.INTERNAL_ONLY, "text"),
            ]
            super().__init__(
                id='reddit_bot',
                name="Reddit Bot",
                icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
                description="Scrape data from reddit",
                node_type=NodeType.AI.value,
                is_active=True,
                inputs=inputs,
                outputs=["post_titles", "post_contents", "post_urls"],
                **kwargs
            )

    async def execute(self, input: dict) -> []:
        service = RedditService()
        subreddit = input.get("subreddit", None)
        query = input.get("query", '')

        if isinstance(subreddit, list):
            raise ValueError("Subreddit should be a string")

        if not isinstance(query, list):
            query = [query]

        try:
            post_limit = int(input.get("post_limit", 10))
        except Exception:
            post_limit = 10

        response = []
        for q in query:
            promise = service.search_reddit(q, subreddit, post_limit)
            response.append(promise)

        response = await asyncio.gather(*response)

        final_response = []
        for data in response:
            post_titles = "\n".join(data["title"].values)
            post_contents = "\n".join(data["body"].values)
            post_urls = "\n".join(data["url"].values)
            final_response.append({
                "post_titles": post_titles,
                "post_contents": post_contents,
                "post_urls": post_urls
            })

        return final_response
