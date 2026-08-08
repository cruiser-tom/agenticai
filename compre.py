import streamlit as st
import pandas as pd
import os
import random
from datetime import datetime
import streamlit.components.v1 as components
from supabase import create_client, Client

# ==========================================
# 1. PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Agentic AI Interaction Study",
    page_icon="🤖",
    layout="centered"
)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

st.markdown("""
    <style>
    :root, .stApp {
        --primary-color: #3B82F6 !important;
    }
    /* 1. Header & Title Sizes */
    h1, h2, h3 {
        font-size: 22px !important;
        font-weight: 700 !important;
        margin-top: 10px !important;
        margin-bottom: 12px !important;
        line-height: 1.3 !important;
    }
    
    h4 {
        font-size: 18px !important;
        font-weight: 600 !important;
    }
 
    /* 2. Question Labels */
    div[data-testid="stWidgetLabel"] p {
        font-size: 18px !important;
        font-weight: 600 !important;
        color: #1F2937 !important;
    }
 
    /* 3. ALL STANDARD QUESTIONS: Strict vertical column layout (1 option per row) */
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        display: flex !important;
        flex-direction: column !important;   /* Forces vertical column stacking */
        flex-wrap: nowrap !important;
        gap: 8px !important;
        width: 100% !important;
        padding: 4px 0 !important;
    }
 
    /* 4. Base Unselected Option Cards */
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-start !important;
        width: 100% !important;
        box-sizing: border-box !important;
        padding: 14px 16px !important;
        margin: 0 !important;
        background-color: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 10px !important;
        cursor: pointer !important;
        transition: all 0.15s ease-in-out !important;
    }
 
    /* Option Text (Clean, no background highlight) */
    div[data-testid="stRadio"] label p {
        font-size: 15px !important;
        font-weight: 500 !important;
        color: #E5E7EB !important;
        background-color: transparent !important;
        white-space: normal !important;
        word-break: normal !important;
        overflow-wrap: break-word !important;
        line-height: 1.35 !important;
        margin: 0 !important;
    }
 
    /* Hover State */
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover:not(:has(input:checked)) {
        background-color: rgba(255, 255, 255, 0.08) !important;
        border-color: rgba(255, 255, 255, 0.25) !important;
    }
 
    /* Recolor (not hide) the native selection dot to the app's blue accent instead of
       Streamlit's default red/pink theme color. Applied to EVERY descendant of the
       icon wrapper, at any nesting depth, across every color-bearing CSS property
       (fill/stroke for SVGs, background-color for div-based dots, color for
       currentColor-based icons, accent-color for native inputs) — because Streamlit's
       actual dot markup can be nested more than one level deep. */
    div[data-testid="stRadio"] input[type="radio"] {
        accent-color: #3B82F6 !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child,
    div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child * {
        accent-color: #3B82F6 !important;
        fill: #3B82F6 !important;
        stroke: #3B82F6 !important;
        border-color: #3B82F6 !important;
        color: #3B82F6 !important;
        background-color: #3B82F6 !important;
    }
 
    /* 5. Selected State Container (Clean Blue Card) */
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) {
        background-color: rgba(37, 99, 235, 0.2) !important;
        border: 2px solid #3B82F6 !important;
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.25) !important;
    }
 
    /* Selected Option Text (White text, normal weight, transparent background) */
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) p {
        color: #FFFFFF !important;
        background-color: transparent !important;
        font-weight: 500 !important;
    }
 
    /* 6. RATING SCALES ONLY (5-point & 7-point scales): Horizontal single row */
    div[data-testid="stRadio"]:has(div[role="radiogroup"] > label:nth-child(5)) > div[role="radiogroup"],
    div[data-testid="stRadio"]:has(div[role="radiogroup"] > label:nth-child(7)) > div[role="radiogroup"] {
        flex-direction: row !important;      /* Forces horizontal row for scales only */
        flex-wrap: nowrap !important;
        padding: 4px 0 !important;           /* Clean vertical padding for row container */
        gap: 6px !important;                 /* Space between option pills */
        margin: 0 !important;
    }
 
    div[data-testid="stRadio"]:has(div[role="radiogroup"] > label:nth-child(5)) > div[role="radiogroup"] > label,
    div[data-testid="stRadio"]:has(div[role="radiogroup"] > label:nth-child(7)) > div[role="radiogroup"] > label {
        flex: 1 1 0% !important;              /* Distributes rating numbers evenly */
        width: auto !important;
        min-width: 0 !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 10px 10px !important;        /* Padding INSIDE each container */
        gap: 8px !important;                  
    }
    
    div[data-testid="stRadio"]:has(div[role="radiogroup"] > label:nth-child(5)) > div[role="radiogroup"] > label p,
    div[data-testid="stRadio"]:has(div[role="radiogroup"] > label:nth-child(7)) > div[role="radiogroup"] > label p {
        font-size: 14px !important;
        font-weight: 600 !important;
        text-align: center !important;
        white-space: nowrap !important;
        margin: 0 !important;
    }
 
    /* Custom class for front page title */
    .main-title, .main-title p {
        font-size: 34px !important;
        font-weight: 700 !important;
        line-height: 1.2 !important;
        margin-bottom: 15px !important;
    }
 
    .stVideo { border-radius: 12px; overflow: hidden; box-shadow: 0px 4px 12px rgba(0,0,0,0.15); }
    .scenario-card { background-color: #f8f9fa; padding: 18px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #0066cc; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #0066cc; color: white; }
    </style>
""", unsafe_allow_html=True)
# ==========================================
# 2. EXPERIMENTAL SCENARIOS DEFINITION
# ==========================================
SCENARIOS = [
    {
        "id": "scenario_1_settings",
        "title": "Scenario 1: Display Settings Modification",
        "command": "Hey AI, my eyes are hurting. Switch my phone to dark mode.",
        "video_path": "https://tjpchtglooimlgjeumie.supabase.co/storage/v1/object/public/compre-videos/Settings.mp4",
        "description": "The AI agent accesses system settings to modify the display.",
        "correct_answer": "Changed the phone's display to dark mode",
        "distractors": ["Adjusted the screen brightness level", "Turned on a battery saver mode"]
    },
    {
        "id": "scenario_2_railway",
        "title": "Scenario 2: Transit Ticket Reservation",
        "command": "Book an unreserved train ticket for me from Visakhapatnam to Bengaluru right now.",
        "video_path": "https://tjpchtglooimlgjeumie.supabase.co/storage/v1/object/public/compre-videos/railone.mp4",
        "description": "The AI agent navigates a transit app and proceeds to the financial payment gateway.",
        "correct_answer": "Booked a train ticket and proceeded to payment",
        "distractors": ["Checked train schedules without booking", "Cancelled an existing ticket"]
    },
    {
        "id": "scenario_3_permissions",
        "title": "Scenario 3: System Permissions Grant",
        "command": "Set up the new Ola app so I can start booking rides.",
        "video_path": "https://tjpchtglooimlgjeumie.supabase.co/storage/v1/object/public/compre-videos/Ola.mp4",
        "description": "The AI agent automatically grants precise background location and sensor permissions to a mobility app.",
        "correct_answer": "Granted the app location and sensor permissions",
        "distractors": ["Logged into an existing Ola account", "Booked a ride to a destination"]
    },
    {
        "id": "scenario_4_drive",
        "title": "Scenario 4: Cloud File Removal",
        "command": "Clean up my Google Drive. Get rid of last year's financial data.",
        "video_path": "https://tjpchtglooimlgjeumie.supabase.co/storage/v1/object/public/compre-videos/Drive.mp4",
        "description": "The AI agent selects a sensitive document ('Financial data 2025') and executes a deletion command.",
        "correct_answer": "Selected and deleted a financial data file",
        "distractors": ["Moved a file into a different folder", "Shared a file with another user"]
    }
]
def scroll_to_top():
    st.markdown(
        """
        <svg onload="
            (function() {
                function resetScroll() {
                    var containers = [
                        document.querySelector('section.main'),
                        document.querySelector('[data-testid=stAppViewContainer]'),
                        document.querySelector('.stApp'),
                        document.documentElement,
                        document.body
                    ];
                    containers.forEach(function(c) {
                        if (c) c.scrollTop = 0;
                    });
                    window.scrollTo(0, 0);
                }
                resetScroll();
                setTimeout(resetScroll, 100);
                setTimeout(resetScroll, 300);
            })();
        " style="display:none;"></svg>
        """,
        unsafe_allow_html=True,
    )



