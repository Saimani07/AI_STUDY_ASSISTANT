# modules/study_plan.py
# ============================================================
# SMART STUDY PLAN GENERATOR
# Generates a personalised 7-day study plan based on the
# student's predicted score, weak areas, and study hours.
#
# Logic:
#   Low score    → heavy revision, basics, short sessions
#   Medium score → balanced theory + practice
#   High score   → advanced problems, mock tests, peer teaching
# ============================================================


# ── Subject / topic pool ──────────────────────────────────────
# Each bucket maps a performance tier to weighted topic focus.
_TOPIC_FOCUS = {
    'Low': {
        'morning':   'Revise fundamental concepts & definitions',
        'afternoon': 'Work through solved examples step-by-step',
        'evening':   'Re-read class notes and textbook summaries',
    },
    'Medium': {
        'morning':   'Review key theories and formulas',
        'afternoon': 'Solve practice problems (medium difficulty)',
        'evening':   'Attempt past exam questions',
    },
    'High': {
        'morning':   'Tackle advanced / challenge problems',
        'afternoon': 'Work on project or research extension topics',
        'evening':   'Take a timed mock test or quiz yourself',
    },
}

# Day-of-week activity themes
_DAY_THEMES = {
    'Monday':    '📖 New Concepts & Theory',
    'Tuesday':   '✏️  Problem Solving & Practice',
    'Wednesday': '🔄 Revision & Weak Area Focus',
    'Thursday':  '📝 Assignment & Note Making',
    'Friday':    '🧪 Mock Test / Self-Quiz',
    'Saturday':  '🔍 Deep Dive into Difficult Topics',
    'Sunday':    '🌿 Light Review & Rest Day',
}

# Weak-area identification thresholds
_WEAK_AREA_RULES = [
    ('study_hours',      lambda v: v < 5,  'Increase daily study time'),
    ('attendance',       lambda v: v < 70, 'Improve class attendance'),
    ('previous_marks',   lambda v: v < 55, 'Strengthen subject fundamentals'),
    ('assignment_score', lambda v: v < 55, 'Complete and review all assignments'),
]


def _identify_weak_areas(study_hours: float,
                          attendance: float,
                          previous_marks: float,
                          assignment_score: float) -> list[str]:
    """
    Return a list of weak-area strings derived from student inputs.
    These are injected into the plan as targeted focus points.
    """
    weak = []
    for _, check, label in _WEAK_AREA_RULES:
        value = {
            'Increase daily study time':             study_hours,
            'Improve class attendance':              attendance,
            'Strengthen subject fundamentals':       previous_marks,
            'Complete and review all assignments':   assignment_score,
        }[label]
        if check(value):
            weak.append(label)
    return weak if weak else ['Maintain current performance level']


def _daily_hours(performance_level: str, user_hours: float) -> dict[str, float]:
    """
    Calculate suggested daily session durations (hours) based on
    the user's available study time and performance level.
    """
    # Amplify hours slightly for low performers, cap for high performers
    multipliers = {'Low': 1.3, 'Medium': 1.0, 'High': 0.85}
    total = min(user_hours * multipliers.get(performance_level, 1.0), 12)

    # Sunday is always lighter
    return {
        'Monday':    round(total * 1.0, 1),
        'Tuesday':   round(total * 1.0, 1),
        'Wednesday': round(total * 1.1, 1),
        'Thursday':  round(total * 0.9, 1),
        'Friday':    round(total * 1.1, 1),
        'Saturday':  round(total * 1.2, 1),
        'Sunday':    round(total * 0.4, 1),
    }


def generate_study_plan(predicted_score: float,
                         performance_level: str,
                         study_hours: float,
                         attendance: float,
                         previous_marks: float,
                         assignment_score: float) -> dict:
    """
    Build and return a complete 7-day study plan.

    Returns
    -------
    {
      'performance_level': str,
      'predicted_score':   float,
      'weak_areas':        [str, ...],
      'strategy':          str,
      'daily_plan':        [
          {
            'day':       str,
            'theme':     str,
            'hours':     float,
            'sessions':  {'morning': str, 'afternoon': str, 'evening': str},
            'focus':     str,       # weak-area injection (rotates)
            'tip':       str,
          }, ...
      ]
    }
    """
    weak_areas = _identify_weak_areas(study_hours, attendance,
                                       previous_marks, assignment_score)
    hours_map  = _daily_hours(performance_level, study_hours)
    focus_map  = _TOPIC_FOCUS[performance_level]

    # Strategy banner shown at top of plan
    strategy_text = {
        'Low':    ('🔴 Focus Strategy: Back-to-basics. Prioritise understanding '
                   'core concepts before anything else. Short, consistent sessions '
                   'beat long irregular ones.'),
        'Medium': ('🟡 Focus Strategy: Balanced approach. Combine revision with '
                   'fresh practice. Identify and patch weak spots systematically.'),
        'High':   ('🟢 Focus Strategy: Mastery mode. Push into advanced material, '
                   'mock exams, and peer discussion to cement top performance.'),
    }

    # Daily motivational tips (rotates through days)
    tips = [
        '💡 Start each session by reviewing yesterday\'s key points.',
        '⏱️ Use the Pomodoro method: 25 min focus, 5 min break.',
        '📓 Write brief notes in your own words after every topic.',
        '🤝 Explain what you learned to a friend — it cements memory.',
        '🧘 Take a 10-min walk before studying to boost concentration.',
        '🎯 Set one specific goal before you open your books.',
        '😴 Sleep 7–8 hours — memory consolidation happens overnight.',
    ]

    days = list(_DAY_THEMES.keys())
    daily_plan = []

    for i, day in enumerate(days):
        # Rotate weak-area focus across the week
        focus_label = weak_areas[i % len(weak_areas)]

        daily_plan.append({
            'day':      day,
            'theme':    _DAY_THEMES[day],
            'hours':    hours_map[day],
            'sessions': {
                'morning':   focus_map['morning'],
                'afternoon': focus_map['afternoon'],
                'evening':   focus_map['evening'],
            },
            'focus':    f'🎯 Weak area: {focus_label}',
            'tip':      tips[i],
        })

    return {
        'performance_level': performance_level,
        'predicted_score':   predicted_score,
        'weak_areas':        weak_areas,
        'strategy':          strategy_text[performance_level],
        'daily_plan':        daily_plan,
    }
