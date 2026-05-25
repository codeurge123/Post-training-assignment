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
