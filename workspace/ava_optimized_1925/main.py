# Dre Proprietary
# Copyright (c) 2023, Ava Optimized 1925
# All rights reserved.

# Importing required libraries
import logging
import os
import sys
from typing import Dict, List

# Setting up logging configuration
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("ava_optimized_1925.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

# Domain-Driven Design (DDD) entities
class User:
    def __init__(self, id: int, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email

class Project:
    def __init__(self, id: int, name: str, description: str):
        self.id = id
        self.name = name
        self.description = description

class Task:
    def __init__(self, id: int, name: str, description: str, status: str):
        self.id = id
        self.name = name
        self.description = description
        self.status = status

# Domain-Driven Design (DDD) repositories
class UserRepository:
    def __init__(self):
        self.users = []

    def save(self, user: User):
        self.users.append(user)

    def get(self, id: int) -> User:
        for user in self.users:
            if user.id == id:
                return user
        return None

class ProjectRepository:
    def __init__(self):
        self.projects = []

    def save(self, project: Project):
        self.projects.append(project)

    def get(self, id: int) -> Project:
        for project in self.projects:
            if project.id == id:
                return project
        return None

class TaskRepository:
    def __init__(self):
        self.tasks = []

    def save(self, task: Task):
        self.tasks.append(task)

    def get(self, id: int) -> Task:
        for task in self.tasks:
            if task.id == id:
                return task
        return None

# Domain-Driven Design (DDD) services
class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(self, name: str, email: str) -> User:
        user = User(len(self.user_repository.users) + 1, name, email)
        self.user_repository.save(user)
        return user

    def get_user(self, id: int) -> User:
        return self.user_repository.get(id)

class ProjectService:
    def __init__(self, project_repository: ProjectRepository):
        self.project_repository = project_repository

    def create_project(self, name: str, description: str) -> Project:
        project = Project(len(self.project_repository.projects) + 1, name, description)
        self.project_repository.save(project)
        return project

    def get_project(self, id: int) -> Project:
        return self.project_repository.get(id)

class TaskService:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    def create_task(self, name: str, description: str, status: str) -> Task:
        task = Task(len(self.task_repository.tasks) + 1, name, description, status)
        self.task_repository.save(task)
        return task

    def get_task(self, id: int) -> Task:
        return self.task_repository.get(id)

# Main application logic
def main():
    user_repository = UserRepository()
    project_repository = ProjectRepository()
    task_repository = TaskRepository()

    user_service = UserService(user_repository)
    project_service = ProjectService(project_repository)
    task_service = TaskService(task_repository)

    # Create users
    user1 = user_service.create_user("John Doe", "john.doe@example.com")
    user2 = user_service.create_user("Jane Doe", "jane.doe@example.com")

    # Create projects
    project1 = project_service.create_project("Project 1", "This is project 1")
    project2 = project_service.create_project("Project 2", "This is project 2")

    # Create tasks
    task1 = task_service.create_task("Task 1", "This is task 1", "In Progress")
    task2 = task_service.create_task("Task 2", "This is task 2", "Done")

    # Log created entities
    logging.info(f"Created user: {user1.name} ({user1.id})")
    logging.info(f"Created user: {user2.name} ({user2.id})")
    logging.info(f"Created project: {project1.name} ({project1.id})")
    logging.info(f"Created project: {project2.name} ({project2.id})")
    logging.info(f"Created task: {task1.name} ({task1.id})")
    logging.info(f"Created task: {task2.name} ({task2.id})")

if __name__ == "__main__":
    main()