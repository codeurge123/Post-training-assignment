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
