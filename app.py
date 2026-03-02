"""
Zena 💗 - Preventive Healthcare for First-Gen & International Female Students
Pink theme, interactive checklist, Myth vs Fact quiz.
"""

from dotenv import load_dotenv

load_dotenv()

from shiny import App, Inputs, Outputs, Session, reactive, render, ui
import pandas as pd
from io import StringIO
import random

from src.api_client import fetch_myhealthfinder
from src.data_processing import process_recommendations, get_clean_for_llm
from src.ai_insights import (
    cultural_context,
    personalized_summary,
    myth_vs_fact,
    MYTH_FACT_QUIZ,
)

TOGGLE_SELECT_JS = """
<script>
(function() {
  // Make every click toggle (no Cmd/Shift needed)
  ["mousedown", "pointerdown", "click"].forEach(function(evt) {
    document.addEventListener(evt, function(e) {
      var row = e.target.closest && e.target.closest(".shiny-data-grid tbody tr");
      if (row && e.isTrusted && !e.metaKey && !e.ctrlKey && !e.shiftKey) {
        Object.defineProperty(e, "metaKey", {get: function() { return true; }});
      }
    }, true);
  });

  // Stamp data-priority on each <tr> so CSS can shade by priority level.
  // Priority is the last visible column (index 2).
  function stampPriorities(grid) {
    grid.querySelectorAll("tbody tr").forEach(function(tr) {
      if (tr.dataset.priority) return;
      var cells = tr.querySelectorAll("td");
      var last = cells[cells.length - 1];
      if (last) tr.dataset.priority = last.textContent.trim();
    });
  }
  new MutationObserver(function() {
    document.querySelectorAll(".shiny-data-grid").forEach(stampPriorities);
  }).observe(document.body, {childList: true, subtree: true});
})();
</script>
"""

