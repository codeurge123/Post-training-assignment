"""
EXPENSE SPLITTER - Full Stack Project
Complete codebase documentation with all frontend and backend code.

This file contains the entire source code of the Expense Splitter application,
a full-stack MERN project for managing shared expenses and group settlements.

PROJECT STRUCTURE:
==================
Backend (Node.js/Express):
- Server: Express.js REST API with MongoDB
- Auth: JWT-based authentication with bcrypt
- Models: User, Group, Expense, Settlement, Notification
- Controllers: Business logic for all entities
- Middleware: Auth, validation, error handling, file uploads
- Routes: API endpoints for all features
- Utilities: Token generation, money calculations, settlement logic

Frontend (React/Vite):
- Pages: Authentication, Dashboard
- Components: Buttons, Cards, Shell, Empty States
- Context: Auth context for session management
- Services: Axios API client
- Utils: Formatting functions
- Styling: Tailwind CSS with dark mode support

HOW TO RUN:
===========

BACKEND:
1. cd golden_response/backend
2. npm install
3. Create .env file with:
   - PORT=5001
   - MONGO_URI=mongodb://127.0.0.1:27017/expense_splitter
   - JWT_SECRET=your-secret-key
   - NODE_ENV=development
4. npm run dev

FRONTEND:
1. cd golden_response/frontend
2. npm install
3. npm run dev

API will run on http://localhost:5001
Frontend will run on http://localhost:5173

================================================================================
BACKEND CODE
================================================================================

===== CONFIGURATION =====

File: backend/src/config/db.js
"""

DB_CONFIG = """
import mongoose from "mongoose";

export const connectDB = async () => {
  const uri = process.env.MONGO_URI || "mongodb://127.0.0.1:27017/expense_splitter";
  try {
    const conn = await mongoose.connect(uri);
    console.log(`MongoDB connected: ${conn.connection.host}`);
  } catch (error) {
    console.error("MongoDB connection failed", error.message);
    process.exit(1);
  }
};
"""

# ===== SERVER SETUP =====

SERVER_JS = """
import path from "node:path";
import { fileURLToPath } from "node:url";
import cors from "cors";
import dotenv from "dotenv";
import express from "express";
import rateLimit from "express-rate-limit";
import helmet from "helmet";
import morgan from "morgan";
import xss from "xss-clean";
import { connectDB } from "./config/db.js";
import authRoutes from "./routes/authRoutes.js";
import expenseRoutes from "./routes/expenseRoutes.js";
import groupRoutes from "./routes/groupRoutes.js";
import insightRoutes from "./routes/insightRoutes.js";
import notificationRoutes from "./routes/notificationRoutes.js";
import settlementRoutes from "./routes/settlementRoutes.js";
import { errorHandler, notFound } from "./middleware/errorMiddleware.js";

dotenv.config();
await connectDB();

const app = express();
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const corsOptions = {
  origin: true,
  credentials: true,
  methods: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
  allowedHeaders: ["Content-Type", "Authorization"]
};

app.use(cors(corsOptions));
app.options("*", cors(corsOptions));
app.use(helmet({ crossOriginResourcePolicy: { policy: "cross-origin" } }));
app.use(express.json({ limit: "2mb" }));
app.use(express.urlencoded({ extended: true }));
app.use(xss());
app.use(morgan("dev"));
app.use(
  rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 250,
    standardHeaders: true,
    legacyHeaders: false
  })
);

app.get("/api/health", (_req, res) => res.json({ status: "ok", app: "Expense Splitter" }));
app.use("/uploads", express.static(path.join(__dirname, "../uploads")));
app.use("/api/auth", authRoutes);
app.use("/api/groups", groupRoutes);
app.use("/api/expenses", expenseRoutes);
app.use("/api/settlements", settlementRoutes);
app.use("/api/insights", insightRoutes);
app.use("/api/notifications", notificationRoutes);

app.use(notFound);
app.use(errorHandler);

const startServer = (port, attemptsLeft = 5) => {
  const server = app.listen(port, () => {
    console.log(`API running on port ${port}`);
  });

  server.on("error", (error) => {
    if (error.code === "EADDRINUSE" && attemptsLeft > 0) {
      const nextPort = Number(port) + 1;
      console.warn(`Port ${port} is already in use. Trying ${nextPort}...`);
      startServer(nextPort, attemptsLeft - 1);
      return;
    }

    console.error(error.message);
    process.exit(1);
  });
};

startServer(Number(process.env.PORT) || 5001);
"""

# ===== DATABASE MODELS =====

USER_MODEL = """
File: backend/src/models/User.js

import bcrypt from "bcryptjs";
import mongoose from "mongoose";

const userSchema = new mongoose.Schema(
  {
    name: { type: String, required: true, trim: true, maxlength: 80 },
    email: { type: String, required: true, unique: true, lowercase: true, trim: true },
    password: { type: String, required: true, minlength: 6, select: false },
    avatar: { type: String, default: "" }
  },
  { timestamps: true }
);

userSchema.pre("save", async function hashPassword(next) {
  if (!this.isModified("password")) return next();
  this.password = await bcrypt.hash(this.password, 12);
  next();
});

userSchema.methods.matchPassword = function matchPassword(password) {
  return bcrypt.compare(password, this.password);
};

export default mongoose.model("User", userSchema);
"""

GROUP_MODEL = """
File: backend/src/models/Group.js

import mongoose from "mongoose";

const memberSchema = new mongoose.Schema(
  {
    user: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
    role: { type: String, enum: ["owner", "member"], default: "member" },
    joinedAt: { type: Date, default: Date.now }
  },
  { _id: false }
);

const groupSchema = new mongoose.Schema(
  {
    name: { type: String, required: true, trim: true, maxlength: 100 },
    description: { type: String, trim: true, maxlength: 300, default: "" },
    type: { type: String, enum: ["Trip", "Flat", "Outing", "Other"], default: "Other" },
    createdBy: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
    members: [memberSchema],
    budgetLimit: { type: Number, default: 0, min: 0 }
  },
  { timestamps: true }
);

groupSchema.index({ "members.user": 1 });

export default mongoose.model("Group", groupSchema);
"""

