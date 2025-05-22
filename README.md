# Django Article Publisher

A lightweight article publishing website built with Django. This application allows administrators to create, edit, and delete articles, while providing a clean interface for visitors to read published content.

## Features

- Public pages for viewing articles
- Admin-only pages for content management
- Rich text editor supporting plain text, BBCode, and HTML
- Custom URL slugs for each article
- Image uploads with caption support
- Article categorization and tagging
- Search functionality by title and content
- Responsive design for all devices

## Prerequisites

- Python 3.9 or higher
- Django 4.2.7
- Pillow 10.1.0 (for image processing)

## Project Structure

```
article_publisher/
├── article_publisher/      # Project settings
├── articles/               # Main application
│   ├── migrations/         # Database migrations
│   ├── static/             # Static files
│   ├── templates/          # HTML templates
│   ├── admin.py            # Admin configuration
│   ├── forms.py            # Form definitions
│   ├── models.py           # Data models
│   ├── urls.py             # URL routing
│   ├── utils.py            # Utility functions
│   └── views.py            # View controllers
├── media/                  # Uploaded files
├── manage.py               # Django management script
└── README.md               # Project documentation
```

## Setup Instructions

1. **Clone the repository**

2. **Create a virtual environment**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Set up the database**
   ```
   python manage.py migrate
   ```

5. **Create a superuser (admin)**
   ```
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```
   python manage.py runserver
   ```

7. **Access the website**
   - Home page: http://127.0.0.1:8000/
   - Admin login: http://127.0.0.1:8000/login/
   - Admin dashboard: http://127.0.0.1:8000/published/

## Usage

### For Visitors
- Browse articles at `/articles/`
- View individual articles at `/article/<slug>/`

### For Administrators
- Log in at `/login/` with your superuser credentials
- Create new articles at `/publish/`
- Manage existing articles at `/published/`
- Edit an article at `/edit/<slug>/`

## Features Documentation

### Content Formats
The system supports three content formats:
- **Plain Text**: Simple text with line breaks
- **BBCode**: Lightweight markup with tags like `[b]`, `[i]`, `[url]`
- **HTML**: Full HTML support for advanced formatting

### Image Management
- Featured image for each article
- Additional images with captions
- Automatic storage in organized directories

### Content Organization
- Categories for broad classification
- Tags for more specific grouping
- Search functionality across titles and content

## License

This project is licensed under the MIT License.