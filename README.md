# Smart Report Generator

A Django-based web application for generating comprehensive student reports with data visualization capabilities.

## 🚀 Features

- Student report generation and management
- Data visualization using Matplotlib and Seaborn
- PDF report generation using FPDF2
- User-friendly web interface
- Student performance analytics
- Customizable report templates

## 🛠️ Technologies Used

- Python 3.11+
- Django 5.1.7
- Pillow (Python Imaging Library)
- FPDF2 for PDF generation
- Matplotlib for data visualization
- Seaborn for statistical data visualization

## 📋 Prerequisites

- Python 3.11 or higher
- Poetry (Python package manager)

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/emretuncer256/smart-report-generator.git
cd smart-report-generator
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Set up the database:
```bash
python manage.py migrate
```

4. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

## 💻 Usage

1. Access the web interface at `http://localhost:8000`
2. Log in with your credentials
3. Navigate through the dashboard to:
   - Generate student reports
   - View performance analytics
   - Export reports in PDF format
   - Manage student data

## 📁 Project Structure

```
SmartReportGenerator/
├── report/              # Main application directory
│   ├── models.py       # Database models
│   ├── views.py        # View logic
│   ├── urls.py         # URL routing
│   ├── utils.py        # Utility functions
│   └── templates/      # HTML templates
├── student/            # Student management app
├── media/             # Media files storage
├── manage.py          # Django management script
└── pyproject.toml     # Project dependencies
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Emre Tuncer - Initial work - [emretuncer.developer@gmail.com](mailto:emretuncer.developer@gmail.com)

## 🙏 Acknowledgments

- Django Documentation
- FPDF2 Documentation
- Matplotlib Documentation
- Seaborn Documentation 