EXPENSE_MODEL = """
File: backend/src/models/Expense.js

import mongoose from "mongoose";

const splitSchema = new mongoose.Schema(
  {
    user: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
    percentage: { type: Number, min: 0, max: 100, default: 0 },
    amount: { type: Number, min: 0, required: true }
  },
  { _id: false }
);

const expenseSchema = new mongoose.Schema(
  {
    title: { type: String, required: true, trim: true, maxlength: 120 },
    amount: { type: Number, required: true, min: 0.01 },
    category: {
      type: String,
      enum: ["Food", "Rent", "Travel", "Shopping", "Utilities", "Entertainment", "Other"],
      default: "Other"
    },
    payer: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
    group: { type: mongoose.Schema.Types.ObjectId, ref: "Group", required: true },
    splitType: { type: String, enum: ["equal", "custom"], default: "equal" },
    splits: [splitSchema],
    billImage: { type: String, default: "" },
    notes: { type: String, maxlength: 500, default: "" },
    createdBy: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true }
  },
  { timestamps: true }
);

expenseSchema.index({ group: 1, createdAt: -1 });

export default mongoose.model("Expense", expenseSchema);
"""

SETTLEMENT_MODEL = """
File: backend/src/models/Settlement.js

import mongoose from "mongoose";

const settlementSchema = new mongoose.Schema(
  {
    group: { type: mongoose.Schema.Types.ObjectId, ref: "Group", required: true },
    from: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
    to: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
    amount: { type: Number, required: true, min: 0.01 },
    status: { type: String, enum: ["pending", "completed", "failed"], default: "completed" },
    note: { type: String, trim: true, maxlength: 250, default: "" },
    recordedBy: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true }
  },
  { timestamps: true }
);

settlementSchema.index({ group: 1, createdAt: -1 });

export default mongoose.model("Settlement", settlementSchema);
"""

NOTIFICATION_MODEL = """
File: backend/src/models/Notification.js

import mongoose from "mongoose";

const notificationSchema = new mongoose.Schema(
  {
    user: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
    group: { type: mongoose.Schema.Types.ObjectId, ref: "Group" },
    type: {
      type: String,
      enum: ["expense_added", "reminder", "settlement_completed", "member_changed"],
      required: true
    },
    title: { type: String, required: true, trim: true },
    message: { type: String, required: true, trim: true },
    read: { type: Boolean, default: false }
  },
  { timestamps: true }
);

notificationSchema.index({ user: 1, read: 1, createdAt: -1 });

export default mongoose.model("Notification", notificationSchema);
"""

# ===== MIDDLEWARE =====

AUTH_MIDDLEWARE = """
File: backend/src/middleware/authMiddleware.js

import jwt from "jsonwebtoken";
import User from "../models/User.js";

export const protect = async (req, res, next) => {
  try {
    const header = req.headers.authorization || "";
    const token = header.startsWith("Bearer ") ? header.split(" ")[1] : null;
    if (!token) return res.status(401).json({ message: "Authentication token required" });

    const decoded = jwt.verify(token, process.env.JWT_SECRET || "dev-secret");
    const user = await User.findById(decoded.id).select("-password");
    if (!user) return res.status(401).json({ message: "User no longer exists" });
    req.user = user;
    next();
  } catch (_error) {
    res.status(401).json({ message: "Invalid or expired token" });
  }
};
"""

ERROR_MIDDLEWARE = """
File: backend/src/middleware/errorMiddleware.js

export const notFound = (req, res, next) => {
  const error = new Error(`Not found: ${req.originalUrl}`);
  res.status(404);
  next(error);
};

export const errorHandler = (err, _req, res, _next) => {
  const status = res.statusCode === 200 ? 500 : res.statusCode;
  res.status(status).json({
    message: err.message || "Server error",
    ...(process.env.NODE_ENV !== "production" ? { stack: err.stack } : {})
  });
};
"""

VALIDATE_MIDDLEWARE = """
File: backend/src/middleware/validate.js

import { validationResult } from "express-validator";

export const validate = (req, res, next) => {
  const errors = validationResult(req);
  if (errors.isEmpty()) return next();
  return res.status(422).json({
    message: "Validation failed",
    errors: errors.array().map((error) => ({ field: error.path, message: error.msg }))
  });
};
"""

UPLOAD_MIDDLEWARE = """
File: backend/src/middleware/upload.js

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import multer from "multer";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const uploadDir = path.join(__dirname, "../../uploads");
fs.mkdirSync(uploadDir, { recursive: true });

const storage = multer.diskStorage({
  destination: (_req, _file, cb) => cb(null, uploadDir),
  filename: (_req, file, cb) => {
    const ext = path.extname(file.originalname);
    cb(null, `${Date.now()}-${Math.round(Math.random() * 1e9)}${ext}`);
  }
});

export const uploadBill = multer({
  storage,
  limits: { fileSize: 3 * 1024 * 1024 },
  fileFilter: (_req, file, cb) => {
    if (!file.mimetype.startsWith("image/")) return cb(new Error("Only bill images are allowed"));
    cb(null, true);
  }
});
"""

# ===== CONTROLLERS =====

AUTH_CONTROLLER = """
File: backend/src/controllers/authController.js

import User from "../models/User.js";
import { generateToken } from "../utils/token.js";

const authResponse = (user) => ({
  token: generateToken(user._id),
  user: { id: user._id, name: user.name, email: user.email, avatar: user.avatar }
});

export const register = async (req, res) => {
  const { name, email, password } = req.body;
  const existing = await User.findOne({ email });
  if (existing) return res.status(409).json({ message: "Email is already registered" });
  const user = await User.create({ name, email, password });
  res.status(201).json(authResponse(user));
};

export const login = async (req, res) => {
  const { email, password } = req.body;
  const user = await User.findOne({ email }).select("+password");
  if (!user || !(await user.matchPassword(password))) {
    return res.status(401).json({ message: "Invalid email or password" });
  }
  res.json(authResponse(user));
};

export const profile = async (req, res) => {
  res.json({ user: { id: req.user._id, name: req.user.name, email: req.user.email, avatar: req.user.avatar } });
};
"""

