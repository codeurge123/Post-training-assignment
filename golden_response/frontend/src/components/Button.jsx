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
