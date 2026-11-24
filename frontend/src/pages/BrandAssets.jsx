
import { useEffect, useRef, useState } from "react";
import {
  Image,
  Upload,
  Search,
  Plus,
  Eye,
  Pencil,
  Trash2,
  CheckCircle2,
  Clock3,
  X,
  ShieldCheck,
  Palette,
  ScanText,
  Accessibility,
  RefreshCw,
  AlertCircle,
  FileImage,
  Loader2,
} from "lucide-react";

import api from "../services/api";
import "../App.css";

const initialForm = {
  name: "",
  asset_type: "LOGO",
  description: "",
};

function getErrorMessage(error) {
  return (
    error.response?.data?.detail ||
    error.message ||
    "Something went wrong. Please try again."
  );
}

function BrandAssets() {
  const fileInputRef = useRef(null);

  const [assets, setAssets] = useState([]);
  const [imageUrls, setImageUrls] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("ALL");

  const [showUpload, setShowUpload] = useState(false);
  const [editingAsset, setEditingAsset] = useState(null);
  const [selectedAsset, setSelectedAsset] = useState(null);

  const [form, setForm] = useState(initialForm);
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState("");

  const [saving, setSaving] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);

  const [analysisForm, setAnalysisForm] = useState({
    approved_colors: "#000000,#FFFFFF",
    alt_text: "",
    foreground_color: "#000000",
    background_color: "#FFFFFF",
    is_large_text: false,
  });

  let currentUser = {};

  try {
    currentUser = JSON.parse(
      localStorage.getItem("brandsentinel_user") || "{}"
    );
  } catch {
    currentUser = {};
  }

  // Normalize the role before checking Admin permissions.
  const canManage =
    String(currentUser.role || "").trim().toUpperCase() ===
    "BRAND_ADMIN";

  const fetchAssets = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/brand-assets/");
      setAssets(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssets();
  }, []);

  useEffect(() => {
    let isMounted = true;
    const createdUrls = [];

    const loadImages = async () => {
      const results = await Promise.all(
        assets.map(async (asset) => {
          try {
            const response = await api.get(
              `/brand-assets/${asset.id}/image`,
              { responseType: "blob" }
            );

            const url = URL.createObjectURL(response.data);
            createdUrls.push(url);

            return [asset.id, url];
          } catch (err) {
            console.error(
              `Image loading failed for asset ${asset.id}`,
              err
            );
            return [asset.id, null];
          }
        })
      );

      if (isMounted) {
        setImageUrls(Object.fromEntries(results));
      }
    };

    if (assets.length) {
      loadImages();
    } else {
      setImageUrls({});
    }

    return () => {
      isMounted = false;
      createdUrls.forEach(URL.revokeObjectURL);
    };
  }, [assets]);

  useEffect(() => {
    if (!selectedFile) {
      setPreview("");
      return;
    }

    const url = URL.createObjectURL(selectedFile);
    setPreview(url);

    return () => URL.revokeObjectURL(url);
  }, [selectedFile]);

  const filteredAssets = assets.filter((asset) => {
    const matchesSearch =
      asset.name?.toLowerCase().includes(search.toLowerCase()) ||
      asset.asset_type?.toLowerCase().includes(search.toLowerCase());

    const matchesFilter =
      filter === "ALL" ||
      (filter === "APPROVED" && asset.is_approved) ||
      (filter === "PENDING" && !asset.is_approved);

    return matchesSearch && matchesFilter;
  });

  const approvedCount = assets.filter(
    (asset) => asset.is_approved
  ).length;

  const pendingCount = assets.filter(
    (asset) => !asset.is_approved
  ).length;

  const openUpload = () => {
    setForm(initialForm);
    setSelectedFile(null);
    setEditingAsset(null);
    setError("");
    setSuccess("");
    setShowUpload(true);
  };

  const openEdit = (asset) => {
    setEditingAsset(asset);

    setForm({
      name: asset.name || "",
      asset_type: asset.asset_type || "LOGO",
      description: asset.description || "",
    });

    setSelectedFile(null);
    setError("");
    setShowUpload(true);
  };

  const closeUpload = () => {
    setShowUpload(false);
    setEditingAsset(null);
    setSelectedFile(null);
    setForm(initialForm);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    const allowedTypes = [
      "image/png",
      "image/jpeg",
      "image/webp",
    ];

    if (!allowedTypes.includes(file.type)) {
      setError(
        "Please select a PNG, JPG, JPEG or WEBP image."
      );
      event.target.value = "";
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError("Image size must not exceed 10 MB.");
      event.target.value = "";
      return;
    }

    setError("");
    setSelectedFile(file);

    if (!form.name.trim()) {
      setForm((previous) => ({
        ...previous,
        name: file.name.replace(/\.[^/.]+$/, ""),
      }));
    }
  };

  const handleUpload = async (event) => {
    event.preventDefault();

    if (!form.name.trim() || !form.asset_type.trim()) {
      setError("Please enter an asset name and type.");
      return;
    }

    if (!editingAsset && !selectedFile) {
      setError("Please select an image to upload.");
      return;
    }

    setSaving(true);
    setError("");
    setSuccess("");

    try {
      if (editingAsset) {
        await api.patch(
          `/brand-assets/${editingAsset.id}`,
          {
            name: form.name.trim(),
            asset_type: form.asset_type.trim(),
            description: form.description.trim() || null,
          }
        );

        setSuccess("Brand asset updated successfully.");
      } else {
        const formData = new FormData();

        formData.append("name", form.name.trim());
        formData.append("asset_type", form.asset_type.trim());
        formData.append("description", form.description.trim());
        formData.append("file", selectedFile);

        await api.post("/brand-assets/upload", formData);

        setSuccess(
          "Asset uploaded successfully. It is awaiting approval."
        );
      }

      closeUpload();
      await fetchAssets();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const toggleApproval = async (asset) => {
    const action = asset.is_approved
      ? "remove approval from"
      : "approve";

    if (
      !window.confirm(
        `Are you sure you want to ${action} this asset?`
      )
    ) {
      return;
    }

    setError("");
    setSuccess("");

    try {
      await api.patch(`/brand-assets/${asset.id}`, {
        is_approved: !asset.is_approved,
      });

      setSuccess(
        asset.is_approved
          ? "Asset approval removed."
          : "Brand asset approved successfully."
      );

      await fetchAssets();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const deactivateAsset = async (asset) => {
    if (!window.confirm(`Deactivate "${asset.name}"?`)) return;

    setError("");
    setSuccess("");

    try {
      await api.delete(`/brand-assets/${asset.id}`);

      setSuccess("Brand asset deactivated successfully.");

      if (selectedAsset?.id === asset.id) {
        setSelectedAsset(null);
      }

      await fetchAssets();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const openDetails = (asset) => {
    setSelectedAsset(asset);
    setAnalysis(null);

    setAnalysisForm({
      approved_colors: "#000000,#FFFFFF",
      alt_text: asset.description || "",
      foreground_color: "#000000",
      background_color: "#FFFFFF",
      is_large_text: false,
    });
  };

  const analyzeImage = async () => {
    if (!selectedAsset) return;

    const colors = analysisForm.approved_colors
      .split(",")
      .map((color) => color.trim())
      .filter(Boolean);

    if (!colors.length) {
      setError("Enter at least one approved brand color.");
      return;
    }

    setAnalyzing(true);
    setError("");
    setAnalysis(null);

    try {
      const response = await api.post(
        `/brand-assets/${selectedAsset.id}/analyze-image`,
        {
          approved_colors: colors,
          alt_text: analysisForm.alt_text || null,
          foreground_color:
            analysisForm.foreground_color || null,
          background_color:
            analysisForm.background_color || null,
          is_large_text: analysisForm.is_large_text,
        }
      );

      setAnalysis(response.data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="page-content brand-assets-page">
      <section className="welcome-section">
        <div>
          <div className="eyebrow">
            <ShieldCheck size={14} />
            BRAND GOVERNANCE
          </div>

          <h1>Brand Assets</h1>

          <p>
            Manage your visual identity, approve brand assets
            and check accessibility compliance.
          </p>
        </div>

        {canManage && (
          <button
            type="button"
            className="primary-button"
            onClick={openUpload}
          >
            <Plus size={18} />
            Upload Asset
          </button>
        )}
      </section>

      {error && (
        <div className="dashboard-error brand-message">
          <AlertCircle size={17} />
          {error}
          <button
            type="button"
            onClick={() => setError("")}
          >
            <X size={16} />
          </button>
        </div>
      )}

      {success && (
        <div className="brand-success">
          <CheckCircle2 size={17} />
          {success}
          <button
            type="button"
            onClick={() => setSuccess("")}
          >
            <X size={16} />
          </button>
        </div>
      )}

      <section className="stats-grid brand-stats">
        <div className="stat-card">
          <div className="stat-top">
            <div className="stat-icon">
              <Image size={20} />
            </div>
          </div>
          <h3>{loading ? "..." : assets.length}</h3>
          <strong>Total assets</strong>
          <p>Active brand assets</p>
        </div>

        <div className="stat-card">
          <div className="stat-top">
            <div className="stat-icon">
              <CheckCircle2 size={20} />
            </div>
          </div>
          <h3>{loading ? "..." : approvedCount}</h3>
          <strong>Approved assets</strong>
          <p>Ready for brand use</p>
        </div>

        <div className="stat-card">
          <div className="stat-top">
            <div className="stat-icon">
              <Clock3 size={20} />
            </div>
          </div>
          <h3>{loading ? "..." : pendingCount}</h3>
          <strong>Pending approval</strong>
          <p>Awaiting review</p>
        </div>
      </section>

      <section className="panel brand-library">
        <div className="panel-heading brand-library-heading">
          <div>
            <h3>Asset Library</h3>
            <p>Browse and manage your brand visuals</p>
          </div>

          <button
            type="button"
            className="text-button"
            onClick={fetchAssets}
            disabled={loading}
          >
            <RefreshCw size={15} />
            Refresh
          </button>
        </div>

        <div className="brand-toolbar">
          <div className="brand-search">
            <Search size={18} />
            <input
              type="text"
              placeholder="Search assets..."
              value={search}
              onChange={(event) =>
                setSearch(event.target.value)
              }
            />
          </div>

          <select
            value={filter}
            onChange={(event) => setFilter(event.target.value)}
            className="brand-filter"
          >
            <option value="ALL">All assets</option>
            <option value="APPROVED">Approved</option>
            <option value="PENDING">Pending approval</option>
          </select>
        </div>

        {loading ? (
          <div className="brand-empty">
            <Loader2 className="spin" size={30} />
            <p>Loading brand assets...</p>
          </div>
        ) : filteredAssets.length === 0 ? (
          <div className="brand-empty">
            <div className="empty-icon">
              <FileImage size={26} />
            </div>

            <h3>No brand assets found</h3>

            <p>
              {search
                ? "Try another search term."
                : "Upload your first brand asset to start building your library."}
            </p>

            {canManage && !search && (
              <button
                type="button"
                className="primary-button"
                onClick={openUpload}
              >
                <Upload size={17} />
                Upload your first asset
              </button>
            )}
          </div>
        ) : (
          <div className="brand-assets-grid">
            {filteredAssets.map((asset) => (
              <article
                className="brand-asset-card"
                key={asset.id}
              >
                <div className="brand-asset-image">
                  {imageUrls[asset.id] ? (
                    <img
                      src={imageUrls[asset.id]}
                      alt={asset.name}
                    />
                  ) : (
                    <div className="empty-icon">
                      <FileImage size={28} />
                    </div>
                  )}

                  <span
                    className={`asset-status ${
                      asset.is_approved ? "approved" : "pending"
                    }`}
                  >
                    {asset.is_approved ? (
                      <CheckCircle2 size={13} />
                    ) : (
                      <Clock3 size={13} />
                    )}
                    {asset.is_approved ? "Approved" : "Pending"}
                  </span>
                </div>

                <div className="brand-asset-info">
                  <div>
                    <span className="asset-type">
                      {asset.asset_type}
                    </span>
                    <h4>{asset.name}</h4>
                    <p>
                      {asset.description ||
                        "No description provided."}
                    </p>
                  </div>

                  <div className="brand-asset-actions">
                    <button
                      type="button"
                      className="asset-action-button"
                      title="View and analyze"
                      onClick={() => openDetails(asset)}
                    >
                      <Eye size={16} />
                    </button>

                    {canManage && (
                      <>
                        <button
                          type="button"
                          className="asset-action-button"
                          title="Edit"
                          onClick={() => openEdit(asset)}
                        >
                          <Pencil size={16} />
                        </button>

                        <button
                          type="button"
                          className="asset-action-button danger"
                          title="Deactivate"
                          onClick={() => deactivateAsset(asset)}
                        >
                          <Trash2 size={16} />
                        </button>
                      </>
                    )}
                  </div>

                  {canManage && (
                    <button
                      type="button"
                      className={`approval-button ${
                        asset.is_approved
                          ? "remove-approval"
                          : ""
                      }`}
                      onClick={() => toggleApproval(asset)}
                    >
                      {asset.is_approved
                        ? "Remove approval"
                        : "Approve asset"}
                    </button>
                  )}
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

      {showUpload && (
        <div className="brand-modal-overlay">
          <div className="brand-modal">
            <div className="brand-modal-header">
              <div>
                <h2>
                  {editingAsset
                    ? "Edit Brand Asset"
                    : "Upload Brand Asset"}
                </h2>
                <p>
                  {editingAsset
                    ? "Update the asset information."
                    : "Add a new visual asset to your brand library."}
                </p>
              </div>

              <button
                type="button"
                className="modal-close"
                onClick={closeUpload}
              >
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleUpload}>
              <label>Asset name *</label>
              <input
                type="text"
                placeholder="e.g. Company Logo"
                value={form.name}
                onChange={(event) =>
                  setForm({
                    ...form,
                    name: event.target.value,
                  })
                }
                required
              />

              <label>Asset type *</label>
              <select
                value={form.asset_type}
                onChange={(event) =>
                  setForm({
                    ...form,
                    asset_type: event.target.value,
                  })
                }
                required
              >
                <option value="LOGO">Logo</option>
                <option value="BANNER">Banner</option>
                <option value="ICON">Icon</option>
                <option value="PRODUCT_IMAGE">
                  Product Image
                </option>
                <option value="SOCIAL_MEDIA">
                  Social Media
                </option>
                <option value="ADVERTISEMENT">
                  Advertisement
                </option>
                <option value="OTHER">Other</option>
              </select>

              <label>Description</label>
              <textarea
                placeholder="Describe this brand asset..."
                rows="3"
                value={form.description}
                onChange={(event) =>
                  setForm({
                    ...form,
                    description: event.target.value,
                  })
                }
              />

              {!editingAsset && (
                <>
                  <label>Choose image *</label>

                  <div
                    className="brand-file-upload"
                    role="button"
                    tabIndex={0}
                    onClick={() =>
                      fileInputRef.current?.click()
                    }
                    onKeyDown={(event) => {
                      if (
                        event.key === "Enter" ||
                        event.key === " "
                      ) {
                        event.preventDefault();
                        fileInputRef.current?.click();
                      }
                    }}
                  >
                    <Upload size={28} />

                    <strong>
                      {selectedFile
                        ? selectedFile.name
                        : "Choose an image"}
                    </strong>

                    <span>
                      PNG, JPG, JPEG or WEBP · Maximum 10 MB
                    </span>

                    <button
                      type="button"
                      className="secondary-button"
                      onClick={(event) => {
                        event.stopPropagation();
                        fileInputRef.current?.click();
                      }}
                    >
                      Browse Files
                    </button>

                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".png,.jpg,.jpeg,.webp,image/png,image/jpeg,image/webp"
                      onChange={handleFileChange}
                      hidden
                    />
                  </div>

                  {preview && (
                    <div className="brand-upload-preview">
                      <img
                        src={preview}
                        alt="Selected preview"
                      />

                      <span>{selectedFile?.name}</span>

                      <button
                        type="button"
                        className="asset-action-button danger"
                        onClick={() => {
                          setSelectedFile(null);

                          if (fileInputRef.current) {
                            fileInputRef.current.value = "";
                          }
                        }}
                      >
                        <X size={16} />
                      </button>
                    </div>
                  )}
                </>
              )}

              <div className="brand-modal-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={closeUpload}
                  disabled={saving}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="primary-button"
                  disabled={saving}
                >
                  {saving ? (
                    <>
                      <Loader2 className="spin" size={17} />
                      Uploading...
                    </>
                  ) : editingAsset ? (
                    "Save changes"
                  ) : (
                    "Upload asset"
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {selectedAsset && (
        <div className="brand-modal-overlay">
          <div className="brand-modal brand-details-modal">
            <div className="brand-modal-header">
              <div>
                <h2>{selectedAsset.name}</h2>
                <p>
                  Brand asset details and accessibility analysis
                </p>
              </div>

              <button
                type="button"
                className="modal-close"
                onClick={() => {
                  setSelectedAsset(null);
                  setAnalysis(null);
                }}
              >
                <X size={20} />
              </button>
            </div>

            <div className="brand-detail-preview">
              {imageUrls[selectedAsset.id] ? (
                <img
                  src={imageUrls[selectedAsset.id]}
                  alt={selectedAsset.name}
                />
              ) : (
                <div className="empty-icon">
                  <FileImage size={28} />
                  <p>Image preview unavailable</p>
                </div>
              )}
            </div>

            <div className="brand-detail-meta">
              <span>
                Type: {selectedAsset.asset_type}
              </span>

              <span>
                Status:{" "}
                {selectedAsset.is_approved
                  ? "Approved"
                  : "Pending"}
              </span>
            </div>

            {canManage && selectedAsset.is_approved && (
              <div className="analysis-section">
                <div className="analysis-heading">
                  <Accessibility size={19} />

                  <div>
                    <h3>Accessibility analysis</h3>
                    <p>
                      Check visual accessibility and brand consistency
                    </p>
                  </div>
                </div>

                <label>Approved brand colors</label>

                <input
                  value={analysisForm.approved_colors}
                  onChange={(event) =>
                    setAnalysisForm({
                      ...analysisForm,
                      approved_colors: event.target.value,
                    })
                  }
                  placeholder="#000000,#FFFFFF"
                />

                <small>
                  Enter hex colors separated by commas.
                </small>

                <label>Alternative text</label>

                <input
                  value={analysisForm.alt_text}
                  onChange={(event) =>
                    setAnalysisForm({
                      ...analysisForm,
                      alt_text: event.target.value,
                    })
                  }
                  placeholder="Describe the image..."
                />

                <div className="analysis-color-grid">
                  <div>
                    <label>Foreground color</label>

                    <input
                      value={analysisForm.foreground_color}
                      onChange={(event) =>
                        setAnalysisForm({
                          ...analysisForm,
                          foreground_color: event.target.value,
                        })
                      }
                    />
                  </div>

                  <div>
                    <label>Background color</label>

                    <input
                      value={analysisForm.background_color}
                      onChange={(event) =>
                        setAnalysisForm({
                          ...analysisForm,
                          background_color: event.target.value,
                        })
                      }
                    />
                  </div>
                </div>

                <label className="analysis-checkbox">
                  <input
                    type="checkbox"
                    checked={analysisForm.is_large_text}
                    onChange={(event) =>
                      setAnalysisForm({
                        ...analysisForm,
                        is_large_text: event.target.checked,
                      })
                    }
                  />

                  Text is large (18pt or 14pt bold)
                </label>

                <button
                  type="button"
                  className="primary-button analysis-button"
                  onClick={analyzeImage}
                  disabled={analyzing}
                >
                  {analyzing ? (
                    <Loader2 className="spin" size={17} />
                  ) : (
                    <ScanText size={17} />
                  )}

                  {analyzing
                    ? "Analyzing..."
                    : "Run image analysis"}
                </button>

                {analysis && (
                  <div className="analysis-results">
                    <h3>
                      <CheckCircle2 size={18} />
                      Analysis results
                    </h3>

                    {[
                      ["OCR Results", analysis.ocr, ScanText],
                      ["Brand Palette", analysis.palette, Palette],
                      [
                        "Alt Text",
                        analysis.alt_text,
                        Accessibility,
                      ],
                      [
                        "Contrast",
                        analysis.contrast,
                        ShieldCheck,
                      ],
                    ].map(([title, value, Icon]) => (
                      <div
                        className="analysis-result-card"
                        key={title}
                      >
                        <Icon size={18} />

                        <div>
                          <strong>{title}</strong>
                          <pre>
                            {JSON.stringify(value, null, 2)}
                          </pre>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {!selectedAsset.is_approved && (
              <div className="pending-analysis-note">
                <Clock3 size={18} />
                This asset must be approved before image analysis can run.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default BrandAssets;
