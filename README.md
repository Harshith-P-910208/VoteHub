# College VoteHub

**College VoteHub** is a comprehensive Django-based online voting platform for colleges with MongoDB Atlas integration, featuring secure authentication, real-time voting, geolocation tracking, and webcam image capture. A secure, transparent, and democratic solution for college elections.

## 🌟 Features

### Student Module
- ✅ Registration with college email validation (@sfscollege.in)
- 🔐 Secure login/logout
- 📊 Dashboard showing active elections
- 🗳️ Interactive voting interface
- 📸 Webcam image capture during voting
- 📍 Geolocation tracking
- ✅ Vote confirmation page
- 🚫 Duplicate vote prevention

### Admin Module
- 📈 Dashboard with statistics
- ➕ Create and manage elections
- 👥 Add and manage candidates
- 📊 Real-time results with charts
- 🗺️ View voter details (images, locations)
- 📅 Election scheduling

### Design Features
- 🎨 Modern glassmorphism UI
- 🌈 Vibrant gradient colors
- ✨ Smooth animations and transitions
- 📱 Fully responsive design
- 🌙 Premium dark theme
- 🎯 Micro-interactions

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- MongoDB Atlas account
- Modern web browser with webcam and location support

### 1. MongoDB Atlas Setup

1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster
3. Create a database user with read/write permissions
4. Whitelist your IP address (or use 0.0.0.0/0 for development)
5. Get your connection string (looks like: `mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/`)

### 2. Project Setup

```bash
# Navigate to project directory
cd college_voting_system

# Activate virtual environment
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies (if not already installed)
pip install -r requirements.txt
```

### 3. Configure MongoDB Connection

Edit `college_voting/settings.py` or use environment variables:

```python
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'college_voting_db',
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': 'YOUR_MONGODB_ATLAS_CONNECTION_STRING_HERE',
        }
    }
}
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Admin User

```bash
python manage.py createsuperuser
```

When prompted:
- Email: `admin@sfscollege.in` (must end with @sfscollege.in)
- Full name: Your name
- Student ID: Any ID (e.g., ADMIN001)
- Password: Your secure password

**Important:** After creating the superuser, you need to manually set `is_admin=True` in MongoDB:

1. Go to MongoDB Atlas dashboard
2. Browse Collections → `users`
3. Find your admin user
4. Edit and set `is_admin: true`

### 6. Run the Development Server

```bash
python manage.py runserver
```

Visit: `http://localhost:8000`

## 🚢 Deployment (Production)

The application is prepared for deployment on platforms like **Render**, **Heroku**, or any VPS.

### 1. Deployment Checklist
- [ ] Set `DEBUG=False` in environment variables
- [ ] Generate a secure `SECRET_KEY`
- [ ] Install `gunicorn` and `whitenoise` (already in `requirements.txt`)
- [ ] Configure `ALLOWED_HOSTS` with your domain

### 2. Environment Variables (.env)
In production, the following variables must be set:
```ini
DEBUG=False
SECRET_KEY=your_secure_random_key
ALLOWED_HOSTS=yourdomain.com,your-app.onrender.com
DB_NAME=college_voting_db
DB_HOST=your_mongodb_atlas_connection_string
EMAIL_HOST_USER=your_email@gmail.com
### 3. Deploy to Vercel (Recommended - Free & Fast)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Harshith-P-910208/VoteHub)

1.  **Click the button above**.
2.  Login to Vercel with GitHub.
3.  Vercel will detect `vercel.json` automatically.
4.  Add Environment Variables:
    - `SECRET_KEY`
    - `EMAIL_HOST_USER`
    - `EMAIL_HOST_PASSWORD`
    - `CLOUDINARY_CLOUD_NAME` (etc...)
5.  Click **Deploy**.

### 4. Deploy to Heroku
1. Create a new app on Heroku.
2. Push code: `git push heroku main`
3. Heroku will automatically detect the `Procfile` and `runtime.txt`.

## 📖 Usage Guide

### For Students

1. **Register**
   - Go to `/accounts/register/`
   - Use your college email (@sfscollege.in)
   - Fill in all required details

2. **Login**
   - Go to `/accounts/login/`
   - Enter your credentials

3. **Vote**
   - View active elections on dashboard
   - Click "Vote Now" on an election
   - Select your candidate
   - Allow camera permissions and capture your photo
   - Allow location permissions
   - Submit your vote

### For Admins

1. **Login**
   - Use your admin credentials
   - You'll be redirected to admin dashboard

2. **Create Election**
   - Click "Create New Election"
   - Fill in title, description, start/end dates
   - Add candidates with photos and descriptions

3. **View Results**
   - Go to any election
   - Click "View Results"
   - See vote counts, percentages, and voter details

## 🔒 Security Features

- Email domain validation (@sfscollege.in only)
- Password hashing with PBKDF2
- CSRF protection
- Duplicate vote prevention
- Secure session management
- Image and location verification
- WhiteNoise for secure static file serving

## 🎨 Design System

- **Colors**: Vibrant gradients (purple-blue-pink theme)
- **Typography**: Outfit (UI), Outfit (headings)
- **Effects**: Glassmorphism, smooth animations
- **Layout**: Responsive grid system
- **Components**: Cards, buttons, forms, tables

## 📁 Project Structure

```
college_voting_system/
├── accounts/              # Authentication app
├── voting/                # Voting logic app
├── static/
├── media/                # User uploads
├── templates/            # HTML templates
├── scripts/              # Utility scripts
├── Procfile              # Production server config
├── runtime.txt           # Python version
└── college_voting/       # Main project settings
```

## 🛠️ Technologies Used

- **Backend**: Django, Python 3.12
- **Database**: MongoDB Atlas (via djongo)
- **Frontend**: HTML5, CSS3, JavaScript
- **Static Assets**: WhiteNoise
- **WSGI**: Gunicorn

## 📄 License

This project is created for educational purposes.

## 👨‍💻 Support

For issues or questions, please check the code comments or reach out.

---

**Built with ❤️ for democratic student governance**
