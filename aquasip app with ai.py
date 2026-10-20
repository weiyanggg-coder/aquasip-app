import base64
import json
import os
import re
from datetime import datetime, time, timedelta

from PIL import Image
import streamlit as st
import streamlit.components.v1 as components

# --- AquaSip AI (prototype, trained on simulated data) ---
try:
    from aquasip_ai import get_recommendation
    AI_AVAILABLE = True
except Exception:
    AI_AVAILABLE = False

# ==========================================
# 1. PATH RESOLUTION & BASE64 HELPER
# ==========================================
script_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(script_dir, "assets", "logo.png")

if not os.path.exists(logo_path):
    logo_path = r"C:\Users\User\Desktop\VS code\Aquasip\assets\logo.png"


def get_image_base64(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""


logo_b64 = get_image_base64(logo_path)

# ==========================================
# 2. PAGE CONFIGURATION
# ==========================================
try:
    app_icon = Image.open(logo_path)
except Exception:
    app_icon = "💧"

st.set_page_config(
    page_title="AquaSip",
    page_icon=app_icon,
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ==========================================
# 3. NATIONAL COMPETITION LEVEL STYLING
# ==========================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    :root {
        --primary-gradient: linear-gradient(135deg, #2563EB 0%, #0284C7 100%);
        --primary-accent: #2563EB;
        --secondary-accent: #0284C7;
        --accent-glow: rgba(37, 99, 235, 0.28);
        --bg-main: #F8FAFC;
        --card-bg: #FFFFFF;
        --card-border: #E2E8F0;
        --text-primary: #0F172A;
        --text-muted: #64748B;
        --shadow-sm: 0 2px 8px rgba(15, 23, 42, 0.04);
        --shadow-md: 0 10px 25px -5px rgba(14, 165, 233, 0.12), 0 4px 12px rgba(15, 23, 42, 0.03);
        --shadow-lg: 0 18px 36px -6px rgba(37, 99, 235, 0.18);
    }

    /* Keyframe Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(14px) scale(0.98);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    .stApp {
        background: radial-gradient(circle at 10% 10%, rgba(224, 242, 254, 0.6) 0%, transparent 45%),
                    radial-gradient(circle at 90% 90%, rgba(219, 234, 254, 0.6) 0%, transparent 45%),
                    #F8FAFC !important;
        background-attachment: fixed !important;
    }

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.011em;
    }

    p, span, div, label, h1, h2, h3, h4, h5, h6, .stCaption {
        color: var(--text-primary) !important;
    }

    .block-container {
        max-width: 440px !important;
        padding: 1.25rem 1.25rem 3.5rem 1.25rem !important;
        animation: fadeInUp 0.45s cubic-bezier(0.16, 1, 0.3, 1);
    }

    #MainMenu, footer, header { visibility: hidden; }

    /* Competition Grade App Cards */
    .app-card {
        background: var(--card-bg) !important;
        border-radius: 18px !important;
        padding: 16px 18px !important;
        border: 1px solid var(--card-border) !important;
        box-shadow: var(--shadow-sm) !important;
        margin-bottom: 12px !important;
        transition: all 0.28s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        position: relative !important;
        overflow: hidden !important;
    }

    .app-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--primary-gradient);
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .app-card:hover {
        transform: translateY(-3px) scale(1.008);
        box-shadow: var(--shadow-md) !important;
        border-color: rgba(56, 189, 248, 0.5) !important;
    }

    .app-card:hover::before {
        opacity: 1;
    }

    /* Expander Styling */
    div[data-testid="stExpander"] {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.25s ease !important;
        margin-bottom: 12px !important;
    }

    div[data-testid="stExpander"]:hover {
        border-color: var(--primary-accent) !important;
        box-shadow: var(--shadow-md) !important;
    }

    div[data-testid="stExpander"] summary {
        background: #FFFFFF !important;
        color: var(--text-primary) !important;
        border-radius: 16px !important;
        padding: 14px 16px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
    }

    div[data-testid="stExpander"] summary:hover {
        background: #F1F5F9 !important;
    }

    div[data-testid="stExpander"] summary *,
    div[data-testid="stExpander"] summary svg {
        color: var(--text-primary) !important;
        fill: var(--text-primary) !important;
    }

    div[data-testid="stExpanderDetails"] {
        background: #FFFFFF !important;
        padding: 14px 16px !important;
        border-top: 1px solid #E2E8F0 !important;
    }

    /* Primary & Secondary Buttons */
    .stButton > button {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em !important;
        border: 1px solid #CBD5E1 !important;
        background: #FFFFFF !important;
        color: #1E293B !important;
        transition: all 0.22s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        font-size: 13.5px !important;
        padding: 0.55rem 0.5rem !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
    }

    .stButton > button:hover {
        background: #F8FAFC !important;
        border-color: var(--primary-accent) !important;
        color: var(--primary-accent) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.15) !important;
    }

    .stButton > button[kind="primary"] {
        background: var(--primary-gradient) !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 6px 20px var(--accent-glow) !important;
    }

    /* Input & Select Box Redesign */
    input, textarea, select,
    div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    div[data-testid="stTextInputRootElement"],
    div[data-testid="stTextInput"] > div,
    div[data-testid="stNumberInput"] > div,
    div[data-testid="stNumberInputContainer"],
    div[data-testid="stSelectbox"] > div,
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: var(--text-primary) !important;
        border-color: #CBD5E1 !important;
        box-shadow: none !important;
        border-radius: 12px !important;
        transition: all 0.2s ease !important;
    }

    div[data-baseweb="select"] * {
        color: var(--text-primary) !important;
        background-color: transparent !important;
    }

    div[data-baseweb="popover"],
    div[data-baseweb="popover"] *,
    ul[role="listbox"],
    li[role="option"] {
        background-color: #FFFFFF !important;
        color: var(--text-primary) !important;
    }

    li[role="option"]:hover {
        background-color: #F1F5F9 !important;
    }

    input, input[type="text"], input[type="password"], input[type="number"] {
        background-color: #FFFFFF !important;
        color: var(--text-primary) !important;
        -webkit-text-fill-color: var(--text-primary) !important;
        font-weight: 500 !important;
    }

    /* Fix File Uploader Styling (Eliminate Dark Charcoal Box) */
    div[data-testid="stFileUploader"],
    section[data-testid="stFileUploaderDropzone"],
    div[data-testid="stFileUploaderDropzone"] {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        border: 1.5px dashed #CBD5E1 !important;
        border-radius: 14px !important;
        color: #0F172A !important;
        padding: 12px !important;
    }

    section[data-testid="stFileUploaderDropzone"] * {
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
    }

    section[data-testid="stFileUploaderDropzone"] button {
        background-color: #F1F5F9 !important;
        border: 1px solid #CBD5E1 !important;
        color: #0F172A !important;
    }

    section[data-testid="stFileUploaderDropzone"] button:hover {
        background-color: #E2E8F0 !important;
        border-color: var(--primary-accent) !important;
    }

    /* Day Checkboxes Horizontal Layout Fix */
    div[data-testid="stCheckbox"] {
        min-width: unset !important;
        margin-right: 0px !important;
    }

    div[data-testid="stCheckbox"] label {
        font-size: 12px !important;
        font-weight: 700 !important;
        padding-left: 2px !important;
        white-space: nowrap !important;
    }

    div[data-testid="stCheckbox"] label p {
        white-space: nowrap !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        word-break: keep-all !important;
    }

    /* Custom Progress Bar Visual */
    .progress-bar-bg {
        width: 100%;
        height: 10px;
        background-color: #E2E8F0;
        border-radius: 999px;
        overflow: hidden;
        margin: 10px 0 4px 0;
    }
    .progress-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #2563EB, #38BDF8);
        border-radius: 999px;
        transition: width 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    </style>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 4. REAL-TIME TIMER, FULLSCREEN ALARM & CONTINUOUS SOUND
