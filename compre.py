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
    page_title="AI Agent Interaction Study",
    page_icon="🤖",
    layout="centered"
)

st.markdown("""
    <style>
    /* 1. Target main question text */
    div[data-testid="stWidgetLabel"] p {
        font-size: 19px !important;
        font-weight: 600 !important;
        color: #1F2937 !important;
    }

    /* 2. Force 1-7 rating scale radio buttons onto a single horizontal line on mobile */
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        flex-direction: row !important;
        flex-wrap: nowrap !important;         /* Prevents wrapping to next line */
        justify-content: space-between !important;
        gap: 2px !important;                  /* Reduces spacing between 1-7 buttons */
        width: 100% !important;
    }

    /* 3. Adjust padding for each radio button choice to fit 7 columns */
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        flex: 1 1 auto !important;
        min-width: 0 !important;
        padding: 4px 2px !important;
        margin: 0 !important;
        justify-content: center !important;
    }

    /* 4. Choice text styling (numbers 1-7) */
    div[data-testid="stRadio"] > div[role="radiogroup"] > label p {
        font-size: 15px !important;          /* Slightly smaller size so 1-7 don't clip */
        text-align: center !important;
    }
    </style>
""", unsafe_allow_html=True)


st.markdown("""
    <style>
    .stVideo { border-radius: 5px; overflow: hidden; box-shadow: 0px 4px 12px rgba(0,0,0,0.15); }
    .scenario-card { background-color: #f8f9fa; padding: 5px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #0066cc; }
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; background-color: #0066cc; color: white; }
    </style>
""", unsafe_allow_html=True)



DATA_FILE = "survey_responses.csv"

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
    st.title("🤖 Autonomous Mobile Agent Risk Study")
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
        request_scroll()
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

    st.markdown("**1. Comprehension Check:** What did the agent do in this clip?")
    comp_answer = st.radio("Comprehension Check", comp_options, index=None, label_visibility="collapsed", key=f"comp_{sc['id']}")

    st.write("")
    st.markdown("**2. Confirmation Preference:** Before this action is completed, what would you want?")
    st.caption("Mirrors minimal / moderate / significant impact tiers from prior UI-impact taxonomy research")
    confirm_pref = st.radio(
        "Confirmation Preference",
        [
            "No confirmation needed — the agent can do this on its own",
            "I'd want a quick confirmation or summary first",
            "No automation — I would want to do this myself"
        ],
        index=None,
        label_visibility="collapsed",
        key=f"confirm_{sc['id']}"
    )

    st.write("")
    st.markdown("**3. Expectation Match:** Did the agent match what you pictured when you gave the instruction?")
    st.caption("1 = Completely Unexpected | 7 = Exactly What I Expected")
    expect = st.radio("Expectation Match", ["1", "2", "3", "4", "5", "6", "7"], index=None, horizontal=True, label_visibility="collapsed", key=f"expect_{sc['id']}")

    st.write("")
    st.markdown("**4. Reversibility:** How easy or difficult is it to undo this action?")
    st.caption("1 = Impossible to Undo | 7 = Extremely Easy to Undo")
    rev = st.radio("Reversibility", ["1", "2", "3", "4", "5", "6", "7"], index=None, horizontal=True, label_visibility="collapsed", key=f"rev_{sc['id']}")
    
    st.write("")
    st.markdown("**5. Financial Impact:** What is the level of financial exposure in this action?")
    st.caption("1 = No Financial Risk | 7 = Severe Financial Loss")
    fin = st.radio("Financial Impact", ["1", "2", "3", "4", "5", "6", "7"], index=None, horizontal=True, label_visibility="collapsed", key=f"fin_{sc['id']}")
    
    st.write("")
    st.markdown("**6. Privacy Exposure:** How much sensitive personal data or permissions are exposed?")
    st.caption("1 = No Sensitive Exposure | 7 = High Sensitive Exposure")
    priv = st.radio("Privacy Exposure", ["1", "2", "3", "4", "5", "6", "7"], index=None, horizontal=True, label_visibility="collapsed", key=f"priv_{sc['id']}")
    
    st.write("")
    st.markdown("**7. Agent Comfort:** How comfortable are you letting an AI execute this without prior approval?")
    st.caption("1 = Completely Uncomfortable | 7 = Completely Comfortable")
    trust = st.radio("Agent Comfort", ["1", "2", "3", "4", "5", "6", "7"], index=None, horizontal=True, label_visibility="collapsed", key=f"trust_{sc['id']}")

    st.write("")
    st.markdown("**8. Execution Confidence:** How confident are you that this action was completed successfully, based on what you saw?")
    st.caption("1 = Not At All Confident | 7 = Completely Confident")
    exec_conf = st.radio("Execution Confidence", ["1", "2", "3", "4", "5", "6", "7"], index=None, horizontal=True, label_visibility="collapsed", key=f"exec_{sc['id']}")

    st.write("")
    st.markdown("**9. Reasoning (optional):** Briefly, why did you choose that confirmation preference?")
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
            request_scroll()
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
                request_scroll()
                st.rerun()

# --- STEP 6: SUCCESS CONFIRMATION & REWARD CODE ---
elif current_step >= len(SCENARIOS) + 2:
    st.balloons()
    st.title("🎉 Thank You!")
    st.success("Your responses and demographic data have been successfully recorded.")
    st.markdown(f"""
    
    ```
    The following code gives you Karma that can be used to get free research participants at SurveySwap.io.

    Go to: https://surveyswap.io/sr/INPA-DKBQ-VTM6

    Or, alternatively, enter the code manually: INPA-DKBQ-VTM6
    ```
    """)

# ==========================================
# 5. ASYNC SCROLL TO TOP EXECUTION
# ==========================================
if st.session_state.should_scroll:
    components.html(
        """
        <script>
            setTimeout(function() {
                const container = window.parent.document.querySelector('[data-testid="stAppViewContainer"]') ||
                                  window.parent.document.querySelector('section.main') ||
                                  window.parent;
                if (container) {
                    container.scrollTop = 0;
                }
                
                const topAnchor = window.parent.document.getElementById('top-anchor');
                if (topAnchor) {
                    topAnchor.scrollIntoView({ behavior: 'instant', block: 'start' });
                }
            }, 150);
        </script>
        """,
        height=0
    )
    st.session_state.should_scroll = False
