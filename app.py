import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import time
from datetime import datetime, date

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & NOTION DESIGN SYSTEM (CSS)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Personal Productivity HQ",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Notion-style visual theme (Dark Mode & Mobile Fixes)
st.markdown("""
    <style>
    /* Main Background & Base Fonts */
    .stApp {
        background-color: #FAFAFA;
        color: #2F3437 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Make task cards and alert boxes readable across all light/dark browser themes */
    .stAlert, .stAlert p, .stAlert span, .stAlert div, .stAlert h4 {
        color: #1F2937 !important;
    }
    
    /* Form inputs and dropdowns */
    input, textarea, select, div[role="combobox"] {
        color: #111827 !important;
        background-color: #FFFFFF !important;
    }
    
    /* Form Expander styling */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E9E9E7 !important;
        border-radius: 8px !important;
        margin-bottom: 1rem !important;
    }
    
    /* Metric Card Values */
    div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: #2F3437 !important;
    }
    
    /* Custom Headers */
    .notion-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #2F3437 !important;
        margin-bottom: 0.2rem;
    }
    
    .notion-subtext {
        color: #787774 !important;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    /* Force mobile button text to be centered and clearly visible */
    div[data-testid="stButton"] button {
        width: 100% !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    
    /* Hide Streamlit default header/footer chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if 'tasks' not in st.session_state:
    st.session_state.tasks = [
        {"id": 1, "task": "Review Q3 Roadmap", "category": "Work",
            "status": "In Progress", "due": date.today()},
        {"id": 2, "task": "Read 20 pages of Deep Work",
            "category": "Personal", "status": "To Do", "due": date.today()},
        {"id": 3, "task": "System Architecture Review",
            "category": "Engineering", "status": "Completed", "due": date.today()}
    ]

if 'habits' not in st.session_state:
    st.session_state.habits = {
        "Morning Meditation": [True, True, False, True, False, True, True],
        "Workout 45m": [True, False, True, True, False, True, False],
        "Journaling": [True, True, True, True, True, False, False]
    }

# -----------------------------------------------------------------------------
# 3. NOTION API INTEGRATION HELPER
# -----------------------------------------------------------------------------


def fetch_notion_database(api_key: str, database_id: str):
    """Fetch live data from a Notion Database."""
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(
                f"Notion API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection failed: {e}")
        return None


# -----------------------------------------------------------------------------
# 4. SIDEBAR NAVIGATION & CONFIG
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚡ **Productivity HQ**")
    st.caption("Minimalist Notion Dashboard")
    st.divider()

    nav = st.radio("Navigate", ["Dashboard Overview", "Task Manager",
                   "Focus Timer (Pomodoro)", "Habit Tracker"], index=0)

    st.divider()
    st.markdown("#### 🔗 **Notion Sync**")
    notion_token = st.text_input("Notion Integration Token", type="password")
    notion_db_id = st.text_input("Notion Database ID")

    if st.button("Sync Notion Database", width="stretch"):
        if notion_token and notion_db_id:
            data = fetch_notion_database(notion_token, notion_db_id)
            if data:
                st.success("Successfully fetched Notion records!")
        else:
            st.warning("Please provide both API Token and Database ID.")

# -----------------------------------------------------------------------------
# 5. DASHBOARD VIEWS
# -----------------------------------------------------------------------------

# --- VIEW 1: OVERVIEW ---
if nav == "Dashboard Overview":
    st.markdown('<div class="notion-header">👋 Welcome back</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="notion-subtext">Here is your daily snapshot and productivity metric summary.</div>',
                unsafe_allow_html=True)

    # Top KPI Metrics
    c1, c2, c3, c4 = st.columns(4)
    total_tasks = len(st.session_state.tasks)
    completed_tasks = sum(
        1 for t in st.session_state.tasks if t["status"] == "Completed")
    pending_tasks = total_tasks - completed_tasks
    completion_rate = int(
        (completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0

    c1.metric("Total Tasks", total_tasks)
    c2.metric("Completed", completed_tasks)
    c3.metric("Pending", pending_tasks)
    c4.metric("Completion Rate", f"{completion_rate}%")

    st.divider()

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("### 📊 **Task Progress Breakdown**")
        df_tasks = pd.DataFrame(st.session_state.tasks)
        if not df_tasks.empty:
            fig = px.pie(
                df_tasks,
                names='status',
                color='status',
                color_discrete_map={'Completed': '#2ECC71',
                                    'In Progress': '#F1C40F', 'To Do': '#E74C3C'},
                hole=0.55
            )
            fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300)
            st.plotly_chart(fig, width="stretch")

    with col_right:
        st.markdown("### 📌 **Quick Notes**")
        st.text_area(
            "Scratchpad", value="• Complete architecture documentation\n• Schedule weekly team sync\n• Review product launch goals", height=240)

# --- VIEW 2: TASK MANAGER ---
elif nav == "Task Manager":
    st.markdown('<div class="notion-header">📋 Task Board</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="notion-subtext">Organize and execute your daily priorities.</div>',
                unsafe_allow_html=True)

    # Add Task Form
    with st.expander("➕ Add New Task / Item", expanded=False):
        with st.form("new_task_form"):
            task_title = st.text_input("Task Description")
            cat = st.selectbox(
                "Category", ["Work", "Personal", "Engineering", "Health"])
            stat = st.selectbox(
                "Status", ["To Do", "In Progress", "Completed"])
            submitted = st.form_submit_button("Add Task")
            if submitted and task_title:
                new_id = len(st.session_state.tasks) + 1
                st.session_state.tasks.append(
                    {"id": new_id, "task": task_title, "category": cat, "status": stat, "due": date.today()})
                st.rerun()

    st.divider()

    # Kanban Columns
    todo_col, in_prog_col, done_col = st.columns(3)

    with todo_col:
        st.markdown("#### 🔴 **To Do**")
        for t in [item for item in st.session_state.tasks if item["status"] == "To Do"]:
            st.info(f"**{t['task']}**\n\n*Category:* {t['category']}")

    with in_prog_col:
        st.markdown("#### 🟡 **In Progress**")
        for t in [item for item in st.session_state.tasks if item["status"] == "In Progress"]:
            st.warning(f"**{t['task']}**\n\n*Category:* {t['category']}")

    with done_col:
        st.markdown("#### 🟢 **Completed**")
        for t in [item for item in st.session_state.tasks if item["status"] == "Completed"]:
            st.success(f"~~{t['task']}~~\n\n*Category:* {t['category']}")

# --- VIEW 3: POMODORO FOCUS TIMER ---
elif nav == "Focus Timer (Pomodoro)":
    st.markdown('<div class="notion-header">⏱️ Focus Timer</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="notion-subtext">Boost deep work sessions using timed intervals.</div>',
                unsafe_allow_html=True)

    t_col1, t_col2 = st.columns([1, 2])

    with t_col1:
        minutes = st.number_input(
            "Session Length (Minutes)", min_value=1, max_value=120, value=25)
        start_timer = st.button("🚀 Start Timer", width="stretch")

    with t_col2:
        if start_timer:
            total_seconds = minutes * 60
            progress_bar = st.progress(0)
            timer_display = st.empty()

            for elapsed in range(total_seconds, -1, -1):
                mins, secs = divmod(elapsed, 60)
                timer_display.markdown(f"# ⏳ `{mins:02d}:{secs:02d}`")
                progress_bar.progress(1.0 - (elapsed / total_seconds))
                time.sleep(1)

            st.balloons()
            st.success("Session complete! Take a break.")

# --- VIEW 4: HABIT TRACKER (BULLETPROOF MOBILE DESIGN) ---
elif nav == "Habit Tracker":
    st.markdown('<div class="notion-header">📅 Weekly Habit Tracker</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="notion-subtext">Tap day buttons to toggle completed habits on mobile or desktop.</div>', unsafe_allow_html=True)

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # Renders interactive buttons with explicit day names embedded inside the text
    for habit_name, status_list in st.session_state.habits.items():
        st.markdown(f"### **{habit_name}**")

        # Render a simple mobile list layout
        for idx, day in enumerate(days):
            is_done = status_list[idx]
            # Green check button if done, gray pending button if not
            label = f"✅ {day} (Done)" if is_done else f"⚪ {day} (Pending)"

            if st.button(label, key=f"btn_{habit_name}_{idx}"):
                st.session_state.habits[habit_name][idx] = not is_done
                st.rerun()

        st.divider()
