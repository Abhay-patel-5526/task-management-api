# Task Management API

A REST API for managing tasks with Flask, SQLAlchemy,
JWT authentication, and role-based authorization.

## Features

- User registration and login
- JWT authentication
- Protected API routes
- Role-based authorization
- Task CRUD operations
- User-task relationships
- Validation and error handling
- Filtering
- Pagination
- Postman API testing

## Tech Stack

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- JWT
- Postman

## API Endpoints

### Authentication

POST /api/register
POST /api/login

### Tasks

POST /api/tasks
GET /api/tasks
GET /api/tasks/<id>
PATCH /api/tasks/<id>
DELETE /api/tasks/<id>

...