PINK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
:root {
  --primary-pink: #F48FB1;
  --light-bg: #FFF0F5;
  --accent-rose: #EC407A;
  --text: #444;
  --white: #ffffff;
}
* { box-sizing: border-box; }
body { font-family: 'Poppins', sans-serif !important; background: var(--light-bg) !important; color: var(--text) !important; margin: 0; }
.bslib-page-fill { background: var(--light-bg) !important; min-height: 100vh; }
.main-content { max-width: min(1000px, 95vw); margin: 0 auto; padding: clamp(16px, 3vw, 24px); }
.zena-header {
  background: linear-gradient(135deg, var(--primary-pink), var(--accent-rose));
  color: white;
  padding: clamp(24px, 4vw, 32px);
  border-radius: 0;
  text-align: center;
  margin-bottom: 0;
  box-shadow: 0 4px 20px rgba(244, 143, 177, 0.3);
  width: 100%;
}
/* Selected rows - priority-based shading applied via JS data attribute */
.shiny-data-grid tbody tr { cursor: pointer; transition: background-color 0.15s; }
.shiny-data-grid tr[data-priority="High"][aria-selected="true"] td { background-color: #f8bbd0 !important; }
.shiny-data-grid tr[data-priority="Routine"][aria-selected="true"] td { background-color: #fce4ec !important; }
.shiny-data-grid tr[data-priority="Informational"][aria-selected="true"] td { background-color: #fef0f5 !important; }
.zena-card {
  background: var(--white);
  border-radius: 16px;
  padding: clamp(16px, 3vw, 20px);
  margin-bottom: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  transition: box-shadow 0.2s;
}
.zena-card:hover { box-shadow: 0 4px 20px rgba(244, 143, 177, 0.2); }
.badge-high { background: var(--accent-rose); color: white; padding: 4px 10px; border-radius: 20px; font-size: 12px; }
.badge-routine { background: var(--primary-pink); color: white; padding: 4px 10px; border-radius: 20px; font-size: 12px; }
.badge-info { background: #e0e0e0; color: #555; padding: 4px 10px; border-radius: 20px; font-size: 12px; }
.disclaimer {
  font-size: 12px; color: #888;
  padding: 12px; background: #fafafa;
  border-radius: 8px; margin-bottom: 20px;
  border-left: 4px solid var(--accent-rose);
}
.score-circle {
  width: clamp(60px, 12vw, 80px); height: clamp(60px, 12vw, 80px);
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-pink), var(--accent-rose));
  color: white;
  display: flex; align-items: center; justify-content: center;
  font-size: clamp(18px, 4vw, 24px); font-weight: 700;
  margin: 0 auto 8px;
}
.welcome-section {
  text-align: center;
  padding: clamp(40px, 8vw, 80px) 24px;
}
.welcome-section h1 { color: var(--accent-rose); font-size: clamp(24px, 5vw, 32px); }
.welcome-section p { color: #666; font-size: clamp(14px, 2.5vw, 16px); max-width: 600px; margin: 16px auto; line-height: 1.6; }
.quiz-card {
  background: linear-gradient(135deg, #fff5f8, #ffe4ec);
  border: 2px solid var(--primary-pink);
  border-radius: 16px;
  padding: 24px;
  margin: 16px 0;
}
.quiz-statement { font-size: 18px; font-weight: 500; margin-bottom: 16px; }
.quiz-buttons { display: flex; gap: 12px; flex-wrap: wrap; justify-content: center; }
.quiz-result { font-weight: 600; margin-top: 12px; padding: 8px; border-radius: 8px; }
.quiz-correct { background: #c8e6c9; color: #2e7d32; }
.quiz-wrong { background: #ffcdd2; color: #c62828; }
@media (max-width: 768px) {
  .main-content { padding: 12px; }
  .quiz-buttons { flex-direction: column; }
}
</style>
"""

COUNTRIES = [
    "United States", "India", "China", "Mexico", "South Korea", "Vietnam",
    "Nigeria", "Brazil", "Canada", "Philippines", "Colombia", "Pakistan",
    "Bangladesh", "Egypt", "Ethiopia", "Iran", "Germany", "Turkey",
    "Indonesia", "Thailand", "Kenya",
]

FALLBACK_SUMMARY = (
    "Based on your profile, key preventive steps include routine screenings, "
    "staying up to date on vaccinations, and scheduling an annual well-woman visit. "
    "These are standard recommendations\u2014talk to your doctor about what\u2019s right for you."
)
FALLBACK_CULTURAL = (
    "In the U.S., preventive care is encouraged even when you feel healthy. "
    "Regular checkups, screenings, and vaccinations help catch issues early. "
    "This may feel different from healthcare norms in your home country, and that\u2019s okay."
)

_ERROR_MARKERS = ("error:", "unavailable", "not found", "unable to generate")


def _is_usable(text: str | None) -> bool:
    """Return True only if *text* is a real AI response, not an error string."""
    if not text or not str(text).strip():
        return False
    lower = str(text).lower()
    return not any(marker in lower for marker in _ERROR_MARKERS)

# ---------------------------------------------------------------------------
# UI — static skeleton with panel_conditional so interactive state is preserved
# ---------------------------------------------------------------------------
app_ui = ui.page_fluid(
    ui.HTML(PINK_CSS),
    ui.HTML(TOGGLE_SELECT_JS),
    ui.div(
        ui.div(
            ui.h2("\U0001f497 Zena \U0001f497", style="margin:0; font-size:clamp(24px, 5vw, 32px);"),
            ui.p("Healthcare in the U.S. explained without the confusion.", style="margin:8px 0 0; opacity:0.95;"),
            class_="zena-header",
        ),
        style="width:100%; padding:0 16px;",
    ),
    ui.div(
        ui.div(
            "This tool provides educational guidance based on U.S. preventive care recommendations. "
            "It is not medical advice.",
            class_="disclaimer",
        ),
        class_="main-content",
    ),
    ui.layout_sidebar(
        ui.sidebar(
            ui.h4("Your Profile", style="color: var(--accent-rose);"),
            ui.input_numeric("age", "Age", 25, min=16, max=60),
            ui.input_select(
                "country",
                "Country Background",
                {c: c for c in COUNTRIES},
                selected="United States",
            ),
            ui.h5("Vaccination Status", style="margin-top:16px; color:#555;"),
            ui.input_checkbox_group(
                "vaccines",
                "Completed",
                choices=["HPV", "Tdap", "Flu", "MMR"],
                selected=[],
            ),
            ui.input_checkbox("unsure", "Unsure about some vaccines", False),
            ui.input_radio_buttons(
                "insurance",
                "Insurance Status",
                {"yes": "Yes", "no": "No"},
                selected="yes",
            ),
            ui.input_action_button(
                "generate",
                "Generate My Preventive Plan",
                class_="btn-primary",
                style="background: var(--accent-rose); border-color: var(--accent-rose); margin-top:16px; width:100%;",
            ),
            width=280,
        ),
        ui.div(
            # ---- Welcome (before first Generate) ----
            ui.panel_conditional(
                "input.generate === 0",
                ui.div(
                    ui.h1("\U0001f497 Welcome to Zena \U0001f497", style="margin-bottom:12px;"),
                    ui.p(
                        "We\u2019re here to help you understand preventive healthcare "
                        "in the United States\u2014without the confusion.",
                        style="font-size:18px;",
                    ),
                    ui.h3("About Zena", style="margin-top:32px; color: var(--accent-rose);"),
                    ui.p(
                        "Zena is designed for first-generation and international female students "
                        "who may come from countries where healthcare works differently. In the U.S., "
                        "preventive care\u2014like screenings, vaccinations, and annual checkups\u2014is "
                        "encouraged even when you feel healthy.",
                    ),
                    ui.p(
                        "Enter your profile on the left, then click "
                        "\u201cGenerate My Preventive Plan\u201d to get your personalized checklist, "
                        "AI summary, and a fun Myth vs Fact quiz!",
                    ),
                    class_="welcome-section",
                ),
            ),
            # ---- Results dashboard (after Generate) ----
            ui.panel_conditional(
                "input.generate > 0",
                # Header
                ui.output_ui("results_header"),
                # Checklist card
                ui.div(
                    ui.h4("\U0001f497 Your Preventive Checklist"),
                    ui.div(
                        ui.div(ui.output_text("readiness_score"), class_="score-circle"),
                        ui.span(
                            "Preventive Readiness Score",
                            style="font-size:14px; color:#666;",
                        ),
                        style="text-align:center; margin:0 0 16px 0;",
                    ),
                    ui.p(
                        "Click rows to mark them as complete.",
                        style="font-size:13px; color:#999; margin-bottom:8px;",
                    ),
                    ui.output_data_frame("checklist_table"),
                    ui.download_button(
                        "download_btn",
                        "\U0001f4e5 Download Checklist",
                        style="margin-top:12px;",
                    ),
                    class_="zena-card",
                ),
                # Summary card
                ui.div(
                    ui.h4("\U0001f497 Your Personalized Summary"),
                    ui.output_ui("summary_content"),
                    class_="zena-card",
                ),
                # Quiz card
                ui.div(
                    ui.h4("\U0001f497 Myth vs Fact Quiz"),
                    ui.p(
                        "Test your knowledge! Is this statement a Myth or a Fact?",
                        style="font-size:14px; color:#666; margin-bottom:12px;",
                    ),
                    ui.div(
                        ui.output_ui("quiz_statement_ui"),
                        ui.div(
                            ui.input_action_button(
                                "quiz_myth", "\u274c Myth",
                                style="background:#ffcdd2; border-color:#ef9a9a;",
                            ),
                            ui.input_action_button(
                                "quiz_fact", "\u2705 Fact",
                                style="background:#c8e6c9; border-color:#a5d6a7;",
                            ),
                            ui.input_action_button(
                                "quiz_next", "\u27a1\ufe0f Next Question",
                                style="background:var(--primary-pink); border-color:var(--primary-pink);",
                            ),
                            class_="quiz-buttons",
                        ),
                        ui.output_ui("quiz_feedback"),
                        class_="quiz-card",
                    ),
                    class_="zena-card",
                ),
            ),
            class_="main-content",
        ),
    ),
)


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------
def server(input: Inputs, output: Outputs, session: Session) -> None:

    # ---- Core data (only recomputed on Generate click) --------------------

    @reactive.calc
    @reactive.event(input.generate)
    def processed_df() -> pd.DataFrame | None:
        try:
            data = fetch_myhealthfinder(
                age=int(input.age()),
                sex="female",
                pregnant="no",
                sexually_active="yes",
                tobacco_use="no",
            )
        except Exception:
            return None
        if not data or "Result" not in data:
            return None
        result = data["Result"]
        recs = result.get("Resources", {}).get("All", {}).get("Resource")
        if not recs:
            return None
        if isinstance(recs, dict):
            recs = [recs]
        completed = list(input.vaccines()) if input.vaccines() else []
        unsure_list = ["unsure"] if input.unsure() else []
        try:
            return process_recommendations(recs, completed, unsure_list)
        except Exception:
            return None

    @reactive.calc
    @reactive.event(input.generate)
    def ai_summary_text() -> str:
        df = processed_df()
        if df is None or df.empty:
            return FALLBACK_SUMMARY
        try:
            clean = get_clean_for_llm(df, 5)
            vax = list(input.vaccines()) if input.vaccines() else []
            text = personalized_summary(clean, vax, int(input.age()))
        except Exception:
            text = ""
        return text if _is_usable(text) else FALLBACK_SUMMARY

    @reactive.calc
    @reactive.event(input.generate)
    def ai_cultural_text() -> str:
        try:
            text = cultural_context()
        except Exception:
            text = ""
        return text if _is_usable(text) else FALLBACK_CULTURAL

    # ---- Quiz state -------------------------------------------------------

    current_quiz: reactive.Value[tuple[str, bool]] = reactive.Value(
        random.choice(MYTH_FACT_QUIZ)
    )
    user_answer: reactive.Value[bool | None] = reactive.Value(None)

    @reactive.Effect
    @reactive.event(input.generate)
    def _init_quiz():
        current_quiz.set(random.choice(MYTH_FACT_QUIZ))
        user_answer.set(None)

    @reactive.Effect
    @reactive.event(input.quiz_myth)
    def _on_myth():
        user_answer.set(False)

    @reactive.Effect
    @reactive.event(input.quiz_fact)
    def _on_fact():
        user_answer.set(True)

    @reactive.Effect
    @reactive.event(input.quiz_next)
    def _next_quiz():
        user_answer.set(None)
        current_quiz.set(random.choice(MYTH_FACT_QUIZ))

    # ---- Render: header ---------------------------------------------------

    @render.ui
    def results_header():
        df = processed_df()
        if df is None or df.empty:
            return ui.div(
                ui.p(
                    "Could not load recommendations. Please try again.",
                    style="text-align:center; padding:48px; color:#666;",
                ),
                class_="zena-card",
            )
        return ui.div(
            ui.h3(
                f"Hi! Based on your age ({input.age()}) and inputs, "
                "here are your preventive priorities."
            ),
            class_="zena-card",
        )

    # ---- Render: checklist ------------------------------------------------

    @render.data_frame
    def checklist_table():
        df = processed_df()
        if df is None or df.empty:
            return render.DataTable(pd.DataFrame())
        out = df[["title", "category", "priority"]].copy()
        out.columns = ["Recommendation", "Category", "Priority"]
        return render.DataTable(out, selection_mode="rows", width="100%")

    @render.text
    def readiness_score():
        df = processed_df()
        if df is None or df.empty:
            return "0%"
        total = len(df)
        if total == 0:
            return "0%"
        try:
            sel = checklist_table.cell_selection()
            checked = len(sel["rows"]) if sel and "rows" in sel else 0
        except Exception:
            checked = 0
        score = (checked / total) * 100
        return f"{int(score)}%"

    # ---- Render: summary --------------------------------------------------

    @render.ui
    def summary_content():
        summary = ai_summary_text()
        cultural = ai_cultural_text()
        return ui.div(
            ui.p(str(summary)),
            ui.h5("Cultural Context"),
            ui.p(str(cultural)),
        )

    # ---- Render: quiz -----------------------------------------------------

    @render.ui
    def quiz_statement_ui():
        statement, _ = current_quiz()
        if not statement:
            return ui.p("Loading...")
        return ui.div(statement, class_="quiz-statement")

    @render.ui
    def quiz_feedback():
        answer = user_answer()
        if answer is None:
            return ui.div()
        _, is_fact = current_quiz()
        correct = answer == is_fact
        if correct:
            msg = "Correct! \U0001f497"
        else:
            msg = "Not quite. It\u2019s a " + ("Fact" if is_fact else "Myth") + "."
        cls = "quiz-result quiz-correct" if correct else "quiz-result quiz-wrong"
        return ui.div(msg, class_=cls)

    # ---- Download ---------------------------------------------------------

    @render.download(filename="zena_checklist.csv")
    def download_btn():
        df = processed_df()
        if df is None or df.empty:
            yield "Recommendation,Category,Priority\nNo data yet. Click Generate first.\n"
            return
        out = StringIO()
        df[["title", "category", "priority"]].to_csv(
            out, index=False,
            header=["Recommendation", "Category", "Priority"],
        )
        yield out.getvalue()


app = App(app_ui, server)
