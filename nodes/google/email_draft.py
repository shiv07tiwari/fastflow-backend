import asyncio

from nodes.base_node import BaseNode, BaseNodeInput, InputType
from services.google import GoogleService


class EmailDraftNode(BaseNode):
    def __init__(self, **kwargs):
        if kwargs:
            super().__init__(**kwargs)
        else:
            inputs = [
                BaseNodeInput("from_email", InputType.COMMON, "text", is_required=True),
                BaseNodeInput("email_body", InputType.COMMON, "text", is_required=True),
                BaseNodeInput("to_email", InputType.COMMON, "text", is_required=True),
                BaseNodeInput("email_subject", InputType.COMMON, "text", is_required=True)
            ]
            super().__init__(
                id='email_draft',
                name="Gmail Draft",
                icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
                description="Create a Gmail draft",
                node_type="ACTION",
                inputs=inputs,
                outputs=["email_draft"],
            )

    async def execute(self, input: dict) -> []:
        email_subject = input.get("email_subject")
        from_email = input.get("from_email")
        to_email = input.get("to_email", [])
        email_body = input.get("email_body")

        service = GoogleService()

        if not isinstance(email_subject, list):
            email_subject = [email_subject]
        if not isinstance(email_body, list):
            email_body = [email_body]
        if not isinstance(to_email, list):
            to_email = [to_email]
        if not isinstance(from_email, list):
            from_email = [from_email]

        responses = []
        for i in range(len(email_subject)):
            _email_subject = email_subject[i] if i < len(email_subject) else ""
            _email_body = email_body[i] if i < len(email_body) else ""
            _to_email = to_email[i] if i < len(to_email) else ""
            _from_email = from_email[i] if i < len(from_email) else ""
            try:
                draft_email = service.draft_email(_email_body, _to_email, _from_email, _email_subject)
            except Exception as e:
                print(f"Error in executing node {self.name}: {e}")
                raise e
            responses.append(draft_email)

        responses = await asyncio.gather(*responses)
        return [
            {
                "email_draft": str(response)
            } for response in responses
        ]