GROUP_CONTROLLER = """
File: backend/src/controllers/groupController.js

import Expense from "../models/Expense.js";
import Group from "../models/Group.js";
import User from "../models/User.js";
import { notifyUsers } from "../utils/notifications.js";
import { calculateGroupLedger } from "../utils/splitter.js";

const ensureMember = (group, userId) => group.members.some((member) => String(member.user._id || member.user) === String(userId));

export const createGroup = async (req, res) => {
  const group = await Group.create({
    ...req.body,
    createdBy: req.user._id,
    members: [{ user: req.user._id, role: "owner" }]
  });
  const populated = await group.populate("members.user", "name email avatar");
  res.status(201).json(populated);
};

export const listGroups = async (req, res) => {
  const groups = await Group.find({ "members.user": req.user._id })
    .populate("members.user", "name email avatar")
    .sort({ updatedAt: -1 });
  res.json(groups);
};

export const getGroup = async (req, res) => {
  const group = await Group.findById(req.params.id).populate("members.user", "name email avatar");
  if (!group) return res.status(404).json({ message: "Group not found" });
  if (!ensureMember(group, req.user._id)) return res.status(403).json({ message: "You are not a member of this group" });
  const [ledger, totalExpense] = await Promise.all([
    calculateGroupLedger(group),
    Expense.aggregate([{ $match: { group: group._id } }, { $group: { _id: null, total: { $sum: "$amount" } } }])
  ]);
  res.json({ group, ledger, totalExpense: totalExpense[0]?.total || 0 });
};

export const addMember = async (req, res) => {
  const { email } = req.body;
  const group = await Group.findById(req.params.id);
  if (!group) return res.status(404).json({ message: "Group not found" });
  if (!ensureMember(group, req.user._id)) return res.status(403).json({ message: "You cannot update this group" });
  const user = await User.findOne({ email });
  if (!user) return res.status(404).json({ message: "No user found for that email" });
  if (!ensureMember(group, user._id)) group.members.push({ user: user._id });
  await group.save();
  await notifyUsers({
    users: [user._id],
    group: group._id,
    type: "member_changed",
    title: "Added to group",
    message: `You were added to ${group.name}`
  });
  res.json(await group.populate("members.user", "name email avatar"));
};

export const removeMember = async (req, res) => {
  const group = await Group.findById(req.params.id);
  if (!group) return res.status(404).json({ message: "Group not found" });
  const requester = group.members.find((member) => String(member.user) === String(req.user._id));
  if (!requester || requester.role !== "owner") return res.status(403).json({ message: "Only owner can remove members" });
  group.members = group.members.filter((member) => String(member.user) !== String(req.params.userId));
  await group.save();
  res.json(await group.populate("members.user", "name email avatar"));
};
"""

EXPENSE_CONTROLLER = """
File: backend/src/controllers/expenseController.js

import Expense from "../models/Expense.js";
import Group from "../models/Group.js";
import { assertPercentTotal } from "../utils/money.js";
import { notifyUsers } from "../utils/notifications.js";
import { buildSplits } from "../utils/splitter.js";

const ensureMember = (group, userId) => group.members.some((member) => String(member.user) === String(userId));

export const listExpenses = async (req, res) => {
  const group = await Group.findById(req.params.groupId);
  if (!group || !ensureMember(group, req.user._id)) return res.status(403).json({ message: "Group access denied" });
  const page = Math.max(Number(req.query.page || 1), 1);
  const limit = Math.min(Number(req.query.limit || 20), 50);
  const [items, total] = await Promise.all([
    Expense.find({ group: group._id })
      .populate("payer", "name email")
      .populate("splits.user", "name email")
      .sort({ createdAt: -1 })
      .skip((page - 1) * limit)
      .limit(limit),
    Expense.countDocuments({ group: group._id })
  ]);
  res.json({ items, total, page, pages: Math.ceil(total / limit) || 1 });
};

export const createExpense = async (req, res) => {
  const group = await Group.findById(req.body.group);
  if (!group || !ensureMember(group, req.user._id)) return res.status(403).json({ message: "Group access denied" });
  if (!ensureMember(group, req.body.payer)) return res.status(422).json({ message: "Payer must be a group member" });

  const memberIds = group.members.map((member) => String(member.user));
  const customSplits = typeof req.body.splits === "string" ? JSON.parse(req.body.splits) : req.body.splits;
  if (req.body.splitType === "custom" && !assertPercentTotal(customSplits || [])) {
    return res.status(422).json({ message: "Custom split percentages must total 100" });
  }

  const expense = await Expense.create({
    title: req.body.title,
    amount: Number(req.body.amount),
    category: req.body.category,
    payer: req.body.payer,
    group: group._id,
    splitType: req.body.splitType || "equal",
    splits: buildSplits({
      amount: Number(req.body.amount),
      splitType: req.body.splitType || "equal",
      memberIds,
      customSplits
    }),
    billImage: req.file ? `/uploads/${req.file.filename}` : "",
    notes: req.body.notes || "",
    createdBy: req.user._id
  });

  await notifyUsers({
    users: memberIds,
    group: group._id,
    type: "expense_added",
    title: "New expense added",
    message: `${req.user.name} added ${expense.title} in ${group.name}`
  });

  res.status(201).json(await expense.populate(["payer", "splits.user"]));
};

export const updateExpense = async (req, res) => {
  const expense = await Expense.findById(req.params.id);
  if (!expense) return res.status(404).json({ message: "Expense not found" });
  const group = await Group.findById(expense.group);
  if (!group || !ensureMember(group, req.user._id)) return res.status(403).json({ message: "Expense access denied" });
  if (String(expense.createdBy) !== String(req.user._id) && String(group.createdBy) !== String(req.user._id)) {
    return res.status(403).json({ message: "Only the creator or group owner can edit this expense" });
  }

  const memberIds = group.members.map((member) => String(member.user));
  const splitType = req.body.splitType || expense.splitType;
  const customSplits = typeof req.body.splits === "string" ? JSON.parse(req.body.splits) : req.body.splits;
  if (splitType === "custom" && !assertPercentTotal(customSplits || expense.splits)) {
    return res.status(422).json({ message: "Custom split percentages must total 100" });
  }

  Object.assign(expense, {
    title: req.body.title ?? expense.title,
    amount: req.body.amount ? Number(req.body.amount) : expense.amount,
    category: req.body.category ?? expense.category,
    payer: req.body.payer ?? expense.payer,
    splitType,
    notes: req.body.notes ?? expense.notes,
    billImage: req.file ? `/uploads/${req.file.filename}` : expense.billImage
  });
  expense.splits = buildSplits({
    amount: expense.amount,
    splitType,
    memberIds,
    customSplits: customSplits || expense.splits
  });
  await expense.save();
  res.json(await expense.populate(["payer", "splits.user"]));
};

export const deleteExpense = async (req, res) => {
  const expense = await Expense.findById(req.params.id);
  if (!expense) return res.status(404).json({ message: "Expense not found" });
  const group = await Group.findById(expense.group);
  if (!group || !ensureMember(group, req.user._id)) return res.status(403).json({ message: "Expense access denied" });
  if (String(expense.createdBy) !== String(req.user._id) && String(group.createdBy) !== String(req.user._id)) {
    return res.status(403).json({ message: "Only the creator or group owner can delete this expense" });
  }
  await expense.deleteOne();
  res.json({ message: "Expense deleted" });
};
"""