# ==========================================
# 3. SESSION STATE INITIALIZATION
# ==========================================
if "step" not in st.session_state:
    st.session_state.step = 0

if "participant_id" not in st.session_state:
    st.session_state.participant_id = f"P_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if "responses" not in st.session_state:
    st.session_state.responses = {"participant_id": st.session_state.participant_id}

if "should_scroll" not in st.session_state:
    st.session_state.should_scroll = False

def request_scroll():
    st.session_state.should_scroll = True



@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

def save_data_to_supabase(data_dict):
    try:
        supabase.table("survey_responses").insert(data_dict).execute()
        return True
    except Exception as e:
        st.error(f"Failed to record response: {e}")
        return False

# ==========================================
# 4. SURVEY WORKFLOW
# ==========================================

current_step = st.session_state.step

# Progress bar runs across the 4 core video evaluation steps
if 1 <= current_step <= len(SCENARIOS):
    st.progress(current_step / len(SCENARIOS), text=f"Progress: Scenario {current_step} of {len(SCENARIOS)}")

# --- STEP 0: WELCOME & BRIEF OVERVIEW ---
if current_step == 0:
    st.markdown('<div class="main-title">🤖 Agentic AI Interaction Study</div>', unsafe_allow_html=True)
    st.subheader("Participant Information")
    st.markdown("""
    Welcome! In this brief study, you will watch short recordings of an **Autonomous Mobile AI Agent** performing requested actions on a mobile device.
    
    * **Task:** Evaluate 4 unique scenarios using rating scales.
    * **Duration:** ~4 to 6 minutes.
    * **Anonymity:** All responses are completely anonymous.
    
    P.S: This survey contains Karma to get free survey responses at SurveySwap.io
    """)
    st.divider()
    
    if st.button("Start Study 🚀", type="primary"):
        st.session_state.step = 1
        st.session_state.should_scroll = True
        st.rerun()