# ==========================================
def render_realtime_timer_and_alarm(reminders, custom_sound_b64="", snooze_minutes=5):
    alarms_json = json.dumps(reminders)
    custom_b64_json = json.dumps(custom_sound_b64)

    timer_alarm_js = f"""
    <script>
    (function() {{
        const parentDoc = window.parent.document;
        const snoozeMinutesVal = {snooze_minutes};

        // Initialize Snooze Alarms Array on parent window
        if (!window.parent.aquasipSnoozeAlarms) {{
            window.parent.aquasipSnoozeAlarms = [];
        }}

        // 1. Setup Fixed Corner Timer Widget
        let clockBadge = parentDoc.getElementById('fixed-realtime-clock');
        if (!clockBadge) {{
            clockBadge = parentDoc.createElement('div');
            clockBadge.id = 'fixed-realtime-clock';
            clockBadge.style.cssText = 'position: fixed; top: 14px; right: 16px; z-index: 999999; background: rgba(255, 255, 255, 0.92); backdrop-filter: blur(8px); border: 1px solid #CBD5E1; border-radius: 20px; padding: 6px 14px; font-family: "Plus Jakarta Sans", sans-serif; font-size: 12.5px; font-weight: 700; color: #2563EB; box-shadow: 0 4px 14px rgba(15, 23, 42, 0.08); display: flex; align-items: center; gap: 6px; user-select: none; transition: all 0.2s ease;';
            parentDoc.body.appendChild(clockBadge);
        }}

        // 2. Audio Synthesizer & Audio Looper Logic
        const customAudioData = {custom_b64_json};
        let activeAudioLoopInterval = null;
        let activeCustomAudioObj = null;

        function stopAlarmAudioLoop() {{
            if (activeAudioLoopInterval) {{
                clearInterval(activeAudioLoopInterval);
                activeAudioLoopInterval = null;
            }}
            if (activeCustomAudioObj) {{
                try {{
                    activeCustomAudioObj.pause();
                    activeCustomAudioObj.currentTime = 0;
                }} catch(e) {{}}
                activeCustomAudioObj = null;
            }}
        }}

        function playSingleAudioTone(soundType) {{
            try {{
                if ((soundType === 'Custom Audio Upload' || soundType === 'Custom Audio Upload') && customAudioData) {{
                    const audio = new Audio(customAudioData);
                    audio.play().catch(e => console.error("Custom audio play error:", e));
                    return;
                }}

                const parentWin = window.parent || window;
                const AudioCtxClass = parentWin.AudioContext || parentWin.webkitAudioContext || window.AudioContext || window.webkitAudioContext;
                if (!AudioCtxClass) return;

                const ctx = new AudioCtxClass();

                function schedule() {{
                    const now = ctx.currentTime;
                    if (soundType === 'Zen Bell') {{
                        const osc = ctx.createOscillator();
                        const gain = ctx.createGain();
                        osc.type = 'sine';
                        osc.frequency.setValueAtTime(432, now);
                        gain.gain.setValueAtTime(0, now);
                        gain.gain.linearRampToValueAtTime(0.5, now + 0.05);
                        gain.gain.exponentialRampToValueAtTime(0.0001, now + 2.0);
                        osc.connect(gain); gain.connect(ctx.destination);
                        osc.start(now); osc.stop(now + 2.1);
                    }} else if (soundType === 'Digital Beep') {{
                        [0, 0.15, 0.3].forEach((offset) => {{
                            const osc = ctx.createOscillator();
                            const gain = ctx.createGain();
                            osc.type = 'square';
                            osc.frequency.setValueAtTime(1000, now + offset);
                            gain.gain.setValueAtTime(0.15, now + offset);
                            gain.gain.exponentialRampToValueAtTime(0.0001, now + offset + 0.08);
                            osc.connect(gain); gain.connect(ctx.destination);
                            osc.start(now + offset); osc.stop(now + offset + 0.09);
                        }});
                    }} else if (soundType === 'Marimba Rise') {{
                        [261.63, 329.63, 392.00, 523.25].forEach((freq, i) => {{
                            const osc = ctx.createOscillator();
                            const gain = ctx.createGain();
                            osc.type = 'triangle';
                            osc.frequency.setValueAtTime(freq, now + i * 0.1);
                            gain.gain.setValueAtTime(0.4, now + i * 0.1);
                            gain.gain.exponentialRampToValueAtTime(0.0001, now + i * 0.1 + 0.3);
                            osc.connect(gain); gain.connect(ctx.destination);
                            osc.start(now + i * 0.1); osc.stop(now + i * 0.1 + 0.32);
                        }});
                    }} else {{
                        // Default Aqua Chime
                        const pulses = [0, 0.35, 0.7];
                        const freqs = [523.25, 659.25, 783.99, 1046.50];
                        pulses.forEach((pulseOffset) => {{
                            freqs.forEach((freq, idx) => {{
                                const osc = ctx.createOscillator();
                                const gain = ctx.createGain();
                                const startTime = now + pulseOffset + (idx * 0.07);
                                osc.type = 'sine';
                                osc.frequency.setValueAtTime(freq, startTime);
                                gain.gain.setValueAtTime(0, startTime);
                                gain.gain.linearRampToValueAtTime(0.35, startTime + 0.02);
                                gain.gain.exponentialRampToValueAtTime(0.0001, startTime + 0.25);
                                osc.connect(gain); gain.connect(ctx.destination);
                                osc.start(startTime); osc.stop(startTime + 0.28);
                            }});
                        }});
                    }}
                }}

                if (ctx.state === 'suspended') {{
                    ctx.resume().then(() => schedule()).catch(() => schedule());
                }} else {{
                    schedule();
                }}
            }} catch(e) {{
                console.error("Audio playback error:", e);
            }}
        }}

        window.parent.playAquaSipAlarmSound = playSingleAudioTone;

        function startContinuousAlarmAudio(soundType) {{
            stopAlarmAudioLoop();

            if ((soundType === 'Custom Audio Upload' || soundType === 'Custom Audio Upload') && customAudioData) {{
                try {{
                    activeCustomAudioObj = new Audio(customAudioData);
                    activeCustomAudioObj.loop = true;
                    activeCustomAudioObj.play().catch(e => console.error("Custom audio play error:", e));
                }} catch(e) {{
                    console.error("Custom audio error:", e);
                }}
                return;
            }}

            playSingleAudioTone(soundType);
            activeAudioLoopInterval = setInterval(() => {{
                playSingleAudioTone(soundType);
            }}, 1600);
        }}

        // 3. Helper: Compute Snooze Time String (e.g. "03:45 PM")
        function calculateSnoozeTargetTimeStr(snoozeMins) {{
            const d = new Date();
            d.setMinutes(d.getMinutes() + snoozeMins);
            let h = d.getHours();
            const m = String(d.getMinutes()).padStart(2, '0');
            const ampm = h >= 12 ? 'PM' : 'AM';
            h = h % 12;
            h = h ? h : 12;
            const paddedH = String(h).padStart(2, '0');
            return `${{paddedH}}:${{m}} ${{ampm}}`;
        }}

        // 4. Prominent Fullscreen Modal Trigger
        function triggerNoticeableAlarmModal(alarmTimeStr, soundType) {{
            startContinuousAlarmAudio(soundType);

            let modal = parentDoc.getElementById('aquasip-fullscreen-alarm-modal');
            if (modal) modal.remove();

            if (!parentDoc.getElementById('alarm-modal-animations-style')) {{
                const animStyle = parentDoc.createElement('style');
                animStyle.id = 'alarm-modal-animations-style';
                animStyle.innerHTML = `
                    @keyframes alarmPulseGlow {{
                        0% {{ transform: scale(0.97); box-shadow: 0 0 35px rgba(37, 99, 235, 0.5); }}
                        100% {{ transform: scale(1.02); box-shadow: 0 0 65px rgba(56, 189, 248, 0.9); }}
                    }}
                    @keyframes bellRingSwing {{
                        0%, 100% {{ transform: rotate(0deg); }}
                        20%, 60% {{ transform: rotate(15deg); }}
                        40%, 80% {{ transform: rotate(-15deg); }}
                    }}
                `;
                parentDoc.head.appendChild(animStyle);
            }}

            modal = parentDoc.createElement('div');
            modal.id = 'aquasip-fullscreen-alarm-modal';
            modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 9999999; background: rgba(15, 23, 42, 0.88); backdrop-filter: blur(14px); display: flex; align-items: center; justify-content: center; padding: 20px; font-family: "Plus Jakarta Sans", sans-serif; box-sizing: border-box;';

            modal.innerHTML = `
                <div style="background: linear-gradient(145deg, #FFFFFF, #F8FAFC); border: 2.5px solid #38BDF8; border-radius: 28px; width: 100%; max-width: 380px; padding: 32px 24px; text-align: center; animation: alarmPulseGlow 1.2s infinite alternate ease-in-out; position: relative; box-sizing: border-box;">
                    <div style="background: linear-gradient(135deg, #2563EB, #0284C7); color: #FFFFFF; display: inline-flex; align-items: center; gap: 6px; padding: 6px 16px; border-radius: 20px; font-weight: 800; font-size: 12px; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 18px;">
                        HYDRATION ALARM
                    </div>
                    
                    <div style="font-size: 64px; margin-bottom: 12px; animation: bellRingSwing 1s infinite ease-in-out; display: inline-block;">
                        
                    </div>

                    <h2 style="font-size: 24px; font-weight: 800; color: #0F172A; margin: 0 0 8px 0; letter-spacing: -0.02em;">Time to Drink Water!</h2>
                    <p style="font-size: 14.5px; font-weight: 700; color: #2563EB; margin: 0 0 6px 0;">Scheduled for ${{alarmTimeStr}}</p>
                    <p style="font-size: 12px; font-weight: 500; color: #64748B; margin: 0 0 24px 0;">Stay hydrated to keep your body & mind energized!</p>

                    <div style="display: flex; flex-direction: column; gap: 10px;">
                        <button id="aquasip-btn-stop" style="background: linear-gradient(135deg, #EF4444, #DC2626); color: #FFFFFF; border: none; border-radius: 14px; padding: 14px; font-weight: 800; font-size: 15px; cursor: pointer; box-shadow: 0 6px 20px rgba(239, 68, 68, 0.35); transition: transform 0.2s ease;">
                            Stop Alarm
                        </button>
                        <button id="aquasip-btn-snooze" style="background: #FFFFFF; color: #2563EB; border: 2px solid #2563EB; border-radius: 14px; padding: 12px; font-weight: 800; font-size: 14px; cursor: pointer; transition: background 0.2s ease;">
                            Snooze (${{snoozeMinutesVal}} Mins)
                        </button>
                    </div>
                </div>
            `;

            parentDoc.body.appendChild(modal);

            const btnStop = parentDoc.getElementById('aquasip-btn-stop');
            const btnSnooze = parentDoc.getElementById('aquasip-btn-snooze');

            btnStop.addEventListener('click', () => {{
                stopAlarmAudioLoop();
                if (modal && modal.parentNode) modal.remove();
            }});

            btnSnooze.addEventListener('click', () => {{
                stopAlarmAudioLoop();
                if (modal && modal.parentNode) modal.remove();

                const snoozeTimeStr = calculateSnoozeTargetTimeStr(snoozeMinutesVal);
                window.parent.aquasipSnoozeAlarms.push({{
                    time: snoozeTimeStr,
                    days: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
                    sound: soundType
                }});

                // Confirmation Banner
                let alertBanner = parentDoc.getElementById('aquasip-alarm-banner');
                if (alertBanner) alertBanner.remove();

                alertBanner = parentDoc.createElement('div');
                alertBanner.id = 'aquasip-alarm-banner';
                alertBanner.style.cssText = 'position: fixed; top: 60px; right: 16px; z-index: 999999; background: linear-gradient(135deg, #2563EB, #0284C7); color: #FFFFFF; padding: 12px 18px; border-radius: 14px; font-weight: 700; font-size: 13px; box-shadow: 0 10px 25px rgba(37,99,235,0.35); display: flex; align-items: center; gap: 8px; animation: fadeInUp 0.3s ease;';
                alertBanner.innerHTML = `<span>💤</span> <span>Alarm snoozed for <b>${{snoozeMinutesVal}} mins</b> (Next: ${{snoozeTimeStr}})!</span>`;
                parentDoc.body.appendChild(alertBanner);

                setTimeout(() => {{
                    if (alertBanner && alertBanner.parentNode) alertBanner.remove();
                }}, 7000);
            }});
        }}

        // 5. Realtime Timer Check Loop
        const activeAlarms = {alarms_json};
        const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
        let lastTriggeredMinuteKey = "";

        function updateClockAndCheckAlarm() {{
            const now = new Date();
            const currentDay = dayNames[now.getDay()];
            let hours = now.getHours();
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            const ampm = hours >= 12 ? 'PM' : 'AM';

            let displayHours = hours % 12;
            displayHours = displayHours ? displayHours : 12;
            const paddedHours = String(displayHours).padStart(2, '0');
            const unpaddedHours = String(displayHours);

            const fullTimeString = `${{currentDay}}, ${{paddedHours}}:${{minutes}}:${{seconds}} ${{ampm}}`;
            const minuteCheckPadded = `${{paddedHours}}:${{minutes}} ${{ampm}}`;
            const minuteCheckUnpadded = `${{unpaddedHours}}:${{minutes}} ${{ampm}}`;

            if (clockBadge) {{
                clockBadge.innerHTML = `<span style="font-size:14px;"></span> <span style="letter-spacing: 0.02em;">${{fullTimeString}}</span>`;
            }}

            const allAlarmList = [
                ...activeAlarms,
                ...(window.parent.aquasipSnoozeAlarms || [])
            ];

            allAlarmList.forEach(alarm => {{
                let alarmTime = "";
                let alarmDays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
                let soundType = "Aqua Chime";

                if (typeof alarm === 'string') {{
                    alarmTime = alarm;
                }} else if (alarm && typeof alarm === 'object') {{
                    alarmTime = alarm.time || "";
                    if (alarm.days && Array.isArray(alarm.days)) {{
                        alarmDays = alarm.days;
                    }}
                    soundType = alarm.sound || "Aqua Chime";
                }}

                const timeMatches = (alarmTime === minuteCheckPadded || alarmTime === minuteCheckUnpadded);
                const dayMatches = alarmDays.includes(currentDay);
                const triggerKey = `${{currentDay}}_${{minuteCheckPadded}}_${{alarmTime}}`;

                if (timeMatches && dayMatches && lastTriggeredMinuteKey !== triggerKey) {{
                    lastTriggeredMinuteKey = triggerKey;
                    triggerNoticeableAlarmModal(alarmTime, soundType);
                }}
            }});
        }}

        if (window.realtimeTimerInterval) clearInterval(window.realtimeTimerInterval);
        window.realtimeTimerInterval = setInterval(updateClockAndCheckAlarm, 1000);
        updateClockAndCheckAlarm();
    }})();
    </script>
    """
    components.html(timer_alarm_js, height=0, width=0)