SETTLEMENT_CONTROLLER = """
File: backend/src/controllers/settlementController.js

import Expense from "../models/Expense.js";
import Group from "../models/Group.js";
import Settlement from "../models/Settlement.js";
import { notifyUsers } from "../utils/notifications.js";
import { calculateGroupLedger } from "../utils/splitter.js";

const ensureMember = (group, userId) => group.members.some((member) => String(member.user._id || member.user) === String(userId));

export const getSettlementSummary = async (req, res) => {
  const group = await Group.findById(req.params.groupId).populate("members.user", "name email");
  if (!group || !ensureMember(group, req.user._id)) return res.status(403).json({ message: "Group access denied" });
  const [ledger, history, totalsByCategory, monthly] = await Promise.all([
    calculateGroupLedger(group),
    Settlement.find({ group: group._id }).populate("from to", "name email").sort({ createdAt: -1 }).limit(30),
    Expense.aggregate([{ $match: { group: group._id } }, { $group: { _id: "$category", total: { $sum: "$amount" } } }]),
    Expense.aggregate([
      { $match: { group: group._id } },
      { $group: { _id: { $dateToString: { date: "$createdAt", format: "%Y-%m" } }, total: { $sum: "$amount" } } },
      { $sort: { _id: 1 } }
    ])
  ]);
  res.json({ ...ledger, history, totalsByCategory, monthly });
};

export const recordPayment = async (req, res) => {
  const group = await Group.findById(req.body.group);
  if (!group || !ensureMember(group, req.user._id)) return res.status(403).json({ message: "Group access denied" });
  const settlement = await Settlement.create({
    group: group._id,
    from: req.body.from,
    to: req.body.to,
    amount: Number(req.body.amount),
    note: req.body.note || "",
    recordedBy: req.user._id,
    status: "completed"
  });
  await notifyUsers({
    users: [req.body.from, req.body.to],
    group: group._id,
    type: "settlement_completed",
    title: "Settlement recorded",
    message: `A payment of ${settlement.amount} was recorded in ${group.name}`
  });
  res.status(201).json(await settlement.populate("from to", "name email"));
};

export const sendReminder = async (req, res) => {
  const group = await Group.findById(req.body.group);
  if (!group || !ensureMember(group, req.user._id)) return res.status(403).json({ message: "Group access denied" });
  await notifyUsers({
    users: [req.body.to],
    group: group._id,
    type: "reminder",
    title: "Payment reminder",
    message: req.body.message || `${req.user.name} sent you a payment reminder for ${group.name}`
  });
  res.json({ message: "Reminder sent" });
};
"""

NOTIFICATION_CONTROLLER = """
File: backend/src/controllers/notificationController.js

import Notification from "../models/Notification.js";

export const listNotifications = async (req, res) => {
  const notifications = await Notification.find({ user: req.user._id }).sort({ createdAt: -1 }).limit(50);
  res.json(notifications);
};

export const markRead = async (req, res) => {
  const notification = await Notification.findOneAndUpdate(
    { _id: req.params.id, user: req.user._id },
    { read: true },
    { new: true }
  );
  if (!notification) return res.status(404).json({ message: "Notification not found" });
  res.json(notification);
};
"""

INSIGHT_CONTROLLER = """
File: backend/src/controllers/insightController.js

import Expense from "../models/Expense.js";
import Group from "../models/Group.js";

const ensureMember = (group, userId) => group.members.some((member) => String(member.user) === String(userId));

export const getInsights = async (req, res) => {
  const group = await Group.findById(req.params.groupId);
  if (!group || !ensureMember(group, req.user._id)) return res.status(403).json({ message: "Group access denied" });

  const [categoryTotals, payerTotals, monthlyTotals, total] = await Promise.all([
    Expense.aggregate([{ $match: { group: group._id } }, { $group: { _id: "$category", total: { $sum: "$amount" } } }, { $sort: { total: -1 } }]),
    Expense.aggregate([{ $match: { group: group._id } }, { $group: { _id: "$payer", total: { $sum: "$amount" } } }, { $sort: { total: -1 } }]),
    Expense.aggregate([
      { $match: { group: group._id } },
      { $group: { _id: { $dateToString: { date: "$createdAt", format: "%Y-%m" } }, total: { $sum: "$amount" } } },
      { $sort: { _id: 1 } }
    ]),
    Expense.aggregate([{ $match: { group: group._id } }, { $group: { _id: null, total: { $sum: "$amount" } } }])
  ]);

  const topCategory = categoryTotals[0];
  const activeSpender = payerTotals[0];
  const current = monthlyTotals.at(-1)?.total || 0;
  const previous = monthlyTotals.at(-2)?.total || 0;
  const trend = previous ? Math.round(((current - previous) / previous) * 100) : 0;
  const warnings = [];
  if (group.budgetLimit && current > group.budgetLimit) warnings.push(`This month is ${Math.round(((current - group.budgetLimit) / group.budgetLimit) * 100)}% over budget.`);
  if (trend > 25) warnings.push(`Spending is up ${trend}% compared with last month.`);

  const suggestions = [
    topCategory ? `${topCategory._id} is the highest spending category. Review repeat purchases there first.` : "Add expenses to unlock category insights.",
    trend > 0 ? "Settle smaller balances weekly to avoid end-of-month confusion." : "Current spending trend is stable. Keep recording bills consistently.",
    warnings.length ? "Create a category budget before adding the next large expense." : "No budget warning right now."
  ];

  res.json({
    total: total[0]?.total || 0,
    topCategory,
    activeSpender,
    monthlyTotals,
    categoryTotals,
    trend,
    warnings,
    suggestions
  });
};
"""

