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