# ==========================================
# 5. FLUENT AUTOMATIC POPPING BOTTLE AVATAR
# ==========================================
def render_draggable_avatar(pct):
    dialogue_pool = {
        "low": [
            "I'm feeling so dry... Feed me water! ",
            "Hey! Time for a quick sip! ",
            "Don't forget to stay hydrated! ",
            "Drag me anywhere you like! ",
        ],
        "mid": [
            "Mmm, belly getting nice and full! ",
            "Great job! Halfway to your goal! ",
            "Keep drinking, master! ",
            "Glug glug glug~ Feels good! ",
        ],
        "full": [
            "Woohoo! 100% Hydrated! ",
            "My belly is full of fresh water! ",
            "You are a hydration champion! ",
            "Feeling super fresh & energized! ",
        ],
    }

    tier = "low" if pct < 40 else ("mid" if pct < 100 else "full")
    dialogue_json = json.dumps(dialogue_pool[tier])

    water_height = int((pct / 100.0) * 65)
    water_y = 75 - water_height

    avatar_js = f"""
    <script>
    (function() {{
        const parentDoc = window.parent.document;
        
        let existing = parentDoc.getElementById('floating-avatar-container');
        let savedLeft = null, savedTop = null, savedBottom = null, savedRight = null;

        if (existing) {{
            savedLeft = existing.style.left;
            savedTop = existing.style.top;
            savedBottom = existing.style.bottom;
            savedRight = existing.style.right;
            existing.remove();
        }} else if (window.parent.aquasipAvatarPos) {{
            savedLeft = window.parent.aquasipAvatarPos.left;
            savedTop = window.parent.aquasipAvatarPos.top;
            savedBottom = window.parent.aquasipAvatarPos.bottom;
            savedRight = window.parent.aquasipAvatarPos.right;
        }}

        if (!parentDoc.getElementById('avatar-float-style')) {{
            const style = parentDoc.createElement('style');
            style.id = 'avatar-float-style';
            style.innerHTML = `
                @keyframes floatIdle {{
                    0% {{ transform: translateY(0px) rotate(0deg); }}
                    50% {{ transform: translateY(-8px) rotate(1.5deg); }}
                    100% {{ transform: translateY(0px) rotate(0deg); }}
                }}
            `;
            parentDoc.head.appendChild(style);
        }}

        const container = parentDoc.createElement('div');
        container.id = 'floating-avatar-container';
        container.style.cssText = 'position: fixed; bottom: 24px; right: 24px; z-index: 999999; cursor: grab; user-select: none; touch-action: none; display: flex; flex-direction: column; align-items: center; width: 150px; filter: drop-shadow(0px 10px 20px rgba(37,99,235,0.25));';

        if (savedLeft || savedTop) {{
            container.style.left = savedLeft;
            container.style.top = savedTop;
            container.style.bottom = savedBottom || 'auto';
            container.style.right = savedRight || 'auto';
        }}

        container.innerHTML = `
            <div id="avatar-speech-bubble" style="background: rgba(255, 255, 255, 0.95); color: #0F172A; backdrop-filter: blur(8px); border: 2px solid #2563EB; border-radius: 16px; padding: 8px 12px; font-size: 11px; font-weight: 700; text-align: center; box-shadow: 0px 8px 20px rgba(15, 23, 42, 0.12); margin-bottom: 8px; position: relative; max-width: 140px; opacity: 1; transform: scale(1); transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.3s ease;">
                <span id="speech-text">Ready to drink?</span>
                <div style="position: absolute; bottom: -8px; left: 50%; transform: translateX(-50%); width: 0; height: 0; border-left: 6px solid transparent; border-right: 6px solid transparent; border-top: 8px solid #2563EB;"></div>
            </div>
            <div id="avatar-graphic" style="width: 72px; height: 88px; transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1); animation: floatIdle 3.2s ease-in-out infinite;">
                <svg viewBox="0 0 100 120" width="72" height="88">
                    <defs>
                        <linearGradient id="waterGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="#38BDF8" />
                            <stop offset="100%" stop-color="#2563EB" />
                        </linearGradient>
                    </defs>
                    <path d="M 20 20 L 30 100 Q 50 110 70 100 L 80 20 Z" fill="#F8FAFC" stroke="#2563EB" stroke-width="4" />
                    <clipPath id="cup-clip">
                        <path d="M 21 21 L 29 99 Q 50 108 71 99 L 79 21 Z" />
                    </clipPath>
                    <rect x="15" y="{water_y}" width="70" height="{water_height + 20}" fill="url(#waterGrad)" opacity="0.9" clip-path="url(#cup-clip)">
                        <animate attributeName="y" values="{water_y}; {water_y - 2}; {water_y}" dur="2s" repeatCount="indefinite" />
                    </rect>
                    <circle cx="40" cy="45" r="4" fill="#0F172A" />
                    <circle cx="60" cy="45" r="4" fill="#0F172A" />
                    <path d="M 43 55 Q 50 62 57 55" fill="none" stroke="#0F172A" stroke-width="3" stroke-linecap="round" />
                    <circle cx="34" cy="52" r="3" fill="#F43F5E" opacity="0.5" />
                    <circle cx="66" cy="52" r="3" fill="#F43F5E" opacity="0.5" />
                    <path d="M 50 20 L 65 -5 L 75 -2" fill="none" stroke="#F43F5E" stroke-width="6" stroke-linecap="round" />
                </svg>
            </div>
        `;

        parentDoc.body.appendChild(container);

        const speechBubble = parentDoc.getElementById('avatar-speech-bubble');
        const speechText = parentDoc.getElementById('speech-text');
        const graphic = parentDoc.getElementById('avatar-graphic');
        const sentences = {dialogue_json};

        let isDragging = false;
        let startX, startY, initialLeft, initialTop;
        let sentenceIdx = 0;

        function triggerPopSpeech() {{
            if (!speechBubble) return;
            speechBubble.style.opacity = '0';
            speechBubble.style.transform = 'translateY(10px) scale(0.8)';

            setTimeout(() => {{
                sentenceIdx = (sentenceIdx + 1) % sentences.length;
                if (speechText) speechText.innerText = sentences[sentenceIdx];
                speechBubble.style.opacity = '1';
                speechBubble.style.transform = 'translateY(0) scale(1)';
            }}, 350);
        }}

        if (window.avatarInterval) clearInterval(window.avatarInterval);
        window.avatarInterval = setInterval(triggerPopSpeech, 6000);

        container.addEventListener('mouseenter', () => {{
            graphic.style.transform = 'scale(1.15) rotate(4deg)';
        }});

        container.addEventListener('mouseleave', () => {{
            graphic.style.transform = 'scale(1) rotate(0deg)';
        }});

        function startDrag(e) {{
            isDragging = true;
            container.style.cursor = 'grabbing';
            const event = e.touches ? e.touches[0] : e;
            startX = event.clientX;
            startY = event.clientY;

            const rect = container.getBoundingClientRect();
            initialLeft = rect.left;
            initialTop = rect.top;
        }}

        function doDrag(e) {{
            if (!isDragging) return;
            const event = e.touches ? e.touches[0] : e;
            const dx = event.clientX - startX;
            const dy = event.clientY - startY;

            const newLeft = (initialLeft + dx) + 'px';
            const newTop = (initialTop + dy) + 'px';

            container.style.left = newLeft;
            container.style.top = newTop;
            container.style.bottom = 'auto';
            container.style.right = 'auto';

            window.parent.aquasipAvatarPos = {{
                left: newLeft,
                top: newTop,
                bottom: 'auto',
                right: 'auto'
            }};
        }}

        function stopDrag() {{
            if (isDragging) {{
                isDragging = false;
                container.style.cursor = 'grab';
                triggerPopSpeech();
            }}
        }}

        container.addEventListener('mousedown', startDrag);
        parentDoc.addEventListener('mousemove', doDrag);
        parentDoc.addEventListener('mouseup', stopDrag);

        container.addEventListener('touchstart', startDrag);
        parentDoc.addEventListener('touchmove', doDrag);
        parentDoc.addEventListener('touchend', stopDrag);
    }})();
    </script>
    """

    components.html(avatar_js, height=0, width=0)


