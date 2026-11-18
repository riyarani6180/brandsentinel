# 🛡️ BrandSentinel
### AI-Powered Brand Compliance & Governance Platform

**BrandSentinel** is a centralized brand compliance platform designed to help organizations maintain consistent, accurate, and trustworthy brand communication.

It evaluates marketing content against approved brand guidelines, verifies factual claims using an approved facts repository, identifies terminology violations, and analyzes brand assets for visual and accessibility compliance.

The platform supports a human-in-the-loop review process, ensuring that final publication decisions remain under the control of authorized reviewers.

---

## 🚀 Problem Statement

Organizations publish content across multiple channels, including advertisements, social media posts, emails, and promotional documents.

Maintaining brand consistency across these channels is challenging because:

- Marketing content may contain prohibited or misleading claims.
- Teams may use inconsistent brand terminology.
- Factual statements may lack approved supporting evidence.
- Visual assets may not follow established brand guidelines.
- Manual compliance reviews can be time-consuming and inconsistent.
- Organizations need accountability and traceability for approval decisions.

BrandSentinel addresses these challenges through a centralized and structured brand compliance workflow.

---

## 💡 Our Solution

BrandSentinel provides a unified platform that checks submitted content against organizational brand policies before publication.

It combines rule-based content analysis, approved-fact verification, brand asset analysis, role-based access control, and human review.

The system follows a structured workflow:

**Submit → Analyze → Detect → Recommend → Review → Approve / Reject / Request Changes → Audit**

---

## ✨ Key Features

### 1. Dashboard
- Centralized compliance overview.
- Submission statistics.
- Risk information.
- Brand asset statistics.
- Quick access to important platform sections.

### 2. Automated Content Compliance
- Analyze submitted promotional content.
- Detect prohibited terminology.
- Identify non-preferred brand terminology.
- Check marketing claims against approved facts.
- Generate compliance findings.
- Calculate submission risk scores.
- Provide suggested corrections for detected violations.

### 3. Brand Guidelines Management
- Create and manage brand guidelines.
- Maintain approved terminology.
- Define prohibited expressions.
- Store brand communication requirements.
- Activate or deactivate guidelines.

### 4. Approved Facts Verification
- Maintain a repository of approved organizational facts.
- Associate factual claims with supporting information.
- Check submitted claims against approved facts.
- Identify supported and unverified statements.
- Track fact validity periods.

### 5. Brand Asset Management
- Manage registered brand assets.
- View existing uploaded images.
- Track asset approval status.
- Analyze approved visual assets.

### 6. Visual & Accessibility Analysis
BrandSentinel provides multiple image analysis checks:

- **OCR Analysis:** Extracts text from images.
- **Brand Palette Analysis:** Checks dominant image colors against approved brand colors.
- **Alternative Text Validation:** Checks whether descriptive alt text is provided.
- **Color Contrast Analysis:** Evaluates foreground and background contrast against WCAG accessibility requirements.

### 7. Human-in-the-Loop Review
Authorized reviewers retain control over final compliance decisions.

Available reviewer actions:

- Approve submissions.
- Reject submissions.
- Request changes.

Creators can submit content and view compliance findings, while review permissions are restricted to authorized users.

### 8. Audit Logs
- Record important platform activities.
- Track submission-related actions.
- Maintain a history of reviewer decisions.
- Improve accountability and traceability.

### 9. Role-Based Access Control
The platform supports different user roles and permission-based access.

- **Brand Admin:** Manages brand policies, approved facts, assets, and administrative operations.
- **Creator:** Submits content and views analysis results.
- **Reviewer:** Reviews compliance findings and makes approval decisions.

---

## 🧰 Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React.js, Vite |
| Styling | CSS |
| Icons | Lucide React |
| Backend | Python, FastAPI |
| Database | SQLite |
| ORM | SQLAlchemy |
| Authentication | JWT-based authentication |
| API Communication | Axios, REST API |
| OCR | Tesseract OCR / configured OCR engine |
| Image Processing | Pillow, configured image analysis libraries |
| Accessibility | WCAG contrast evaluation |

---

## 🏗️ System Architecture

```text
                 USER
                   |
                   v
          React + Vite Frontend
                   |
                   v
              Axios API
                   |
                   v
            FastAPI Backend
                   |
       +-----------+-----------+
       |           |           |
       v           v           v
 Authentication  Compliance  Brand Asset
 & Permissions    Engine      Analysis
       |           |           |
       |      +----+----+      |
       |      |         |      |
       |      v         v      v
       |   Guidelines Approved OCR
       |              Facts   Palette
       |                      Contrast
       |                      Alt Text
       |
       v
    SQLite Database
       |
       v
    Audit Logs
```

