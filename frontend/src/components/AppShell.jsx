import { Bell, LogOut, Moon, Plus, SunMedium, Users } from "lucide-react";
import Button from "./Button";
import { useAuth } from "../context/AuthContext";

export default function AppShell({ children, groups, activeGroupId, onSelectGroup, onNewGroup, notifications }) {
  const { user, logout, toggleTheme } = useAuth();
  return (
    <div className="min-h-screen bg-stone-100 dark:bg-slate-950">
      <header className="sticky top-0 z-20 border-b border-stone-200 bg-white/90 backdrop-blur dark:border-slate-800 dark:bg-slate-950/90">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-3">
          <div>
            <h1 className="text-lg font-bold tracking-normal">Expense Splitter</h1>
            <p className="text-xs text-stone-500 dark:text-stone-400">Signed in as {user?.name}</p>
          </div>
          <div className="flex items-center gap-2">
            <button title="Notifications" className="relative rounded-md p-2 hover:bg-stone-100 dark:hover:bg-slate-800">
              <Bell size={19} />
              {notifications?.some((item) => !item.read) ? <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-coral" /> : null}
            </button>
            <button title="Toggle theme" className="rounded-md p-2 hover:bg-stone-100 dark:hidden" onClick={toggleTheme}>
              <Moon size={19} />
            </button>
            <button title="Toggle theme" className="hidden rounded-md p-2 hover:bg-slate-800 dark:block" onClick={toggleTheme}>
              <SunMedium size={19} />
            </button>
            <button title="Log out" className="rounded-md p-2 hover:bg-stone-100 dark:hover:bg-slate-800" onClick={logout}>
              <LogOut size={19} />
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl gap-4 px-4 py-4 lg:grid-cols-[260px_1fr]">
        <aside className="h-fit rounded-lg bg-white p-3 shadow-soft dark:bg-slate-900">
          <div className="mb-3 flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <Users size={18} /> Groups
            </div>
            <Button variant="ghost" className="min-h-8 px-2" onClick={onNewGroup} title="Create group">
              <Plus size={17} />
            </Button>
          </div>
          <div className="grid gap-1">
            {groups.map((group) => (
              <button
                key={group._id}
                onClick={() => onSelectGroup(group._id)}
                className={`rounded-md px-3 py-2 text-left text-sm ${
                  activeGroupId === group._id ? "bg-ink text-white dark:bg-mint dark:text-slate-950" : "hover:bg-stone-100 dark:hover:bg-slate-800"
                }`}
              >
                <span className="block font-semibold">{group.name}</span>
                <span className="text-xs opacity-75">{group.members?.length || 0} members</span>
              </button>
            ))}
          </div>
        </aside>
        <main>{children}</main>
      </div>
    </div>
  );
}
