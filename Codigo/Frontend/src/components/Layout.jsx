import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function Layout({ children }) {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h2>DashVendas</h2>

       <nav className="sidebar-nav">
          <Link to="/">Dashboard</Link>
          {(user?.role === "analista" || user?.role === "administrador") && (
            <Link to="/imports">Importar Excel</Link>
          )}
          {user?.role === "administrador" && <Link to="/users">Usuários</Link>}
          <Link to="/kpis">KPIs</Link>
        </nav>

        <div className="sidebar-footer">
          <small>{user?.nome}</small>
          <small>{user?.role}</small>
          <button onClick={logout}>Sair</button>
        </div>
      </aside>

      <main className="content">{children}</main>
    </div>
  );
}