# ===== UTILITIES =====

TOKEN_UTIL = """
File: backend/src/utils/token.js

import jwt from "jsonwebtoken";

export const generateToken = (id) =>
  jwt.sign({ id }, process.env.JWT_SECRET || "dev-secret", {
    expiresIn: "7d"
  });
"""

MONEY_UTIL = """
File: backend/src/utils/money.js

export const roundMoney = (value) => Math.round((Number(value) + Number.EPSILON) * 100) / 100;

export const assertPercentTotal = (splits) => {
  const total = roundMoney(splits.reduce((sum, split) => sum + Number(split.percentage || 0), 0));
  return Math.abs(total - 100) <= 0.01;
};
"""

NOTIFICATIONS_UTIL = """
File: backend/src/utils/notifications.js

import Notification from "../models/Notification.js";

export const notifyUsers = async ({ users, group, type, title, message }) => {
  const uniqueUsers = [...new Set(users.map(String))];
  if (!uniqueUsers.length) return [];
  return Notification.insertMany(
    uniqueUsers.map((user) => ({
      user,
      group,
      type,
      title,
      message
    }))
  );
};
"""

SPLITTER_UTIL = """
File: backend/src/utils/splitter.js

import Expense from "../models/Expense.js";
import Settlement from "../models/Settlement.js";
import { roundMoney } from "./money.js";

export const buildSplits = ({ amount, splitType, memberIds, customSplits = [] }) => {
  const total = roundMoney(amount);
  if (splitType === "custom") {
    return customSplits.map((split) => ({
      user: split.user,
      percentage: Number(split.percentage),
      amount: roundMoney((total * Number(split.percentage)) / 100)
    }));
  }

  const share = roundMoney(total / memberIds.length);
  const splits = memberIds.map((user) => ({ user, percentage: roundMoney(100 / memberIds.length), amount: share }));
  const drift = roundMoney(total - splits.reduce((sum, split) => sum + split.amount, 0));
  if (splits.length && drift !== 0) splits[0].amount = roundMoney(splits[0].amount + drift);
  return splits;
};

export const calculateGroupLedger = async (group) => {
  const memberIds = group.members.map((member) => String(member.user._id || member.user));
  const names = new Map(
    group.members.map((member) => {
      const user = member.user;
      return [String(user._id || user), user.name || "Member"];
    })
  );
  const balances = new Map(memberIds.map((id) => [id, 0]));
  const expenses = await Expense.find({ group: group._id });
  const settlements = await Settlement.find({ group: group._id, status: "completed" });

  expenses.forEach((expense) => {
    balances.set(String(expense.payer), roundMoney((balances.get(String(expense.payer)) || 0) + expense.amount));
    expense.splits.forEach((split) => {
      balances.set(String(split.user), roundMoney((balances.get(String(split.user)) || 0) - split.amount));
    });
  });

  settlements.forEach((settlement) => {
    balances.set(String(settlement.from), roundMoney((balances.get(String(settlement.from)) || 0) + settlement.amount));
    balances.set(String(settlement.to), roundMoney((balances.get(String(settlement.to)) || 0) - settlement.amount));
  });

  const balanceList = [...balances.entries()].map(([user, balance]) => ({
    user,
    name: names.get(user) || "Member",
    balance: roundMoney(balance)
  }));

  const debtors = balanceList.filter((item) => item.balance < -0.01).sort((a, b) => a.balance - b.balance);
  const creditors = balanceList.filter((item) => item.balance > 0.01).sort((a, b) => b.balance - a.balance);
  const suggestions = [];
  let debtorIndex = 0;
  let creditorIndex = 0;

  while (debtorIndex < debtors.length && creditorIndex < creditors.length) {
    const debtor = debtors[debtorIndex];
    const creditor = creditors[creditorIndex];
    const amount = roundMoney(Math.min(Math.abs(debtor.balance), creditor.balance));
    if (amount > 0) {
      suggestions.push({ from: debtor.user, fromName: debtor.name, to: creditor.user, toName: creditor.name, amount });
      debtor.balance = roundMoney(debtor.balance + amount);
      creditor.balance = roundMoney(creditor.balance - amount);
    }
    if (Math.abs(debtor.balance) <= 0.01) debtorIndex += 1;
    if (Math.abs(creditor.balance) <= 0.01) creditorIndex += 1;
  }

  return { balances: balanceList, suggestions };
};
"""

# ===== ROUTES =====

AUTH_ROUTES = """
File: backend/src/routes/authRoutes.js

import { Router } from "express";
import { body } from "express-validator";
import { login, profile, register } from "../controllers/authController.js";
import { protect } from "../middleware/authMiddleware.js";
import { validate } from "../middleware/validate.js";

const router = Router();

router.post(
  "/register",
  [body("name").trim().isLength({ min: 2 }), body("email").isEmail().normalizeEmail(), body("password").isLength({ min: 6 })],
  validate,
  register
);
router.post("/login", [body("email").isEmail().normalizeEmail(), body("password").notEmpty()], validate, login);
router.get("/profile", protect, profile);

export default router;
"""