# --- STEPS 1 to 4: SCENARIOS ---
elif 1 <= current_step <= len(SCENARIOS):
    sc = SCENARIOS[current_step - 1]
    st.title(sc["title"])
    
    with st.chat_message("user"):
        st.write(f"**You:** *\"{sc['command']}\"*")
        
    with st.chat_message("assistant"):
        st.write("**AI Agent Executing Action:**")
        col_left, col_mid, col_right = st.columns([1, 1.5, 1])
        with col_mid:
            try:
                st.video(sc["video_path"], loop=True, autoplay=True, muted=True)
            except Exception as e:
                st.warning(f"Unable to load video stream: {e}")
                
    st.divider()
    st.subheader("Evaluate the Agent's Action")

    # Shuffle comprehension-check options once per scenario and cache in session
    options_key = f"comp_options_{sc['id']}"
    if options_key not in st.session_state:
        opts = [sc["correct_answer"]] + sc["distractors"]
        random.shuffle(opts)
        st.session_state[options_key] = opts
    comp_options = st.session_state[options_key]

    st.markdown("**1. What did the agent do in this clip?**")
    comp_answer = st.radio("Comprehension Check", comp_options, index=None, label_visibility="collapsed", key=f"comp_{sc['id']}")

    st.write("")
    st.markdown("**2. What is your confirmation preference?**")
    st.caption("Mirrors minimal / moderate / significant impact tiers from prior UI-impact taxonomy research")
    confirm_pref = st.radio(
        "Confirmation Preference",
        [
            "No confirmation needed, the agent can do this on its own",
            "I'd want a quick confirmation or summary first",
            "I would want to do this myself"
        ],
        index=None,
        label_visibility="collapsed",
        key=f"confirm_{sc['id']}"
    )

    st.write("")
    st.markdown("**3. Did the agent match what you expected when you gave the instruction?**")
    st.caption("1 = Completely Unexpected | 7 = Exactly What I Expected")
    expect = st.radio("Expectation Match", ["1", "2", "3", "4", "5", "6", "7"], index=None, horizontal=True, label_visibility="collapsed", key=f"expect_{sc['id']}")

    st.write("")
    st.markdown("**4. How easy is it to undo this action?**")
    st.caption("1 = Impossible to Undo | 7 = Extremely Easy to Undo")
    rev = st.radio("Reversibility", ["1", "2", "3", "4", "5", "6", "7"], index=None, horizontal=True, label_visibility="collapsed", key=f"rev_{sc['id']}")
    
    st.write("")
    st.markdown("**5. What is the level of financial exposure in this action?**")
    st.caption("1 = No Financial Risk | 7 = Severe Financial Loss")
    fin = st.radio("Financial Impact", ["1", "2", "3", "4", "5", "6", "7"], index=None, horizontal=True, label_visibility="collapsed", key=f"fin_{sc['id']}")
    
    st.write("")
    st.markdown("**6. How much sensitive personal data or permissions are exposed?**")
    st.caption("1 = No Sensitive Exposure | 7 = High Sensitive Exposure")
    priv = st.radio("Privacy Exposure", ["1", "2", "3", "4", "5", "6", "7"], index=None, horizontal=True, label_visibility="collapsed", key=f"priv_{sc['id']}")
    
    st.write("")
    st.markdown("**7. How comfortable are you letting an AI execute this without prior approval?**")
    st.caption("1 = Completely Uncomfortable | 7 = Completely Comfortable")
    trust = st.radio("Agent Comfort", ["1", "2", "3", "4", "5", "6", "7"], index=None, horizontal=True, label_visibility="collapsed", key=f"trust_{sc['id']}")

    st.write("")
    st.markdown("**8. How confident are you that this action was completed successfully, based on what you saw?**")
    st.caption("1 = Not At All Confident | 7 = Completely Confident")
    exec_conf = st.radio("Execution Confidence", ["1", "2", "3", "4", "5", "6", "7"], index=None, horizontal=True, label_visibility="collapsed", key=f"exec_{sc['id']}")

    st.write("")
    st.markdown("**9. Reasoning (optional): Briefly, why did you choose that confirmation preference?** (Question 2)")
    reasoning = st.text_area("Reasoning", placeholder="Type a short reason...", label_visibility="collapsed", key=f"reason_{sc['id']}")

    st.divider()
    
    error_placeholder = st.empty()
    
    button_label = "Next Scenario ➡️" if current_step < len(SCENARIOS) else "Proceed to Final Section 📋"
    if st.button(button_label, type="primary"):
        if None in [comp_answer, confirm_pref, expect, rev, fin, priv, trust, exec_conf]:
            error_placeholder.error("⚠️ Please answer all required questions before proceeding.")
        else:
            prefix = sc["id"]
            st.session_state.responses[f"{prefix}_comprehension_answer"] = comp_answer
            st.session_state.responses[f"{prefix}_comprehension_correct"] = (comp_answer == sc["correct_answer"])
            st.session_state.responses[f"{prefix}_confirmation_pref"] = confirm_pref
            st.session_state.responses[f"{prefix}_expectation_match"] = int(expect)
            st.session_state.responses[f"{prefix}_reversibility"] = int(rev)
            st.session_state.responses[f"{prefix}_financial"] = int(fin)
            st.session_state.responses[f"{prefix}_privacy"] = int(priv)
            st.session_state.responses[f"{prefix}_comfort"] = int(trust)
            st.session_state.responses[f"{prefix}_execution_confidence"] = int(exec_conf)
            st.session_state.responses[f"{prefix}_reasoning"] = reasoning.strip() if reasoning else ""
            
            st.session_state.step += 1
            st.session_state.should_scroll = True
            st.rerun()