# ==========================================
# 6. SESSION STATE INITIALIZATION
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "Log In"
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Home"
if "user" not in st.session_state:
    st.session_state.user = {"name": "Alex", "email": "alex@example.com"}
if "goal" not in st.session_state:
    st.session_state.goal = 2000
if "selected_cup" not in st.session_state:
    st.session_state.selected_cup = 200
if "sub_page" not in st.session_state:
    st.session_state.sub_page = None
if "cart" not in st.session_state:
    st.session_state.cart = []
if "shop_msg" not in st.session_state:
    st.session_state.shop_msg = None
if "alarm_success_msg" not in st.session_state:
    st.session_state.alarm_success_msg = None

if "reminders" not in st.session_state:
    st.session_state.reminders = []

if "custom_sound_b64" not in st.session_state:
    st.session_state.custom_sound_b64 = ""

if "snooze_duration" not in st.session_state:
    st.session_state.snooze_duration = 5

# Initialize Day Checkbox Keys Directly for Stateful Preset Buttons
all_days_list = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
for d_name in all_days_list:
    cb_key = f"cb_day_{d_name}"
    if cb_key not in st.session_state:
        st.session_state[cb_key] = True

if "water_logs" not in st.session_state:
    st.session_state.water_logs = []

if "weekly_status" not in st.session_state:
    st.session_state.weekly_status = [
        "fail",
        "fail",
        "fail",
        "fail",
        "fail",
        "fail",
        "fail",
    ]


