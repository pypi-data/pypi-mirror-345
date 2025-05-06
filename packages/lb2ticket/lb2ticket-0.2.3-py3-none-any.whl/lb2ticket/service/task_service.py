from typing import Optional
from lb2ticket.service.api_service import APIService, ApiException
from lb2ticket.model.task import Task, CloseTask  


class TaskService(APIService):
    def __init__(self, application_config):
        super().__init__(application_config=application_config)
        self.base_url = "/v1/task/"

    def create(self, ticket_id: str, title: str, action_time: int) -> Task:
        task = Task(ticket_id=ticket_id, title=title, action_time=action_time)
        json = self.post(task.serialize())
        new_task = Task()
        new_task.load_json(json)
        return new_task

    def find_by_id(self, task_id: str) -> Task:
        json =self.get(f"/{task_id}")
        task = Task()
        task.load_json(json)
        return task 

    def close(self, task_id: str, resolution: str, action_time: int):
        close_task = CloseTask(id=task_id, comment=resolution, action_time=action_time)
        self.put(path=f"/{task_id}/close", obj=close_task.serialize())

    def execute(self, task_id: str, action_time: int):
        self.put(path=f"/{task_id}/execute/{action_time}")

    def create_scaled(self, ticket_id: str, title: str, action_time: int) -> Task:
        task = Task(ticket_id=ticket_id, title=title, action_time=action_time)
        json = self.post(task.serialize(), path=f"{ticket_id}/scaled")
        task = Task()
        task.load_json(json)
        return task