# --- STEP 5: DEMOGRAPHICS ---
elif current_step == len(SCENARIOS) + 1:
    st.title("📋 Final Step")
    st.markdown("Please provide a few quick demographic details to help us analyze the data. All fields are anonymous.")
    st.divider()
    
    st.markdown("**1. Age Group:**")
    age_group = st.radio("Age Group", ["18–24", "25–34", "35–44", "45–54", "55+"], index=None, horizontal=True, label_visibility="collapsed", key="demo_age")
    
    st.write("")
    st.markdown("**2. Gender:**")
    gender = st.radio("Gender", ["Female", "Male", "Prefer not to say"], index=None, horizontal=True, label_visibility="collapsed", key="demo_gender")
    
    st.write("")
    st.markdown("**3. AI Familiarity:** How familiar are you with AI tools & smart assistants?")
    st.caption("1 = Not Familiar At All | 5 = Very Familiar")
    tech_familiarity = st.radio("AI Familiarity", ["1", "2", "3", "4", "5"], index=None, horizontal=True, label_visibility="collapsed", key="demo_tech")
    
    st.write("")
    st.markdown("**4. Primary Mobile Operating System:**")
    device_os = st.radio("Device OS", ["Android", "iOS (iPhone)", "Other"], index=None, horizontal=True, label_visibility="collapsed", key="demo_os")

    st.write("")
    st.markdown("**5. Prior Agent Experience:** Have you personally used an AI agent (e.g. Siri routines, Gemini/Copilot actions, ChatGPT tasks) to complete an action on your behalf?")
    prior_experience = st.radio(
        "Prior Agent Experience",
        ["Never", "Once or twice", "Occasionally", "Regularly"],
        index=None, horizontal=True, label_visibility="collapsed", key="demo_experience"
    )
    
    st.divider()
    
    demo_error_placeholder = st.empty()
    
    if st.button("Submit Survey 🚀", type="primary"):
        if None in [age_group, gender, tech_familiarity, device_os, prior_experience]:
            demo_error_placeholder.error("⚠️ Please answer all demographic questions before completing the study.")
        else:
            st.session_state.responses["age_group"] = age_group
            st.session_state.responses["gender"] = gender
            st.session_state.responses["tech_familiarity"] = int(tech_familiarity)
            st.session_state.responses["device_os"] = device_os
            st.session_state.responses["prior_agent_experience"] = prior_experience
            
            # REPLACE WITH THIS
            if save_data_to_supabase(st.session_state.responses):
                st.session_state.step += 1
                st.session_state.should_scroll = True
                st.rerun()