# ==========================================
# 7. AUTHENTICATION SCREEN
# ==========================================
def render_auth():
    st.markdown(
        f"""
        <div style="text-align: center; padding: 24px 0 16px 0;">
            <img src="data:image/png;base64,{logo_b64}" style="width: 64px; height: 64px; object-fit: contain; margin-bottom: 12px; filter: drop-shadow(0 6px 12px rgba(37,99,235,0.25));" />
            <h2 style="background: linear-gradient(135deg, #2563EB 0%, #0284C7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 28px; margin: 0; letter-spacing: -0.02em;">AquaSip</h2>
            <p style="font-size: 13px; color: #64748B !important; margin-top: 4px; font-weight: 500;">Smart Hydration Tracker & Companion</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    if st.session_state.auth_mode == "Create Account":
        st.markdown(
            "<h3 style='text-align: center; font-size: 18px; font-weight: 700; color: #0F172A !important;'>Create Account</h3>",
            unsafe_allow_html=True,
        )
        email = st.text_input(
            "Email", placeholder="name@example.com", key="reg_email"
        )
        password = st.text_input("Password", type="password", key="reg_pass")

        if st.button("Get Started", use_container_width=True, type="primary"):
            if email:
                st.session_state.user["email"] = email
                st.session_state.user["name"] = (
                    email.split("@")[0].capitalize()
                )
            st.session_state.logged_in = True
            st.rerun()
    else:
        st.markdown(
            "<h3 style='text-align: center; font-size: 18px; font-weight: 700; color: #0F172A !important;'>Welcome Back</h3>",
            unsafe_allow_html=True,
        )
        email = st.text_input(
            "Email",
            value=st.session_state.user["email"],
            key="login_email",
        )
        password = st.text_input(
            "Password", type="password", value="12345678", key="login_pass"
        )

        if st.button("Sign In", use_container_width=True, type="primary"):
            st.session_state.logged_in = True
            st.rerun()

    st.markdown(
        "<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 24px 0;'>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button(
            "Create Account",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.auth_mode == "Create Account"
                else "secondary"
            ),
        ):
            st.session_state.auth_mode = "Create Account"
            st.rerun()
    with c2:
        if st.button(
            "Log In",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.auth_mode == "Log In"
                else "secondary"
            ),
        ):
            st.session_state.auth_mode = "Log In"
            st.rerun()


# ==========================================
# 8. NAVIGATION HEADER
# ==========================================
def render_app_header():
    col_title, col_logout = st.columns([3.2, 1])
    with col_title:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 10px;">
                <img src="data:image/png;base64,{logo_b64}" style="width: 34px; height: 34px; object-fit: contain; filter: drop-shadow(0 4px 8px rgba(37,99,235,0.2));" />
                <h3 style="background: linear-gradient(135deg, #2563EB 0%, #0284C7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin:0; font-weight:800; font-size: 22px; letter-spacing: -0.02em;">AquaSip</h3>
            </div>
        """,
            unsafe_allow_html=True,
        )
    with col_logout:
        if st.button("Log Out", key="top_logout"):
            st.session_state.logged_in = False
            st.session_state.sub_page = None
            st.rerun()

    tabs = ["Home", "History", "Shop", "Setting"]
    cols = st.columns(4)
    for idx, tab_name in enumerate(tabs):
        with cols[idx]:
            is_active = st.session_state.current_tab == tab_name
            if st.button(
                tab_name,
                key=f"nav_btn_{tab_name}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.session_state.current_tab = tab_name
                st.session_state.sub_page = None
                st.rerun()

    st.markdown(
        "<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True
    )
    return st.session_state.current_tab


# ==========================================
# 8b. AI HYDRATION INSIGHT (prototype)
# ==========================================
def render_ai_insight(total_drank):
    """Shows the AI prediction + a small suggested amount. Never crashes the app."""
    if not AI_AVAILABLE:
        return
    try:
        now = datetime.now()
        hour = now.hour + now.minute / 60
        recent = []
        for log in st.session_state.water_logs:
            t = datetime.strptime(log["time"], "%I:%M:%S %p").time()
            logged = datetime.combine(now.date(), t)
            if timedelta(0) <= now - logged <= timedelta(hours=2):
                recent.append(log["amount"])
        avg_recent = sum(recent) / len(recent) if recent else 0
        res = get_recommendation(hour, total_drank, len(recent), avg_recent)
    except Exception:
        return

    remaining = max(0, st.session_state.goal - total_drank)
    if res["status"] == "outside_hours":
        title, msg = "AI Insight", "AI tips are active from 7:00 AM to 10:00 PM."
    elif remaining == 0:
        title, msg = "AI Insight", "Goal reached today. Great job!"
    elif res["status"] == "on_track":
        title, msg = "AI Insight", "You're on track. Keep sipping at your own pace."
    else:
        amt = min(res["suggested_ml"], remaining)
        title = "AI Insight"
        msg = f"You're behind today's pace. Try sipping about {amt} ml over the next 2 hours."

    st.markdown(
        f"""
        <div class="app-card" style="margin-top: 14px; padding: 14px 18px;">
            <div style="font-size: 12px; font-weight: 700; color: #2563EB !important; text-transform: uppercase; letter-spacing: 0.04em;">{title}</div>
            <div style="font-size: 14px; font-weight: 600; margin-top: 6px;">{msg}</div>
            <div style="font-size: 11px; color: #64748B !important; margin-top: 8px;">
                Predicted next 2h intake: {res['predicted_2h_ml']} ml. Prototype trained on simulated data. Not medical advice.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================
# 9. HOME SCREEN
# ==========================================
def render_home():
    if st.session_state.sub_page == "Switch Cup":
        render_switch_cup()
        return

    total_drank = sum([log["amount"] for log in st.session_state.water_logs])
    pct = min(100, int((total_drank / st.session_state.goal) * 100))

    st.markdown(
        f"""
        <div style="display: flex; gap: 12px; margin-bottom: 12px;">
            <div class="app-card" style="flex: 1; text-align: center; margin-bottom: 0; padding: 18px 12px;">
                <div style="font-size: 12px; font-weight: 600; color: #64748B !important; text-transform: uppercase; letter-spacing: 0.04em;">Goal Target</div>
                <div style="font-size: 22px; font-weight: 800; color: #2563EB !important; margin-top: 2px;">{st.session_state.goal} <span style="font-size: 14px; font-weight: 600;">ml</span></div>
            </div>
            <div class="app-card" style="flex: 1; text-align: center; margin-bottom: 0; padding: 18px 12px;">
                <div style="font-size: 12px; font-weight: 600; color: #64748B !important; text-transform: uppercase; letter-spacing: 0.04em;">Progress</div>
                <div style="font-size: 22px; font-weight: 800; color: #0284C7 !important; margin-top: 2px;">{pct}%</div>
            </div>
        </div>

        <div class="app-card" style="margin-bottom: 16px; padding: 14px 18px;">
            <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: 700; color: #0F172A !important;">
                <span>Daily Intake: {total_drank} ml</span>
                <span style="color: #2563EB !important;">{st.session_state.goal - total_drank if total_drank < st.session_state.goal else 0} ml remaining</span>
            </div>
            <div class="progress-bar-bg">
                <div class="progress-bar-fill" style="width: {pct}%;"></div>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    c_btn, c_reset = st.columns([1.3, 1])
    with c_btn:
        if st.button("Switch Cup Size", use_container_width=True):
            st.session_state.sub_page = "Switch Cup"
            st.rerun()

    with c_reset:
        if st.button("Reset Water", use_container_width=True):
            st.session_state.water_logs = []
            st.rerun()

    if st.button(
        f"Quick Drink ({st.session_state.selected_cup}ml)",
        type="primary",
        use_container_width=True,
    ):
        now_str = datetime.now().strftime("%I:%M:%S %p").lower()
        st.session_state.water_logs.insert(
            0, {"time": now_str, "amount": st.session_state.selected_cup}
        )
        st.rerun()

    render_ai_insight(total_drank)

    if st.session_state.water_logs:
        st.markdown(
            "<h4 style='margin-top: 22px; margin-bottom: 12px; font-size: 15px; font-weight: 700; color: #0F172A !important;'>Today's Hydration Logs</h4>",
            unsafe_allow_html=True,
        )
        for log in st.session_state.water_logs:
            st.markdown(
                f"""
                <div class="app-card" style="display: flex; justify-content: space-between; align-items: center; padding: 14px 18px;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div style="background: rgba(224, 242, 254, 0.8); border-radius: 10px; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 18px;">🥛</div>
                        <span style="font-weight: 700; color: #2563EB !important; font-size: 14px;">{log['time']}</span>
                    </div>
                    <div style="font-weight: 800; color: #0F172A !important; font-size: 15px;">{log['amount']} <span style="font-size: 12px; font-weight: 600; color: #64748B !important;">ml</span></div>
                </div>
            """,
                unsafe_allow_html=True,
            )


# ==========================================
# 10. SWITCH CUP SCREEN WITH CUSTOM CUP SIZE
# ==========================================
def render_switch_cup():
    st.markdown(
        "<h3 style='font-size: 18px; font-weight: 700; color: #2563EB !important; margin-bottom: 14px;'>Select or Custom Cup Size</h3>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="app-card" style="text-align: center; padding: 12px; margin-bottom: 16px; background: #EFF6FF !important;">
            <span style="font-size: 13px; font-weight: 600; color: #1E40AF !important;">Currently Selected Size: <b>{st.session_state.selected_cup} ml</b></span>
        </div>
    """,
        unsafe_allow_html=True,
    )

    cups = [
        {"name": "100 ml", "val": 100, "icon": "☕"},
        {"name": "200 ml", "val": 200, "icon": "🥛"},
        {"name": "300 ml", "val": 300, "icon": "🥤"},
        {"name": "400 ml", "val": 400, "icon": "🍾"},
        {"name": "500 ml", "val": 500, "icon": "🧴"},
        {"name": "600 ml", "val": 600, "icon": "🏺"},
    ]

    cols = st.columns(3)
    for idx, cup in enumerate(cups):
        with cols[idx % 3]:
            st.markdown(
                f"""
                <div class="app-card" style="text-align: center; padding: 14px 8px; margin-bottom: 8px;">
                    <div style="font-size: 26px;">{cup['icon']}</div>
                    <div style="font-size: 13px; font-weight: 700; margin-top: 6px;">{cup['name']}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )
            if st.button(
                "Select",
                key=f"select_cup_{cup['val']}",
                use_container_width=True,
                type="primary" if st.session_state.selected_cup == cup["val"] else "secondary",
            ):
                st.session_state.selected_cup = cup["val"]
                st.session_state.sub_page = None
                st.rerun()

    st.markdown(
        "<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 18px 0;'>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h4 style='font-size: 15px; font-weight: 700; color: #0F172A !important; margin-bottom: 8px;'>Custom Cup Size</h4>",
        unsafe_allow_html=True,
    )

    custom_cup = st.number_input(
        "Enter custom water volume (ml):",
        min_value=1,
        max_value=5000,
        value=int(st.session_state.selected_cup),
        step=50,
        key="custom_cup_input",
    )

    if st.button("Set Custom Cup Size", type="primary", use_container_width=True):
        st.session_state.selected_cup = int(custom_cup)
        st.session_state.sub_page = None
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Back to Home", use_container_width=True):
        st.session_state.sub_page = None
        st.rerun()


# ==========================================
# 11. HISTORY SCREEN
# ==========================================
def render_history():
    st.markdown(
        "<h4 style='font-size: 15px; font-weight: 700; margin-bottom: 2px; color: #0F172A !important;'>Weekly Goal Tracker</h4>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='font-size: 12px; color: #64748B !important; margin-bottom: 14px; font-weight: 500;'>Automated tracking based on daily progress (Goal Met ✅ | Missed ❌)</p>",
        unsafe_allow_html=True,
    )

    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    today_str = datetime.now().strftime("%a")
    today_idx = days.index(today_str) if today_str in days else 0

    total_drank = sum([log["amount"] for log in st.session_state.water_logs])
    goal_completed = total_drank >= st.session_state.goal

    st.session_state.weekly_status[today_idx] = "pass" if goal_completed else "fail"

    cols = st.columns(7)

    for idx, day in enumerate(days):
        with cols[idx]:
            is_today = (idx == today_idx)
            header_color = "#2563EB" if is_today else "#64748B"
            st.markdown(
                f"<div style='text-align: center; font-size: 11px; font-weight: 700; color: {header_color} !important; margin-bottom: 4px;'>{day}</div>",
                unsafe_allow_html=True,
            )
            status = st.session_state.weekly_status[idx]
            icon = "✅" if status in ("pass", "trophy", "tick") else "❌"

            st.markdown(
                f"""
                <div style="text-align: center; background: #FFFFFF; border: 1px solid {'#2563EB' if is_today else '#CBD5E1'}; border-radius: 12px; padding: 10px 0; font-size: 18px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);">
                    {icon}
                </div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown(
        "<h4 style='margin-top: 26px; margin-bottom: 12px; font-size: 15px; font-weight: 700; color: #0F172A !important;'>Hydration Overview</h4>",
        unsafe_allow_html=True,
    )

    report_data = [
        ("Weekly Average", "2000 ml/day"),
        ("Monthly Average", "1850 ml/day"),
        ("Best Hydration Day", "2500 ml"),
        ("Total Water Consumed", "56,000 ml"),
    ]

    for label, val in report_data:
        st.markdown(
            f"""
            <div class="app-card" style="display: flex; justify-content: space-between; align-items: center; padding: 14px 18px;">
                <span style="color: #64748B !important; font-size: 13px; font-weight: 600;">{label}</span>
                <span style="color: #2563EB !important; font-weight: 800; font-size: 14px;">{val}</span>
            </div>
        """,
            unsafe_allow_html=True,
        )


# ==========================================
# 12. SHOP SCREEN
# ==========================================
def add_to_cart(prod):
    for item in st.session_state.cart:
        if item["name"] == prod["name"]:
            item["qty"] += 1
            st.session_state.shop_msg = (
                f"Updated quantity for {prod['name']} in cart!"
            )
            return
    st.session_state.cart.append(
        {
            "name": prod["name"],
            "price": prod["price"],
            "qty": 1,
            "desc": prod["desc"],
        }
    )
    st.session_state.shop_msg = f"Added {prod['name']} to your cart!"


def render_shop():
    if st.session_state.sub_page == "Cart":
        render_cart()
        return

    c_title, c_cart = st.columns([2, 1])
    with c_title:
        st.markdown(
            "<h3 style='margin:0; font-size: 20px; font-weight: 800; color: #2563EB !important;'>Bottle Shop</h3>",
            unsafe_allow_html=True,
        )
    with c_cart:
        total_items = sum([item["qty"] for item in st.session_state.cart])
        if st.button(
            f"Cart ({total_items})",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.sub_page = "Cart"
            st.session_state.shop_msg = None
            st.rerun()

    if st.session_state.shop_msg:
        st.success(st.session_state.shop_msg)

    search_query = st.text_input(
        "Search Bottles",
        placeholder="Search Aqua bottles...",
        key="shop_search",
    )
    sort_option = st.selectbox(
        "Sort by",
        ["Popularity", "Price: Low to High", "Price: High to Low"],
        key="shop_sort",
    )

    st.markdown(
        "<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True
    )

    products = [
        {
            "name": "AquaBig",
            "price": 85.00,
            "desc": "Thermoregulated double-walled construction keeps drinks cold for 24h.",
            "popularity": 1,
            "image_filename": "Untitled design (2).png",
        },
        {
            "name": "AquaMid",
            "price": 60.00,
            "desc": "Versatile mid-sized container constructed with food-grade steel.",
            "popularity": 2,
            "image_filename": "Untitled design (1).png",
        },
        {
            "name": "AquaSlim",
            "price": 45.00,
            "desc": "Sleek and lightweight insulated bottle designed for daily travel.",
            "popularity": 3,
            "image_filename": "Untitled design.png",
        },
    ]

    if search_query:
        products = [
            p
            for p in products
            if search_query.lower() in p["name"].lower()
            or search_query.lower() in p["desc"].lower()
        ]

    if sort_option == "Price: Low to High":
        products = sorted(products, key=lambda x: x["price"])
    elif sort_option == "Price: High to Low":
        products = sorted(products, key=lambda x: x["price"], reverse=True)

    if not products:
        st.info("No matching bottles found.")
        return

    for prod in products:
        col_img, col_info = st.columns([1, 2.2])

        with col_img:
            prod_img_path = os.path.join(
                script_dir, "assets", prod.get("image_filename", "")
            )
            if not os.path.exists(prod_img_path):
                prod_img_path = os.path.join(
                    r"C:\Users\User\Desktop\VS code\Aquasip\assets",
                    prod.get("image_filename", ""),
                )

            if os.path.exists(prod_img_path) and os.path.isfile(prod_img_path):
                st.image(prod_img_path, use_container_width=True)
            else:
                st.markdown(
                    """
                    <div style="background-color: #F1F5F9; border-radius: 14px; height: 110px; display: flex; align-items: center; justify-content: center; font-size: 38px;">
                        
                    </div>
                """,
                    unsafe_allow_html=True,
                )

        with col_info:
            st.markdown(
                f"<h4 style='margin:0; font-size: 16px; font-weight:800; color: #0F172A !important;'>{prod['name']}</h4>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<p style='font-size: 11.5px; color: #64748B !important; margin: 3px 0 6px 0; line-height: 1.4;'>{prod['desc']}</p>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='color: #2563EB !important; font-weight: 800; font-size: 15px; margin-bottom: 8px;'>RM {prod['price']:.2f}</div>",
                unsafe_allow_html=True,
            )

            b1, b2 = st.columns(2)
            with b1:
                if st.button(
                    "Add Cart",
                    key=f"add_{prod['name']}",
                    use_container_width=True,
                ):
                    add_to_cart(prod)
                    st.rerun()
            with b2:
                if st.button(
                    "Buy Now",
                    key=f"buy_{prod['name']}",
                    type="primary",
                    use_container_width=True,
                ):
                    st.session_state.cart = [
                        {
                            "name": prod["name"],
                            "price": prod["price"],
                            "qty": 1,
                            "desc": prod["desc"],
                        }
                    ]
                    st.session_state.sub_page = "Cart"
                    st.session_state.shop_msg = None
                    st.rerun()

        st.markdown(
            "<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 14px 0;'>",
            unsafe_allow_html=True,
        )


def render_cart():
    st.markdown(
        "<h3 style='color: #2563EB !important; text-align: center; font-size: 18px; font-weight: 800;'>Your Shopping Cart</h3>",
        unsafe_allow_html=True,
    )

    if not st.session_state.cart:
        st.info("Your cart is currently empty")
        if st.button(
            "Back to Shop", type="primary", use_container_width=True
        ):
            st.session_state.sub_page = None
            st.rerun()
        return

    subtotal = 0.0

    for idx, item in enumerate(st.session_state.cart):
        item_total = item["price"] * item["qty"]
        subtotal += item_total

        st.markdown(
            f"""
            <div class="app-card" style="margin-bottom: 10px; padding: 14px 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-size: 30px;">🧴</span>
                        <div>
                            <h4 style="margin:0; font-size: 15px; font-weight: 800; color: #0F172A !important;">{item['name']}</h4>
                            <span style="font-weight: 700; color: #2563EB !important; font-size: 12.5px;">RM {item['price']:.2f} each</span>
                        </div>
                    </div>
                    <div style="text-align: right; font-weight: 800; color: #0F172A !important; font-size: 15px;">
                        RM {item_total:.2f}
                    </div>
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

        c_dec, c_qty, c_inc, c_del = st.columns([1, 1.5, 1, 1.5])
        with c_dec:
            if st.button("➖", key=f"dec_{idx}", use_container_width=True):
                if item["qty"] > 1:
                    item["qty"] -= 1
                else:
                    st.session_state.cart.pop(idx)
                st.rerun()
        with c_qty:
            st.markdown(
                f"<div style='text-align:center; padding-top:6px; font-weight:800; font-size: 14px;'>Qty: {item['qty']}</div>",
                unsafe_allow_html=True,
            )
        with c_inc:
            if st.button("➕", key=f"inc_{idx}", use_container_width=True):
                item["qty"] += 1
                st.rerun()
        with c_del:
            if st.button(
                "Remove", key=f"del_{idx}", use_container_width=True
            ):
                st.session_state.cart.pop(idx)
                st.rerun()

        st.markdown(
            "<hr style='border: none; border-top: 1px dashed #E2E8F0; margin: 10px 0;'>",
            unsafe_allow_html=True,
        )

    discount = subtotal * 0.10 if subtotal > 50 else 0.0
    shipping = 5.00
    total = subtotal - discount + shipping

    st.markdown(
        f"""
        <div class="app-card" style="margin-top: 16px; padding: 18px;">
            <h5 style="margin: 0 0 12px 0; font-size: 15px; font-weight: 800; color: #0F172A !important;">Order Summary</h5>
            <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px; font-weight: 500;">
                <span style="color: #64748B !important;">Subtotal</span><span style="font-weight: 700;">RM {subtotal:.2f}</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px; font-weight: 500;">
                <span style="color: #64748B !important;">Discount</span><span style="color: #10B981 !important; font-weight: 700;">-RM {discount:.2f}</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 10px; font-weight: 500;">
                <span style="color: #64748B !important;">Shipping</span><span style="font-weight: 700;">RM {shipping:.2f}</span>
            </div>
            <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; font-weight: 800; font-size: 16px; color: #2563EB !important;">
                <span>Total Amount</span><span>RM {total:.2f}</span>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Back to Shop", use_container_width=True):
            st.session_state.sub_page = None
            st.rerun()
    with c2:
        if st.button(
            "Proceed Checkout", type="primary", use_container_width=True
        ):
            st.session_state.cart = []
            st.balloons()
            st.success("Transaction successful! Your order is on its way.")


# ==========================================
# 13. TIME & DAY HELPERS
# ==========================================
def get_nearest_quarter_time():
    now = datetime.now()
    minutes = now.minute
    remainder = minutes % 15
    add_mins = (15 - remainder) if remainder != 0 else 0
    target_dt = now.replace(second=0, microsecond=0) + timedelta(minutes=add_mins)
    return target_dt.strftime("%I:%M %p")


def generate_standard_quarter_times():
    times = []
    for h in range(24):
        for m in (0, 15, 30, 45):
            dt_obj = datetime(2026, 1, 1, h, m)
            times.append(dt_obj.strftime("%I:%M %p"))
    return times


def validate_and_format_time(user_input):
    if not user_input or not user_input.strip():
        return False, "Please enter an alarm time.", None

    time_str = user_input.strip().upper()

    # 12-hour format with AM/PM (e.g. 03:15 PM, 3:15PM, 12:00 AM)
    match_12 = re.match(r"^(\d{1,2}):(\d{2})\s*(AM|PM)$", time_str)
    if match_12:
        hr, mn, ampm = int(match_12.group(1)), int(match_12.group(2)), match_12.group(3)
        if not (1 <= hr <= 12):
            return False, f"Invalid hour '{hr}'. Hour must be between 1 and 12.", None
        if not (0 <= mn <= 59):
            return False, f"Invalid minute '{mn:02d}'. Minutes must be between 00 and 59.", None
        return True, None, f"{hr:02d}:{mn:02d} {ampm}"

    # 24-hour format (e.g. 15:30, 08:15)
    match_24 = re.match(r"^(\d{1,2}):(\d{2})$", time_str)
    if match_24:
        hr, mn = int(match_24.group(1)), int(match_24.group(2))
        if not (0 <= hr <= 23):
            return False, f"Invalid hour '{hr}'. 24-hour hour must be between 00 and 23.", None
        if not (0 <= mn <= 59):
            return False, f"Invalid minute '{mn:02d}'. Minutes must be between 00 and 59.", None
        ampm = "AM" if hr < 12 else "PM"
        hr12 = hr % 12
        if hr12 == 0:
            hr12 = 12
        return True, None, f"{hr12:02d}:{mn:02d} {ampm}"

    return (
        False,
        f"Invalid time format '{user_input}'. Please use format like '03:15 PM' or '15:30'.",
        None,
    )


def format_alarm_days(days_list):
    all_days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    weekends = ["Sun", "Sat"]

    if set(days_list) == set(all_days):
        return "Mon-Sun"
    elif set(days_list) == set(weekdays):
        return "Mon-Fri (Weekdays)"
    elif set(days_list) == set(weekends):
        return "Sat-Sun (Weekends)"
    else:
        sorted_days = [d for d in all_days if d in days_list]
        return ", ".join(sorted_days) if sorted_days else "No Days"


# Preset Callbacks for Active Days
def set_days_all():
    for d in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]:
        st.session_state[f"cb_day_{d}"] = True


def set_days_weekdays():
    for d in ["Mon", "Tue", "Wed", "Thu", "Fri"]:
        st.session_state[f"cb_day_{d}"] = True
    for d in ["Sun", "Sat"]:
        st.session_state[f"cb_day_{d}"] = False


def set_days_weekends():
    for d in ["Sun", "Sat"]:
        st.session_state[f"cb_day_{d}"] = True
    for d in ["Mon", "Tue", "Wed", "Thu", "Fri"]:
        st.session_state[f"cb_day_{d}"] = False


def set_days_clear():
    for d in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]:
        st.session_state[f"cb_day_{d}"] = False


# ==========================================
# 14. SETTINGS SCREEN
# ==========================================
def render_settings():
    st.markdown(
        "<h4 style='font-size: 15px; font-weight: 700; color: #0F172A !important;'>Hydration Goal</h4>",
        unsafe_allow_html=True,
    )

    new_goal = st.number_input(
        "Goal Target (ml):",
        value=st.session_state.goal,
        step=100,
        key="setting_goal_input",
    )
    if new_goal != st.session_state.goal:
        st.session_state.goal = new_goal

    st.markdown(
        "<h4 style='margin-top: 22px; font-size: 15px; font-weight: 700; color: #0F172A !important;'>Reminders & Sound Customization</h4>",
        unsafe_allow_html=True,
    )

    if st.session_state.alarm_success_msg:
        st.success(st.session_state.alarm_success_msg)

    # ------------------------------------------
    # EXPANDER: ALARM & SOUND SETUP
    # ------------------------------------------
    with st.expander("➕ Add Custom Alarm", expanded=True if not st.session_state.reminders else False):

        # --- 1. UNIFIED TIME SELECTION & DIRECT MANUAL ENTRY BAR ---
        default_q_time = get_nearest_quarter_time()
        standard_times = generate_standard_quarter_times()

        st.markdown(
            "<div style='font-size: 13px; font-weight: 700; color: #0F172A !important; margin-bottom: 4px;'>Alarm Time:</div>",
            unsafe_allow_html=True,
        )

        col_select, col_type = st.columns([1.1, 1.3])

        with col_select:
            preset_idx = standard_times.index(default_q_time) if default_q_time in standard_times else 0
            selected_preset_time = st.selectbox(
                "Pick Standard Time:",
                options=standard_times,
                index=preset_idx,
                key="unified_time_selectbox",
            )

        with col_type:
            typed_time_val = st.text_input(
                "Or Type Custom Time:",
                value=selected_preset_time,
                placeholder="e.g. 03:47 PM or 15:47",
                key="unified_time_text_input",
            )

        # Validate User Time Entry
        is_valid_time, time_err_msg, formatted_time = validate_and_format_time(typed_time_val)

        if not is_valid_time:
            st.error(time_err_msg)

        st.markdown("<hr style='border:none; border-top:1px solid #E2E8F0; margin:14px 0;'>", unsafe_allow_html=True)

        # --- 2. ARRANGED ACTIVE DAYS SELECTOR ---
        st.markdown(
            "<div style='font-size: 13px; font-weight: 700; color: #0F172A !important; margin-bottom: 8px;'>Active Days:</div>",
            unsafe_allow_html=True,
        )

        pr_row1_col1, pr_row1_col2 = st.columns(2)
        with pr_row1_col1:
            st.button("All Days", key="btn_preset_all", on_click=set_days_all, use_container_width=True)
        with pr_row1_col2:
            st.button("Weekdays", key="btn_preset_weekdays", on_click=set_days_weekdays, use_container_width=True)

        pr_row2_col1, pr_row2_col2 = st.columns(2)
        with pr_row2_col1:
            st.button("Weekends", key="btn_preset_weekends", on_click=set_days_weekends, use_container_width=True)
        with pr_row2_col2:
            st.button("Clear", key="btn_preset_clear", on_click=set_days_clear, use_container_width=True)

        st.markdown("<div style='margin-bottom: 6px;'></div>", unsafe_allow_html=True)

        day_cols = st.columns(7)
        selected_days = []

        for idx, d_name in enumerate(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]):
            cb_key = f"cb_day_{d_name}"
            with day_cols[idx]:
                checked = st.checkbox(
                    d_name,
                    key=cb_key,
                )
                if checked:
                    selected_days.append(d_name)

        st.markdown("<hr style='border:none; border-top:1px solid #E2E8F0; margin:14px 0;'>", unsafe_allow_html=True)

        # --- 3. ALARM SOUND OPTIONS & SNOOZE TIME DURATION SETTING ---
        st.markdown(
            "<div style='font-size: 13px; font-weight: 700; color: #0F172A !important; margin-bottom: 6px;'>Alarm Sound & Snooze Options:</div>",
            unsafe_allow_html=True,
        )

        sound_choices = [
            "Aqua Chime",
            "Zen Bell",
            "Digital Beep",
            "Marimba Rise",
            "Custom Audio Upload",
        ]

        selected_sound = st.selectbox(
            "Select Sound Preset:",
            sound_choices,
            index=0,
            key="alarm_sound_preset_selectbox",
        )

        snooze_options = [5, 10, 15, 20, 30]
        curr_snooze_idx = snooze_options.index(st.session_state.snooze_duration) if st.session_state.snooze_duration in snooze_options else 0
        selected_snooze = st.selectbox(
            "Snooze Duration:",
            snooze_options,
            format_func=lambda x: f"{x} Minutes",
            index=curr_snooze_idx,
            key="snooze_duration_selectbox",
        )
        st.session_state.snooze_duration = selected_snooze

        if selected_sound == "Custom Audio Upload":
            uploaded_audio_file = st.file_uploader(
                "Upload Custom Sound File (.mp3, .wav, .ogg):",
                type=["mp3", "wav", "ogg"],
                key="audio_file_uploader_widget",
            )
            if uploaded_audio_file is not None:
                audio_bytes = uploaded_audio_file.read()
                mime = uploaded_audio_file.type or "audio/mp3"
                encoded = base64.b64encode(audio_bytes).decode()
                st.session_state.custom_sound_b64 = f"data:{mime};base64,{encoded}"
                st.success("Custom audio file loaded successfully!")

        st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

        # --- 4. SAVE & TEST SOUND BUTTONS ---
        c_save, c_test = st.columns([2, 1])
        with c_save:
            if st.button(
                f"Save Alarm ({formatted_time if is_valid_time else 'Invalid'})",
                type="primary",
                use_container_width=True,
            ):
                if not is_valid_time:
                    st.session_state.alarm_success_msg = time_err_msg
                elif not selected_days:
                    st.session_state.alarm_success_msg = (
                        "Please select at least one active day for the alarm!"
                    )
                else:
                    new_alarm_entry = {
                        "time": formatted_time,
                        "days": selected_days,
                        "sound": selected_sound,
                    }
                    if new_alarm_entry not in st.session_state.reminders:
                        st.session_state.reminders.append(new_alarm_entry)
                        day_str = format_alarm_days(selected_days)
                        st.session_state.alarm_success_msg = (
                            f"Alarm set for {formatted_time} ({day_str}) [{selected_sound}]!"
                        )
                    else:
                        st.session_state.alarm_success_msg = (
                            f"Alarm for {formatted_time} is already set."
                        )
                st.rerun()

        with c_test:
            if st.button("Test Sound", use_container_width=True):
                escaped_sound = json.dumps(selected_sound)
                test_sound_js = f"""
                <script>
                (function() {{
                    if (window.parent && typeof window.parent.playAquaSipAlarmSound === 'function') {{
                        window.parent.playAquaSipAlarmSound({escaped_sound});
                    }}
                }})();
                </script>
                """
                components.html(test_sound_js, height=0, width=0)

    # --- ACTIVE ALARMS LIST ---
    if not st.session_state.reminders:
        st.info("No active alarms. Set a custom hydration alarm above!")
    else:
        for idx, alarm in enumerate(list(st.session_state.reminders)):
            if isinstance(alarm, str):
                alarm_time = alarm
                alarm_days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
                alarm_sound = " Aqua Chime"
            else:
                alarm_time = alarm.get("time", "")
                alarm_days = alarm.get("days", ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])
                alarm_sound = alarm.get("sound", " Aqua Chime")

            day_badge = format_alarm_days(alarm_days)

            col_info, col_del = st.columns([3, 1])
            with col_info:
                st.markdown(
                    f"""
                    <div class="app-card" style="margin-bottom: 8px; padding: 12px 16px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div style="font-weight: 800; font-size: 15px; color: #0F172A !important;"> {alarm_time}</div>
                            <span style="font-size: 11px; font-weight:700; color:#2563EB;">{alarm_sound}</span>
                        </div>
                        <div style="margin-top: 6px;">
                            <span style="font-size: 11px; font-weight: 700; background: #E0F2FE; color: #0369A1 !important; padding: 3px 8px; border-radius: 6px;">{day_badge}</span>
                        </div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
            with col_del:
                if st.button(
                    "Delete", key=f"del_alarm_{idx}", use_container_width=True
                ):
                    st.session_state.reminders.pop(idx)
                    st.session_state.alarm_success_msg = None
                    st.rerun()


# ==========================================
# 15. MAIN ROUTER
# ==========================================
def main():
    if not st.session_state.logged_in:
        render_auth()
    else:
        total_drank = sum(
            [log["amount"] for log in st.session_state.water_logs]
        )
        pct = min(100, int((total_drank / st.session_state.goal) * 100))

        render_draggable_avatar(pct)
        render_realtime_timer_and_alarm(st.session_state.reminders, st.session_state.custom_sound_b64, st.session_state.snooze_duration)
        selected_page = render_app_header()

        if selected_page == "Home":
            render_home()
        elif selected_page == "History":
            render_history()
        elif selected_page == "Shop":
            render_shop()
        elif selected_page == "Setting":
            render_settings()


if __name__ == "__main__":
    main()