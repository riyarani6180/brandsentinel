
import { useState } from "react";
import { FileText, Send, CheckCircle2, AlertCircle } from "lucide-react";
import api from "../services/api";
import "./Submissions.css";

function Submissions() {
  const savedUser = JSON.parse(
    localStorage.getItem("brandsentinel_user") || "{}"
  );

  const [formData, setFormData] = useState({
    title: "",
    content: "",
    channel: "",
    submitted_by: savedUser.full_name || savedUser.email || "",
  });

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");
    setError("");

    try {
      await api.post("/review-submissions/", formData);

      setMessage("Your submission was created successfully!");

      setFormData({
        title: "",
        content: "",
        channel: "",
        submitted_by: savedUser.full_name || savedUser.email || "",
      });
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Unable to create submission. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="submission-page">
      <div className="submission-heading">
        <div>
          <span className="submission-eyebrow">
            BRAND GOVERNANCE
          </span>
          <h1>New Submission</h1>
          <p>
            Submit your content for brand compliance review.
          </p>
        </div>

        <div className="submission-icon">
          <FileText size={28} />
        </div>
      </div>

      <div className="submission-card">
        <div className="submission-card-heading">
          <h2>Content details</h2>
          <p>Provide the information about your content below.</p>
        </div>

        {message && (
          <div className="submission-success">
            <CheckCircle2 size={20} />
            {message}
          </div>
        )}

        {error && (
          <div className="submission-error">
            <AlertCircle size={20} />
            {String(error)}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="submission-field">
            <label htmlFor="title">Submission title</label>
            <input
              id="title"
              name="title"
              type="text"
              placeholder="Enter your content title"
              value={formData.title}
              onChange={handleChange}
              required
            />
          </div>

          <div className="submission-field">
            <label htmlFor="content">Content to review</label>
            <textarea
              id="content"
              name="content"
              placeholder="Paste the content you want BrandSentinel to review..."
              value={formData.content}
              onChange={handleChange}
              rows={8}
              required
            />
          </div>

          <div className="submission-field">
            <label htmlFor="channel">Publishing channel</label>
            <select
              id="channel"
              name="channel"
              value={formData.channel}
              onChange={handleChange}
              required
            >
              <option value="">Select publishing channel</option>
              <option value="Website">Website</option>
              <option value="Social Media">Social Media</option>
              <option value="Blog">Blog</option>
              <option value="Email">Email</option>
              <option value="Advertisement">Advertisement</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div className="submission-field">
            <label htmlFor="submitted_by">Submitted by</label>
            <input
              id="submitted_by"
              name="submitted_by"
              type="text"
              value={formData.submitted_by}
              onChange={handleChange}
              placeholder="Your name"
              required
            />
          </div>

          <button
            type="submit"
            className="submission-submit"
            disabled={loading}
          >
            <Send size={18} />
            {loading ? "Submitting..." : "Create Submission"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Submissions;