GROUP_ROUTES = """
File: backend/src/routes/groupRoutes.js

import { Router } from "express";
import { body } from "express-validator";
import { addMember, createGroup, getGroup, listGroups, removeMember } from "../controllers/groupController.js";
import { protect } from "../middleware/authMiddleware.js";
import { validate } from "../middleware/validate.js";

const router = Router();

router.use(protect);
router.route("/").get(listGroups).post([body("name").trim().isLength({ min: 2 }), body("budgetLimit").optional().isNumeric()], validate, createGroup);
router.get("/:id", getGroup);
router.post("/:id/members", [body("email").isEmail().normalizeEmail()], validate, addMember);
router.delete("/:id/members/:userId", removeMember);

export default router;
"""

EXPENSE_ROUTES = """
File: backend/src/routes/expenseRoutes.js

import { Router } from "express";
import { body } from "express-validator";
import { createExpense, deleteExpense, listExpenses, updateExpense } from "../controllers/expenseController.js";
import { protect } from "../middleware/authMiddleware.js";
import { uploadBill } from "../middleware/upload.js";
import { validate } from "../middleware/validate.js";

const router = Router();

const expenseRules = [
  body("title").trim().isLength({ min: 2 }),
  body("amount").isFloat({ min: 0.01 }),
  body("category").optional().trim(),
  body("payer").isMongoId(),
  body("group").isMongoId(),
  body("splitType").optional().isIn(["equal", "custom"])
];

router.use(protect);
router.get("/group/:groupId", listExpenses);
router.post("/", uploadBill.single("billImage"), expenseRules, validate, createExpense);
router.put("/:id", uploadBill.single("billImage"), validate, updateExpense);
router.delete("/:id", deleteExpense);

export default router;
"""

SETTLEMENT_ROUTES = """
File: backend/src/routes/settlementRoutes.js

import { Router } from "express";
import { body } from "express-validator";
import { getSettlementSummary, recordPayment, sendReminder } from "../controllers/settlementController.js";
import { protect } from "../middleware/authMiddleware.js";
import { validate } from "../middleware/validate.js";

const router = Router();

router.use(protect);
router.get("/:groupId", getSettlementSummary);
router.post(
  "/pay",
  [body("group").isMongoId(), body("from").isMongoId(), body("to").isMongoId(), body("amount").isFloat({ min: 0.01 })],
  validate,
  recordPayment
);
router.post("/remind", [body("group").isMongoId(), body("to").isMongoId()], validate, sendReminder);

export default router;
"""

NOTIFICATION_ROUTES = """
File: backend/src/routes/notificationRoutes.js

import { Router } from "express";
import { listNotifications, markRead } from "../controllers/notificationController.js";
import { protect } from "../middleware/authMiddleware.js";

const router = Router();

router.use(protect);
router.get("/", listNotifications);
router.patch("/:id/read", markRead);

export default router;
"""

INSIGHT_ROUTES = """
File: backend/src/routes/insightRoutes.js

import { Router } from "express";
import { getInsights } from "../controllers/insightController.js";
import { protect } from "../middleware/authMiddleware.js";

const router = Router();

router.use(protect);
router.get("/:groupId", getInsights);

export default router;
"""

# ===== BACKEND PACKAGE.JSON =====

BACKEND_PACKAGE_JSON = """
File: backend/package.json

{
  "name": "expense-splitter-backend",
  "version": "1.0.0",
  "type": "module",
  "main": "src/server.js",
  "scripts": {
    "dev": "nodemon src/server.js",
    "start": "node src/server.js"
  },
  "dependencies": {
    "bcryptjs": "^2.4.3",
    "cors": "^2.8.5",
    "dotenv": "^16.4.5",
    "express": "^4.18.3",
    "express-rate-limit": "^7.2.0",
    "express-validator": "^7.0.1",
    "helmet": "^7.1.0",
    "jsonwebtoken": "^9.0.2",
    "mongoose": "^8.2.1",
    "morgan": "^1.10.0",
    "multer": "^1.4.5-lts.1",
    "sanitize-html": "^2.12.1",
    "xss-clean": "^0.1.4"
  },
  "devDependencies": {
    "nodemon": "^3.1.0"
  }
}
"""

# ===== FRONTEND CODE =====

"""
================================================================================
FRONTEND CODE
================================================================================

===== FRONTEND MAIN FILES =====

File: frontend/index.html
"""

FRONTEND_INDEX_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Expense Splitter</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
"""

FRONTEND_MAIN_JSX = """
File: frontend/src/main.jsx

import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.jsx";
import { AuthProvider } from "./context/AuthContext.jsx";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
"""

FRONTEND_APP_JSX = """
File: frontend/src/App.jsx

import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import AuthPage from "./pages/AuthPage";
import Dashboard from "./pages/Dashboard";
import { useAuth } from "./context/AuthContext";

const PrivateRoute = ({ children }) => {
  const { user } = useAuth();
  return user ? children : <Navigate to="/auth" replace />;
};

export default function App() {
  const { user } = useAuth();
  return (
    <Routes>
      <Route path="/auth" element={user ? <Navigate to="/" replace /> : <AuthPage />} />
      <Route
        path="/*"
        element={
          <PrivateRoute>
            <Dashboard />
          </PrivateRoute>
        }
      />
    </Routes>
  );
}
"""

FRONTEND_STYLES_CSS = """
File: frontend/src/styles.css

@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  color-scheme: light;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.dark {
  color-scheme: dark;
}

body {
  margin: 0;
  min-width: 320px;
  background: #f7f5f0;
  color: #18212f;
}

.dark body {
  background: #14171f;
  color: #f7f5f0;
}

input,
select,
textarea {
  @apply rounded-md border border-stone-300 bg-white px-3 py-2 text-sm text-ink outline-none transition focus:border-mint focus:ring-2 focus:ring-mint/20 dark:border-slate-700 dark:bg-slate-900 dark:text-stone-100;
}

button {
  @apply transition;
}
"""

# ===== FRONTEND CONTEXT =====

AUTH_CONTEXT = """
File: frontend/src/context/AuthContext.jsx

