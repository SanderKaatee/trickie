# 🎲 Trickie

> A humorous twist on Dutch payment requests - where your friends can gamble instead of just paying!

Trickie is a parody app, adding a "double or nothing" gambling element to money requests. Built as a demonstration project showcasing full-stack web development skills.

## 🎯 Concept

Instead of boring payment requests, Trickie lets recipients choose their adventure:
- **Pay normally** - Just like any other payment app
- **Double or Nothing** - Spin the wheel of fortune!
  - 🎉 **Win**: The app pays double to the requester (you pay nothing!)
  - 😢 **Lose**: You pay double the original amount

*Don't worry - this is just a demo app. No real money changes hands!*

## 🛠️ Technology Stack

**Backend:**
- Python 3.12 with Flask
- SQLAlchemy ORM with SQLite database
- Session-based user tracking with cookie persistence
- RESTful API design

**Frontend:**
- Responsive HTML5/CSS3 with custom design system
- Vanilla JavaScript with Canvas API for interactive wheel
- CSS animations and transitions
- Progressive Web App features

**DevOps:**
- Docker containerization
- Gunicorn WSGI server
- Production-ready configuration

## 🚀 Features

### Core Functionality
- **Multi-step creation flow**: Name → Amount → Description
- **Interactive spinning wheel**: Canvas-based game with realistic physics
- **Real-time status updates**: Live polling for payment status
- **Creator dashboard**: Track all your Trickies with statistics
- **Shareable links**: Direct URLs for payment requests

### User Experience
- **Mobile-first responsive design**
- **Smooth animations and micro-interactions**
- **Confetti celebrations** for wins
- **Toast notifications** for user feedback
- **Accessible form controls** and navigation

### Technical Highlights
- **Cookie-based creator tracking** without user accounts
- **Enum-based state management** for payment statuses
- **Client-side URL generation** and sharing
- **Modular CSS architecture** with CSS custom properties
- **Error handling and graceful degradation**

## 📁 Project Structure

```
trickie/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── .gitignore           # Git ignore rules
├── static/
│   ├── css/
│   │   └── style.css    # Custom design system
│   └── js/
│       ├── wheel.js     # Canvas-based spinning wheel
│       └── confetti.js  # Win celebration effects
└── templates/           # Jinja2 HTML templates
    ├── _base.html      # Base template with navigation
    ├── landing.html    # Homepage
    ├── name.html       # Step 1: Creator name
    ├── amount.html     # Step 2: Payment amount
    ├── description.html # Step 3: Payment description
    ├── dashboard.html  # Creator dashboard
    ├── request.html    # Payment request page
    └── result.html     # Win/lose result page
```

## 🎨 Design Philosophy

The UI draws inspiration from modern fintech apps while adding playful gambling elements:

- **Color palette**: Deep indigo, mint green, rose, and golden accents
- **Typography**: Poppins font family for friendly, modern feel
- **Animations**: Smooth CSS transitions with JavaScript-enhanced interactions
- **Responsive**: Mobile-first approach with flexible grid layouts

## 🔧 Installation & Setup

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/trickie.git
cd trickie

# Build and run with Docker
docker build -t trickie .
docker run -p 8000:8000 trickie
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
```

Visit `http://localhost:5000` (development) or `http://localhost:8000` (Docker)

## 🎮 How to Use

1. **Create a Trickie**
   - Enter your name
   - Set the payment amount
   - Add a description

2. **Share the link** with your friend

3. **Your friend decides**:
   - Pay normally (boring!)
   - Or gamble with "Double or Nothing"

4. **Watch the wheel spin** and see the result!

5. **Check your dashboard** to track all your Trickies

## 🧪 Technical Decisions

### Backend Architecture
- **Flask over Django**: Lightweight framework perfect for this scope
- **SQLAlchemy ORM**: Clean database interactions with relationship management
- **Cookie-based tracking**: Avoid user registration complexity while maintaining state
- **Enum pattern**: Type-safe status management for payment states

### Frontend Approach
- **Vanilla JavaScript**: No framework overhead for simple interactions
- **Canvas API**: Custom wheel implementation for complete control over game mechanics
- **CSS Grid/Flexbox**: Modern layout techniques for responsive design
- **Progressive enhancement**: Core functionality works without JavaScript

### Database Design
```sql
-- Simplified schema
CREATE TABLE trickie (
    id INTEGER PRIMARY KEY,
    slug VARCHAR(36) UNIQUE,
    creator_name VARCHAR(100),
    creator_token VARCHAR(8),    -- For tracking without accounts
    amount_cents INTEGER,
    description VARCHAR(140),
    wants_double BOOLEAN,
    result ENUM('PENDING', 'WIN', 'LOSE', 'NORMAL'),
    created_at DATETIME
);
```


## 🎭 About This Project

Trickie was created as a humorous side project to demonstrate full-stack development capabilities while having fun with a familiar Dutch concept. It showcases:

- **Clean, maintainable code architecture**
- **Modern web development practices**
- **Attention to user experience details**
- **Production-ready deployment setup**

The project balances technical sophistication with playful design, showing that serious development skills can create delightful user experiences.

## 📝 License

This is a demonstration project. Feel free to explore the code, but please don't actually use it to gamble with real money! 

---

*Built with ❤️ and a sense of humor in The Netherlands*