import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import Icon, { BrandMark } from "./Icon";

/* Itens de navegação com os perfis autorizados (espelha o backend). */
const NAV = [
  { to: "/", label: "Dashboard", icon: "dashboard", section: "Visão Geral", roles: null },
  { to: "/meu-desempenho", label: "Meu Desempenho", icon: "user", section: "Visão Geral", roles: ["vendedor"] },

  { to: "/kpis", label: "Indicadores", icon: "kpi", section: "Análise", roles: ["gestor", "administrador", "executivo"] },
  { to: "/metas", label: "Metas", icon: "target", section: "Análise", roles: ["gestor", "administrador", "executivo"] },
  { to: "/alertas", label: "Alertas", icon: "bell", section: "Análise", roles: ["gestor", "administrador", "executivo"] },
  { to: "/assistente", label: "Assistente IA", icon: "robot", section: "Análise", roles: ["gestor", "administrador", "executivo"] },

  { to: "/imports", label: "Importação", icon: "upload", section: "Operações", roles: ["analista", "administrador"] },
  { to: "/relatorios", label: "Relatórios", icon: "report", section: "Operações", roles: ["gestor", "administrador", "executivo"] },

  { to: "/users", label: "Usuários", icon: "users", section: "Administração", roles: ["administrador"] },
  { to: "/logs", label: "Auditoria", icon: "logs", section: "Administração", roles: ["administrador"] },
];

const ROLE_LABEL = {
  administrador: "Administrador",
  gestor: "Gestor comercial",
  analista: "Analista de dados",
  vendedor: "Vendedor",
  executivo: "Executivo",
};

export default function Layout({ title, crumb, intro, actions, children }) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [open, setOpen] = useState(false);

  const allowed = NAV.filter((item) => !item.roles || item.roles.includes(user?.role));

  const sections = [];
  allowed.forEach((item) => {
    let group = sections.find((s) => s.name === item.section);
    if (!group) {
      group = { name: item.section, items: [] };
      sections.push(group);
    }
    group.items.push(item);
  });

  const initials = (user?.nome || "U")
    .split(" ")
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <div className="shell">
      <aside className={`sidebar ${open ? "open" : ""}`}>
        <div className="brand">
          <BrandMark size={34} />
          <span className="name">Dash<b>Vendas</b></span>
        </div>

        <nav>
          {sections.map((section) => (
            <div key={section.name}>
              <div className="nav-section">{section.name}</div>
              {section.items.map((item) => {
                const active =
                  item.to === "/"
                    ? location.pathname === "/"
                    : location.pathname.startsWith(item.to);
                return (
                  <Link
                    key={item.to}
                    to={item.to}
                    className={`nav-link ${active ? "active" : ""}`}
                    onClick={() => setOpen(false)}
                  >
                    <Icon name={item.icon} />
                    {item.label}
                  </Link>
                );
              })}
            </div>
          ))}
        </nav>

        <div className="sidebar-foot">
          <div className="user-card">
            <div className="avatar">{initials}</div>
            <div className="meta">
              <div className="n">{user?.nome}</div>
              <div className="r">{ROLE_LABEL[user?.role] || user?.role}</div>
            </div>
          </div>
          <button className="logout-btn" onClick={logout}>Sair da conta</button>
        </div>
      </aside>

      <div className="main">
        <header className="topbar">
          <div>
            {crumb && <div className="crumb">{crumb}</div>}
            <h1>{title}</h1>
          </div>
          <div className="right">
            {actions}
            <button
              className="btn-ghost btn btn-sm"
              style={{ display: "none" }}
              onClick={() => setOpen((v) => !v)}
            >
              Menu
            </button>
          </div>
        </header>

        <main className="content fade-in">
          {intro && <p className="page-intro">{intro}</p>}
          {children}
        </main>
      </div>
    </div>
  );
}
