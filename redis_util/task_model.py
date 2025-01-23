from typing import Optional


class Task:
    def __init__(
        self,
        chat_id: Optional[int] = None,
        user_id: Optional[int] = None,
        message_id: Optional[int] = None,
        file_id: Optional[str] = None,
        mime_type: Optional[str] = None,
        filter_type: Optional[str] = None,
        text: Optional[str] = None
    ):
        self.chat_id = chat_id
        self.user_id = user_id
        self.message_id = message_id
        self.file_id = file_id
        self.mime_type = mime_type
        self.filter_type = filter_type
        self.text = text
    
    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.chat_id = data.get("chat_id")
        obj.user_id = data.get("user_id")
        obj.message_id = data.get("message_id")
        obj.file_id = data.get("file_id")
        obj.mime_type = data.get("mime_type")
        obj.filter_type = data.get("filter_type")
        obj.text = data.get("text")
        return obj