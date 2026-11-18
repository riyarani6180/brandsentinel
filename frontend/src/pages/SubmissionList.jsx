
import { useState, useEffect } from "react";
import {
  FileText,
  Search,
  RefreshCw,
  Plus,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Eye,
  Sparkles,
} from "lucide-react";

import api from "../services/api";
import "./SubmissionList.css";

export default function SubmissionList({
  onNewSubmission,
  onViewSubmission,
}) {
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [analyzingId, setAnalyzingId] = useState(null);
  const [actionMessage, setActionMessage] = useState("");

  const fetchSubmissions = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/review-submissions/");
      setSubmissions(
        Array.isArray(response.data) ? response.data : []
      );
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Unable to load submissions. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubmissions();
  }, []);

  const analyzeSubmission = async (submissionId) => {
    setAnalyzingId(submissionId);
    setActionMessage("");
    setError("");

    try {
      await api.post(
        `/review-submissions/${submissionId}/analyze`
      );

      setActionMessage(
        `Submission #${submissionId} analyzed successfully!`
      );

      await fetchSubmissions();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Analysis failed. Please try again."
      );
    } finally {
      setAnalyzingId(null);
    }
  };

  const filteredSubmissions = submissions.filter((submission) => {
    const search = searchTerm.toLowerCase();

    return (
      submission.title?.toLowerCase().includes(search) ||
      submission.channel?.toLowerCase().includes(search) ||
      submission.submitted_by?.toLowerCase().includes(search) ||
      submission.status?.toLowerCase().includes(search)
    );
  });

  const getStatusClass = (status) => {
    const value = status?.toLowerCase() || "";

    if (value.includes("approved")) return "status-approved";
    if (value.includes("reject")) return "status-rejected";
    if (value.includes("pending")) return "status-pending";
    if (value.includes("review")) return "status-review";

    return "status-default";
  };

  const formatDate = (date) => {
    if (!date) return "—";

    const parsedDate = new Date(date);

    if (Number.isNaN(parsedDate.getTime())) return "—";

    return parsedDate.toLocaleString();
  };

  return (
    <div className="submission-list-page">
      <div className="list-heading">
        <div>
          <span className="list-eyebrow">BRAND GOVERNANCE</span>
          <h1>Submissions</h1>
          <p>
            View and manage all content submitted for brand review.
          </p>
        </div>

        <button
          className="new-submission-button"
          onClick={onNewSubmission}
        >
          <Plus size={18} />
          New Submission
        </button>
      </div>

      <div className="list-stats">
        <div className="list-stat-card">
          <div className="list-stat-icon blue">
            <FileText size={21} />
          </div>
          <div>
            <span>Total submissions</span>
            <h2>{submissions.length}</h2>
          </div>
        </div>

        <div className="list-stat-card">
          <div className="list-stat-icon orange">
            <Clock size={21} />
          </div>
          <div>
            <span>Pending reviews</span>
            <h2>
              {submissions.filter((item) =>
                item.status?.toLowerCase().includes("pending")
              ).length}
            </h2>
          </div>
        </div>

        <div className="list-stat-card">
          <div className="list-stat-icon green">
            <CheckCircle2 size={21} />
          </div>
          <div>
            <span>Approved</span>
            <h2>
              {submissions.filter((item) =>
                item.status?.toLowerCase().includes("approved")
              ).length}
            </h2>
          </div>
        </div>

        <div className="list-stat-card">
          <div className="list-stat-icon red">
            <AlertTriangle size={21} />
          </div>
          <div>
            <span>Rejected</span>
            <h2>
              {submissions.filter((item) =>
                item.status?.toLowerCase().includes("reject")
              ).length}
            </h2>
          </div>
        </div>
      </div>

      <div className="submission-table-card">
        <div className="table-toolbar">
          <div>
            <h2>All submissions</h2>
            <p>Content review records from your workspace.</p>
          </div>

          <div className="table-actions">
            <div className="submission-search">
              <Search size={18} />
              <input
                type="text"
                placeholder="Search submissions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            <button
              className="refresh-button"
              onClick={fetchSubmissions}
              disabled={loading || analyzingId !== null}
              title="Refresh submissions"
            >
              <RefreshCw
                size={18}
                className={loading ? "spinning" : ""}
              />
            </button>
          </div>
        </div>

        {actionMessage && (
          <div className="submission-action-success">
            <CheckCircle2 size={18} />
            {actionMessage}
          </div>
        )}

        {error && (
          <div className="submission-list-error">
            {error}
            <button onClick={fetchSubmissions}>Try again</button>
          </div>
        )}

        {loading ? (
          <div className="list-loading">
            <RefreshCw size={25} className="spinning" />
            <p>Loading submissions...</p>
          </div>
        ) : filteredSubmissions.length === 0 ? (
          <div className="list-empty">
            <div className="list-empty-icon">
              <FileText size={28} />
            </div>

            <h3>
              {searchTerm
                ? "No matching submissions"
                : "No submissions found"}
            </h3>

            <p>
              {searchTerm
                ? "Try searching with a different keyword."
                : "Create your first submission to see it here."}
            </p>

            {!searchTerm && (
              <button
                className="new-submission-button"
                onClick={onNewSubmission}
              >
                <Plus size={17} />
                Create submission
              </button>
            )}
          </div>
        ) : (
          <div className="table-responsive">
            <table className="submission-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Submission</th>
                  <th>Channel</th>
                  <th>Submitted by</th>
                  <th>Status</th>
                  <th>Risk score</th>
                  <th>Created at</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {filteredSubmissions.map((submission) => (
                  <tr key={submission.id}>
                    <td>#{submission.id}</td>

                    <td className="submission-title-cell">
                      <FileText size={17} />
                      {submission.title}
                    </td>

                    <td>{submission.channel || "—"}</td>

                    <td>{submission.submitted_by || "—"}</td>

                    <td>
                      <span
                        className={`submission-status ${getStatusClass(
                          submission.status
                        )}`}
                      >
                        {submission.status || "Unknown"}
                      </span>
                    </td>

                    <td>{submission.risk_score ?? "—"}</td>

                    <td>{formatDate(submission.created_at)}</td>

                    <td>
                      <div className="submission-row-actions">
                        <button
                          className="analyze-submission-button"
                          title="Analyze submission"
                          onClick={() =>
                            analyzeSubmission(submission.id)
                          }
                          disabled={analyzingId !== null}
                        >
                          {analyzingId === submission.id ? (
                            <RefreshCw
                              size={16}
                              className="spinning"
                            />
                          ) : (
                            <Sparkles size={16} />
                          )}
                          {analyzingId === submission.id
                            ? "Analyzing"
                            : "Analyze"}
                        </button>

                        <button
                          className="view-submission-button"
                          title="View submission details"
                          onClick={() =>
                            onViewSubmission(submission.id)
                          }
                        >
                          <Eye size={17} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
