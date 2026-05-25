import React, { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { IndianRupee, Plus, ReceiptText, Send, Sparkles, Users } from "lucide-react";
import AppShell from "../components/AppShell";
import Button from "../components/Button";
import EmptyState from "../components/EmptyState";
import StatCard from "../components/StatCard";
import api from "../services/api";
import { currency, shortDate } from "../utils/format";

const colors = ["#3ea987", "#ef6f61", "#f6b44b", "#5577c6", "#8f6bbd", "#64748b"];
const categories = ["Food", "Rent", "Travel", "Shopping", "Utilities", "Entertainment", "Other"];

export default function Dashboard() {
  const [groups, setGroups] = useState([]);
  const [activeGroupId, setActiveGroupId] = useState("");
  const [groupDetail, setGroupDetail] = useState(null);
  const [expenses, setExpenses] = useState([]);
  const [summary, setSummary] = useState(null);
  const [insights, setInsights] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [panel, setPanel] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const activeGroup = groupDetail?.group;

  const loadGroups = async () => {
    const { data } = await api.get("/groups");
    setGroups(data);
    if (!activeGroupId && data[0]) setActiveGroupId(data[0]._id);
  };

  const loadGroupData = async (groupId) => {
    if (!groupId) return;
    setLoading(true);
    try {
      const [groupRes, expenseRes, settlementRes, insightRes, notificationRes] = await Promise.all([
        api.get(`/groups/${groupId}`),
        api.get(`/expenses/group/${groupId}`),
        api.get(`/settlements/${groupId}`),
        api.get(`/insights/${groupId}`),
        api.get("/notifications")
      ]);
      setGroupDetail(groupRes.data);
      setExpenses(expenseRes.data.items);
      setSummary(settlementRes.data);
      setInsights(insightRes.data);
      setNotifications(notificationRes.data);
    } catch (err) {
      setError(err.message || "Could not load dashboard");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGroups().catch((err) => setError(err.message || "Could not load groups"));
  }, []);

  useEffect(() => {
    loadGroupData(activeGroupId);
  }, [activeGroupId]);

  const refresh = async () => {
    await loadGroups();
    await loadGroupData(activeGroupId);
  };

  const chartCategories = useMemo(
    () => (summary?.totalsByCategory || []).map((item) => ({ name: item._id, value: item.total })),
    [summary]
  );
  const monthly = useMemo(() => (summary?.monthly || []).map((item) => ({ month: item._id, total: item.total })), [summary]);

  return (
    <AppShell
      groups={groups}
      activeGroupId={activeGroupId}
      onSelectGroup={setActiveGroupId}
      onNewGroup={() => setPanel("group")}
      notifications={notifications}
    >
      {error ? <p className="mb-4 rounded-md bg-coral/10 px-3 py-2 text-sm text-coral">{error}</p> : null}
      {!groups.length && !loading ? (
        <EmptyState title="Create your first group" description="Start a trip, flat, or outing group before adding shared expenses." action={<Button onClick={() => setPanel("group")}><Plus size={17} /> New group</Button>} />
      ) : (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="grid gap-4">
          <div className="flex flex-col justify-between gap-3 rounded-lg bg-white p-5 shadow-soft dark:bg-slate-900 md:flex-row md:items-center">
            <div>
              <h2 className="text-2xl font-bold">{activeGroup?.name || "Loading group"}</h2>
              <p className="text-sm text-stone-500 dark:text-stone-400">{activeGroup?.description || "Dashboard for shared expenses and settlements."}</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button variant="secondary" onClick={() => setPanel("member")}><Users size={17} /> Add member</Button>
              <Button onClick={() => setPanel("expense")}><Plus size={17} /> Add expense</Button>
            </div>
          </div>

          <section className="grid gap-4 md:grid-cols-3">
            <StatCard label="Total group expenses" value={currency(groupDetail?.totalExpense)} icon={IndianRupee} tone="mint" />
            <StatCard label="Open settlements" value={summary?.suggestions?.length || 0} icon={Send} tone="coral" />
            <StatCard label="Members" value={activeGroup?.members?.length || 0} icon={Users} tone="amber" />
          </section>

          <section className="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
            <Panel title="Monthly spending">
              <ResponsiveContainer width="100%" height={260}>
                <AreaChart data={monthly}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value) => currency(value)} />
                  <Area type="monotone" dataKey="total" stroke="#3ea987" fill="#3ea98755" />
                </AreaChart>
              </ResponsiveContainer>
            </Panel>
            <Panel title="Category breakdown">
              {chartCategories.length ? (
                <ResponsiveContainer width="100%" height={260}>
                  <PieChart>
                    <Pie data={chartCategories} dataKey="value" nameKey="name" innerRadius={55} outerRadius={90}>
                      {chartCategories.map((_, index) => <Cell key={index} fill={colors[index % colors.length]} />)}
                    </Pie>
                    <Tooltip formatter={(value) => currency(value)} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <EmptyState title="No category data" description="Add expenses to populate this chart." />
              )}
            </Panel>
          </section>

          <section className="grid gap-4 xl:grid-cols-[1fr_1fr]">
            <Panel title="Balances">
              <div className="grid gap-2">
                {(groupDetail?.ledger?.balances || []).map((item) => (
                  <div key={item.user} className="flex items-center justify-between rounded-md bg-stone-50 px-3 py-2 dark:bg-slate-800">
                    <span className="font-medium">{item.name}</span>
                    <span className={item.balance >= 0 ? "text-mint" : "text-coral"}>{currency(item.balance)}</span>
                  </div>
                ))}
              </div>
            </Panel>
            <Panel title="Settlement summary">
              <div className="grid gap-2">
                {(summary?.suggestions || []).length ? summary.suggestions.map((item) => (
                  <div key={`${item.from}-${item.to}-${item.amount}`} className="flex flex-wrap items-center justify-between gap-2 rounded-md bg-stone-50 px-3 py-2 dark:bg-slate-800">
                    <span>{item.fromName} pays {item.toName}</span>
                    <div className="flex items-center gap-2">
                      <strong>{currency(item.amount)}</strong>
                      <Button className="min-h-8 px-3" onClick={() => recordSettlement(item)}>Settle</Button>
                    </div>
                  </div>
                )) : <EmptyState title="All settled" description="No payments are pending for this group." />}
              </div>
            </Panel>
          </section>

          <section className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
            <Panel title="Transactions">
              <div className="grid gap-2">
                {expenses.length ? expenses.map((expense) => (
                  <div key={expense._id} className="grid gap-2 rounded-md border border-stone-200 p-3 dark:border-slate-800 md:grid-cols-[1fr_auto] md:items-center">
                    <div>
                      <div className="flex items-center gap-2 font-semibold"><ReceiptText size={17} /> {expense.title}</div>
                      <p className="text-sm text-stone-500 dark:text-stone-400">{expense.category} • paid by {expense.payer?.name} • {shortDate(expense.createdAt)}</p>
                    </div>
                    <strong>{currency(expense.amount)}</strong>
                  </div>
                )) : <EmptyState title="No expenses yet" description="Add a shared bill to calculate balances." />}
              </div>
            </Panel>
            <Panel title="AI spending insights">
              <div className="grid gap-3">
                <div className="rounded-md bg-mint/10 p-3 text-sm">
                  <Sparkles className="mb-2 text-mint" size={20} />
                  <strong>Trend: {insights?.trend || 0}%</strong>
                  <p className="mt-1 text-stone-600 dark:text-stone-300">{insights?.topCategory?._id || "No category"} leads spending.</p>
                </div>
                {(insights?.warnings || []).map((warning) => <p key={warning} className="rounded-md bg-coral/10 px-3 py-2 text-sm text-coral">{warning}</p>)}
                {(insights?.suggestions || []).map((suggestion) => <p key={suggestion} className="text-sm text-stone-600 dark:text-stone-300">{suggestion}</p>)}
                <ResponsiveContainer width="100%" height={170}>
                  <BarChart data={chartCategories}>
                    <XAxis dataKey="name" />
                    <Tooltip formatter={(value) => currency(value)} />
                    <Bar dataKey="value" fill="#ef6f61" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Panel>
          </section>
        </motion.div>
      )}
      {panel === "group" ? <GroupForm onClose={() => setPanel("")} onDone={refresh} /> : null}
      {panel === "member" && activeGroup ? <MemberForm groupId={activeGroup._id} onClose={() => setPanel("")} onDone={refresh} /> : null}
      {panel === "expense" && activeGroup ? <ExpenseForm group={activeGroup} onClose={() => setPanel("")} onDone={refresh} /> : null}
    </AppShell>
  );

  async function recordSettlement(item) {
    await api.post("/settlements/pay", { group: activeGroupId, from: item.from, to: item.to, amount: item.amount });
    await refresh();
  }
}

