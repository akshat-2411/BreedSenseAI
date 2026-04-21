# 🐄 BreedSense AI — Intelligent Cattle Breed Recognition

> A high-precision, deep learning–powered web platform for identifying Indian cattle breeds in real time. Designed for farmers, veterinarians, and livestock management agencies.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Architecture](#project-architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Running the App](#running-the-app)
- [API Reference](#api-reference)
- [Admin Panel](#admin-panel)
- [Supported Breeds](#supported-breeds)
- [Configuration](#configuration)
- [License](#license)

---

## Overview

**BreedSense AI** is a full-stack Flask web application that uses a fine-tuned **ResNet-18 deep learning model** to classify images of cattle into their corresponding indigenous Indian breeds. The system provides not only a breed prediction and confidence score, but also a **Grad-CAM visual heatmap** to explain *where* in the image the model focused its attention — making the AI decision interpretable and trustworthy.

All predictions are securely persisted in a **MongoDB** database, enabling full audit trails, user-level history, and admin-level analytics dashboards.

---

## Key Features

| Feature | Description |
|---|---|
| 🧠 **Deep Learning Inference** | ResNet-18 model fine-tuned on 50 Indian cattle breed classes |
| 🗺️ **Grad-CAM Explainability** | Visual activation heatmap overlaid on the input image |
| 📄 **PDF Report Generation** | Downloadable professional PDF reports per prediction (via `reportlab`) |
| 🔊 **Voice Accessibility** | Web Speech API announces breed results aloud; supports mute/unmute with `localStorage` persistence |
| 👤 **User Authentication** | Full register/login/logout via Flask-Login with bcrypt password hashing |
| 🛡️ **Role-Based Access Control** | `user` and `admin` roles with protected routes via `@admin_required` decorator |
| 📊 **Admin Analytics Dashboard** | Real-time charts (Chart.js) for daily usage trends and breed distribution |
| 📜 **Prediction History** | Per-user paginated history with thumbnails and PDF download links |
| 🔒 **Secure File Handling** | UUID-prefixed filenames, 16 MB upload limit, extension whitelisting |

---

## Tech Stack

### Backend
- **Python 3.12** — Runtime
- **Flask 3.1.0** — Web framework (Application Factory pattern)
- **PyTorch 2.6.0 + Torchvision 0.21.0** — Deep learning inference
- **pymongo 4.11.3** — MongoDB ODM
- **Flask-Login 0.6.3** — Session management & authentication
- **bcrypt 4.2.1** — Password hashing
- **reportlab 4.4.10** — In-memory PDF generation
- **matplotlib 3.10.0 + numpy 2.2.3** — Grad-CAM heatmap rendering
- **Pillow 11.1.0** — Image preprocessing
- **Gunicorn 23.0.0** — Production WSGI server
- **Flask-CORS 5.0.1** — Cross-Origin Resource Sharing
- **python-dotenv 1.0.1** — Environment variable management

### Frontend
- **Jinja2** — Server-side templating
- **TailwindCSS v3** (CDN) — Utility-first styling
- **Chart.js** (CDN) — Admin dashboard charts
- **Lucide Icons** (CDN) — Consistent icon set
- **Web Speech API** — Browser-native voice synthesis

### Database
- **MongoDB** — Predictions collection + Users collection

---

## Project Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Browser Client                        │
│  (TailwindCSS UI · Chart.js · Web Speech API · Lucide)     │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP / REST
┌────────────────────────▼────────────────────────────────────┐
│                    Flask Application                        │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │  main_   │  │  auth_   │  │ predict_ │  │  admin_   │  │
│  │  routes  │  │  routes  │  │  routes  │  │  routes   │  │
│  └──────────┘  └──────────┘  └──────────┘  └───────────┘  │
│                                                             │
│  ┌────────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │ PredictionSvc  │  │  GradCAM    │  │  ReportService  │ │
│  │  (ResNet-18)   │  │  Service    │  │  (reportlab)    │ │
│  └────────────────┘  └─────────────┘  └─────────────────┘ │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │               AnalyticsService (MongoDB Aggregations)│  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────▼───────────────┐
         │           MongoDB             │
         │   cattle_breed_db             │
         │   ├── users                   │
         │   └── predictions             │
         └───────────────────────────────┘
```

---

## Project Structure

```
Project/
├── app.py                      # Application factory & entry point
├── config.py                   # Dev/Prod configuration classes
├── requirements.txt            # Python dependencies
├── make_admin.py               # CLI utility to promote a user to admin
├── breed_info.json             # Breed metadata (origin, milk yield, purpose)
├── inference.py                # Standalone inference script
│
├── models/
│   ├── user.py                 # User model (Flask-Login compatible)
│   ├── classes.txt             # 50 breed class labels (one per line)
│   └── weights/
│       └── best_model.pth      # Trained ResNet-18 weights
│
├── routes/
│   ├── main_routes.py          # Public pages (/, /upload, /history, /about)
│   ├── auth_routes.py          # /auth/login, /auth/register, /auth/logout
│   ├── predict_routes.py       # POST /api/predict, GET /api/prediction/download/<id>
│   └── admin_routes.py         # /admin/* with RBAC; includes /admin/api/stats
│
├── services/
│   ├── prediction_service.py   # ResNet-18 inference wrapper (lazy singleton)
│   ├── gradcam_service.py      # Grad-CAM heatmap generation & overlay
│   ├── report_service.py       # PDF report generation (reportlab, in-memory)
│   └── analytics_service.py   # MongoDB aggregation pipelines for dashboard
│
├── utils/
│   └── helpers.py              # @admin_required decorator, load_breed_info()
│
├── static/
│   ├── uploads/                # User-uploaded cattle images
│   ├── heatmaps/               # Generated Grad-CAM overlay images
│   └── js/
│       └── speech.js           # Web Speech API voice synthesis utility
│
└── templates/
    ├── base.html               # Shared layout (navbar, footer)
    ├── index.html              # Landing / home page
    ├── upload.html             # Image upload & prediction UI
    ├── history.html            # Per-user prediction history
    ├── about.html              # About page with team section
    ├── auth/
    │   ├── login.html
    │   └── register.html
    └── admin/
        └── dashboard.html      # Admin panel (overview, users, predictions, charts)
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- MongoDB running locally (`mongodb://localhost:27017/`) or a remote URI
- `pip` and `venv`

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/akshat-2411/breedsense-ai.git
cd breedsense-ai

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```env
FLASK_ENV=development
SECRET_KEY=your-very-secret-key-here
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=cattle_breed_db
MODEL_PATH=models/weights/best_model.pth
NUM_CLASSES=50
```

### Running the App

```bash
python app.py
```

The application will be available at **http://127.0.0.1:5000**.

For production, use Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

---

## API Reference

All prediction endpoints are under the `/api` prefix and require authentication (`@login_required`).

### `POST /api/predict`

Submit an image for breed classification.

**Request:** `multipart/form-data` with field `image` (JPEG, PNG, WEBP — max 16 MB)

**Response:**
```json
{
  "breed": "Gir",
  "confidence": 94.73,
  "heatmap_url": "/static/heatmaps/gradcam_abc123.png",
  "prediction_id": "6629a0f2e13a4b...",
  "info": {
    "origin": "Gujarat, India",
    "milk_yield": "1200–1800 litres/lactation",
    "purpose": "Dairy",
    "physical_characteristics": "..."
  }
}
```

---

### `GET /api/prediction/download/<prediction_id>`

Download a **PDF report** for a given prediction.

- Requires ownership (or `admin` role)
- Returns: `application/pdf` attachment named `BreedSense_Report_<id>.pdf`

---

### `GET /admin/api/stats`

Returns dashboard analytics data (admin only).

**Response:**
```json
{
  "total_predictions": 148,
  "top_breed": "Gir",
  "breed_distribution": {
    "labels": ["Gir", "Sahiwal", "Hallikar", "..."],
    "values": [42, 31, 18, "..."]
  },
  "daily_usage": {
    "labels": ["Apr 01", "Apr 02", "..."],
    "values": [5, 12, "..."]
  }
}
```

---

## Admin Panel

The admin panel is accessible at `/admin/` for users with `role = "admin"`.

To promote a registered user to admin from the CLI:

```bash
python make_admin.py user@example.com
```

### Admin Panel Sections

| Section | Description |
|---|---|
| **Overview** | Stats cards (Total Users, Total Predictions, System Status) + Grad-CAM history table |
| **User Management** | Full registered user list with roles and join dates |
| **All Predictions** | Complete prediction log with delete functionality (confirmation modal) |
| **Charts** | Line chart (daily usage, 30 days) + Doughnut chart (breed distribution) |

---

## Supported Breeds

The model is trained across **50 Indian cattle breed classes**. The five primary breeds featured in the UI are:

| Breed | Region of Origin | Primary Purpose |
|---|---|---|
| **Gir** | Gujarat | Dairy |
| **Sahiwal** | Punjab (Pakistan/India) | Dairy |
| **Red Sindhi** | Sindh, Pakistan | Dairy |
| **Tharparkar** | Rajasthan | Dual-purpose |
| **Kankrej** | Gujarat/Rajasthan | Draft & Dairy |

Full class list is located in `models/classes.txt`.

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `dev-secret-key` | Flask session signing key |
| `MONGO_URI` | `mongodb://localhost:27017/` | MongoDB connection string |
| `MONGO_DB_NAME` | `cattle_breed_db` | Target database name |
| `MODEL_PATH` | `models/weights/best_model.pth` | Path to PyTorch weights file |
| `NUM_CLASSES` | `50` | Number of output classes |
| `FLASK_ENV` | `development` | `development` or `production` |

Max upload size is hardcoded to **16 MB** in `config.py`. Allowed file types: `png`, `jpg`, `jpeg`, `webp`.

---

## License

This project is licensed under the terms of the GNU General Public License v3.0 (GPL-3.0) file included in this repository.