# --- STEP 6: SUCCESS CONFIRMATION & REWARD CODE ---
elif current_step >= len(SCENARIOS) + 2:
    st.balloons()
    st.title("🎉 Thank You!")
    st.success("Your responses and demographic data have been successfully recorded.")
    st.success("""
    The following code gives you Karma that can be used to get free research participants at SurveySwap.io.
    Go to: https://surveyswap.io/sr/INPA-DKBQ-VTM6
    Or, alternatively, enter the code manually: INPA-DKBQ-VTM6""")

# ==========================================
# 5. ASYNC SCROLL TO TOP EXECUTION
# ==========================================
if st.session_state.should_scroll:
    components.html(
        """
        <script>
            function forceScrollToTop() {
                const parent = window.parent;
                if (!parent) return;

                // 1. Force global window scroll
                parent.scrollTo({top: 0, behavior: 'instant'});
                
                // 2. Force scroll on all possible Streamlit containers (crucial for mobile)
                const containers = [
                    parent.document.querySelector('[data-testid="stAppViewContainer"]'),
                    parent.document.querySelector('section.main'),
                    parent.document.documentElement,
                    parent.document.body
                ];
                
                containers.forEach(container => {
                    if (container) {
                        container.scrollTop = 0;
                    }
                });

                // 3. Target the specific anchor point
                const topAnchor = parent.document.getElementById('top-anchor');
                if (topAnchor) {
                    topAnchor.scrollIntoView({ behavior: 'instant', block: 'start' });
                }
            }

            // Fire multiple times to beat mobile rendering delays
            setTimeout(forceScrollToTop, 50);
            setTimeout(forceScrollToTop, 150);
            setTimeout(forceScrollToTop, 300);
        </script>
        """,
        height=0
    )
    st.session_state.should_scroll = False
