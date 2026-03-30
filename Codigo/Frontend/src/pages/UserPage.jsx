import React, { useEffect, useState } from "react";
import Layout from "../components/layout";
import api from "../api/client";

export default function UserPage() {
  const [users, setUsers] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadUsers() {
      try {
        const res = await api.get("/dashboard/users");
        setUsers(res.data);
      } catch (err) {
        setError("Não foi possível carregar os usuários.");
      }
    }

    loadUsers();
  }, []);

  return (
    <Layout>
      <h1>Usuários</h1>

      {error && <p className="error">{error}</p>}

      <div className="card">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Nome</th>
              <th>Email</th>
              <th>Perfil</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td>{user.id}</td>
                <td>{user.nome}</td>
                <td>{user.email}</td>
                <td>{user.role}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Layout>
  );
}