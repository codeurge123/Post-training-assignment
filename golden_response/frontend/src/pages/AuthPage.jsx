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
