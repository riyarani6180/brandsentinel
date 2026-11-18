
import { useEffect, useState } from "react";
import {
  ArrowLeft,
  FileText,
  AlertTriangle,
  RefreshCw,
  CheckCircle2,
  XCircle,
  MessageSquare,
} from "lucide-react";

import api from "../services/api";

function SubmissionDetails({ submissionId, onBack }) {
  const [submission, setSubmission] = useState(null);
  const [findings, setFindings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const currentUser = JSON.parse(
    localStorage.getItem("brandsentinel_user") || "{}"
  );

  const role = currentUser.role;

  const canApprove =
    role === "AUTHORISED_REVIEWER" || role === "BRAND_ADMIN";

  const canReject =
    role === "AUTHORISED_REVIEWER" || role === "BRAND_ADMIN";

  const canRequestChanges =
    role === "AUTHORISED_REVIEWER" ||
    role === "BRAND_ADMIN" ||
    role === "BRAND_MANAGER";

  const fetchDetails = async () => {
    setLoading(true);
    setError("");

    try {
      const [submissionResponse, findingsResponse] =
        await Promise.all([
          api.get(`/review-submissions/${submissionId}`),
          api.get(`/review-findings/submission/${submissionId}`),
        ]);

      setSubmission(submissionResponse.data);

      setFindings(
        Array.isArray(findingsResponse.data)
          ? findingsResponse.data
          : []
      );
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to load submission details."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetails();
  }, [submissionId]);

  const performReviewAction = async (action, endpoint, confirmation) => {
    const confirmed = window.confirm(confirmation);

    if (!confirmed) return;

    setActionLoading(true);
    setError("");
    setSuccess("");

    try {
      const response = await api.post(
        `/review-submissions/${submissionId}/${endpoint}`
      );

      setSuccess(
        response.data?.message || `Submission ${action} successfully.`
      );

      await fetchDetails();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          `Unable to ${action.toLowerCase()} this submission.`
      );
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="page-content">
        <p>Loading submission details...</p>
      </div>
    );
  }

  if (error && !submission) {
    return (
      <div className="page-content">
        <button className="secondary-button" onClick={onBack}>
          <ArrowLeft size={16} /> Back
        </button>

        <div className="dashboard-error">{error}</div>

        <button className="secondary-button" onClick={fetchDetails}>
          <RefreshCw size={16} /> Try Again
        </button>
      </div>
    );
  }

  if (!submission) return null;

  const isFinalStatus = ["APPROVED", "REJECTED"].includes(
    submission.status
  );

  return (
    <div className="page-content">
      <section className="welcome-section">
        <div>
          <button className="secondary-button" onClick={onBack}>
            <ArrowLeft size={16} /> Back to Submissions
          </button>

          <h1>Submission Details</h1>
          <p>Inspect submission information and compliance findings.</p>
        </div>

        <button
          className="secondary-button"
          onClick={fetchDetails}
          disabled={actionLoading}
        >
          <RefreshCw size={16} /> Refresh
        </button>
      </section>

      {success && (
        <div className="success-message">
          <CheckCircle2 size={18} /> {success}
        </div>
      )}

      {error && (
        <div className="dashboard-error">{error}</div>
      )}

      <section className="panel submission-details-panel">
        <h2>
          <FileText size={20} /> Submission Information
        </h2>

        <div className="details-grid">
          <div>
            <span>Submission ID</span>
            <strong>#{submission.id}</strong>
          </div>

          <div>
            <span>Title</span>
            <strong>{submission.title || "—"}</strong>
          </div>

          <div>
            <span>Content Type</span>
            <strong>{submission.content_type || "—"}</strong>
          </div>

          <div>
            <span>Submitted By</span>
            <strong>{submission.submitted_by || "—"}</strong>
          </div>

          <div>
            <span>Status</span>
            <strong>{submission.status || "—"}</strong>
          </div>

          <div>
            <span>Risk Score</span>
            <strong>{submission.risk_score ?? "Not available"}</strong>
          </div>
        </div>

        <div className="submission-content">
          <h3>Submitted Content</h3>
          <p>{submission.content || "No content available."}</p>
        </div>
      </section>

      <section className="panel submission-details-panel">
        <h2>
          <AlertTriangle size={20} /> Compliance Findings
        </h2>

        {findings.length === 0 ? (
          <p>No findings are associated with this submission.</p>
        ) : (
          findings.map((finding) => (
            <div className="detail-finding" key={finding.id}>
              <div className="finding-heading">
                <strong>{finding.finding_type}</strong>
                <span>{finding.severity}</span>
              </div>

              <p>{finding.description}</p>

              {finding.suggested_fix && (
                <p>
                  <strong>Suggested Fix:</strong>{" "}
                  {finding.suggested_fix}
                </p>
              )}

              <small>
                Verification: {finding.verification_status}
              </small>
            </div>
          ))
        )}
      </section>

      {!isFinalStatus && (
        <section className="panel submission-details-panel">
          <h2>Reviewer Actions</h2>
          <p>Choose an action after reviewing the submission.</p>

          <div className="review-action-buttons">
            {canApprove && (
              <button
                className="primary-button"
                disabled={actionLoading}
                onClick={() =>
                  performReviewAction(
                    "Approve",
                    "approve",
                    "Are you sure you want to approve this submission?"
                  )
                }
              >
                <CheckCircle2 size={17} />
                {actionLoading ? "Processing..." : "Approve"}
              </button>
            )}

            {canReject && (
              <button
                className="danger-button"
                disabled={actionLoading}
                onClick={() =>
                  performReviewAction(
                    "Reject",
                    "reject",
                    "Are you sure you want to reject this submission?"
                  )
                }
              >
                <XCircle size={17} />
                Reject
              </button>
            )}

            {canRequestChanges && (
              <button
                className="secondary-button"
                disabled={actionLoading}
                onClick={() =>
                  performReviewAction(
                    "Request Changes",
                    "request-changes",
                    "Are you sure you want to request changes to this submission?"
                  )
                }
              >
                <MessageSquare size={17} />
                Request Changes
              </button>
            )}

            {!canApprove && !canReject && !canRequestChanges && (
              <p>You do not have permission to review this submission.</p>
            )}
          </div>
        </section>
      )}

      {isFinalStatus && (
        <section className="panel submission-details-panel">
          <h2>Review Completed</h2>
          <p>This submission has been marked as {submission.status}.</p>
        </section>
      )}
    </div>
  );
}

export default SubmissionDetails;
