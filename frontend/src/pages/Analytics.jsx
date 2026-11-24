
import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Legend,
} from "recharts";
import {
  ShieldCheck,
  FileText,
  AlertTriangle,
  CheckCircle2,
  RefreshCw,
  Search,
  Activity,
} from "lucide-react";

import api from "../services/api";
import "./Analytics.css";

const COLORS = ["#16a34a", "#eab308", "#f97316", "#dc2626"];

function StatCard({ title, value, note, icon: Icon }) {
  return (
    <div className="analytics-stat-card">
      <div className="analytics-stat-icon">
        <Icon size={21} />
      </div>
      <h2>{value}</h2>
      <strong>{title}</strong>
      <p>{note}</p>
    </div>
  );
}

export default function Analytics() {
  const [overview, setOverview] = useState(null);
  const [trends, setTrends] = useState(null);
  const [audit, setAudit] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [submissionId, setSubmissionId] = useState("");
  const [report, setReport] = useState(null);
  const [reportError, setReportError] = useState("");

  const fetchAnalytics = async () => {
    setLoading(true);
    setError("");

    try {
      const results = await Promise.all([
        api.get("/compliance/overview"),
        api.get("/compliance/trends"),
        api.get("/compliance/audit-summary"),
      ]);

      setOverview(results[0].data);
      setTrends(results[1].data);
      setAudit(results[2].data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Unable to load analytics. Please check your access permissions and backend."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchReport = async () => {
    if (!submissionId.trim()) {
      setReportError("Enter a submission ID.");
      return;
    }

    setReport(null);
    setReportError("");

    try {
      const response = await api.get(
        `/compliance/reports/${submissionId.trim()}`
      );
      setReport(response.data);
    } catch (err) {
      setReportError(
        err.response?.data?.detail || "Unable to load this report."
      );
    }
  };

  if (loading) {
    return (
      <div className="analytics-page">
        <p className="analytics-message">Loading analytics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-page">
        <div className="analytics-error">{error}</div>
        <button className="analytics-refresh" onClick={fetchAnalytics}>
          <RefreshCw size={16} /> Retry
        </button>
      </div>
    );
  }

  if (!overview || !trends || !audit) {
    return (
      <div className="analytics-page">
        <p className="analytics-message">No analytics data available.</p>
      </div>
    );
  }

  const statusData = Object.entries(
    overview.submissions?.by_status || {}
  ).map(([name, value]) => ({ name, value }));

  const riskData = Object.entries(
    overview.risk_distribution || {}
  ).map(([name, value]) => ({ name, value }));

  const severityData = Object.entries(
    overview.findings?.by_severity || {}
  ).map(([name, value]) => ({ name, value }));

  const verificationData = Object.entries(
    overview.findings?.by_verification_status || {}
  ).map(([name, value]) => ({ name, value }));

  return (
    <div className="analytics-page">
      <section className="analytics-heading">
        <div>
          <span className="analytics-eyebrow">
            <Activity size={15} /> BRAND PERFORMANCE
          </span>
          <h1>Analytics & Reports</h1>
          <p>
            Monitor compliance, identify risks and understand review activity.
          </p>
        </div>

        <button className="analytics-refresh" onClick={fetchAnalytics}>
          <RefreshCw size={16} /> Refresh
        </button>
      </section>

      <section className="analytics-stats-grid">
        <StatCard
          title="Total submissions"
          value={overview.submissions?.total ?? 0}
          note="Recorded submissions"
          icon={FileText}
        />
        <StatCard
          title="Approval rate"
          value={`${overview.submissions?.approval_rate ?? 0}%`}
          note="Approved submissions"
          icon={CheckCircle2}
        />
        <StatCard
          title="Total findings"
          value={overview.findings?.total ?? 0}
          note="Detected compliance findings"
          icon={AlertTriangle}
        />
        <StatCard
          title="Audit events"
          value={audit.total_events ?? 0}
          note="Recorded system activities"
          icon={ShieldCheck}
        />
      </section>

      <section className="analytics-chart-grid">
        <div className="analytics-panel">
          <h3>Submission trends</h3>
          <p>Daily submission activity</p>
          {trends.daily_submissions?.length ? (
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={trends.daily_submissions}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="count"
                  stroke="#4f46e5"
                  strokeWidth={3}
                  name="Submissions"
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="analytics-empty">No trend data available yet.</p>
          )}
        </div>

        <div className="analytics-panel">
          <h3>Risk distribution</h3>
          <p>Submissions grouped by risk level</p>
          {riskData.some((item) => item.value > 0) ? (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={riskData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={90}
                  label
                >
                  {riskData.map((item, index) => (
                    <Cell
                      key={item.name}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="analytics-empty">No risk data available yet.</p>
          )}
        </div>

        <div className="analytics-panel">
          <h3>Submission status</h3>
          <p>Current review status breakdown</p>
          {statusData.length ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={statusData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="value" fill="#6366f1" name="Submissions" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="analytics-empty">No status data available yet.</p>
          )}
        </div>

        <div className="analytics-panel">
          <h3>Finding severity</h3>
          <p>Detected issues by severity</p>
          {severityData.length ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={severityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="value" fill="#f97316" name="Findings" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="analytics-empty">No findings recorded yet.</p>
          )}
        </div>
      </section>

      <section className="analytics-panel analytics-detail-panel">
        <h3>Finding verification</h3>
        <p>Verification status of detected findings</p>
        {verificationData.length ? (
          <div className="analytics-breakdown">
            {verificationData.map((item) => (
              <div className="analytics-breakdown-row" key={item.name}>
                <span>{item.name.replaceAll("_", " ")}</span>
                <strong>{item.value}</strong>
              </div>
            ))}
          </div>
        ) : (
          <p className="analytics-empty">No verification data available.</p>
        )}
      </section>

      <section className="analytics-panel analytics-detail-panel">
        <h3>Audit activity</h3>
        <p>Recent recorded system activities</p>
        {audit.recent_activity?.length ? (
          <div className="analytics-table-wrap">
            <table className="analytics-table">
              <thead>
                <tr>
                  <th>Action</th>
                  <th>Entity</th>
                  <th>Entity ID</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {audit.recent_activity.map((item) => (
                  <tr key={item.id}>
                    <td>{item.action || "Unknown"}</td>
                    <td>{item.entity_type || "Unknown"}</td>
                    <td>{item.entity_id ?? "—"}</td>
                    <td>
                      {item.created_at
                        ? new Date(item.created_at).toLocaleString()
                        : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="analytics-empty">No audit activity available yet.</p>
        )}
      </section>

      <section className="analytics-panel analytics-report-panel">
        <h3>Explainable submission report</h3>
        <p>Enter a submission ID to view its recorded findings and explanations.</p>

        <div className="analytics-report-search">
          <input
            type="number"
            min="1"
            placeholder="Enter submission ID"
            value={submissionId}
            onChange={(event) => setSubmissionId(event.target.value)}
          />
          <button onClick={fetchReport}>
            <Search size={16} /> Generate report
          </button>
        </div>

        {reportError && (
          <div className="analytics-error">{reportError}</div>
        )}

        {report && (
          <div className="analytics-report-result">
            <h4>{report.submission?.title}</h4>
            <p>
              Submission #{report.submission?.id} · Status:{" "}
              {report.submission?.status}
            </p>

            <div className="analytics-report-summary">
              <span>Total findings: {report.summary?.total_findings ?? 0}</span>
              <span>High: {report.summary?.high_findings ?? 0}</span>
              <span>Critical: {report.summary?.critical_findings ?? 0}</span>
            </div>

            {report.findings?.map((finding) => (
              <div className="analytics-finding" key={finding.id}>
                <strong>
                  {finding.finding_type} · {finding.severity}
                </strong>
                <p>{finding.description}</p>
                <p><b>Evidence:</b> {finding.evidence || "Not recorded"}</p>
                <p><b>Suggested fix:</b> {finding.suggested_fix || "Not provided"}</p>
                <small>
                  Verification: {finding.verification_status || "Unknown"} ·
                  Confidence: {finding.confidence ?? "N/A"}
                </small>
              </div>
            ))}

            <p className="analytics-report-note">{report.report_note}</p>
          </div>
        )}
      </section>
    </div>
  );
}
