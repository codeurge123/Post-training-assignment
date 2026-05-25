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
