# Tracerfy Local Development Setup

This guide will help you set up both the frontend and backend servers locally.

## 🚀 Quick Start

### Frontend (React + Vite)
```bash
cd exact-site-replica-main
npm install
npm run dev
```
**Frontend URL:** http://localhost:5173

### Backend (FastAPI + Python)
```bash
cd tracify_backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
**Backend URL:** http://localhost:8000
**API Docs:** http://localhost:8000/docs

---

## 📋 Detailed Setup Instructions

### Prerequisites
- Node.js (v16 or higher)
- Python (v3.8 or higher)
- pip (Python package manager)
- Git

---

## Frontend Setup

### 1. Navigate to Frontend Directory
```bash
cd exact-site-replica-main
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Start Development Server
```bash
npm run dev
```

### 4. Access Frontend
Open your browser and go to: **http://localhost:5173**

---

## Backend Setup

### 1. Navigate to Backend Directory
```bash
cd tracify_backend
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
```bash
# Copy the example environment file
cp .env.example .env
# Edit .env with your configuration
```

### 5. Start Backend Server
```bash
# Method 1: Using uvicorn directly
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Method 2: Using the start script
python start.py start
```

### 6. Access Backend
- **API Base URL:** http://localhost:8000
- **Interactive API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

## 🎯 Credit Purchase Page Features

### Working Features
- ✅ Professional UI with gradient backgrounds
- ✅ Real-time credit balance display
- ✅ Interactive credit package selection
- ✅ Discount code system (try: SAVE10, SAVE20, WELCOME, TEST)
- ✅ Mock payment processing
- ✅ Loading states and error handling
- ✅ Success notifications
- ✅ Responsive design

### Discount Codes for Testing
- `SAVE10` - 10% discount
- `SAVE20` - 20% discount  
- `WELCOME` - 15% discount
- `TEST` - 5% discount

---

## 🔧 API Endpoints

### Credit System
- `GET /api/v1/credits/balance` - Get user credit balance
- `GET /api/v1/credits/packages` - Get available credit packages
- `POST /api/v1/credits/purchase` - Purchase credits
- `GET /api/v1/credits/transactions` - Get transaction history
- `GET /api/v1/credits/stats` - Get credit statistics

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Get current user info

---

## 🐛 Troubleshooting

### Frontend Issues
- **Port already in use:** Change port in `vite.config.ts` or use `npm run dev -- --port 3001`
- **Dependencies not found:** Run `npm install` to reinstall packages
- **Import errors:** Check that all files exist in the correct directories

### Backend Issues
- **Module not found:** Make sure you're in the `tracify_backend/backend` directory
- **Database connection error:** Check your `.env` file configuration
- **Port already in use:** Use `--port 8001` or a different port

### Common Solutions
1. **Clear node_modules:** `rm -rf node_modules && npm install`
2. **Clear Python cache:** Delete `__pycache__` folders
3. **Restart servers:** Stop both servers and restart them
4. **Check logs:** Look at terminal output for error messages

---

## 📱 Testing the Application

### 1. Test Frontend
1. Open http://localhost:5173 in your browser
2. Navigate to the Credits/Purchase page
3. Try selecting different credit packages
4. Test discount codes
5. Simulate a purchase

### 2. Test Backend API
1. Open http://localhost:8000/docs in your browser
2. Test the API endpoints interactively
3. Check credit packages endpoint
4. Test credit balance endpoint

---

## 🎨 Current Status

### ✅ Completed
- Professional UI design
- Mock credit service implementation
- Real-time calculations
- Discount code system
- Loading states and error handling
- Success notifications
- Responsive layout

### 🔄 In Progress
- Backend server startup
- Database connection setup
- Real API integration

---

## 📞 Support

If you encounter any issues:
1. Check the terminal output for error messages
2. Verify all dependencies are installed
3. Ensure both servers are running on correct ports
4. Check network/firewall settings if needed

---

**Enjoy your professional Tracerfy credit purchase system! 🚀**
