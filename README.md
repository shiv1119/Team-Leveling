# 🌐 Service Sphere

### 🔗 **Project Video**:  
[![Watch Video](https://img.shields.io/badge/🎥%20Watch%20Video-Click%20Here-red)](https://drive.google.com/file/d/1BcdqpYm3tIkvyUZ4fCE418QETPQKPSwg/view?usp=sharing)

---

<div align="center">
  <img src="./.github/service-sphere-banner.png" alt="Service Sphere" width="80%" />

  &#xa0;

  <a href="https://yourwebsite.com">🔗 Live Demo</a>
</div>

## 🚀 Introduction

**Service Sphere** is a multi-client service platform that allows businesses to showcase their services efficiently. It provides an intuitive interface for service providers to list their services and for users to book them seamlessly.

## ✨ Features

✔ **User Registration & Authentication** (Sign up, Login, Password Reset)  
✔ **Service Creation & Management** (Multi-step service creation process)  
✔ **Booking System** (Real-time booking confirmations & notifications)  
✔ **Dynamic Working Hours** (Providers can set their availability)  
✔ **Service Reviews & Ratings**  
✔ **Secure Payments & Refund Handling**  
✔ **In-app & Email Notifications**  
✔ **Dark Mode Support** 🌙  
✔ **Mobile-Friendly & PWA Ready** 📱  

## 🛠️ Technologies Used

- **Frontend:** HTML, CSS, Bootstrap  
- **Backend:** Django, Django REST Framework  
- **Database:** PostgreSQL  
- **Authentication:** Django Auth, Social Authentication  
- **Payments:** Stripe / Razorpay  
- **Deployment:** Docker, Nginx, Gunicorn  

## 📜 Requirements

Before you begin, ensure you have **Python 3.x** and **Git** installed.

## 🚀 Getting Started

### 🛠️ Setup & Installation

```bash
# Clone the repository
git clone https://github.com/your-username/service-sphere.git

# Navigate into the project
cd service-sphere

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# Set up the database (PostgreSQL recommended)
python manage.py makemigrations
python manage.py migrate

# Create a superuser for admin access
python manage.py createsuperuser

# Run the server
python manage.py runserver

# Open in browser: http://127.0.0.1:8000
