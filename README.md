# 💼 Work-connect

**Work-connect** is a comprehensive job portal platform that bridges the gap between companies and talented professionals. It enables businesses to discover and recruit skilled individuals while empowering job seekers to find their ideal employment opportunities and project-based work.

## ✨ Features

- **For Job Seekers**
  - Browse and search for job opportunities
  - Filter jobs by category, location, and skills
  - Apply to positions directly through the platform
  - Create and manage professional profiles
  - Discover project-based work opportunities

- **For Recruiters/Companies**
  - Post job openings and project listings
  - Search and filter through candidate profiles
  - Manage applications and candidate communications
  - Find skilled professionals for specific roles

- **General Features**
  - User authentication and profile management
  - Advanced search with pagination
  - Responsive design for all devices
  - Media upload support for resumes and company logos

## 🛠️ Technology Stack

- **Backend**: Python (Django Framework)
- **Frontend**: HTML, CSS
- **Database**: SQLite (development) / PostgreSQL (recommended for production)
- **Version Control**: Git

## 📁 Project Structure

Work-connect/
- jobPortal/ # Main application for job seekers
- recruiter/ # Application for recruiters/companies
- media/ # User-uploaded media files
- manage.py # Django management script
- db.sqlite3 # SQLite database file
- fix_templates.py # Template fix utility
- test.py # Testing script with search/pagination
- lab.py # Development utilities

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. Clone the repository
   git clone https://github.com/Abrehmant7/Work-connect.git
   cd Work-connect

2. Create and activate a virtual environment
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

3. Install dependencies
   pip install -r requirements.txt

4. Apply database migrations
   python manage.py migrate

5. Create a superuser (for admin access)
   python manage.py createsuperuser

6. Run the development server
   python manage.py runserver

7. Access the application
   Open your browser and go to: http://127.0.0.1:8000

## 🔧 Development

### Running Tests
python test.py

### Database Management
- To reset the database: Delete db.sqlite3 and run migrations again
- To create a new migration: python manage.py makemigrations
- To apply migrations: python manage.py migrate

### Template Fixes
If you encounter template-related issues, run:
python fix_templates.py

## 📦 Deployment

For production deployment, consider:

1. Switch to a production database (PostgreSQL, MySQL)
2. Set up a production web server (Gunicorn, uWSGI with Nginx)
3. Configure environment variables for sensitive data
4. Enable HTTPS/SSL
5. Set DEBUG = False in settings.py

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (git checkout -b feature/AmazingFeature)
3. Commit your changes (git commit -m 'Add some AmazingFeature')
4. Push to the branch (git push origin feature/AmazingFeature)
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 👥 Authors

- Abrehmant7 - Initial work and maintenance

## 🙏 Acknowledgments

- Django community for the excellent framework
- All contributors who help improve Work-connect

## 📧 Contact

For questions, suggestions, or issues, please open a GitHub issue or contact the repository owner.

---

Made with ❤️ for the job-seeking community
