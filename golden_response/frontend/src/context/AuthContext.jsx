import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import api from "../services/api";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => JSON.parse(localStorage.getItem("expense-user") || "null"));
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", localStorage.getItem("theme") === "dark");
  }, []);

  const setSession = ({ token, user: sessionUser }) => {
    localStorage.setItem("expense-token", token);
    localStorage.setItem("expense-user", JSON.stringify(sessionUser));
    setUser(sessionUser);
  };

  const login = async (payload) => {
    setLoading(true);
    try {
      const { data } = await api.post("/auth/login", payload);
      setSession(data);
    } finally {
      setLoading(false);
    }
  };

  const register = async (payload) => {
    setLoading(true);
    try {
      const { data } = await api.post("/auth/register", payload);
      setSession(data);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("expense-token");
    localStorage.removeItem("expense-user");
    setUser(null);
  };

  const toggleTheme = () => {
    const next = document.documentElement.classList.contains("dark") ? "light" : "dark";
    localStorage.setItem("theme", next);
    document.documentElement.classList.toggle("dark", next === "dark");
  };

  const value = useMemo(() => ({ user, loading, login, register, logout, toggleTheme }), [user, loading]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => useContext(AuthContext);
