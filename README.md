   # ⚡ DataPure

![DataPure Banner](https://img.shields.io/badge/DataPure-Clean_Your_Data_Instantly-6D28D9?style=for-the-badge&logo=data-analysis)
![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask)
![Vercel Ready](https://img.shields.io/badge/Deployed_on-Vercel-000000?style=for-the-badge&logo=vercel)

**DataPure** is a modern, high-performance web application designed to instantly clean, standardize, and fix messy data files (CSV, Excel, JSON). It features a premium "Dark Glassmorphism" UI and relies exclusively on powerful Python tools like Pandas and SciPy for backend processing.

🚀 **Live Demo:** [https://data-pure.vercel.app/](https://data-pure.vercel.app/)

---

## ✨ Features

*   **🪄 8+ Cleaning Modules:**
    *   Handle missing values (Mean, Median, Mode, Drop).
    *   Find and remove duplicate records.
    *   Auto-standardize Text (Trim whitespace, fix casing).
    *   Standardize Date Formats (Auto-converts to `YYYY-MM-DD`).
    *   Infer Data Types (Fix numbers imported as strings).
    *   Drop Columns based on missing threshold percentage.
    *   Remove Statistical Outliers (via IQR or Z-Score).
*   **🎨 Premium UI / UX:** Beautiful dark glassmorphism design with animated blobbing backgrounds, interactive stat cards, toast notifications, and drag-and-drop file support.
*   **📊 Interactive Cleaning Reports:** Receive a visual timeline of all steps applied to your data, along with a circular "Data Quality Score" meter.
*   **🚀 Serverless Ready:** Architecture fully optimized for Vercel Serverless deployments (uses `/tmp` routing).

---

## 🛠️ Tech Stack

*   **Frontend:** HTML5, Premium CSS (Inter font, Flexbox, CSS Variables), Vanilla JS.
*   **Backend:** Python 3.12, Flask 3.0.x
*   **Data Science Engine:** Pandas 2.2.x, NumPy, SciPy
*   **Infrastructure:** Vercel (Serverless Functions)

---

## 🚀 Quick Start (Local Development)

To run DataPure locally on your machine, follow these steps:

**1. Clone the repository:**
```bash
git clone https://github.com/Manju4599/Data-Pure.git
cd Data-Pure
```

**2. Install Dependencies:**
```bash
pip install -r requirements.txt
```

**3. Run the Flask App:**
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

---

## ☁️ Deployment (Vercel)

This application is securely pre-configured to be deployed natively on Vercel.

1. Connect your Github repository to your **Vercel Dashboard**.
2. Vercel will automatically detect the settings from `vercel.json` and `.python-version`.
3. Under **Environment Variables**, add:
   * **Key:** `SECRET_KEY`
   * **Value:** (Any random secure string, e.g., `datapure-prod-1234`)
4. Click **Deploy**.

---

## 📁 File Structure

```text
Data-Pure/
├── api/
│   └── index.py         # Vercel Serverless Entry Point
├── static/
│   ├── css/style.css    # Premium Glassmorphism styling core
│   └── js/main.js       # Toast notifications & UI interactions
├── templates/
│   ├── base.html        # Underlying layout component
│   ├── index.html       # Landing and cleaner config UI
│   └── results.html     # Real-time report UI
├── utils/
│   ├── file_handler.py    # Temporary storage / cleanup manager
│   └── simple_cleaner.py  # Core Pandas data manipulation logic
├── app.py               # Main Flask Application
├── config.py            # Environment configurations
├── requirements.txt     # Python Dependencies
├── vercel.json          # Deployment configuration properties
└── README.md
```

---
*Created by [Manju4599](https://github.com/Manju4599)*
