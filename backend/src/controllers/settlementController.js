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
