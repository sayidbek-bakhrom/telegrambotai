from pydantic import BaseModel

class MessageRequest(BaseModel):
    """
    Model for incoming chat message request.

    Attributes:
        user_id (int): Telegram user ID sending the message.
        message (str): The message text from the user.
    """
    user_id: int
    message: str


class SummarizeRequest(BaseModel):
    """
    Model for incoming summarization request.

    Attributes:
        text (str): The text content to summarize.
    """
    text: str