import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import api from "../services/api";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => JSON.parse(localStorage.getItem("expense-user") || "null"));
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", localStorage.getItem("theme") === "dark");
  }, []);

  const setSession = ({ token, user: sessionUser }) => {
    localStorage.setItem("expense-token", token);
    localStorage.setItem("expense-user", JSON.stringify(sessionUser));
    setUser(sessionUser);
  };

  const login = async (payload) => {
    setLoading(true);
    try {
      const { data } = await api.post("/auth/login", payload);
      setSession(data);
    } finally {
      setLoading(false);
    }
  };

  const register = async (payload) => {
    setLoading(true);
    try {
      const { data } = await api.post("/auth/register", payload);
      setSession(data);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("expense-token");
    localStorage.removeItem("expense-user");
    setUser(null);
  };

  const toggleTheme = () => {
    const next = document.documentElement.classList.contains("dark") ? "light" : "dark";
    localStorage.setItem("theme", next);
    document.documentElement.classList.toggle("dark", next === "dark");
  };

  const value = useMemo(() => ({ user, loading, login, register, logout, toggleTheme }), [user, loading]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => useContext(AuthContext);
"""

# ===== FRONTEND SERVICES =====

API_SERVICE = """
File: frontend/src/services/api.js

import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:5001/api"
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("expense-token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(error.response?.data || { message: "Network error" })
);

export default api;
"""

# ===== FRONTEND UTILS =====

FORMAT_UTIL = """
File: frontend/src/utils/format.js

export const currency = (value) =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value || 0);

export const shortDate = (date) => new Intl.DateTimeFormat("en-IN", { day: "numeric", month: "short" }).format(new Date(date));
"""

# ===== FRONTEND COMPONENTS =====

BUTTON_COMPONENT = """
File: frontend/src/components/Button.jsx

import React from "react";

export default function Button({ children, className = "", variant = "primary", ...props }) {
  const styles = {
    primary: "bg-ink text-white hover:bg-ink/90 dark:bg-mint dark:text-slate-950",
    secondary: "bg-white text-ink ring-1 ring-stone-200 hover:bg-stone-50 dark:bg-slate-900 dark:text-stone-100 dark:ring-slate-700",
    danger: "bg-coral text-white hover:bg-coral/90",
    ghost: "text-ink hover:bg-stone-100 dark:text-stone-100 dark:hover:bg-slate-800"
  };
  return (
    <button
      className={`inline-flex min-h-10 items-center justify-center gap-2 rounded-md px-4 py-2 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60 ${styles[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
"""

STAT_CARD_COMPONENT = """
File: frontend/src/components/StatCard.jsx

import React from "react";

export default function StatCard({ label, value, icon: Icon, tone = "mint" }) {
  const tones = {
    mint: "bg-mint/15 text-mint",
    coral: "bg-coral/15 text-coral",
    amber: "bg-amber/20 text-amber",
    ink: "bg-ink/10 text-ink dark:bg-white/10 dark:text-white"
  };
  return (
    <section className="rounded-lg bg-white p-4 shadow-soft dark:bg-slate-900">
      <div className="flex items-center justify-between">
        <p className="text-sm text-stone-500 dark:text-stone-400">{label}</p>
        {Icon ? (
          <span className={`rounded-md p-2 ${tones[tone]}`}>
            <Icon size={18} />
          </span>
        ) : null}
      </div>
      <strong className="mt-3 block text-2xl font-bold">{value}</strong>
    </section>
  );
}
"""

EMPTY_STATE_COMPONENT = """
File: frontend/src/components/EmptyState.jsx

import React from "react";

export default function EmptyState({ title, description, action }) {
  return (
    <div className="rounded-lg border border-dashed border-stone-300 bg-white/70 p-8 text-center dark:border-slate-700 dark:bg-slate-900/70">
      <h3 className="text-base font-semibold">{title}</h3>
      <p className="mx-auto mt-2 max-w-md text-sm text-stone-600 dark:text-stone-300">{description}</p>
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}
"""

APP_SHELL_COMPONENT = """
File: frontend/src/components/AppShell.jsx

import React from "react";
import { Bell, LogOut, Moon, Plus, SunMedium, Users } from "lucide-react";
import Button from "./Button";
import { useAuth } from "../context/AuthContext";

export default function AppShell({ children, groups, activeGroupId, onSelectGroup, onNewGroup, notifications }) {
  const { user, logout, toggleTheme } = useAuth();
  return (
    <div className="min-h-screen bg-stone-100 dark:bg-slate-950">
      <header className="sticky top-0 z-20 border-b border-stone-200 bg-white/90 backdrop-blur dark:border-slate-800 dark:bg-slate-950/90">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-3">
          <div>
            <h1 className="text-lg font-bold tracking-normal">Expense Splitter</h1>
            <p className="text-xs text-stone-500 dark:text-stone-400">Signed in as {user?.name}</p>
          </div>
          <div className="flex items-center gap-2">
            <button title="Notifications" className="relative rounded-md p-2 hover:bg-stone-100 dark:hover:bg-slate-800">
              <Bell size={19} />
              {notifications?.some((item) => !item.read) ? <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-coral" /> : null}
            </button>
            <button title="Toggle theme" className="rounded-md p-2 hover:bg-stone-100 dark:hidden" onClick={toggleTheme}>
              <Moon size={19} />
            </button>
            <button title="Toggle theme" className="hidden rounded-md p-2 hover:bg-slate-800 dark:block" onClick={toggleTheme}>
              <SunMedium size={19} />
            </button>
            <button title="Log out" className="rounded-md p-2 hover:bg-stone-100 dark:hover:bg-slate-800" onClick={logout}>
              <LogOut size={19} />
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl gap-4 px-4 py-4 lg:grid-cols-[260px_1fr]">
        <aside className="h-fit rounded-lg bg-white p-3 shadow-soft dark:bg-slate-900">
          <div className="mb-3 flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <Users size={18} /> Groups
            </div>
            <Button variant="ghost" className="min-h-8 px-2" onClick={onNewGroup} title="Create group">
              <Plus size={17} />
            </Button>
          </div>
          <div className="grid gap-1">
            {groups.map((group) => (
              <button
                key={group._id}
                onClick={() => onSelectGroup(group._id)}
                className={`rounded-md px-3 py-2 text-left text-sm ${
                  activeGroupId === group._id ? "bg-ink text-white dark:bg-mint dark:text-slate-950" : "hover:bg-stone-100 dark:hover:bg-slate-800"
                }`}
              >
                <span className="block font-semibold">{group.name}</span>
                <span className="text-xs opacity-75">{group.members?.length || 0} members</span>
              </button>
            ))}
          </div>
        </aside>
        <main>{children}</main>
      </div>
    </div>
  );
}
"""

# ===== FRONTEND PAGES =====

AUTH_PAGE = """
File: frontend/src/pages/AuthPage.jsx

import React, { useState } from "react";
import { CreditCard, Loader2 } from "lucide-react";
import Button from "../components/Button";
import { useAuth } from "../context/AuthContext";

export default function AuthPage() {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const { login, register, loading } = useAuth();

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    try {
      if (mode === "login") await login({ email: form.email, password: form.password });
      else await register(form);
    } catch (err) {
      setError(err.message || "Something went wrong");
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-stone-100 px-4 py-8 dark:bg-slate-950">
      <section className="grid w-full max-w-5xl overflow-hidden rounded-lg bg-white shadow-soft dark:bg-slate-900 md:grid-cols-[1fr_420px]">
        <div className="flex min-h-[520px] flex-col justify-between bg-ink p-8 text-white dark:bg-slate-800">
          <div className="flex items-center gap-3">
            <span className="rounded-md bg-mint p-3 text-slate-950">
              <CreditCard size={24} />
            </span>
            <span className="text-xl font-bold">Expense Splitter</span>
          </div>
          <div>
            <h1 className="max-w-xl text-4xl font-bold tracking-normal">Split bills, settle faster, understand spending.</h1>
            <p className="mt-4 max-w-lg text-stone-200">
              Create groups, upload bills, calculate equal or custom splits, send reminders, and get spending insights in one place.
            </p>
          </div>
          <div className="grid grid-cols-3 gap-3 text-sm text-stone-200">
            <span>JWT auth</span>
            <span>Smart settlements</span>
            <span>AI-style insights</span>
          </div>
        </div>
        <form onSubmit={submit} className="flex flex-col justify-center gap-4 p-6">
          <div>
            <h2 className="text-2xl font-bold">{mode === "login" ? "Welcome back" : "Create account"}</h2>
            <p className="text-sm text-stone-500 dark:text-stone-400">Use MongoDB-backed secure authentication.</p>
          </div>
          {mode === "register" ? (
            <label className="grid gap-1 text-sm">
              Name
              <input required value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
            </label>
          ) : null}
          <label className="grid gap-1 text-sm">
            Email
            <input required type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} />
          </label>
          <label className="grid gap-1 text-sm">
            Password
            <input required type="password" minLength={6} value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} />
          </label>
          {error ? <p className="rounded-md bg-coral/10 px-3 py-2 text-sm text-coral">{error}</p> : null}
          <Button disabled={loading}>
            {loading ? <Loader2 className="animate-spin" size={17} /> : null}
            {mode === "login" ? "Log in" : "Create account"}
          </Button>
          <button type="button" className="text-sm font-semibold text-mint" onClick={() => setMode(mode === "login" ? "register" : "login")}>
            {mode === "login" ? "Need an account? Register" : "Already registered? Log in"}
          </button>
        </form>
      </section>
    </main>
  );
}
"""

DASHBOARD_PAGE = """
File: frontend/src/pages/Dashboard.jsx
[Full Dashboard implementation with forms and charts - See source for complete code]

Key Features:
- Group management and selection
- Expense tracking with categories
- Settlement calculations and suggestions
- AI-powered insights with spending trends
- Monthly spending visualization
- Category breakdown charts
- Member balance tracking
- Real-time notifications

The Dashboard includes:
1. StatCard display for key metrics
2. Monthly spending area chart
3. Category breakdown pie chart
4. Member balance list
5. Settlement suggestions
6. Transaction history
7. AI spending insights with warnings
8. Modal forms for creating groups, adding members, and recording expenses
"""

# ===== FRONTEND CONFIG =====

VITE_CONFIG = """
File: frontend/vite.config.js

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5173
  }
});
"""

TAILWIND_CONFIG = """
File: frontend/tailwind.config.js

export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#18212f",
        mint: "#3ea987",
        coral: "#ef6f61",
        amber: "#f6b44b"
      },
      boxShadow: {
        soft: "0 18px 50px rgba(24, 33, 47, 0.12)"
      }
    }
  },
  plugins: []
};
"""

POSTCSS_CONFIG = """
File: frontend/postcss.config.js

export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {}
  }
};
"""

# ===== FRONTEND PACKAGE.JSON =====

FRONTEND_PACKAGE_JSON = """
File: frontend/package.json

{
  "name": "expense-splitter-frontend",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite --host 0.0.0.0",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@vitejs/plugin-react": "^4.2.1",
    "axios": "^1.6.8",
    "framer-motion": "^11.0.8",
    "lucide-react": "^0.468.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.22.3",
    "recharts": "^2.12.2"
  },
  "devDependencies": {
    "autoprefixer": "^10.4.18",
    "postcss": "^8.4.35",
    "tailwindcss": "^3.4.1",
    "vite": "^5.1.4"
  }
}
"""

# ===== ENVIRONMENT SETUP =====

BACKEND_ENV = """
File: .env (Backend)

PORT=5001
MONGO_URI=mongodb+srv://bansalyash316_db_user:Rv7ljsytxs60BjfO@cluster0.5t2kxf7.mongodb.net
JWT_SECRET=fdf438726d3a38edbf908eb98e19052f39020c51e64280871386863a87880b18058d7c6adabb37a0
CLIENT_URL=http://localhost:5173
NODE_ENV=development
"""

FRONTEND_ENV = """
File: .env (Frontend)

VITE_API_URL=http://localhost:5001/api
"""

print(__doc__)
