# modules/chatbot.py
# ============================================================
# RULE-BASED STUDY CHATBOT
# A keyword-matching chatbot that answers common student
# questions without any external API calls.
#
# How it works:
#   1. Lowercase the user message.
#   2. Check each rule's keywords against the message.
#   3. Return the first matching response.
#   4. If nothing matches, return the fallback reply.
# ============================================================

import random
import re

# ── Knowledge base ────────────────────────────────────────────
# Each entry: (list_of_trigger_keywords, list_of_possible_responses)
# The bot picks one response at random when a rule fires,
# so repeated questions feel less robotic.

_RULES: list[tuple[list[str], list[str]]] = [

    # ── Greetings ─────────────────────────────────────────────
    (['hello', 'hi', 'hey', 'howdy', 'greetings'], [
        "Hello! 👋 I'm your AI Study Assistant. Ask me anything about studying!",
        "Hi there! Ready to help you ace your exams. What's on your mind?",
        "Hey! How can I help you study smarter today?",
    ]),

    # ── Farewells ─────────────────────────────────────────────
    (['bye', 'goodbye', 'see you', 'later', 'exit'], [
        "Goodbye! Keep studying hard — you've got this! 💪",
        "See you! Remember: consistency beats cramming. Good luck!",
    ]),

    # ── Thanks ────────────────────────────────────────────────
    (['thank', 'thanks', 'thx', 'appreciate'], [
        "You're welcome! Happy to help. 😊",
        "Anytime! Keep up the great work!",
    ]),

    # ── Study effectively ─────────────────────────────────────
    (['study effectively', 'study better', 'study smart', 'how to study',
      'study tips', 'best way to study'], [
        ("📚 Here are proven study strategies:\n"
         "1. Make a schedule and stick to it\n"
         "2. Use active recall — test yourself instead of re-reading\n"
         "3. Spaced repetition: review material after 1 day, 3 days, 1 week\n"
         "4. Take short breaks (Pomodoro: 25 min study / 5 min break)\n"
         "5. Teach the concept to someone else"),
    ]),

    # ── Concentration / focus ─────────────────────────────────
    (['concentrate', 'focus', 'distracted', 'distraction', 'attention'], [
        ("🎯 Tips to improve focus:\n"
         "• Put your phone on silent or in another room\n"
         "• Study in a clean, quiet environment\n"
         "• Start with your hardest subject when energy is highest\n"
         "• Use background white noise or lo-fi music\n"
         "• Set a clear goal for each session (e.g. 'finish chapter 3')"),
    ]),

    # ── Memory / retention ────────────────────────────────────
    (['remember', 'memorize', 'memory', 'retention', 'forget', 'recall'], [
        ("🧠 Memory improvement techniques:\n"
         "• Use mnemonics and acronyms for lists\n"
         "• Visualise concepts as diagrams or mind-maps\n"
         "• Practice retrieval: close the book and write what you remember\n"
         "• Sleep 7–8 hours — memory consolidates during deep sleep\n"
         "• Review notes within 24 hours of a lecture"),
    ]),

    # ── Motivation ────────────────────────────────────────────
    (['motivat', 'inspire', 'lazy', 'procrastinat', 'not studying',
      'cant study', "can't study", 'unmotivated'], [
        ("💪 Staying motivated:\n"
         "• Break big goals into tiny daily tasks — small wins build momentum\n"
         "• Reward yourself after completing a session (snack, walk, game)\n"
         "• Visualise your goal: why does this exam matter to you?\n"
         "• Study with a friend or join a study group\n"
         "• Track your progress — seeing improvement is its own reward"),
    ]),

    # ── Time management ───────────────────────────────────────
    (['time management', 'manage time', 'schedule', 'timetable',
      'plan my study', 'study plan'], [
        ("📅 Time management for students:\n"
         "• Block fixed study hours each day (treat them like class time)\n"
         "• Prioritise topics by difficulty × exam weightage\n"
         "• Use this app's Study Plan Generator for a personalised schedule!\n"
         "• Review and adjust your plan weekly\n"
         "• Leave buffer days for revision before exams"),
    ]),

    # ── Exam preparation ─────────────────────────────────────
    (['exam', 'test', 'preparation', 'prepare', 'revision', 'revise'], [
        ("🎓 Exam preparation checklist:\n"
         "✅ Start revision at least 2 weeks before the exam\n"
         "✅ Solve previous years' question papers under timed conditions\n"
         "✅ Make a 1-page cheat sheet of key formulas / concepts per subject\n"
         "✅ Identify and fix weak areas early (use this app's prediction!)\n"
         "✅ Get 8 hours of sleep the night before — don't cram"),
    ]),

    # ── Math / problem solving ────────────────────────────────
    (['math', 'maths', 'mathematics', 'problem solving', 'formula',
      'equation', 'calculation'], [
        ("➕ Tips for maths / problem-solving subjects:\n"
         "• Practice daily — maths is a skill, not just knowledge\n"
         "• Always understand the 'why' behind a formula\n"
         "• Write out each step clearly; don't skip lines\n"
         "• When stuck, look at a solved example then close it and try again\n"
         "• Do at least 5 varied problems per concept"),
    ]),

    # ── Reading / theory subjects ─────────────────────────────
    (['read', 'reading', 'theory', 'textbook', 'notes', 'note taking'], [
        ("📖 Reading & note-taking strategies:\n"
         "• Use the SQ3R method: Survey → Question → Read → Recite → Review\n"
         "• Write notes in your own words (don't just copy)\n"
         "• Highlight sparingly — only the single most important phrase per para\n"
         "• Create mind-maps to connect concepts visually\n"
         "• Use this app to auto-summarise your notes instantly!"),
    ]),

    # ── Sleep ─────────────────────────────────────────────────
    (['sleep', 'tired', 'fatigue', 'rest', 'insomnia'], [
        ("😴 Sleep is non-negotiable for learning:\n"
         "• Aim for 7–9 hours every night\n"
         "• Avoid screens 30 min before bed\n"
         "• A consistent sleep schedule improves deep sleep quality\n"
         "• A 20-min afternoon nap can boost afternoon study performance\n"
         "• Never sacrifice sleep to study — you'll forget it all anyway"),
    ]),

    # ── Stress / anxiety ─────────────────────────────────────
    (['stress', 'anxiety', 'anxious', 'nervous', 'worried', 'overwhelmed',
      'pressure', 'panic'], [
        ("🌿 Managing exam stress:\n"
         "• Take slow, deep breaths when anxious (4 sec in / 4 sec out)\n"
         "• Break your workload into very small tasks\n"
         "• Exercise for 20 minutes — it's as effective as a mild anxiolytic\n"
         "• Talk to a friend, family member, or counsellor\n"
         "• Remember: one exam does not define your future"),
    ]),

    # ── Attendance ────────────────────────────────────────────
    (['attendance', 'class', 'lecture', 'skip', 'miss'], [
        ("📋 Why attendance matters:\n"
         "• Research shows >85% attendance strongly correlates with higher scores\n"
         "• Professors often hint at exam topics during lectures\n"
         "• Class discussions clarify doubts faster than solo study\n"
         "• Missing class creates gaps that take 3× longer to self-study"),
    ]),

    # ── Group study ───────────────────────────────────────────
    (['group study', 'study group', 'study with friends', 'peer'], [
        ("👥 Making group study work:\n"
         "• Keep groups small (3–4 people) for focus\n"
         "• Assign topics: each person teaches one section\n"
         "• Quiz each other — retrieval practice in groups is powerful\n"
         "• Set a clear agenda and time limit before you start\n"
         "• Avoid turning it into a social session!"),
    ]),

    # ── Performance prediction ────────────────────────────────
    (['predict', 'score', 'performance', 'marks', 'grade', 'result'], [
        ("🔮 About the Performance Predictor:\n"
         "Enter your Study Hours, Attendance, Previous Marks, and Assignment Score "
         "in the Performance tab. The ML model (Linear Regression, R²≈0.9996) "
         "will predict your likely final score and classify it as Low / Medium / High.\n"
         "Use the Study Plan Generator to act on the prediction!"),
    ]),

    # ── App features ──────────────────────────────────────────
    (['what can you do', 'features', 'help', 'how does this work',
      'what is this app', 'app features'], [
        ("🚀 This AI Study Assistant can:\n"
         "📄 Tab 1 — Upload notes (PDF/TXT) → get an instant AI summary + practice questions\n"
         "📊 Tab 2 — View NLP analysis results\n"
         "🔮 Tab 3 — Enter your stats → predict exam score + get a 7-day study plan + see a performance graph\n"
         "💬 This chatbot — ask any study-related question!\n"
         "Just type your question below and I'll answer."),
    ]),
]

# ── Fallback responses ────────────────────────────────────────
_FALLBACK = [
    ("🤔 I don't have a specific answer for that. Try asking about:\n"
     "• How to study effectively\n"
     "• Time management tips\n"
     "• Exam preparation\n"
     "• Memory techniques\n"
     "• Managing stress"),
    ("❓ I'm not sure about that one. You can ask me things like:\n"
     "'How do I improve my concentration?' or 'Tips for memorizing better'"),
]


# ── Public API ────────────────────────────────────────────────

def chatbot_reply(user_message: str) -> str:
    """
    Process a user message and return the chatbot's reply string.

    Matching is case-insensitive keyword search.
    Multi-word keywords are matched as substrings.
    """
    msg = user_message.lower().strip()

    # Remove punctuation for cleaner matching
    msg_clean = re.sub(r'[^\w\s]', ' ', msg)

    for keywords, responses in _RULES:
        for kw in keywords:
            # Support multi-word keywords (substring match)
            if kw in msg_clean or kw in msg:
                return random.choice(responses)

    return random.choice(_FALLBACK)
