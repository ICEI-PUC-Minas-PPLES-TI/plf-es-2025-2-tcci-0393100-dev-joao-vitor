import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import api from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem("dashvendas_user");
    return raw ? JSON.parse(raw) : null;
  });

  const [token, setToken] = useState(() => localStorage.getItem("dashvendas_token"));

  useEffect(() => {
    if (token) {
      localStorage.setItem("dashvendas_token", token);
    } else {
      localStorage.removeItem("dashvendas_token");
    }
  }, [token]);

  useEffect(() => {
    if (user) {
      localStorage.setItem("dashvendas_user", JSON.stringify(user));
    } else {
      localStorage.removeItem("dashvendas_user");
    }
  }, [user]);

  const login = async (email, password) => {
    const { data } = await api.post("/auth/login", { email, password });
    setToken(data.access_token);
    setUser(data.user);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
  };

  const value = useMemo(
    () => ({
      user,
      token,
      login,
      logout,
      isAuthenticated: !!token,
    }),
    [user, token]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}