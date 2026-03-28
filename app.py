# app.py  (UPDATED – v2)
# ============================================================
# MAIN FLASK APPLICATION
# Entry point – wires all modules together and serves the UI.
#
# NEW in v2:
#   • /api/study-plan  → Smart Study Plan Generator
#   • /api/graph       → Performance Graph (matplotlib → base64)
#   • /api/chat        → Rule-based Chatbot
# ============================================================

import os
import sys

# Ensure project root is on PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify

# ── Existing modules ─────────────────────────────────────────
from modules.preprocessor      import preprocess, extract_text_from_pdf
from modules.summarizer         import summarize_by_ratio
from modules.question_generator import generate_questions
from modules.ml_model           import train_model
from modules.predictor          import predict_score, generate_recommendations

# ── NEW modules (v2) ─────────────────────────────────────────
from modules.study_plan      import generate_study_plan
from modules.graph_generator import generate_performance_graph
from modules.chatbot         import chatbot_reply

# ── App setup ────────────────────────────────────────────────
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB upload limit

# Train / load the ML model once at startup
print("Loading / training ML model ...")
MODEL, SCALER, METRICS = train_model()
print(f"Model ready  |  R2 = {METRICS.get('r2', 'cached')}")


# ════════════════════════════════════════════════════════════
# EXISTING ROUTES (unchanged)
# ════════════════════════════════════════════════════════════

@app.route('/')
def index():
    """Serve the main single-page interface."""
    return render_template('index.html')


@app.route('/api/process-text', methods=['POST'])
def process_text():
    """
    Accepts either raw text (JSON) or a PDF file (multipart).
    Returns summarised notes and generated questions.
    """
    try:
        raw_text = ''
        if 'file' in request.files:
            f = request.files['file']
            if f.filename.lower().endswith('.pdf'):
                raw_text = extract_text_from_pdf(f.read())
            else:
                raw_text = f.read().decode('utf-8', errors='ignore')
        elif request.is_json:
            raw_text = request.json.get('text', '')
        else:
            raw_text = request.form.get('text', '')

        if not raw_text.strip():
            return jsonify({'error': 'No text provided.'}), 400

        processed = preprocess(raw_text)
        text      = processed['cleaned_text']
        summary   = summarize_by_ratio(text, ratio=0.30)
        questions = generate_questions(text, num_questions=8)

        return jsonify({
            'summary':        summary,
            'questions':      questions,
            'word_count':     len(processed['words']),
            'sentence_count': len(processed['sentences']),
        })

    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Accepts student stats (JSON).
    Returns predicted score, performance level, and recommendations.
    """
    try:
        data = request.json or {}

        study_hours      = float(data.get('study_hours', 0))
        attendance       = float(data.get('attendance', 0))
        previous_marks   = float(data.get('previous_marks', 0))
        assignment_score = float(data.get('assignment_score', 0))

        errors = []
        if not (0 <= study_hours <= 24):
            errors.append('study_hours must be 0-24')
        if not (0 <= attendance <= 100):
            errors.append('attendance must be 0-100')
        if not (0 <= previous_marks <= 100):
            errors.append('previous_marks must be 0-100')
        if not (0 <= assignment_score <= 100):
            errors.append('assignment_score must be 0-100')
        if errors:
            return jsonify({'error': '\n'.join(errors)}), 400

        result = predict_score(MODEL, SCALER,
                               study_hours, attendance,
                               previous_marks, assignment_score)

        recs = generate_recommendations(
            study_hours, attendance, previous_marks,
            assignment_score, result['performance_level']
        )

        return jsonify({**result, 'recommendations': recs})

    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/model-info', methods=['GET'])
def model_info():
    """Return model training metrics and feature importances."""
    from modules.ml_model import get_feature_importance
    return jsonify({
        'metrics':            METRICS,
        'feature_importance': get_feature_importance(MODEL),
    })


# ════════════════════════════════════════════════════════════
# NEW ROUTES – v2
# ════════════════════════════════════════════════════════════

@app.route('/api/study-plan', methods=['POST'])
def study_plan():
    """
    NEW – Smart Study Plan Generator
    Accepts student stats + predicted_score + performance_level.
    Returns a 7-day daily study plan dict.
    """
    try:
        data = request.json or {}

        study_hours       = float(data.get('study_hours', 5))
        attendance        = float(data.get('attendance', 75))
        previous_marks    = float(data.get('previous_marks', 60))
        assignment_score  = float(data.get('assignment_score', 60))
        predicted_score   = float(data.get('predicted_score', 60))
        performance_level = data.get('performance_level', 'Medium')

        plan = generate_study_plan(
            predicted_score   = predicted_score,
            performance_level = performance_level,
            study_hours       = study_hours,
            attendance        = attendance,
            previous_marks    = previous_marks,
            assignment_score  = assignment_score,
        )

        return jsonify(plan)

    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/graph', methods=['POST'])
def performance_graph():
    """
    NEW – Performance Graph
    Generates a matplotlib PNG showing predicted score vs study hours.
    Returns { 'image': 'data:image/png;base64,...' }
    """
    try:
        data = request.json or {}

        study_hours      = float(data.get('study_hours', 5))
        attendance       = float(data.get('attendance', 75))
        previous_marks   = float(data.get('previous_marks', 60))
        assignment_score = float(data.get('assignment_score', 60))
        predicted_score  = float(data.get('predicted_score', 60))

        image_b64 = generate_performance_graph(
            model                = MODEL,
            scaler               = SCALER,
            user_study_hours     = study_hours,
            user_attendance      = attendance,
            user_prev_marks      = previous_marks,
            user_assignment      = assignment_score,
            user_predicted_score = predicted_score,
        )

        return jsonify({'image': image_b64})

    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    NEW – Rule-based Study Chatbot
    Accepts { 'message': '...' } and returns { 'reply': '...' }.
    """
    try:
        data    = request.json or {}
        message = str(data.get('message', '')).strip()

        if not message:
            return jsonify({'reply': 'Please type a question!'}), 400

        reply = chatbot_reply(message)
        return jsonify({'reply': reply})

    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


# ── Run ───────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
