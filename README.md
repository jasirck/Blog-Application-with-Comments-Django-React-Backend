# Django Blog API with JWT Authentication

## Overview
This is a backend API for a blog application built with Django and Django REST framework (DRF), using JWT for authentication. The API supports user authentication, blog post creation, commenting, and liking posts.

## Features
- JWT authentication (Login, Register, Logout)
- CRUD operations for blog posts
- Nested comments for posts
- Like/unlike functionality
- Filtering, searching, and sorting posts
- Soft delete for posts

---

## Installation and Setup

### 1. Clone the repository:
```bash
git clone https://github.com/jasirck/Blog-Application-with-Comments-Django-React-Backend.git
cd Blog-Application-with-Comments-Django-React-Backend
```

### 2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate 
```

### 3. Install dependencies:
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables:
Create a `.env` file and add the following:
```
SECRET_KEY='django-insecure-2)tr*i6!-c_6q-5qh^b(_fqkfe1$j*ip)p!@))!5ofo$fem+qz'
DEBUG=True
ALLOWED_HOSTS='http://127.0.0.1:8000/'
```

### 5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```


### 6. Run the server:
```bash
python manage.py runserver
```

---

## Authentication

### Register a new user:
**POST** `/api/auth/register/`
```json
{
  "username": "exampleuser",
  "email": "user@example.com",
  "password": "securepassword"
}
```

### Login:
**POST** `/api/auth/login/`
```json
{
  "username": "exampleuser",
  "password": "securepassword"
}
```
Response:
```json
{
  "access": "your_jwt_access_token",
  "refresh": "your_jwt_refresh_token"
}
```



## API Endpoints

### Blog Posts
- **GET** `/api/posts/` - List all posts
- **POST** `/api/posts/` - Create a new post
- **GET** `/api/posts/<id>/` - Retrieve a post
- **PUT** `/api/posts/<id>/` - Update a post
- **DELETE** `/api/posts/<id>/` - Soft delete a post

### Comments
- **GET** `/api/comments/?post=<post_id>` - Get comments for a post
- **POST** `/api/comments/` - Add a comment
- **DELETE** `/api/comments/<id>/` - Delete a comment

### Likes
- **POST** `/api/posts/<id>/like/` - Like or unlike a post