function Panel({ title, children }) {
  return (
    <section className="rounded-lg bg-white p-4 shadow-soft dark:bg-slate-900">
      <h3 className="mb-3 text-base font-bold">{title}</h3>
      {children}
    </section>
  );
}

function Modal({ title, children, onClose }) {
  return (
    <div className="fixed inset-0 z-40 grid place-items-center bg-black/40 p-4">
      <div className="w-full max-w-lg rounded-lg bg-white p-5 shadow-soft dark:bg-slate-900">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-lg font-bold">{title}</h3>
          <Button variant="ghost" onClick={onClose}>Close</Button>
        </div>
        {children}
      </div>
    </div>
  );
}

function GroupForm({ onClose, onDone }) {
  const [form, setForm] = useState({ name: "", description: "", type: "Other", budgetLimit: 0 });
  const submit = async (event) => {
    event.preventDefault();
    await api.post("/groups", form);
    await onDone();
    onClose();
  };
  return (
    <Modal title="Create group" onClose={onClose}>
      <form onSubmit={submit} className="grid gap-3">
        <input required placeholder="Group name" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
        <textarea placeholder="Description" value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} />
        <select value={form.type} onChange={(event) => setForm({ ...form, type: event.target.value })}>
          {["Trip", "Flat", "Outing", "Other"].map((type) => <option key={type}>{type}</option>)}
        </select>
        <input type="number" min="0" placeholder="Monthly budget" value={form.budgetLimit} onChange={(event) => setForm({ ...form, budgetLimit: event.target.value })} />
        <Button>Create</Button>
      </form>
    </Modal>
  );
}

