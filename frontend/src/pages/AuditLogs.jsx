
import { useEffect, useMemo, useState } from "react";
import {
  ClipboardList,
  RefreshCw,
  Search,
  Clock,
  User,
  Activity,
  AlertCircle,
} from "lucide-react";

import api from "../services/api";

function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  const fetchLogs = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/audit-logs/");

      setLogs(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to load audit logs."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const filteredLogs = useMemo(() => {
    const term = search.toLowerCase();

    return logs.filter((log) =>
      [
        log.action,
        log.entity_type,
        log.entity_id,
        log.user_id,
        log.details,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(term)
    );
  }, [logs, search]);

  const formatDate = (date) => {
    if (!date) return "—";

    const parsedDate = new Date(date);

    if (Number.isNaN(parsedDate.getTime())) return date;

    return parsedDate.toLocaleString();
  };

  const formatDetails = (details) => {
    if (!details) return "No additional details";

    try {
      const parsed =
        typeof details === "string"
          ? JSON.parse(details)
          : details;

      return JSON.stringify(parsed, null, 2);
    } catch {
      return String(details);
    }
  };

  return (
    <div className="page-content">
      <section className="welcome-section">
        <div>
          <h1>Audit Logs</h1>
          <p>
            Track user activities and important actions
            performed across BrandSentinel.
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={fetchLogs}
          disabled={loading}
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon purple">
            <ClipboardList size={22} />
          </div>
          <div>
            <span>Total Activities</span>
            <h2>{logs.length}</h2>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon blue">
            <Activity size={22} />
          </div>
          <div>
            <span>Filtered Activities</span>
            <h2>{filteredLogs.length}</h2>
          </div>
        </div>
      </section>

      <section className="panel audit-panel">
        <div className="audit-toolbar">
          <div>
            <h2>
              <ClipboardList size={20} />
              Activity History
            </h2>
            <p>Latest recorded activities</p>
          </div>

          <div className="audit-search">
            <Search size={17} />
            <input
              type="text"
              placeholder="Search activities..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>

        {loading ? (
          <div className="audit-message">
            <RefreshCw size={20} />
            Loading audit logs...
          </div>
        ) : error ? (
          <div className="audit-error">
            <AlertCircle size={20} />
            <span>{error}</span>
            <button
              className="secondary-button"
              onClick={fetchLogs}
            >
              Try Again
            </button>
          </div>
        ) : filteredLogs.length === 0 ? (
          <div className="audit-message">
            No audit activities found.
          </div>
        ) : (
          <div className="audit-table-wrapper">
            <table className="audit-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Action</th>
                  <th>User ID</th>
                  <th>Entity</th>
                  <th>Details</th>
                  <th>Date & Time</th>
                </tr>
              </thead>

              <tbody>
                {filteredLogs.map((log) => (
                  <tr key={log.id}>
                    <td>#{log.id}</td>

                    <td>
                      <span className="audit-action">
                        {log.action || "—"}
                      </span>
                    </td>

                    <td>
                      <span className="audit-user">
                        <User size={14} />
                        {log.user_id ?? "—"}
                      </span>
                    </td>

                    <td>
                      <strong>{log.entity_type || "—"}</strong>
                      <small>
                        {log.entity_id
                          ? `ID: ${log.entity_id}`
                          : ""}
                      </small>
                    </td>

                    <td>
                      <pre className="audit-details">
                        {formatDetails(log.details)}
                      </pre>
                    </td>

                    <td>
                      <span className="audit-date">
                        <Clock size={14} />
                        {formatDate(log.created_at)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

export default AuditLogs;
