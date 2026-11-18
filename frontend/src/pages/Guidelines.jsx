
import { useEffect, useMemo, useState } from "react";
import {
  BookOpen,
  Plus,
  Search,
  RefreshCw,
  Eye,
  Pencil,
  Trash2,
  X,
  FileText,
  Calendar,
  ShieldCheck,
  AlertCircle,
} from "lucide-react";

import api from "../services/api";

function Guidelines() {
  const [guidelines, setGuidelines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [search, setSearch] = useState("");

  const [showForm, setShowForm] = useState(false);
  const [selectedGuideline, setSelectedGuideline] = useState(null);
  const [editingGuideline, setEditingGuideline] = useState(null);
  const [saving, setSaving] = useState(false);

  const [formData, setFormData] = useState({
    name: "",
    description: "",
    source_filename: "",
    content: "",
  });

  let currentUser = {};

  try {
    currentUser = JSON.parse(
      localStorage.getItem("brandsentinel_user") || "{}"
    );
  } catch {
    currentUser = {};
  }

  const isAdmin = currentUser.role === "BRAND_ADMIN";

  // Fetch active guidelines from the backend.
  const fetchGuidelines = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/guidelines/");
      setGuidelines(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      console.error("Fetch guidelines error:", err);

      setError(
        err.response?.data?.detail ||
          "Unable to load guidelines. Please check your connection."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGuidelines();
  }, []);

  // Search and filter guidelines.
  const filteredGuidelines = useMemo(() => {
    const term = search.toLowerCase().trim();

    if (!term) return guidelines;

    return guidelines.filter((item) =>
      [
        item.name,
        item.description,
        item.source_filename,
        item.content,
      ]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(term))
    );
  }, [guidelines, search]);

  // Open create guideline form.
  const openCreateForm = () => {
    setEditingGuideline(null);

    setFormData({
      name: "",
      description: "",
      source_filename: "",
      content: "",
    });

    setError("");
    setSuccess("");
    setShowForm(true);
  };

  // Open edit guideline form.
  const openEditForm = (guideline) => {
    setEditingGuideline(guideline);

    setFormData({
      name: guideline.name || "",
      description: guideline.description || "",
      source_filename: guideline.source_filename || "",
      content: guideline.content || "",
    });

    setError("");
    setSuccess("");
    setShowForm(true);
    setSelectedGuideline(null);
  };

  // Close form and reset fields.
  const closeForm = () => {
    setShowForm(false);
    setEditingGuideline(null);

    setFormData({
      name: "",
      description: "",
      source_filename: "",
      content: "",
    });
  };

  // Handle input changes.
  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  // Create or update guideline.
  const handleSubmit = async (event) => {
    event.preventDefault();

    console.log("Create Guideline button clicked");
    console.log("Form data:", formData);

    setSaving(true);
    setError("");
    setSuccess("");

    try {
      let response;

      if (editingGuideline) {
        response = await api.put(
          `/guidelines/${editingGuideline.id}`,
          {
            name: formData.name.trim(),
            description: formData.description.trim() || null,
            content: formData.content.trim(),
          }
        );

        setSuccess("Guideline updated successfully!");
      } else {
        response = await api.post("/guidelines/", {
          name: formData.name.trim(),
          description: formData.description.trim() || null,
          source_filename: formData.source_filename.trim() || null,
          content: formData.content.trim(),
        });

        setSuccess("Guideline created successfully!");
      }

      console.log("Save response:", response.data);

      // Close form.
      setShowForm(false);
      setEditingGuideline(null);

      setFormData({
        name: "",
        description: "",
        source_filename: "",
        content: "",
      });

      // Refresh guidelines list separately.
      try {
        const listResponse = await api.get("/guidelines/");

        setGuidelines(
          Array.isArray(listResponse.data)
            ? listResponse.data
            : []
        );
      } catch (refreshError) {
        console.error("Guideline refresh error:", refreshError);

        setError(
          "Guideline was saved, but the list could not be refreshed. Click Refresh."
        );
      }
    } catch (err) {
      console.error("Guideline save error:", err);

      setSuccess("");

      setError(
        err.response?.data?.detail ||
          err.message ||
          "Unable to save guideline. Please try again."
      );
    } finally {
      setSaving(false);
    }
  };

  // Deactivate guideline.
  const handleDeactivate = async (guideline) => {
    const confirmed = window.confirm(
      `Are you sure you want to deactivate "${guideline.name}"?`
    );

    if (!confirmed) return;

    setError("");
    setSuccess("");

    try {
      await api.delete(`/guidelines/${guideline.id}`);

      setSelectedGuideline(null);

      const response = await api.get("/guidelines/");

      setGuidelines(
        Array.isArray(response.data) ? response.data : []
      );

      setSuccess("Guideline deactivated successfully!");
    } catch (err) {
      console.error("Deactivate guideline error:", err);

      setError(
        err.response?.data?.detail ||
          "Unable to deactivate guideline."
      );
    }
  };

  // Format date.
  const formatDate = (date) => {
    if (!date) return "—";

    const parsedDate = new Date(date);

    if (Number.isNaN(parsedDate.getTime())) return "—";

    return parsedDate.toLocaleDateString();
  };

  return (
    <div className="page-content guidelines-page">

      {/* Page Header */}
      <section className="welcome-section guidelines-welcome">
        <div>
          <div className="eyebrow">
            <ShieldCheck size={14} />
            BRAND GOVERNANCE
          </div>

          <h1>Brand Guidelines</h1>

          <p>
            Maintain and manage the rules that keep every publication
            consistent with your brand.
          </p>
        </div>

        {isAdmin && (
          <button
            className="primary-button"
            onClick={openCreateForm}
          >
            <Plus size={18} />
            Add Guideline
          </button>
        )}
      </section>

      {/* Summary Cards */}
      <section className="guidelines-summary">
        <div className="guideline-summary-card">
          <div className="guideline-summary-icon">
            <BookOpen size={21} />
          </div>

          <div>
            <span>Total active guidelines</span>
            <strong>{guidelines.length}</strong>
          </div>
        </div>

        <div className="guideline-summary-card">
          <div className="guideline-summary-icon">
            <FileText size={21} />
          </div>

          <div>
            <span>Latest version</span>

            <strong>
              {guidelines.length
                ? `v${Math.max(
                    ...guidelines.map((item) => item.version || 1)
                  )}`
                : "—"}
            </strong>
          </div>
        </div>
      </section>

      {/* Success Message */}
      {success && (
        <div className="guidelines-alert guidelines-success">
          <ShieldCheck size={18} />
          {success}
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="guidelines-alert guidelines-error">
          <AlertCircle size={18} />
          {error}
        </div>
      )}

      {/* Guidelines List */}
      <section className="panel guidelines-panel">
        <div className="guidelines-toolbar">
          <div>
            <h3>All Guidelines</h3>
            <p>Browse your organization's active brand rules.</p>
          </div>

          <div className="guidelines-toolbar-actions">
            <div className="guidelines-search">
              <Search size={17} />

              <input
                type="text"
                placeholder="Search guidelines..."
                value={search}
                onChange={(event) => setSearch(event.target.value)}
              />
            </div>

            <button
              className="guidelines-refresh"
              onClick={() => {
                setSuccess("");
                fetchGuidelines();
              }}
              disabled={loading}
              title="Refresh guidelines"
            >
              <RefreshCw size={17} />
            </button>
          </div>
        </div>

        {loading ? (
          <div className="guidelines-empty">
            <RefreshCw
              size={25}
              className="guidelines-loading-icon"
            />
            <p>Loading guidelines...</p>
          </div>
        ) : filteredGuidelines.length === 0 ? (
          <div className="guidelines-empty">
            <div className="empty-icon">
              <BookOpen size={25} />
            </div>

            <h3>
              {search
                ? "No matching guidelines"
                : "No guidelines found"}
            </h3>

            <p>
              {search
                ? "Try another search term."
                : "Your active brand guidelines will appear here."}
            </p>

            {isAdmin && !search && (
              <button
                className="secondary-button"
                onClick={openCreateForm}
              >
                <Plus size={16} />
                Create first guideline
              </button>
            )}
          </div>
        ) : (
          <div className="guidelines-grid">
            {filteredGuidelines.map((guideline) => (
              <article
                className="guideline-card"
                key={guideline.id}
              >
                <div className="guideline-card-top">
                  <div className="guideline-card-icon">
                    <BookOpen size={21} />
                  </div>

                  <span className="guideline-version">
                    Version {guideline.version}
                  </span>
                </div>

                <h3>{guideline.name}</h3>

                <p className="guideline-description">
                  {guideline.description ||
                    "No description provided."}
                </p>

                <div className="guideline-meta">
                  <span>
                    <Calendar size={14} />
                    {formatDate(
                      guideline.updated_at || guideline.created_at
                    )}
                  </span>

                  {guideline.source_filename && (
                    <span>
                      <FileText size={14} />
                      {guideline.source_filename}
                    </span>
                  )}
                </div>

                <div className="guideline-card-actions">
                  <button
                    className="guideline-view-button"
                    onClick={() => setSelectedGuideline(guideline)}
                  >
                    <Eye size={16} />
                    View
                  </button>

                  {isAdmin && (
                    <>
                      <button
                        className="guideline-edit-button"
                        onClick={() => openEditForm(guideline)}
                        title="Edit guideline"
                      >
                        <Pencil size={16} />
                      </button>

                      <button
                        className="guideline-delete-button"
                        onClick={() => handleDeactivate(guideline)}
                        title="Deactivate guideline"
                      >
                        <Trash2 size={16} />
                      </button>
                    </>
                  )}
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

      {/* Create / Edit Guideline Modal */}
      {showForm && (
        <div className="guidelines-modal-overlay">
          <div className="guidelines-modal">
            <div className="guidelines-modal-header">
              <div>
                <h2>
                  {editingGuideline
                    ? "Edit Guideline"
                    : "Add New Guideline"}
                </h2>

                <p>
                  {editingGuideline
                    ? "Update the brand guideline information."
                    : "Add a new rule to your brand knowledge base."}
                </p>
              </div>

              <button
                className="guidelines-modal-close"
                onClick={closeForm}
                type="button"
              >
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              <label htmlFor="guideline-name">
                Guideline name *
              </label>

              <input
                id="guideline-name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="e.g. Brand Voice and Tone"
                minLength={2}
                maxLength={200}
                required
              />

              <label htmlFor="guideline-description">
                Description
              </label>

              <input
                id="guideline-description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="Briefly describe this guideline"
              />

              {!editingGuideline && (
                <>
                  <label htmlFor="guideline-source">
                    Source filename
                  </label>

                  <input
                    id="guideline-source"
                    name="source_filename"
                    value={formData.source_filename}
                    onChange={handleChange}
                    placeholder="e.g. brand_manual.pdf"
                  />
                </>
              )}

              <label htmlFor="guideline-content">
                Guideline content *
              </label>

              <textarea
                id="guideline-content"
                name="content"
                value={formData.content}
                onChange={handleChange}
                placeholder="Enter the complete brand rules and instructions..."
                rows={7}
                required
              />

              <div className="guidelines-form-actions">
                <button
                  type="button"
                  className="guidelines-cancel-button"
                  onClick={closeForm}
                  disabled={saving}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="primary-button"
                  disabled={saving}
                >
                  {saving
                    ? "Saving..."
                    : editingGuideline
                    ? "Save Changes"
                    : "Create Guideline"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* View Guideline Modal */}
      {selectedGuideline && (
        <div className="guidelines-modal-overlay">
          <div className="guidelines-modal guideline-detail-modal">
            <div className="guidelines-modal-header">
              <div>
                <span className="guideline-version">
                  Version {selectedGuideline.version}
                </span>

                <h2>{selectedGuideline.name}</h2>

                <p>
                  {selectedGuideline.description ||
                    "No description provided."}
                </p>
              </div>

              <button
                className="guidelines-modal-close"
                onClick={() => setSelectedGuideline(null)}
              >
                <X size={20} />
              </button>
            </div>

            <div className="guideline-detail-meta">
              <span>
                <Calendar size={15} />
                Created: {formatDate(selectedGuideline.created_at)}
              </span>

              <span>
                <Calendar size={15} />
                Updated: {formatDate(selectedGuideline.updated_at)}
              </span>

              {selectedGuideline.source_filename && (
                <span>
                  <FileText size={15} />
                  Source: {selectedGuideline.source_filename}
                </span>
              )}
            </div>

            <div className="guideline-content-box">
              <h4>Guideline Content</h4>
              <p>{selectedGuideline.content}</p>
            </div>

            <div className="guidelines-form-actions">
              <button
                className="guidelines-cancel-button"
                onClick={() => setSelectedGuideline(null)}
              >
                Close
              </button>

              {isAdmin && (
                <button
                  className="primary-button"
                  onClick={() => openEditForm(selectedGuideline)}
                >
                  <Pencil size={16} />
                  Edit Guideline
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Guidelines;
