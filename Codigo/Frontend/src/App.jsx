import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import ProtectedRoute from "./auth/ProtectedRoute";

import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import VendedorPage from "./pages/VendedorPage";
import KpiPage from "./pages/KpiPage";
import MetasPage from "./pages/MetasPage";
import AlertasPage from "./pages/AlertasPage";
import AssistentePage from "./pages/AssistentePage";
import ImportPage from "./pages/ImportPage";
import RelatoriosPage from "./pages/RelatoriosPage";
import UserPage from "./pages/UserPage";
import LogsPage from "./pages/LogsPage";

/* Perfis do sistema (espelha o backend):
   administrador, gestor, analista, vendedor, executivo. */

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          {/* Dashboard — acessível a todos os perfis autenticados */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />

          {/* UC01 — Desempenho individual (exclusivo do vendedor) */}
          <Route
            path="/meu-desempenho"
            element={
              <ProtectedRoute roles={["vendedor"]}>
                <VendedorPage />
              </ProtectedRoute>
            }
          />

          {/* UC02 — Indicadores consolidados */}
          <Route
            path="/kpis"
            element={
              <ProtectedRoute roles={["gestor", "administrador", "executivo"]}>
                <KpiPage />
              </ProtectedRoute>
            }
          />

          {/* UC03/UC04 — Metas */}
          <Route
            path="/metas"
            element={
              <ProtectedRoute roles={["gestor", "administrador", "executivo"]}>
                <MetasPage />
              </ProtectedRoute>
            }
          />

          {/* UC05 — Alertas */}
          <Route
            path="/alertas"
            element={
              <ProtectedRoute roles={["gestor", "administrador", "executivo"]}>
                <AlertasPage />
              </ProtectedRoute>
            }
          />

          {/* UC12/UC13 — Assistente IA */}
          <Route
            path="/assistente"
            element={
              <ProtectedRoute roles={["gestor", "administrador", "executivo"]}>
                <AssistentePage />
              </ProtectedRoute>
            }
          />

          {/* UC08/UC09/UC10 — Importação em 3 etapas */}
          <Route
            path="/imports"
            element={
              <ProtectedRoute roles={["analista", "administrador"]}>
                <ImportPage />
              </ProtectedRoute>
            }
          />

          {/* UC06/UC07/UC15 — Relatórios e agendamentos */}
          <Route
            path="/relatorios"
            element={
              <ProtectedRoute roles={["gestor", "administrador", "executivo"]}>
                <RelatoriosPage />
              </ProtectedRoute>
            }
          />

          {/* UC14 — Gestão de usuários */}
          <Route
            path="/users"
            element={
              <ProtectedRoute roles={["administrador"]}>
                <UserPage />
              </ProtectedRoute>
            }
          />

          {/* US13 — Logs de auditoria */}
          <Route
            path="/logs"
            element={
              <ProtectedRoute roles={["administrador"]}>
                <LogsPage />
              </ProtectedRoute>
            }
          />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
