# AI-Powered Smart Expense Splitter

A full-stack MERN Expense Splitter for friends, roommates, flats, trips, and outings. It supports JWT authentication, group management, equal/custom expense splitting, bill image uploads, settlement minimization, notifications, charts, and rule-based AI spending insights.

## Stack

- Frontend: React, Vite, Tailwind CSS, Recharts, Framer Motion, Lucide icons
- Backend: Node.js, Express.js, MongoDB, Mongoose, JWT, Bcrypt, Multer
- Security: Helmet, rate limiting, XSS cleanup, validation, hashed passwords, env-based secrets

## Project Structure

```bash
backend/
  src/
    config/
    controllers/
    middleware/
    models/
    routes/
    utils/
frontend/
  src/
    components/
    context/
    pages/
    services/
    utils/
```

## Features

- Register/login with JWT authentication
- Create groups for trips, flats, outings, and other shared expenses
- Add members by registered email
- Add expenses with title, amount, category, payer, equal/custom split, and bill image
- View total expenses, member balances, transactions, monthly charts, and category charts
- Generate settlement suggestions with a greedy debt minimization algorithm
- Record settlements and update balances
- Send and store in-app notifications for expenses, reminders, settlements, and member changes
- Generate rule-based insights for highest category, spending trends, active spender, budget warnings, and cost-cutting suggestions
- Responsive UI with dark/light mode, loading states, empty states, and validation errors

## Setup

### 1. Install dependencies

```bash
npm run install:all
```

### 2. Configure backend environment

```bash
cp backend/.env.example backend/.env
```

Update `backend/.env` if needed:

```env
PORT=5000
MONGO_URI=mongodb://127.0.0.1:27017/expense_splitter
JWT_SECRET=replace-with-a-long-random-secret
CLIENT_URL=http://localhost:5173
CLIENT_URLS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000
```

### 3. Start MongoDB

Use a local MongoDB server or MongoDB Atlas. For local development, make sure MongoDB is listening at the `MONGO_URI` above.

### 4. Run the app

```bash
npm run dev
```

Frontend: `http://localhost:5173`

Backend health check: `http://localhost:5000/api/health`

If your frontend runs on another domain or port, add it to `CLIENT_URLS` as a comma-separated origin. The backend already allows common local React/Vite origins and handles CORS preflight requests.

## API Summary

### Auth

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/profile`

### Groups

- `GET /api/groups`
- `POST /api/groups`
- `GET /api/groups/:id`
- `POST /api/groups/:id/members`
- `DELETE /api/groups/:id/members/:userId`

### Expenses

- `GET /api/expenses/group/:groupId`
- `POST /api/expenses`
- `PUT /api/expenses/:id`
- `DELETE /api/expenses/:id`

### Settlements

- `GET /api/settlements/:groupId`
- `POST /api/settlements/pay`
- `POST /api/settlements/remind`

### Insights and Notifications

- `GET /api/insights/:groupId`
- `GET /api/notifications`
- `PATCH /api/notifications/:id/read`

## Smart Settlement Logic

Each expense credits the payer and debits every split participant by their share. Completed settlements adjust the ledger. The backend then separates debtors and creditors and greedily matches them by amount, producing a small list of payment suggestions.

## Notes

- Bill images are saved to `backend/uploads` and served from `/uploads`.
- AI insights are rule-based so the project works without external API keys.
- For production, set a strong `JWT_SECRET`, use MongoDB Atlas, configure HTTPS, and store bill images in Cloudinary or another object store.
