# AI-Powered Smart Expense Splitter

## Project Overview

AI-Powered Smart Expense Splitter is a full-stack MERN application designed to simplify shared expense management for roommates, college students, travel groups, and friends living together.

Managing expenses manually in chats or notes often creates confusion about:

* Who paid
* Who owes money
* Pending balances
* Settlement calculations

This platform automates the entire process using intelligent expense tracking, debt minimization algorithms, AI-generated spending insights, and secure financial record management.

The application focuses on scalability, security, clean UI/UX, and production-level backend architecture.

---

# Features

## Core Features

* User Authentication (JWT-based)
* Group Creation & Management
* Add/Edit/Delete Expenses
* Equal & Custom Expense Splits
* Smart Debt Simplification
* Real-Time Balance Tracking
* Expense Categories
* Bill Upload Support
* AI-Based Spending Insights
* Dashboard Analytics
* Secure REST APIs
* Mobile Responsive UI

---

# Smart Settlement Engine

The application uses a greedy debt minimization algorithm to reduce the total number of transactions required among group members.

### Example

Instead of:

* A pays B → ₹500
* B pays C → ₹500

The system simplifies it to:

* A pays C → ₹500

This minimizes unnecessary money transfers and improves settlement clarity.

---

# Tech Stack

## Frontend

* React.js
* Tailwind CSS
* React Router DOM
* Axios
* Framer Motion
* Chart.js

## Backend

* Node.js
* Express.js
* MongoDB
* Mongoose
* JWT Authentication
* Bcrypt.js
* Multer

## AI Integration

* Gemini API / Google Gen AI SDK

## Optional Integrations

* Cloudinary
* Socket.IO
* OCR APIs

---

# Folder Structure

```bash
expense-splitter/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── context/
│   │   ├── assets/
│   │   ├── App.jsx
│   │   └── main.jsx
│
├── backend/
│   ├── controllers/
│   ├── middleware/
│   ├── models/
│   ├── routes/
│   ├── utils/
│   ├── config/
│   ├── server.js
│   └── package.json
```

---

# Database Models

## User Model

Stores:

* Name
* Email
* Password
* Avatar

## Group Model

Stores:

* Group name
* Members
* Group creator

## Expense Model

Stores:

* Expense title
* Amount
* Category
* Payer
* Split information
* Bill image
* Group reference

---

# API Endpoints

## Authentication

```bash
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/profile
```

## Groups

```bash
POST   /api/groups/create
GET    /api/groups/:id
PUT    /api/groups/add-member
DELETE /api/groups/remove-member
```

## Expenses

```bash
POST   /api/expenses/add
GET    /api/expenses/group/:groupId
PUT    /api/expenses/:id
DELETE /api/expenses/:id
```

## Settlements

```bash
GET  /api/settlements/:groupId
POST /api/settlements/pay
```

---

# AI Spending Insights

The platform analyzes historical expense patterns and generates:

* Spending trends
* Budget warnings
* Expense category summaries
* Cost-saving suggestions

Example:

* “Food spending increased by 35% this month.”
* “Travel expenses exceeded the average weekly budget.”

---

# Installation & Setup

## Clone Repository

```bash
git clone https://github.com/your-username/expense-splitter.git
cd expense-splitter
```

---

# Backend Setup

```bash
cd backend
npm install
```

## Create `.env`

```env
PORT=5000
MONGO_URI=your_mongodb_connection
JWT_SECRET=your_secret_key
GEMINI_API_KEY=your_gemini_api_key
CLOUDINARY_API_KEY=your_cloudinary_key
```

## Start Backend Server

```bash
npm run dev
```

---

# Frontend Setup

```bash
cd frontend
npm install
```

## Start Frontend

```bash
npm run dev
```

---

# Security Features

The application includes multiple production-level security safeguards:

* JWT Authentication
* Password Hashing
* Rate Limiting
* Input Validation
* MongoDB Injection Prevention
* XSS Protection
* Secure Environment Variables

---

# Performance Optimizations

* Lazy Loading
* Optimized MongoDB Queries
* Efficient Settlement Calculations
* Responsive UI Rendering
* API Rate Limiting
* Optimized React Component Structure

---

# Deployment

## Frontend

Recommended:

* Vercel
* Netlify

## Backend

Recommended:

* Render
* Railway

## Database

* MongoDB Atlas

---

# Future Enhancements

## Planned Features

* OCR Bill Scanning
* Real-Time Notifications
* PWA Support
* Export PDF Reports
* Multi-Currency Support
* Recurring Expense Tracking
* UPI Payment Integration
* AI Budget Forecasting

---

# Evaluation Methodology

This project was designed and evaluated using production-quality software engineering principles:

* Correctness
* Scalability
* Code Maintainability
* Security
* Performance Optimization
* User Experience
* API Design
* Architectural Clarity

The comparison between LLM-generated responses was performed using:

* Dimension-wise evaluation
* Likert scale scoring
* Production readiness analysis
* Completeness and correctness benchmarks

---

# Project Outcome

The AI-Powered Smart Expense Splitter acts as a modern fintech-style solution that:

* Simplifies group expense management
* Reduces payment confusion
* Automates settlements
* Provides intelligent spending analysis
* Delivers a scalable startup-ready architecture

This project is highly valuable for:

* Full Stack Portfolio
* Fintech Projects
* Internship Applications
* Startup MVPs
* Resume Building

---