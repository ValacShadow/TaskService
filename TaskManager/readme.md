# Task Management System

A Django-based web application for managing tasks with user roles and API integration.

## Features

- **User Roles**: 
  - Manager (View all tasks, assign to any user)
  - Executive (View only assigned/created tasks)
- **Task Management**:
  - Create tasks with name, description, due date, and status
  - Assign tasks to multiple users
  - Filter tasks by status and due date
- **API Integration**:
  - RESTful APIs for all operations
- **User Interface**:
  - Login funcitonality
  - Dashboard to show all tasks. 
  - Real-time filtering
  - Searchable user assignment
  - Create task form

## Technologies Used

- Django 4.x
- Django REST Framework
- SQLite (Default)
- HTML5/CSS3
- JavaScript (Vanilla)

## Setup Instructions

### Prerequisites
- Python 3.9+

### Installation
create superuser 
I have also shared the endpoints file, for postman


### API Endpoints

Method	Endpoint	                    Description
POST	/api/tasks/add 	            Create new task
PATCH	/api/tasks/{id}/assign/	    Assign task to users
GET	    /api/users/{id}/tasks/	        Get tasks for specific user
GET	    /api/task-types/	            Get available task types
GET	    /api/users/	                    Get all users


## Steps 
- Create a super user, using python manage.py createsuperuser
- you cna create more users from admin panel.
- You can use apis through frontend or postman
- You have to provide basic auth to create tasks.
