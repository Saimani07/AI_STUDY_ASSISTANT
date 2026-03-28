# modules/predictor.py
# ============================================================
# PREDICTION MODULE
# Uses the trained Linear Regression model to predict a
# student's Final_Score and classify performance level.
# ============================================================

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler


def predict_score(model: LinearRegression,
                  scaler: StandardScaler,
                  study_hours: float,
                  attendance: float,
                  previous_marks: float,
                  assignment_score: float) -> dict:
    """
    Predict the Final_Score for a student.

    Parameters
    ----------
    All numeric inputs come from the web form.

    Returns
    -------
    dict with keys: predicted_score, performance_level, confidence_band
    """
    features = np.array([[study_hours, attendance,
                           previous_marks, assignment_score]])

    # Scale using the same scaler fitted during training
    features_scaled = scaler.transform(features)

    raw_score = model.predict(features_scaled)[0]

    # Clamp to [0, 100]
    predicted_score = float(np.clip(raw_score, 0, 100))

    # ── Performance level classification ─────────────────────
    if predicted_score >= 75:
        performance_level = "High"
    elif predicted_score >= 50:
        performance_level = "Medium"
    else:
        performance_level = "Low"

    # ── Simple confidence band (±5 marks) ───────────────────
    confidence_band = (
        round(max(0, predicted_score - 5), 1),
        round(min(100, predicted_score + 5), 1),
    )

    return {
        'predicted_score':   round(predicted_score, 1),
        'performance_level': performance_level,
        'confidence_band':   confidence_band,
    }


# ============================================================
# RECOMMENDATION MODULE
# Provides personalised study advice based on prediction.
# ============================================================

# Thematic advice library
_ADVICE = {
    'study_hours': {
        'low':    ("📚 You're studying fewer than 5 hours/week. "
                   "Aim for at least 6–8 hours to see a significant score improvement."),
        'medium': ("⏱️ Your study hours are decent. Consider spreading sessions "
                   "across the week rather than cramming."),
        'high':   ("🌟 Great study commitment! Make sure to include active recall "
                   "and spaced repetition for maximum retention."),
    },
    'attendance': {
        'low':    ("🚨 Attendance below 70 % is a major risk factor. "
                   "Prioritise attending all upcoming classes."),
        'medium': ("📋 Aim for 90 %+ attendance; every class you miss is "
                   "content you'll need to self-teach later."),
        'high':   ("✅ Excellent attendance! You're building a strong foundation."),
    },
    'previous_marks': {
        'low':    ("🔄 Your baseline marks suggest gaps in fundamentals. "
                   "Revisit core concepts before moving to advanced topics."),
        'medium': ("📈 Solid foundation. Focus on your weak subjects to push "
                   "your overall marks higher."),
        'high':   ("🏆 Strong previous performance – keep the momentum going!"),
    },
    'assignment': {
        'low':    ("📝 Submit all pending assignments. Assignments often count "
                   "toward your final grade and reinforce learning."),
        'medium': ("✍️ Try to improve assignment quality by reviewing feedback "
                   "and revising before submission."),
        'high':   ("💯 Outstanding assignment scores – your consistent effort shows."),
    },
    'overall': {
        'Low':    [
            "🗓️ Create a structured daily study schedule and stick to it.",
            "🤝 Form or join a study group for peer support.",
            "🧑‍🏫 Visit your professor during office hours for personalised help.",
            "🔁 Use the Pomodoro technique (25 min study / 5 min break).",
            "📊 Track your progress weekly to stay motivated.",
        ],
        'Medium': [
            "🎯 Set specific, measurable goals for each study session.",
            "🃏 Use flashcards and active recall to strengthen memory.",
            "📖 Read beyond the syllabus – context deepens understanding.",
            "🧪 Attempt past-year question papers under timed conditions.",
            "💤 Ensure 7–8 hours of sleep; it directly improves retention.",
        ],
        'High':   [
            "🚀 Challenge yourself with advanced problems and research topics.",
            "🏅 Consider tutoring peers – teaching is the best way to learn.",
            "📚 Explore elective subjects that complement your strengths.",
            "🌐 Look for internships or projects to apply your knowledge.",
            "🥇 Maintain balance – physical health boosts cognitive performance.",
        ],
    },
}


def generate_recommendations(study_hours: float,
                              attendance: float,
                              previous_marks: float,
                              assignment_score: float,
                              performance_level: str) -> dict:
    """
    Return personalised recommendations based on student inputs
    and predicted performance level.
    """

    def _tier(value, low_thresh, high_thresh):
        if value < low_thresh:  return 'low'
        if value < high_thresh: return 'medium'
        return 'high'

    tips = {
        'study_hours':    _ADVICE['study_hours'][_tier(study_hours, 5, 8)],
        'attendance':     _ADVICE['attendance'][_tier(attendance, 70, 90)],
        'previous_marks': _ADVICE['previous_marks'][_tier(previous_marks, 50, 75)],
        'assignment':     _ADVICE['assignment'][_tier(assignment_score, 50, 75)],
        'overall':        _ADVICE['overall'].get(performance_level,
                                                  _ADVICE['overall']['Medium']),
    }
    return tips