function MemberForm({ groupId, onClose, onDone }) {
  const [email, setEmail] = useState("");
  const submit = async (event) => {
    event.preventDefault();
    await api.post(`/groups/${groupId}/members`, { email });
    await onDone();
    onClose();
  };
  return (
    <Modal title="Add member" onClose={onClose}>
      <form onSubmit={submit} className="grid gap-3">
        <input required type="email" placeholder="Member email" value={email} onChange={(event) => setEmail(event.target.value)} />
        <Button>Add member</Button>
      </form>
    </Modal>
  );
}

function ExpenseForm({ group, onClose, onDone }) {
  const members = group.members || [];
  const [form, setForm] = useState({ title: "", amount: "", category: "Food", payer: members[0]?.user?._id || "", splitType: "equal", billImage: null });
  const [splits, setSplits] = useState(() => members.map((member) => ({ user: member.user._id, percentage: Math.round(10000 / members.length) / 100 })));
  const submit = async (event) => {
    event.preventDefault();
    const body = new FormData();
    Object.entries(form).forEach(([key, value]) => value !== null && body.append(key, value));
    if (form.splitType === "custom") body.append("splits", JSON.stringify(splits));
    await api.post("/expenses", body, { headers: { "Content-Type": "multipart/form-data" } });
    await onDone();
    onClose();
  };
  return (
    <Modal title="Add expense" onClose={onClose}>
      <form onSubmit={submit} className="grid gap-3">
        <input required placeholder="Title" value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} />
        <input required type="number" min="0.01" step="0.01" placeholder="Amount" value={form.amount} onChange={(event) => setForm({ ...form, amount: event.target.value })} />
        <select value={form.category} onChange={(event) => setForm({ ...form, category: event.target.value })}>{categories.map((cat) => <option key={cat}>{cat}</option>)}</select>
        <select value={form.payer} onChange={(event) => setForm({ ...form, payer: event.target.value })}>
          {members.map((member) => <option key={member.user._id} value={member.user._id}>{member.user.name}</option>)}
        </select>
        <select value={form.splitType} onChange={(event) => setForm({ ...form, splitType: event.target.value })}>
          <option value="equal">Equal split</option>
          <option value="custom">Custom percentage</option>
        </select>
        {form.splitType === "custom" ? (
          <div className="grid gap-2">
            {members.map((member, index) => (
              <label key={member.user._id} className="grid gap-1 text-sm">
                {member.user.name}
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.01"
                  value={splits[index]?.percentage || 0}
                  onChange={(event) => setSplits(splits.map((split) => split.user === member.user._id ? { ...split, percentage: event.target.value } : split))}
                />
              </label>
            ))}
          </div>
        ) : null}
        <input type="file" accept="image/*" onChange={(event) => setForm({ ...form, billImage: event.target.files[0] })} />
        <Button>Add expense</Button>
      </form>
    </Modal>
  );
}
