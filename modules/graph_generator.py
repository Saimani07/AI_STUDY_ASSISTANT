# modules/graph_generator.py
# ============================================================
# PERFORMANCE GRAPH MODULE
# Generates a matplotlib chart showing how predicted score
# varies with study hours (given fixed other parameters),
# and marks the user's own position on the curve.
#
# The chart is encoded as a base64 PNG string so Flask can
# embed it directly in a JSON response — no file I/O needed.
# ============================================================

import io
import base64
import numpy as np
import matplotlib
matplotlib.use('Agg')          # non-interactive backend (no display needed)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler


def generate_performance_graph(model: LinearRegression,
                                scaler: StandardScaler,
                                user_study_hours: float,
                                user_attendance: float,
                                user_prev_marks: float,
                                user_assignment: float,
                                user_predicted_score: float) -> str:
    """
    Build and return a base64-encoded PNG of the performance graph.

    The curve shows predicted score across study hours 1–12,
    holding attendance, previous_marks, and assignment_score
    fixed at the user's values.

    Parameters
    ----------
    model / scaler            : trained ML artefacts
    user_*                    : student's actual input values
    user_predicted_score      : the score already computed by predict_score()

    Returns
    -------
    str  – data:image/png;base64,<encoded>   (ready for <img src=...>)
    """

    # ── Generate curve data ───────────────────────────────────
    hour_range = np.linspace(1, 12, 120)          # smooth X-axis

    # Build feature matrix: vary study_hours, fix everything else
    X_curve = np.column_stack([
        hour_range,
        np.full_like(hour_range, user_attendance),
        np.full_like(hour_range, user_prev_marks),
        np.full_like(hour_range, user_assignment),
    ])
    X_scaled    = scaler.transform(X_curve)
    y_curve     = np.clip(model.predict(X_scaled), 0, 100)

    # ── Colour zones (Low / Medium / High) ───────────────────
    zone_colours = {
        'Low':    '#ef4444',   # red
        'Medium': '#f59e0b',   # amber
        'High':   '#10b981',   # green
    }

    # ── Plot ──────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 4.5))
    fig.patch.set_facecolor('#111827')
    ax.set_facecolor('#1a2235')

    # Shaded performance zones
    ax.axhspan(0,  50,  alpha=0.10, color='#ef4444', zorder=0)
    ax.axhspan(50, 75,  alpha=0.10, color='#f59e0b', zorder=0)
    ax.axhspan(75, 100, alpha=0.10, color='#10b981', zorder=0)

    # Horizontal zone labels (right edge)
    for label, y_mid, colour in [('Low', 25, '#ef4444'),
                                   ('Medium', 62.5, '#f59e0b'),
                                   ('High', 87.5, '#10b981')]:
        ax.text(11.8, y_mid, label, color=colour, fontsize=7,
                va='center', ha='right', alpha=0.7,
                fontfamily='monospace')

    # Prediction curve (gradient via line collection)
    from matplotlib.collections import LineCollection
    points  = np.array([hour_range, y_curve]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = LineCollection(segments, cmap='cool', linewidth=2.5, zorder=3)
    lc.set_array(y_curve)
    ax.add_collection(lc)

    # User's data point
    ax.scatter([user_study_hours], [user_predicted_score],
               color='#ffffff', s=100, zorder=6,
               edgecolors='#3b82f6', linewidths=2.5,
               label='Your position')

    # Dashed crosshairs to axes
    ax.axvline(user_study_hours, color='#3b82f6',
               linestyle='--', linewidth=0.8, alpha=0.5, zorder=2)
    ax.axhline(user_predicted_score, color='#3b82f6',
               linestyle='--', linewidth=0.8, alpha=0.5, zorder=2)

    # Annotation bubble
    ax.annotate(
        f'  You: {user_predicted_score:.1f}',
        xy=(user_study_hours, user_predicted_score),
        xytext=(user_study_hours + 0.5, user_predicted_score + 5),
        color='#e2e8f0', fontsize=9, fontweight='bold',
        arrowprops=dict(arrowstyle='->', color='#3b82f6', lw=1.2),
        bbox=dict(boxstyle='round,pad=0.3', fc='#1a2235',
                  ec='#3b82f6', lw=1),
        zorder=7,
    )

    # ── Axes styling ─────────────────────────────────────────
    ax.set_xlim(1, 12)
    ax.set_ylim(0, 100)
    ax.set_xlabel('Study Hours per Week', color='#94a3b8', fontsize=10)
    ax.set_ylabel('Predicted Score (%)', color='#94a3b8', fontsize=10)
    ax.set_title('Study Hours vs Predicted Score',
                 color='#e2e8f0', fontsize=12, fontweight='bold', pad=12)

    ax.tick_params(colors='#64748b', labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor('#1f2d45')

    ax.grid(color='#1f2d45', linewidth=0.6, linestyle='--', zorder=1)

    # Legend
    patch_low    = mpatches.Patch(color='#ef4444', alpha=0.5, label='Low (<50)')
    patch_med    = mpatches.Patch(color='#f59e0b', alpha=0.5, label='Medium (50–75)')
    patch_high   = mpatches.Patch(color='#10b981', alpha=0.5, label='High (>75)')
    dot_you      = plt.Line2D([0], [0], marker='o', color='w',
                               markerfacecolor='white',
                               markeredgecolor='#3b82f6',
                               markersize=8, label='Your position')
    ax.legend(handles=[patch_low, patch_med, patch_high, dot_you],
              loc='lower right', facecolor='#111827',
              edgecolor='#1f2d45', labelcolor='#94a3b8',
              fontsize=7.5, framealpha=0.9)

    plt.tight_layout()

    # ── Encode to base64 ─────────────────────────────────────
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=140,
                facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    return f'data:image/png;base64,{encoded}'
