export default function EmptyState({ title, description, action }) {
  return (
    <div className="rounded-lg border border-dashed border-stone-300 bg-white/70 p-8 text-center dark:border-slate-700 dark:bg-slate-900/70">
      <h3 className="text-base font-semibold">{title}</h3>
      <p className="mx-auto mt-2 max-w-md text-sm text-stone-600 dark:text-stone-300">{description}</p>
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}
