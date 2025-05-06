from lb2ticket.model.base_model import BaseModel
from dataclasses import dataclass

@dataclass
class Task(BaseModel):
    id = None
    title = None
    number = None
    ticketId = None
    action_time = None

    def __init__(self, title=None, ticket_id=None, action_time=None):
        self.title = title
        self.ticketId=ticket_id
        self.action_time = action_time

    # @property
    def serialize(self):
        return {
           'id': self.id,
           'title': self.title,
           'number': self.number,
           'ticketId': self.ticketId
        }
    
@dataclass
class CloseTask(BaseModel):
    id = None
    comment = None
    action_time = None

    def __init__(self, comment=None, id=None, action_time=None):
        self.comment = comment
        self.id=id
        self.action_time = action_time
    
    # @property
    def serialize(self):
        return {
           'id': self.id,
           'comment': self.comment
        }