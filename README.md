# AI Study Assistant

## 🚀 Live Demo
👉 https://ai-study-assistant-pq5w.onrender.com
# 🎓 AI-Powered Study Assistant with Performance Prediction

A complete end-to-end AI web application built with **Flask**, **NLTK**, and **scikit-learn** that:

- Summarises your study material using **TextRank NLP**
- Generates **practice questions** via POS-tag rule-based NLP
- **Predicts your exam score** using Linear Regression
- Gives **personalised study recommendations**

---

## 📁 Folder Structure

```
study_assistant/
│
├── app.py                        ← Flask entry point (main server)
│
├── modules/
│   ├── __init__.py
│   ├── preprocessor.py           ← Text cleaning & tokenisation
│   ├── summarizer.py             ← TextRank summarisation
│   ├── question_generator.py     ← NLP question generation
│   ├── ml_model.py               ← Linear Regression training
│   └── predictor.py              ← Prediction + recommendations
│
├── templates/
│   └── index.html                ← Single-page web UI
│
├── data/
│   └── student_performance.csv   ← Sample dataset (50 rows)
│
├── models/                       ← Auto-created: saved model files
│   ├── lr_model.pkl
│   └── scaler.pkl
│
└── requirements.txt
```

---

## 🚀 Step-by-Step Setup

### Step 1 – Prerequisites

Make sure you have **Python 3.10+** installed:
```bash
python --version
```

### Step 2 – Create & activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 – Install dependencies

```bash
pip install -r requirements.txt
```

This installs:
| Package | Used for |
|---------|----------|
| `flask` | Web server & routing |
| `nltk` | Tokenisation, POS tagging, stopwords |
| `scikit-learn` | Linear Regression, scaling, metrics |
| `pandas` | Dataset loading |
| `numpy` | Numerical operations |
| `PyMuPDF` | PDF text extraction |

### Step 4 – Download NLTK data (one-time)

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger'); nltk.download('punkt_tab')"
```

### Step 5 – Run the application

```bash
python app.py
```

You will see:
```
🔧 Loading / training ML model …
✅ Model ready  |  R² = 0.9996
 * Running on http://0.0.0.0:5000
```

### Step 6 – Open in your browser

Go to: **http://localhost:5000**

---

## 🖥️ How to Use the App

### Tab 1 – Study Material
1. Drag-and-drop a **PDF** or **.txt** file, OR paste text directly
2. Click **⚡ Analyse Text**

### Tab 2 – Analysis
- View the **AI summary** (TextRank, ~30 % of original)
- Review **auto-generated practice questions**
- Click → **Predict Performance**

### Tab 3 – Performance
1. Enter your **study hours/week**, **attendance %**, **previous marks**, and **assignment score**
2. Click **🔮 Predict My Score**
3. See:
   - Predicted final score (0–100)
   - Performance level: **Low / Medium / High**
   - Confidence range (±5)
   - Personalised recommendations

---

## 🧠 How Each Module Works

### `preprocessor.py`
- Strips noise (extra whitespace, non-ASCII)
- Splits into sentences (`sent_tokenize`)
- Tokenises words, removes stopwords

### `summarizer.py`
- Implements **TextRank**: scores each sentence by word frequency × IDF weight
- Selects the top-scoring 30 % of sentences, restored in original order

### `question_generator.py`
- Uses **NLTK POS tagging** to identify nouns and verbs
- Applies 5 rule templates:
  - *What is X?* · *How does X work?* · *Why is X considered Y?* · *Define X.* · *Fill in the blank*

### `ml_model.py`
- Loads `student_performance.csv` (50 labelled samples)
- Features: Study_Hours, Attendance, Previous_Marks, Assignment_Score
- Target: Final_Score
- Pipeline: StandardScaler → LinearRegression (R² ≈ 0.9996)

### `predictor.py`
- Takes 4 numeric inputs, scales them, returns predicted score
- Classifies: **High** (≥ 75) · **Medium** (≥ 50) · **Low** (< 50)
- Maps inputs to personalised advice from a curated recommendation library

---

## 📊 Sample Dataset Columns

| Column | Range | Description |
|--------|-------|-------------|
| Study_Hours | 1–10 | Weekly study hours |
| Attendance | 48–100 | Class attendance % |
| Previous_Marks | 33–88 | Last exam score |
| Assignment_Score | 38–90 | Average assignment % |
| Final_Score | 28–92 | **Target variable** |

---

## ❓ Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: nltk` | Run `pip install nltk` |
| `LookupError: punkt` | Run the NLTK download command in Step 4 |
| Port 5000 in use | Edit `app.py` → change `port=5000` to `port=5001` |
| PDF not extracting | Ensure `PyMuPDF` is installed; text-only PDFs work best |

---

## 🛠️ Tech Stack

```
Frontend  : HTML5 · CSS3 · Vanilla JS  (served by Flask)
Backend   : Python 3.10+ · Flask 3.x
NLP       : NLTK (tokenisation, POS tagging, stopwords)
ML        : scikit-learn LinearRegression + StandardScaler
Data      : pandas · numpy
PDF       : PyMuPDF (fitz)
```

---

*Built as a beginner-friendly, end-to-end AI project demonstrating NLP + ML integration.*
