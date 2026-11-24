
import { useEffect, useState } from "react";
import {
  ShieldCheck,
  LayoutDashboard,
  Activity,
  FileText,
  BookOpen,
  BadgeCheck,
  Image,
  ClipboardList,
  Settings,
  Bell,
  Search,
  Plus,
  ArrowUpRight,
  AlertTriangle,
  CheckCircle2,
  Clock3,
  Menu,
  X,
  Sparkles,
  LogOut,
  RefreshCw,
} from "lucide-react";

import Login from "./pages/Login";
import Submissions from "./pages/Submissions";
import SubmissionList from "./pages/SubmissionList";
import SubmissionDetails from "./pages/SubmissionDetails";
import ReviewFindings from "./pages/ReviewFindings";
import AuditLogs from "./pages/AuditLogs";
import Guidelines from "./pages/Guidelines";
import ApprovedFacts from "./pages/ApprovedFacts";
import BrandAssets from "./pages/BrandAssets";
import Analytics from "./pages/Analytics";

import api from "./services/api";
import "./App.css";

const navigation = [
  { name: "Dashboard", icon: LayoutDashboard },
  { name: "Submissions", icon: FileText },
  { name: "Review Findings", icon: AlertTriangle },
  { name: "Analytics", icon: Activity },
  { name: "Guidelines", icon: BookOpen },
  { name: "Approved Facts", icon: BadgeCheck },
  { name: "Brand Assets", icon: Image },
  { name: "Audit Logs", icon: ClipboardList },
];

function getRecords(response) {
  const data = response?.data;

  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.items)) return data.items;
  if (Array.isArray(data?.results)) return data.results;

  return [];
}