---

## 🔄 How BrandSentinel Works

1. **Content Submission:** A creator submits promotional content through the platform.
2. **Automatic Analysis:** The backend analyzes the submitted content against active brand guidelines and approved facts.
3. **Violation Detection:** The system identifies prohibited terms, non-preferred terminology, and unsupported claims.
4. **Risk Assessment:** A risk score is calculated based on the severity of detected findings.
5. **Suggested Corrections:** The platform provides recommendations to help address compliance issues.
6. **Human Review:** An authorized reviewer examines the findings and submitted content.
7. **Final Decision:** The reviewer approves, rejects, or requests changes.
8. **Audit Tracking:** Important actions are recorded for accountability.

---

## 📊 Risk Assessment Method

BrandSentinel calculates a risk score using severity-based weights.

| Finding Severity | Risk Weight |
|---|---:|
| Critical | 40 |
| High | 25 |
| Medium | 15 |
| Low | 5 |

The total risk score is capped at 100.

The platform categorizes submission status according to the calculated score:

| Condition | Submission Status |
|---|---|
| Risk score = 0 | PASSED |
| Risk score between 1 and 59 | NEEDS_REVISION |
| Risk score 60 or higher | REQUIRES_REVIEW |

---

## 📁 Project Structure

```text
BrandSentinel/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── security/
│   │   ├── accessibility/
│   │   ├── database/
│   │   └── main.py
│   │
│   ├── uploads/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.jsx
│   │
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
└── README.md
```

---

## ⚙️ Installation & Setup

### Prerequisites

Make sure you have installed:

- Python 3.10 or later (use the version supported by your dependencies).
- Node.js and npm.
- Git.

### 1. Clone the Repository

```bash
git clone https://github.com/riyarani6180/brandsentinel.git
cd brandsentinel
```

### 2. Backend Setup

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install backend dependencies:

```bash
pip install -r backend/requirements.txt
```

Start the FastAPI server:

```bash
python -m uvicorn app.main:app --reload --app-dir backend
```

Backend URL:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### 3. Frontend Setup

Open another terminal:

```bash
cd frontend
npm install
```

Create a `.env` file inside the frontend directory:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Start the development server:

```bash
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

---

## 🔐 Security & Access Control

BrandSentinel incorporates:

- JWT-based authentication.
- Protected API endpoints.
- Role-based authorization.
- Permission-controlled reviewer operations.
- Audit logging for important actions.

**Important:** Never commit passwords, secret keys, access tokens, or private environment files to the public repository.

---

## 🧪 Testing & Validation

The following application workflows have been manually tested during development:

- User authentication and role-based access.
- Dashboard statistics and asset counts.
- Automatic content compliance analysis.
- Prohibited and non-preferred terminology detection.
- Approved-fact verification.
- Risk score generation.
- Reviewer approval, rejection, and change-request actions.
- Audit log generation.
- Brand image display and image accessibility analysis.
- OCR, color palette, alt text, and contrast checks.

---

## 🔮 Future Enhancements

The following improvements are planned for future development:

1. **Advanced Multimodal Compliance:** Extend compliance analysis to additional content formats, including documents, advertisements, and social media creatives.
2. **Context-Aware Correction Engine:** Generate more precise alternative wording for detected compliance violations.
3. **Advanced Governance Analytics:** Introduce compliance trends, recurring violation reports, and organization-wide analytics.
4. **Enhanced Asset Upload Experience:** Improve the frontend asset upload and management workflow.
5. **Integration Support:** Connect with external content management and marketing platforms.

---

## 🎯 Project Impact

BrandSentinel aims to help organizations:

- Maintain consistent brand communication.
- Reduce the risk of misleading marketing claims.
- Improve brand guideline enforcement.
- Strengthen accessibility awareness.
- Streamline content review workflows.
- Improve accountability through audit trails.

---

## 👩‍💻 Development Team

**Project:** BrandSentinel  
**Team:** SoloPlayer  
**Developer:** Riya Rani  
**GitHub:** [riyarani6180](https://github.com/riyarani6180)

---

## 📜 License

This project is developed for educational, innovation, and hackathon purposes.

A formal open-source license can be added when the repository's distribution terms are finalized.

---

**BrandSentinel — Making Every Brand Communication Consistent, Compliant, and Trustworthy.** 🛡️