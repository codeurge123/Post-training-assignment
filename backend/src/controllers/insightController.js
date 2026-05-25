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