function App() {
  const [activePage, setActivePage] = useState("Dashboard");
  const [selectedSubmissionId, setSelectedSubmissionId] = useState(null);

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loggedOut, setLoggedOut] = useState(false);

  const [submissions, setSubmissions] = useState([]);
  const [findings, setFindings] = useState([]);
  const [loadingDashboard, setLoadingDashboard] = useState(true);
  const [dashboardError, setDashboardError] = useState("");

  const token = localStorage.getItem("brandsentinel_token");

  let currentUser = {};

  try {
    currentUser = JSON.parse(
      localStorage.getItem("brandsentinel_user") || "{}"
    );
  } catch {
    currentUser = {};
  }

  const userName = currentUser.full_name || "Workspace User";

  const userRole = String(currentUser.role || "User")
    .trim()
    .toUpperCase();

  const canCreate = userRole === "CREATOR";
  const isAdmin = userRole === "BRAND_ADMIN";

  // Admin sees every navigation option.
  // Creators do not see Analytics or Audit Logs.
  const visibleNavigation = isAdmin
    ? navigation
    : navigation.filter(
        ({ name }) => !["Analytics", "Audit Logs"].includes(name)
      );

  const logout = () => {
    localStorage.removeItem("brandsentinel_token");
    localStorage.removeItem("brandsentinel_user");
    setLoggedOut(true);
  };

  const fetchDashboardData = async () => {
    setLoadingDashboard(true);
    setDashboardError("");

    try {
      const results = await Promise.allSettled([
        api.get("/review-submissions/"),
        api.get("/review-findings/"),
      ]);

      if (results[0].status === "fulfilled") {
        setSubmissions(getRecords(results[0].value));
      } else {
        setDashboardError(
          "Unable to load submissions. Please check your login and backend."
        );
      }

      if (results[1].status === "fulfilled") {
        setFindings(getRecords(results[1].value));
      } else {
        setFindings([]);
      }
    } catch {
      setDashboardError("Unable to load dashboard information.");
    } finally {
      setLoadingDashboard(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchDashboardData();
    }
  }, [token]);

  if (!token || loggedOut) {
    return <Login />;
  }

  // Protect Admin-only pages from non-admin navigation.
  const selectPage = (page) => {
    if (!isAdmin && ["Analytics", "Audit Logs"].includes(page)) {
      setActivePage("Dashboard");
      setSidebarOpen(false);
      return;
    }

    setActivePage(page);
    setSidebarOpen(false);
  };

  const approvedCount = submissions.filter(
    (item) => item.status === "APPROVED"
  ).length;

  const pendingCount = submissions.filter((item) =>
    ["PENDING", "SUBMITTED", "UNDER_REVIEW"].includes(item.status)
  ).length;

  const highRiskCount = findings.filter((item) =>
    ["HIGH", "CRITICAL"].includes(
      String(item.severity || item.risk_level || "").toUpperCase()
    )
  ).length;

  const recentSubmissions = [...submissions]
    .sort(
      (a, b) =>
        new Date(b.created_at || 0) -
        new Date(a.created_at || 0)
    )
    .slice(0, 5);

  return (
    <div className="app-shell">
      {sidebarOpen && (
        <div
          className="mobile-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-logo">
            <ShieldCheck size={25} />
          </div>

          <div>
            <h2>BrandSentinel</h2>
            <span>BRAND GOVERNANCE</span>
          </div>

          <button
            className="close-sidebar"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={20} />
          </button>
        </div>

        <div className="workspace-label">WORKSPACE</div>

        <nav className="navigation">
          {visibleNavigation.map(({ name, icon: Icon }) => (
            <button
              key={name}
              className={`nav-item ${
                activePage === name ? "active" : ""
              }`}
              onClick={() => selectPage(name)}
            >
              <Icon size={19} />
              <span>{name}</span>

              {name === "Submissions" && (
                <span className="nav-count">
                  {submissions.length}
                </span>
              )}

              {name === "Review Findings" && (
                <span className="nav-count">
                  {findings.length}
                </span>
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <button
            className="nav-item"
            onClick={() => selectPage("Settings")}
          >
            <Settings size={19} />
            <span>Settings</span>
          </button>

          <div className="profile">
            <div className="avatar">
              {userName.charAt(0).toUpperCase()}
            </div>

            <div className="profile-info">
              <strong>{userName}</strong>
              <span>{userRole.replaceAll("_", " ")}</span>
            </div>
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="topbar-left">
            <button
              className="menu-button"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu size={22} />
            </button>

            <div className="breadcrumb">
              Workspace <span>/</span> {activePage}
            </div>
          </div>

          <div className="topbar-actions">
            <button className="icon-button" aria-label="Search">
              <Search size={19} />
            </button>

            <button
              className="icon-button"
              aria-label="Notifications"
            >
              <Bell size={19} />
            </button>

            <div className="top-avatar">
              {userName.charAt(0).toUpperCase()}
            </div>

            <button
              className="logout-button"
              onClick={logout}
              title="Log out"
            >
              <LogOut size={18} />
              <span>Logout</span>
            </button>
          </div>
        </header>

        {activePage === "Dashboard" ? (
          <div className="page-content">
            <section className="welcome-section">
              <div>
                <div className="eyebrow">
                  <Sparkles size={14} />
                  BRAND GOVERNANCE PLATFORM
                </div>

                <h1>
                  Good day! <span>Welcome back, {userName}.</span>
                </h1>

                <p>
                  Monitor your brand compliance and review content
                  before publication.
                </p>
              </div>

              {canCreate && (
                <button
                  className="primary-button"
                  onClick={() => selectPage("New Submission")}
                >
                  <Plus size={18} />
                  New Submission
                </button>
              )}
            </section>

            <section className="hero-card">
              <div className="hero-content">
                <span className="hero-tag">
                  YOUR BRAND. YOUR STANDARDS.
                </span>

                <h2>
                  Keep every publication
                  <br />
                  true to your brand.
                </h2>

                <p>
                  Review content, identify inconsistencies and
                  maintain brand integrity with explainable findings
                  and human oversight.
                </p>

                {canCreate && (
                  <button
                    className="hero-button"
                    onClick={() => selectPage("New Submission")}
                  >
                    Start a review
                    <ArrowUpRight size={17} />
                  </button>
                )}
              </div>

              <div className="hero-art">
                <div className="art-circle circle-one"></div>
                <div className="art-circle circle-two"></div>

                <div className="shield-art">
                  <ShieldCheck size={76} strokeWidth={1.3} />
                </div>

                <div className="floating-card">
                  <CheckCircle2 size={18} />

                  <div>
                    <strong>Brand protection</strong>
                    <span>Review with confidence</span>
                  </div>
                </div>
              </div>
            </section>

            <div className="section-heading">
              <div>
                <h2>Overview</h2>
                <p>Your workspace at a glance</p>
              </div>

              <button
                className="text-button"
                onClick={fetchDashboardData}
                disabled={loadingDashboard}
              >
                <RefreshCw size={15} />
                Refresh
              </button>
            </div>

            {dashboardError && (
              <div className="dashboard-error">
                {dashboardError}
              </div>
            )}

            <section className="stats-grid">
              <StatCard
                icon={FileText}
                title="Total submissions"
                value={loadingDashboard ? "..." : submissions.length}
                note="All recorded submissions"
              />

              <StatCard
                icon={Clock3}
                title="Pending reviews"
                value={loadingDashboard ? "..." : pendingCount}
                note="Awaiting reviewer action"
              />

              <StatCard
                icon={AlertTriangle}
                title="High-risk findings"
                value={loadingDashboard ? "..." : highRiskCount}
                note="High and critical severity"
              />

              <StatCard
                icon={CheckCircle2}
                title="Approved content"
                value={loadingDashboard ? "..." : approvedCount}
                note="Successfully reviewed"
              />
            </section>

            <section className="bottom-grid">
              <div className="panel recent-panel">
                <div className="panel-heading">
                  <div>
                    <h3>Recent submissions</h3>
                    <p>Latest content review activity</p>
                  </div>

                  <button
                    className="text-button"
                    onClick={() => selectPage("Submissions")}
                  >
                    View all
                    <ArrowUpRight size={15} />
                  </button>
                </div>

                {loadingDashboard ? (
                  <div className="empty-state">
                    <p>Loading submissions...</p>
                  </div>
                ) : recentSubmissions.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-icon">
                      <FileText size={25} />
                    </div>

                    <h4>No submissions to display</h4>

                    <p>
                      Your submitted content and review status will
                      appear here.
                    </p>

                    {canCreate && (
                      <button
                        className="secondary-button"
                        onClick={() => selectPage("New Submission")}
                      >
                        Create submission
                        <Plus size={16} />
                      </button>
                    )}
                  </div>
                ) : (
                  <div className="recent-submissions-list">
                    {recentSubmissions.map((item) => (
                      <div
                        className="recent-submission-item"
                        key={item.id}
                      >
                        <div>
                          <strong>{item.title}</strong>
                          <span>
                            #{item.id} · {item.channel || "Unknown channel"}
                          </span>
                        </div>

                        <div className="recent-submission-status">
                          <span>{item.status}</span>
                          <small>
                            Risk: {item.risk_score ?? "—"}
                          </small>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="panel quick-panel">
                <div className="panel-heading">
                  <div>
                    <h3>Quick access</h3>
                    <p>Manage your brand knowledge</p>
                  </div>
                </div>

                <QuickLink
                  icon={BookOpen}
                  title="Brand guidelines"
                  description="Manage brand rules"
                  onClick={() => selectPage("Guidelines")}
                />

                <QuickLink
                  icon={BadgeCheck}
                  title="Approved facts"
                  description="Verify approved information"
                  onClick={() => selectPage("Approved Facts")}
                />

                <QuickLink
                  icon={Image}
                  title="Brand assets"
                  description="Review approved visual assets"
                  onClick={() => selectPage("Brand Assets")}
                />

                {isAdmin && (
                  <QuickLink
                    icon={ClipboardList}
                    title="Audit history"
                    description="Track important actions"
                    onClick={() => selectPage("Audit Logs")}
                  />
                )}
              </div>
            </section>

            <footer className="footer">
              <span>© 2026 BrandSentinel</span>
              <span>Intelligent Brand Governance Platform</span>
            </footer>
          </div>
        ) : activePage === "Submission Details" ? (
          <SubmissionDetails
            submissionId={selectedSubmissionId}
            onBack={() => selectPage("Submissions")}
          />
        ) : activePage === "Submissions" ? (
          <SubmissionList
            onNewSubmission={() => selectPage("New Submission")}
            onViewSubmission={(id) => {
              setSelectedSubmissionId(id);
              selectPage("Submission Details");
            }}
          />
        ) : activePage === "Review Findings" ? (
          <ReviewFindings />
        ) : activePage === "Analytics" ? (
          isAdmin ? (
            <Analytics />
          ) : (
            <AccessDenied />
          )
        ) : activePage === "Audit Logs" ? (
          isAdmin ? (
            <AuditLogs />
          ) : (
            <AccessDenied />
          )
        ) : activePage === "Guidelines" ? (
          <Guidelines />
        ) : activePage === "Approved Facts" ? (
          <ApprovedFacts />
        ) : activePage === "Brand Assets" ? (
          <BrandAssets />
        ) : activePage === "New Submission" ? (
          canCreate ? (
            <Submissions />
          ) : (
            <div className="page-content">
              <div className="dashboard-error">
                Your account does not have permission to create submissions.
                Please log in with a Creator account.
              </div>
            </div>
          )
        ) : (
          <div className="page-content">
            <section className="welcome-section">
              <div>
                <div className="eyebrow">BRAND GOVERNANCE</div>
                <h1>{activePage}</h1>
                <p>
                  Manage and review your {activePage.toLowerCase()}.
                </p>
              </div>
            </section>

            <div className="panel placeholder-panel">
              <div className="empty-icon">
                <Sparkles size={25} />
              </div>

              <h3>{activePage} page</h3>

              <p>
                This section will be connected to your BrandSentinel
                backend in the next steps.
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

function AccessDenied() {
  return (
    <div className="page-content">
      <div className="dashboard-error">
        You do not have permission to access this page.
        Please log in with an Admin account.
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, title, value, note }) {
  return (
    <div className="stat-card">
      <div className="stat-top">
        <div className="stat-icon">
          <Icon size={20} />
        </div>
        <ArrowUpRight size={17} className="stat-arrow" />
      </div>

      <h3>{value}</h3>
      <strong>{title}</strong>
      <p>{note}</p>
    </div>
  );
}

function QuickLink({ icon: Icon, title, description, onClick }) {
  return (
    <button className="quick-link" onClick={onClick}>
      <div className="quick-icon">
        <Icon size={19} />
      </div>

      <div>
        <strong>{title}</strong>
        <span>{description}</span>
      </div>

      <ArrowUpRight size={16} className="quick-arrow" />
    </button>
  );
}

export default App;
