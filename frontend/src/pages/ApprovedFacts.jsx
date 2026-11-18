
import { useEffect, useMemo, useState } from "react";
import {
  Plus,
  Search,
  RefreshCw,
  ShieldCheck,
  FileText,
  CalendarDays,
  Pencil,
  Trash2,
  X,
  CheckCircle2,
  AlertCircle,
  Clock3,
  Filter,
  ExternalLink,
} from "lucide-react";

import api from "../services/api";

function ApprovedFacts() {
  const [facts, setFacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [showForm, setShowForm] = useState(false);
  const [editingFact, setEditingFact] = useState(null);

  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const emptyForm = {
    title: "",
    fact_content: "",
    category: "",
    source_reference: "",
    valid_until: "",
    is_active: true,
  };

  const [formData, setFormData] = useState(emptyForm);

  const fetchFacts = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/approved-facts/");
      setFacts(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      console.error("Fetch approved facts error:", err);
      setError(
        err.response?.data?.detail ||
          "Unable to load approved facts. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFacts();
  }, []);

  const categories = useMemo(() => {
    return [
      "All",
      ...new Set(facts.map((fact) => fact.category).filter(Boolean)),
    ];
  }, [facts]);

  const filteredFacts = useMemo(() => {
    return facts.filter((fact) => {
      const search = searchTerm.toLowerCase();

      const matchesSearch =
        fact.title?.toLowerCase().includes(search) ||
        fact.fact_content?.toLowerCase().includes(search) ||
        fact.category?.toLowerCase().includes(search) ||
        fact.source_reference?.toLowerCase().includes(search);

      const matchesCategory =
        selectedCategory === "All" ||
        fact.category === selectedCategory;

      return matchesSearch && matchesCategory;
    });
  }, [facts, searchTerm, selectedCategory]);

  const activeCount = facts.filter((fact) => fact.is_active).length;

  const expiredCount = facts.filter(
    (fact) =>
      fact.valid_until &&
      fact.valid_until < new Date().toISOString().split("T")[0]
  ).length;

  const openCreateForm = () => {
    setEditingFact(null);
    setFormData(emptyForm);
    setError("");
    setSuccess("");
    setShowForm(true);
  };

  const openEditForm = (fact) => {
    setEditingFact(fact);

    setFormData({
      title: fact.title || "",
      fact_content: fact.fact_content || "",
      category: fact.category || "",
      source_reference: fact.source_reference || "",
      valid_until: fact.valid_until || "",
      is_active: fact.is_active,
    });

    setError("");
    setSuccess("");
    setShowForm(true);
  };

  const closeForm = () => {
    if (saving) return;

    setShowForm(false);
    setEditingFact(null);
    setFormData(emptyForm);
    setError("");
  };

  const handleInputChange = (event) => {
    const { name, value, type, checked } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setSaving(true);
    setError("");
    setSuccess("");

    try {
      const payload = {
        title: formData.title.trim(),
        fact_content: formData.fact_content.trim(),
        category: formData.category.trim(),
        source_reference: formData.source_reference.trim() || null,
        valid_until: formData.valid_until || null,
        is_active: formData.is_active,
      };

      if (editingFact) {
        await api.put(
          `/approved-facts/${editingFact.id}`,
          payload
        );

        setSuccess("Approved fact updated successfully!");
      } else {
        await api.post("/approved-facts/", payload);

        setSuccess("Approved fact created successfully!");
      }

      setShowForm(false);
      setEditingFact(null);
      setFormData(emptyForm);

      await fetchFacts();
    } catch (err) {
      console.error("Save approved fact error:", err);

      setError(
        err.response?.data?.detail ||
          err.message ||
          "Unable to save approved fact."
      );
    } finally {
      setSaving(false);
    }
  };

  const handleDeactivate = async (fact) => {
    const confirmed = window.confirm(
      `Are you sure you want to deactivate "${fact.title}"?`
    );

    if (!confirmed) return;

    setError("");
    setSuccess("");

    try {
      await api.delete(`/approved-facts/${fact.id}`);

      setSuccess("Approved fact deactivated successfully!");
      await fetchFacts();
    } catch (err) {
      console.error("Deactivate approved fact error:", err);

      setError(
        err.response?.data?.detail ||
          "Unable to deactivate approved fact."
      );
    }
  };

  const formatDate = (dateValue) => {
    if (!dateValue) return "No expiry date";

    return new Date(`${dateValue}T00:00:00`).toLocaleDateString(
      "en-IN",
      {
        day: "numeric",
        month: "short",
        year: "numeric",
      }
    );
  };

  const getExpiryStatus = (fact) => {
    if (!fact.is_active) {
      return { label: "Inactive", className: "inactive" };
    }

    if (
      fact.valid_until &&
      fact.valid_until < new Date().toISOString().split("T")[0]
    ) {
      return { label: "Expired", className: "expired" };
    }

    return { label: "Active", className: "active" };
  };

  return (
    <div className="approved-facts-page">

      {/* PAGE HEADER */}
      <div className="approved-facts-header">
        <div>
          <div className="approved-facts-heading">
            <div className="approved-facts-heading-icon">
              <ShieldCheck size={25} />
            </div>

            <div>
              <h1>Approved Facts</h1>
              <p>
                Manage verified brand information and trusted claims.
              </p>
            </div>
          </div>
        </div>

        <div className="approved-facts-header-actions">
          <button
            className="af-refresh-button"
            onClick={fetchFacts}
            disabled={loading}
          >
            <RefreshCw size={16} />
            Refresh
          </button>

          <button
            className="af-primary-button"
            onClick={openCreateForm}
          >
            <Plus size={18} />
            Add Approved Fact
          </button>
        </div>
      </div>

      {/* ALERTS */}
      {success && (
        <div className="af-alert af-success-alert">
          <CheckCircle2 size={18} />
          {success}
          <button onClick={() => setSuccess("")}>
            <X size={16} />
          </button>
        </div>
      )}

      {error && !showForm && (
        <div className="af-alert af-error-alert">
          <AlertCircle size={18} />
          {error}
          <button onClick={() => setError("")}>
            <X size={16} />
          </button>
        </div>
      )}

      {/* SUMMARY CARDS */}
      <div className="af-summary-grid">

        <div className="af-summary-card">
          <div className="af-summary-icon af-purple">
            <FileText size={21} />
          </div>
          <div>
            <p>Total Facts</p>
            <h2>{facts.length}</h2>
          </div>
        </div>

        <div className="af-summary-card">
          <div className="af-summary-icon af-green">
            <ShieldCheck size={21} />
          </div>
          <div>
            <p>Active Facts</p>
            <h2>{activeCount}</h2>
          </div>
        </div>

        <div className="af-summary-card">
          <div className="af-summary-icon af-orange">
            <Clock3 size={21} />
          </div>
          <div>
            <p>Expired Facts</p>
            <h2>{expiredCount}</h2>
          </div>
        </div>

        <div className="af-summary-card">
          <div className="af-summary-icon af-blue">
            <Filter size={21} />
          </div>
          <div>
            <p>Categories</p>
            <h2>{categories.length - 1}</h2>
          </div>
        </div>

      </div>

      {/* FACTS SECTION */}
      <section className="af-content-panel">

        <div className="af-panel-header">
          <div>
            <h2>Verified Brand Information</h2>
            <p>
              Browse and manage facts approved for brand communication.
            </p>
          </div>

          <span className="af-count-label">
            {filteredFacts.length} facts
          </span>
        </div>

        {/* SEARCH AND FILTER */}
        <div className="af-toolbar">

          <div className="af-search-box">
            <Search size={18} />
            <input
              type="text"
              placeholder="Search facts, categories or sources..."
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
            />
          </div>

          <select
            value={selectedCategory}
            onChange={(event) => setSelectedCategory(event.target.value)}
            className="af-category-select"
          >
            {categories.map((category) => (
              <option key={category} value={category}>
                {category === "All" ? "All Categories" : category}
              </option>
            ))}
          </select>

        </div>

        {/* FACTS LIST */}
        {loading ? (
          <div className="af-loading">
            <RefreshCw className="af-spin" size={25} />
            <p>Loading approved facts...</p>
          </div>
        ) : filteredFacts.length === 0 ? (
          <div className="af-empty-state">
            <div className="af-empty-icon">
              <FileText size={30} />
            </div>

            <h3>No approved facts found</h3>
            <p>
              {searchTerm || selectedCategory !== "All"
                ? "Try changing your search or category filter."
                : "Start by adding your first verified brand fact."}
            </p>

            {!searchTerm && selectedCategory === "All" && (
              <button
                className="af-primary-button"
                onClick={openCreateForm}
              >
                <Plus size={17} />
                Add First Fact
              </button>
            )}
          </div>
        ) : (
          <div className="af-facts-grid">

            {filteredFacts.map((fact) => {
              const expiryStatus = getExpiryStatus(fact);

              return (
                <article className="af-fact-card" key={fact.id}>

                  <div className="af-fact-card-top">
                    <span className="af-category-tag">
                      {fact.category || "Uncategorized"}
                    </span>

                    <span
                      className={`af-status-tag ${expiryStatus.className}`}
                    >
                      {expiryStatus.label}
                    </span>
                  </div>

                  <h3>{fact.title}</h3>

                  <p className="af-fact-content">
                    {fact.fact_content}
                  </p>

                  {fact.source_reference && (
                    <div className="af-source-row">
                      <ExternalLink size={15} />
                      <span>{fact.source_reference}</span>
                    </div>
                  )}

                  <div className="af-expiry-row">
                    <CalendarDays size={16} />
                    <span>
                      Valid until: {formatDate(fact.valid_until)}
                    </span>
                  </div>

                  <div className="af-card-footer">
                    <span className="af-fact-id">
                      FACT #{fact.id}
                    </span>

                    <div className="af-card-actions">
                      <button
                        className="af-edit-button"
                        onClick={() => openEditForm(fact)}
                        title="Edit fact"
                      >
                        <Pencil size={16} />
                        Edit
                      </button>

                      {fact.is_active && (
                        <button
                          className="af-delete-button"
                          onClick={() => handleDeactivate(fact)}
                          title="Deactivate fact"
                        >
                          <Trash2 size={16} />
                        </button>
                      )}
                    </div>
                  </div>

                </article>
              );
            })}

          </div>
        )}

      </section>

      {/* CREATE / EDIT MODAL */}
      {showForm && (
        <div
          className="af-modal-overlay"
          onClick={(event) => {
            if (event.target === event.currentTarget) {
              closeForm();
            }
          }}
        >
          <div className="af-modal">

            <div className="af-modal-header">
              <div>
                <h2>
                  {editingFact ? "Edit Approved Fact" : "Add Approved Fact"}
                </h2>
                <p>
                  Add verified information with a reliable source.
                </p>
              </div>

              <button
                className="af-modal-close"
                onClick={closeForm}
                disabled={saving}
              >
                <X size={20} />
              </button>
            </div>

            {error && (
              <div className="af-alert af-error-alert">
                <AlertCircle size={17} />
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit}>

              <label>Fact Title *</label>
              <input
                type="text"
                name="title"
                placeholder="e.g. Product Battery Life"
                value={formData.title}
                onChange={handleInputChange}
                minLength={2}
                required
              />

              <label>Fact Content *</label>
              <textarea
                name="fact_content"
                placeholder="Enter the exact verified brand information..."
                value={formData.fact_content}
                onChange={handleInputChange}
                rows={4}
                required
              />

              <label>Category *</label>
              <input
                type="text"
                name="category"
                placeholder="e.g. Product Specification"
                value={formData.category}
                onChange={handleInputChange}
                required
              />

              <label>Source Reference</label>
              <input
                type="text"
                name="source_reference"
                placeholder="e.g. Official Product Specification - Page 4"
                value={formData.source_reference}
                onChange={handleInputChange}
              />

              <label>Valid Until</label>
              <input
                type="date"
                name="valid_until"
                value={formData.valid_until}
                onChange={handleInputChange}
                min={new Date().toISOString().split("T")[0]}
              />

              {editingFact && (
                <label className="af-active-checkbox">
                  <input
                    type="checkbox"
                    name="is_active"
                    checked={formData.is_active}
                    onChange={handleInputChange}
                  />
                  Fact is active
                </label>
              )}

              <div className="af-form-actions">
                <button
                  type="button"
                  className="af-cancel-button"
                  onClick={closeForm}
                  disabled={saving}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="af-primary-button"
                  disabled={saving}
                >
                  {saving ? (
                    <>
                      <RefreshCw size={16} className="af-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <CheckCircle2 size={17} />
                      {editingFact ? "Save Changes" : "Create Fact"}
                    </>
                  )}
                </button>
              </div>

            </form>
          </div>
        </div>
      )}

    </div>
  );
}

export default ApprovedFacts;
