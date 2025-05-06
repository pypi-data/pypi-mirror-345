
from lb2ticket.model.base_model import BaseModel
from dataclasses import dataclass

@dataclass
class Ticket(BaseModel):
    id = None
    title = None
    description = None
    number = None
    clientId = None
    clientName = None
    action = None
    action_time = None

    def __init__(self, title=None, description=None, action=None, action_time=None):
        self.description = description
        self.title=title
        self.action = action
        self.action_time

    # @property
    def serialize(self):
        return {
           'id': self.id,
           'title': self.title,
           'description': self.description,
           'number': self.number,
           'clientId': self.clientId,
           'clientName': self.clientName,
           'action': self.action
        }
	
@dataclass
class CloseTicket(BaseModel):
    id = None
    resolution = None
    action_time = None

    def __init__(self, id=None, resolution=None, action_time=None):
        self.id = id
        self.resolution=resolution
        self.action_time = action_time

    # @property
    def serialize(self):
        return {
           'id': self.id,
           'resolution': self.resolution
        }