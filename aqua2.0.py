"""AquaSip — a polished, self-contained Streamlit hydration companion.

Run with: streamlit run aquasip_app.py
"""

import base64
import html
from datetime import datetime, time

import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="AquaSip | Hydration, beautifully",
    page_icon="💧",
    layout="centered",
    initial_sidebar_state="collapsed",
)


PRODUCTS = [
    {
        "name": "AquaBig",
        "price": 85.00,
        "description": "1L thermal powerhouse — ice-cold hydration for 24 hours.",
        "detail": "1,000 ml · double-wall steel",
        "accent": "#73D7FF",
        "dark": "#0E5F9E",
        "tag": "BEST SELLER",
        "popularity": 1,
    },
    {
        "name": "AquaMid",
        "price": 60.00,
        "description": "The all-day essential, crafted from food-grade steel.",
        "detail": "650 ml · leakproof lid",
        "accent": "#A8F0D2",
        "dark": "#15856B",
        "tag": "EVERYDAY",
        "popularity": 2,
    },
    {
        "name": "AquaSlim",
        "price": 45.00,
        "description": "A lightweight, sleek bottle made for life in motion.",
        "detail": "450 ml · travel-light",
        "accent": "#D8C5FF",
        "dark": "#714AB4",
        "tag": "NEW DROP",
        "popularity": 3,
    },
]


def init_state():
    """Create all session values once, so each original app function stays available."""
    defaults = {
        "logged_in": False,
        "auth_mode": "Log In",
        "current_tab": "Home",
        "sub_page": None,
        "user": {"name": "Alex", "email": "alex@example.com"},
        "goal": 2000,
        "selected_cup": 200,
        "water_logs": [
            {"time": "10:30 p.m.", "amount": 200},
            {"time": "09:30 p.m.", "amount": 100},
            {"time": "08:30 p.m.", "amount": 150},
            {"time": "07:30 p.m.", "amount": 100},
        ],
        "weekly_status": [True, True, True, True, True, False, False],
        "cart": [],
        "shop_msg": None,
        "alarm_success_msg": None,
        "reminders": ["06:30 AM", "09:00 AM", "12:30 PM"],
        "order_success": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def inject_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap');

        :root {
            --ink: #12253E;
            --muted: #71839A;
            --sky: #23A9EA;
            --deep-sky: #087FBE;
            --mint: #58D6A7;
            --paper: #F7FBFE;
            --line: #E4EDF3;
            --card: rgba(255,255,255,.88);
        }
        .stApp {
            background:
                radial-gradient(circle at 5% 2%, rgba(78, 203, 255, .21), transparent 22rem),
                radial-gradient(circle at 94% 20%, rgba(117, 236, 196, .17), transparent 18rem),
                #F7FBFE;
            color: var(--ink);
        }
        #MainMenu, footer, header {visibility: hidden;}
        .block-container {max-width: 760px; padding: 1.25rem 1.1rem 4.5rem;}
        html, body, [class*="css"] {font-family: 'DM Sans', sans-serif; color: var(--ink);}
        h1,h2,h3,h4,h5 {font-family: 'Outfit', sans-serif !important; letter-spacing: -.035em; color: var(--ink) !important;}
        p {color: var(--muted);}
        [data-testid="stVerticalBlock"] {gap: .65rem;}
        [data-testid="stForm"] {border: 0; padding: 0;}

        .brand-lockup {display:flex; align-items:center; gap:10px;}
        .brand-mark {width:40px;height:40px;border-radius:14px;display:grid;place-items:center;
            background:linear-gradient(145deg,#35C6F8,#1688D1);box-shadow:0 8px 20px rgba(27,151,214,.24);}
        .brand-name {font:700 23px/1 'Outfit',sans-serif;letter-spacing:-.06em;color:#12253E;}
        .eyebrow {font-size:10px;font-weight:800;letter-spacing:.15em;color:#1688D1;text-transform:uppercase;}
        .app-card, .metric-card, .product-shell, .log-row, .setting-card {
            background:var(--card);border:1px solid rgba(222,235,243,.9);box-shadow:0 13px 32px rgba(31,89,124,.06);
            border-radius:22px;
        }
        .section-title {font:700 20px/1.2 'Outfit',sans-serif;margin:22px 0 3px;color:var(--ink);letter-spacing:-.04em;}
        .section-copy {font-size:13px;margin:0 0 12px;color:var(--muted);}

        .hero-card {position:relative;overflow:hidden;min-height:280px;padding:24px;border-radius:28px;
            color:#fff;background:linear-gradient(135deg,#0B77BC 0%,#15A7DD 53%,#62D6B7 130%);
            box-shadow:0 22px 45px rgba(16,133,192,.24);}
        .hero-card:before,.hero-card:after {content:"";position:absolute;border-radius:50%;border:1px solid rgba(255,255,255,.15);}
        .hero-card:before {width:315px;height:315px;right:-145px;top:-145px;}
        .hero-card:after {width:160px;height:160px;right:-45px;bottom:-96px;background:rgba(255,255,255,.08);}
        .hero-content {position:relative;z-index:1;display:flex;justify-content:space-between;align-items:center;gap:16px;}
        .hero-kicker {font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;opacity:.72;}
        .hero-title {font:700 30px/1.05 'Outfit',sans-serif;letter-spacing:-.055em;margin:8px 0;color:#fff;}
        .hero-copy {font-size:13px;line-height:1.45;max-width:260px;color:rgba(255,255,255,.82);margin:0;}
        .goal-chip {display:inline-flex;margin-top:16px;align-items:center;gap:6px;padding:7px 10px;border-radius:999px;
            font-size:11px;font-weight:700;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.2);}
        .progress-orb {--p:25%;width:138px;height:138px;flex:0 0 auto;border-radius:50%;padding:9px;
            background:conic-gradient(#fff var(--p),rgba(255,255,255,.21) 0);box-shadow:0 10px 24px rgba(0,62,108,.2);}
        .progress-inner {width:100%;height:100%;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;
            color:#fff;background:linear-gradient(140deg,#0F8ACA,#1AA9DD);}
        .progress-number {font:800 30px/1 'Outfit',sans-serif;letter-spacing:-.06em;}
        .progress-caption {font-size:10px;opacity:.75;margin-top:4px;}
        .hero-bottom {position:relative;z-index:1;margin-top:24px;display:flex;gap:18px;padding-top:16px;border-top:1px solid rgba(255,255,255,.18);}
        .hero-stat b {display:block;font:700 15px/1.2 'Outfit',sans-serif;color:#fff;}.hero-stat span{font-size:10px;opacity:.7;}

        .metric-card {padding:15px 16px;min-height:74px;}.metric-icon{font-size:18px;}.metric-label{font-size:11px;color:var(--muted);margin-top:4px;}.metric-value{font:700 18px/1.1 'Outfit',sans-serif;color:var(--ink);margin-top:1px;}
        .log-row {display:flex;justify-content:space-between;align-items:center;padding:13px 15px;margin-bottom:8px;transition:transform .2s ease, box-shadow .2s ease;}
        .log-row:hover,.product-shell:hover {transform:translateY(-2px);box-shadow:0 18px 36px rgba(31,89,124,.10);}.log-time{font-weight:700;font-size:13px;color:var(--ink);}.log-meta{font-size:11px;color:var(--muted);margin-top:2px;}.log-amount{font:700 15px 'Outfit',sans-serif;color:#087FBE;}.drop-dot{width:31px;height:31px;border-radius:11px;display:grid;place-items:center;background:#E9F8FF;margin-right:10px;}
        .mini-badge {display:inline-flex;align-items:center;gap:5px;padding:5px 8px;border-radius:999px;background:#EEF9F5;color:#188765;font-size:10px;font-weight:800;letter-spacing:.04em;}
        .empty-state {padding:26px;text-align:center;border:1px dashed #CBDCE6;border-radius:20px;color:var(--muted);background:rgba(255,255,255,.55);}

        .cup-card {padding:16px 10px;text-align:center;border-radius:18px;border:1px solid var(--line);background:rgba(255,255,255,.7);}.cup-card.selected{background:#E8F8FF;border-color:#72CCEF;}.cup-icon{font-size:26px;}.cup-size{font:700 14px 'Outfit',sans-serif;margin-top:6px;color:var(--ink);}.cup-label{font-size:10px;color:var(--muted);}
        .week-card {padding:13px 8px;text-align:center;border-radius:16px;background:rgba(255,255,255,.74);border:1px solid var(--line);}.week-day{font-size:10px;font-weight:800;color:var(--muted);text-transform:uppercase;}.week-icon{font-size:19px;margin-top:4px;}
        .product-shell {padding:15px;border-radius:22px;min-height:315px;transition:transform .2s ease,box-shadow .2s ease;}.product-art{height:118px;border-radius:17px;display:grid;place-items:center;margin-bottom:12px;overflow:hidden;}.product-tag{font-size:9px;font-weight:800;letter-spacing:.1em;color:#0D83BF;}.product-name{font:700 20px/1 'Outfit',sans-serif;margin:5px 0;color:var(--ink);}.product-detail{font-size:10px;color:var(--muted);}.product-price{font:700 18px 'Outfit',sans-serif;color:#087FBE;margin:8px 0;}
        .cart-item {padding:15px;margin-bottom:8px;}.cart-item-name{font:700 16px 'Outfit',sans-serif;color:var(--ink);}.summary-card {padding:18px;}.summary-line {display:flex;justify-content:space-between;font-size:13px;margin:8px 0;color:var(--muted);}.summary-total{display:flex;justify-content:space-between;margin-top:13px;padding-top:13px;border-top:1px solid var(--line);font:700 19px 'Outfit',sans-serif;color:var(--ink);}
        .setting-card{padding:16px;margin:8px 0;}.alarm-time{font:700 17px 'Outfit',sans-serif;color:var(--ink);}.alarm-sub{font-size:11px;color:var(--muted);margin-top:3px;}

        .stButton>button {min-height:40px;border-radius:13px;border:1px solid #D9E7EF;background:rgba(255,255,255,.84);color:#20405A;font-weight:700;font-size:12px;transition:all .2s ease;}
        .stButton>button:hover {border-color:#62C6ED;color:#087FBE;transform:translateY(-1px);box-shadow:0 8px 17px rgba(28,146,202,.11);}
        .stButton>button[kind="primary"] {border:0;color:#fff;background:linear-gradient(135deg,#0F88C8,#22B9E9);box-shadow:0 8px 18px rgba(19,150,210,.23);}.stButton>button[kind="primary"]:hover {color:#fff;background:linear-gradient(135deg,#0879B8,#13AEDD);}
        div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-baseweb="select"] > div {border-radius:13px!important;border-color:#D9E7EF!important;background:rgba(255,255,255,.85)!important;color:var(--ink)!important;}
        div[data-testid="stNumberInputContainer"] {border-radius:13px!important;overflow:hidden;border:1px solid #D9E7EF!important;}div[data-testid="stNumberInputContainer"] input{border:0!important;}
        div[data-testid="stExpander"] {border:1px solid #DFEBF2;border-radius:16px;background:rgba(255,255,255,.7);overflow:hidden;}div[data-testid="stExpander"] summary {font-weight:700;color:var(--ink);}
        [data-testid="stAlert"] {border-radius:14px;}
        @media(max-width: 520px){.block-container{padding:1rem .8rem 5rem}.hero-card{padding:20px;min-height:250px}.hero-title{font-size:25px}.progress-orb{width:110px;height:110px}.progress-number{font-size:25px}.hero-copy{font-size:12px}.product-shell{min-height:0}.brand-name{font-size:21px;}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def brand(mark_only=False):
    mark = """
        <div class="brand-mark" aria-label="AquaSip">
          <svg width="22" height="25" viewBox="0 0 22 25" fill="none" aria-hidden="true">
            <path d="M11 1.7C7.5 6.7 3.4 10.7 3.4 15.2a7.6 7.6 0 0015.2 0C18.6 10.7 14.5 6.7 11 1.7z" fill="white" fill-opacity=".96"/>
            <path d="M7.7 16.1c.2 1.7 1.5 3 3.3 3.2" stroke="#19A3DC" stroke-width="1.6" stroke-linecap="round"/>
          </svg>
        </div>
    """
    if mark_only:
        return mark
    return f'<div class="brand-lockup">{mark}<div class="brand-name">AquaSip</div></div>'


def total_water():
    return sum(log["amount"] for log in st.session_state.water_logs)


def current_percent():
    return min(100, round(total_water() / max(st.session_state.goal, 1) * 100))


def add_water(amount=None):
    amount = amount or st.session_state.selected_cup
    st.session_state.water_logs.insert(
        0, {"time": datetime.now().strftime("%I:%M %p").lower(), "amount": amount}
    )


def bottle_svg(accent, dark):
    """Inline product artwork: no missing image paths or external assets."""
    svg = f'''<svg width="112" height="140" viewBox="0 0 112 140" fill="none" xmlns="http://www.w3.org/2000/svg">
      <ellipse cx="57" cy="128" rx="33" ry="7" fill="#0D5E91" opacity=".12"/>
      <rect x="42" y="8" width="30" height="13" rx="5" fill="{dark}"/><rect x="39" y="17" width="36" height="10" rx="5" fill="#F6FDFF"/>
      <path d="M33 29c0-6 5-10 11-10h26c6 0 11 4 11 10l4 82c.6 13-9.8 18-28 18s-28.6-5-28-18l4-82Z" fill="{accent}"/>
      <path d="M37 34c0-5 4-9 9-9h22c5 0 9 4 9 9l3 72c.4 10-8 15-23 15s-23.4-5-23-15l3-72Z" fill="white" fill-opacity=".38"/>
      <path d="M44 35c-3 17-3 49-1 66" stroke="white" stroke-opacity=".72" stroke-width="4" stroke-linecap="round"/>
      <rect x="44" y="66" width="26" height="18" rx="5" fill="{dark}" opacity=".92"/><path d="M49 75h16" stroke="white" stroke-width="2" stroke-linecap="round"/>
    </svg>'''
    return base64.b64encode(svg.encode()).decode()


def render_draggable_avatar(pct):
    """The original draggable bottle companion, rebuilt to feel intentional."""
    messages = (
        ["A tiny sip now?", "Your future self says thank you.", "Hydration looks good on you."]
        if pct < 40
        else ["You are building a brilliant habit.", "Halfway there — keep the flow going!", "Aqua high-five!"]
        if pct < 100
        else ["Goal complete. You did that!", "Hydration hero unlocked!", "What a refreshing win."]
    )
    mascot = """
    <script>
    (() => {
      const doc = window.parent.document;
      if (window.parent.aquaMascotCleanup) window.parent.aquaMascotCleanup();
      const old = doc.getElementById('aquasip-mascot'); if (old) old.remove();
      const node = doc.createElement('div'); node.id = 'aquasip-mascot';
      node.style.cssText = 'position:fixed;right:20px;bottom:18px;z-index:999999;display:flex;flex-direction:column;align-items:center;cursor:grab;user-select:none;touch-action:none;filter:drop-shadow(0 11px 14px rgba(12,101,149,.18))';
      node.innerHTML = `<div id="aqua-note" style="max-width:150px;margin-bottom:5px;padding:8px 10px;border:1px solid #C8E9F7;border-radius:13px;background:#fff;color:#18425D;font:700 11px/1.3 Arial,sans-serif;text-align:center;box-shadow:0 8px 18px rgba(17,75,109,.12)"></div><div id="aqua-bottle" style="width:62px;height:75px;animation:aquaBob 3s ease-in-out infinite"><svg viewBox="0 0 80 100" width="62" height="75"><defs><clipPath id="bottleClip"><path d="M24 23h32l4 59c.5 9-8 13-20 13S19.5 91 20 82l4-59Z"/></clipPath></defs><path d="M29 8h22v13H29z" rx="3" fill="#0A80BE"/><path d="M24 23h32l4 59c.5 9-8 13-20 13S19.5 91 20 82l4-59Z" fill="#F7FDFF" stroke="#1598D0" stroke-width="3"/><rect id="aqua-fill" x="18" y="__WATER_Y__" width="46" height="50" fill="#54D0F5" clip-path="url(#bottleClip)"/><circle cx="33" cy="49" r="2.7" fill="#16435F"/><circle cx="47" cy="49" r="2.7" fill="#16435F"/><path d="M34 58q6 5 12 0" stroke="#16435F" stroke-width="2.2" fill="none" stroke-linecap="round"/></svg></div>`;
      const style = doc.createElement('style'); style.id = 'aqua-mascot-style'; style.textContent='@keyframes aquaBob{0%,100%{transform:translateY(0) rotate(-1deg)}50%{transform:translateY(-6px) rotate(1deg)}}'; doc.head.appendChild(style);
      doc.body.appendChild(node);
      const lines = __MESSAGES__; let i = 0; const note = node.querySelector('#aqua-note');
      const show = () => { note.style.opacity=0; setTimeout(()=>{note.textContent=lines[i++ % lines.length];note.style.opacity=1},180);}; show();
      const timer = setInterval(show, 6200); let drag=false, sx=0, sy=0, left=0, top=0;
      const down = e => {drag=true;node.setPointerCapture?.(e.pointerId);const r=node.getBoundingClientRect();sx=e.clientX;sy=e.clientY;left=r.left;top=r.top;node.style.cursor='grabbing';};
      const move = e => {if(!drag)return;node.style.left=Math.max(0,Math.min(innerWidth-155,left+e.clientX-sx))+'px';node.style.top=Math.max(0,Math.min(innerHeight-120,top+e.clientY-sy))+'px';node.style.right='auto';node.style.bottom='auto';};
      const up = () => {drag=false;node.style.cursor='grab';};
      node.addEventListener('pointerdown',down);doc.addEventListener('pointermove',move);doc.addEventListener('pointerup',up);
      window.parent.aquaMascotCleanup=()=>{clearInterval(timer);node.remove();style.remove();doc.removeEventListener('pointermove',move);doc.removeEventListener('pointerup',up)};
    })();
    </script>
    """.replace("__WATER_Y__", str(83 - int(pct * 0.43))).replace("__MESSAGES__", str(messages).replace("'", '"'))
    components.html(mascot, height=0, width=0)


def render_auth():
    st.markdown('<div style="height:22px"></div>', unsafe_allow_html=True)
    st.markdown(
        f'''<div class="app-card" style="padding:28px 24px 22px;max-width:460px;margin:0 auto;">
          <div style="display:flex;justify-content:center">{brand()}</div>
          <div style="text-align:center;margin:25px 0 20px"><div class="eyebrow">YOUR DAILY RESET</div>
          <h1 style="font-size:31px;margin:8px 0 8px">Small sips.<br>Meaningful change.</h1>
          <p style="font-size:13px;margin:0">A beautifully simple way to build your hydration ritual.</p></div></div>''',
        unsafe_allow_html=True,
    )
    mode = st.session_state.auth_mode
    with st.form("auth_form", clear_on_submit=False):
        st.markdown(
            f'<h3 style="font-size:18px;margin:14px 0 4px">{"Create your account" if mode == "Create Account" else "Welcome back"}</h3><p class="section-copy">{"Start your hydrated era in seconds." if mode == "Create Account" else "Pick up your hydration streak where you left it."}</p>',
            unsafe_allow_html=True,
        )
        email = st.text_input("Email address", value=st.session_state.user["email"] if mode == "Log In" else "", placeholder="name@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Start sipping  →" if mode == "Create Account" else "Sign in  →", type="primary", use_container_width=True)
    if submitted:
        if mode == "Create Account" and not email.strip():
            st.warning("Add an email address to create your AquaSip profile.")
        else:
            if email.strip():
                st.session_state.user = {"name": email.split("@")[0].replace(".", " ").title(), "email": email.strip()}
            st.session_state.logged_in = True
            st.rerun()
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        if st.button("Create account", use_container_width=True, type="primary" if mode == "Create Account" else "secondary"):
            st.session_state.auth_mode = "Create Account"; st.rerun()
    with right:
        if st.button("I already have an account", use_container_width=True, type="primary" if mode == "Log In" else "secondary"):
            st.session_state.auth_mode = "Log In"; st.rerun()


def render_app_header():
    left, right = st.columns([4.2, 1])
    with left:
        st.markdown(brand(), unsafe_allow_html=True)
    with right:
        if st.button("Log out", key="logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.sub_page = None
            st.rerun()

    st.markdown('<div style="height:3px"></div>', unsafe_allow_html=True)
    tabs = [("Home", "◉"), ("History", "◌"), ("Shop", "♧"), ("Setting", "⚙")]
    nav = st.columns(4)
    for column, (label, icon) in zip(nav, tabs):
        with column:
            if st.button(f"{icon}  {label}", key=f"nav_{label}", type="primary" if st.session_state.current_tab == label else "secondary", use_container_width=True):
                st.session_state.current_tab = label
                st.session_state.sub_page = None
                st.rerun()
    st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
    return st.session_state.current_tab


def render_home():
    if st.session_state.sub_page == "Switch Cup":
        render_switch_cup()
        return
    total, goal, pct = total_water(), st.session_state.goal, current_percent()
    remaining = max(goal - total, 0)
    name = html.escape(st.session_state.user["name"].split()[0])
    greeting = "You’ve made a fresh start today." if pct < 40 else "Your hydration rhythm is taking shape." if pct < 100 else "Today’s hydration goal is in the bag."
    st.markdown(
        f'''<div class="hero-card"><div class="hero-content"><div><div class="hero-kicker">GOOD DAY, {name.upper()} ✦</div>
          <div class="hero-title">Hydrate your<br>brightest self.</div><p class="hero-copy">{greeting}</p>
          <div class="goal-chip">✦ {remaining:,} ml left to your goal</div></div>
          <div class="progress-orb" style="--p:{pct}%"><div class="progress-inner"><div class="progress-number">{pct}%</div><div class="progress-caption">complete</div></div></div></div>
          <div class="hero-bottom"><div class="hero-stat"><b>{total:,} ml</b><span>water logged</span></div><div class="hero-stat"><b>{goal:,} ml</b><span>daily intention</span></div><div class="hero-stat"><b>{max(1, sum(st.session_state.weekly_status))} days</b><span>this week</span></div></div></div>''',
        unsafe_allow_html=True,
    )
    a, b, c = st.columns(3)
    with a: st.markdown(f'<div class="metric-card"><div class="metric-icon">◒</div><div class="metric-label">Selected cup</div><div class="metric-value">{st.session_state.selected_cup} ml</div></div>', unsafe_allow_html=True)
    with b: st.markdown(f'<div class="metric-card"><div class="metric-icon">◈</div><div class="metric-label">Remaining</div><div class="metric-value">{remaining:,} ml</div></div>', unsafe_allow_html=True)
    with c: st.markdown(f'<div class="metric-card"><div class="metric-icon">✦</div><div class="metric-label">Next milestone</div><div class="metric-value">{min(100, ((pct // 25) + 1) * 25)}%</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Make a moment of it</div><p class="section-copy">One intentional tap. One healthier habit.</p>', unsafe_allow_html=True)
    quick, cup = st.columns([1.65, 1])
    with quick:
        if st.button(f"Add {st.session_state.selected_cup} ml  💧", type="primary", use_container_width=True):
            add_water(); st.rerun()
    with cup:
        if st.button("Change cup", use_container_width=True):
            st.session_state.sub_page = "Switch Cup"; st.rerun()

    st.markdown('<div class="section-title">Today’s flow</div><p class="section-copy">Every sip is a vote for the energy you want to feel.</p>', unsafe_allow_html=True)
    if not st.session_state.water_logs:
        st.markdown('<div class="empty-state">Your first sip of the day is waiting for you. 💧</div>', unsafe_allow_html=True)
    for index, log in enumerate(st.session_state.water_logs):
        st.markdown(
            f'''<div class="log-row"><div style="display:flex;align-items:center"><div class="drop-dot">💧</div><div><div class="log-time">{html.escape(log["time"])}</div><div class="log-meta">Hydration entry #{len(st.session_state.water_logs)-index}</div></div></div><div class="log-amount">+{log["amount"]} ml</div></div>''',
            unsafe_allow_html=True,
        )


def render_switch_cup():
    st.markdown('<div class="eyebrow">PERSONALISE YOUR POUR</div><div class="section-title" style="margin-top:5px">Choose your cup</div><p class="section-copy">We’ll remember it for your next quick-add.</p>', unsafe_allow_html=True)
    cups = [(100, "☕", "A tiny reset"), (200, "🥛", "Your usual"), (300, "🥤", "A generous sip"), (400, "🧊", "A cool refill"), (500, "🧴", "Big energy"), (600, "🏺", "Full focus")]
    for row_start in range(0, len(cups), 3):
        cols = st.columns(3)
        for col, (size, icon, label) in zip(cols, cups[row_start:row_start + 3]):
            selected = st.session_state.selected_cup == size
            with col:
                st.markdown(f'<div class="cup-card {"selected" if selected else ""}"><div class="cup-icon">{icon}</div><div class="cup-size">{size} ml</div><div class="cup-label">{label}</div></div>', unsafe_allow_html=True)
                if st.button("Selected" if selected else "Choose", key=f"cup_{size}", type="primary" if selected else "secondary", use_container_width=True):
                    st.session_state.selected_cup = size
                    st.session_state.sub_page = None
                    st.rerun()
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    if st.button("← Back to today", use_container_width=True):
        st.session_state.sub_page = None; st.rerun()


def render_history():
    success_count = sum(st.session_state.weekly_status)
    st.markdown(f'<div class="eyebrow">YOUR CONSISTENCY, VISUALISED</div><div class="section-title" style="margin-top:5px">A week in motion</div><p class="section-copy">{success_count} intentional day{"s" if success_count != 1 else ""} this week. Tap any day to update it.</p>', unsafe_allow_html=True)
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    columns = st.columns(7)
    for i, (column, day) in enumerate(zip(columns, days)):
        with column:
            state = st.session_state.weekly_status[i]
            st.markdown(f'<div class="week-card"><div class="week-day">{day}</div><div class="week-icon">{"✦" if state else "·"}</div></div>', unsafe_allow_html=True)
            if st.button("Done" if state else "Missed", key=f"week_{i}", type="primary" if state else "secondary", use_container_width=True):
                st.session_state.weekly_status[i] = not state
                st.rerun()
    total = total_water()
    progress = current_percent()
    st.markdown('<div class="section-title">Your hydration story</div><p class="section-copy">Useful signals, without turning wellness into homework.</p>', unsafe_allow_html=True)
    entries = [
        ("Today’s intake", f"{total:,} ml", "A small practice with a real impact."),
        ("Goal progress", f"{progress}%", "Keep your rhythm, not just the number."),
        ("Weekly wins", f"{success_count}/7 days", "Consistency is the quiet superpower."),
        ("Lifetime splash", f"{56_000 + total:,} ml", "Every logged sip is part of the story."),
    ]
    for label, value, copy in entries:
        st.markdown(f'<div class="log-row"><div><div class="log-time">{label}</div><div class="log-meta">{copy}</div></div><div class="log-amount">{value}</div></div>', unsafe_allow_html=True)


def add_to_cart(product):
    for item in st.session_state.cart:
        if item["name"] == product["name"]:
            item["qty"] += 1
            st.session_state.shop_msg = f"{product['name']} quantity updated in your cart."
            return
    st.session_state.cart.append({"name": product["name"], "price": product["price"], "qty": 1, "detail": product["detail"]})
    st.session_state.shop_msg = f"{product['name']} is now in your cart."


def render_shop():
    if st.session_state.sub_page == "Cart":
        render_cart()
        return
    item_count = sum(item["qty"] for item in st.session_state.cart)
    title, cart = st.columns([3.2, 1])
    with title:
        st.markdown('<div class="eyebrow">AQUASIP OBJECTS</div><div class="section-title" style="margin-top:5px">Carry the ritual</div><p class="section-copy">Purposeful bottles for every kind of day.</p>', unsafe_allow_html=True)
    with cart:
        st.markdown('<div style="height:25px"></div>', unsafe_allow_html=True)
        if st.button(f"Cart · {item_count}", type="primary", use_container_width=True):
            st.session_state.sub_page = "Cart"; st.session_state.shop_msg = None; st.rerun()
    if st.session_state.shop_msg:
        st.success(st.session_state.shop_msg)
        st.session_state.shop_msg = None
    filter_col, sort_col = st.columns([1.5, 1])
    with filter_col: query = st.text_input("Find your bottle", placeholder="Search AquaBig, steel, travel…")
    with sort_col: sort = st.selectbox("Sort collection", ["Most loved", "Price: low to high", "Price: high to low"])
    products = [p for p in PRODUCTS if query.lower() in p["name"].lower() or query.lower() in p["description"].lower()]
    if sort == "Price: low to high": products.sort(key=lambda p: p["price"])
    elif sort == "Price: high to low": products.sort(key=lambda p: p["price"], reverse=True)
    if not products:
        st.markdown('<div class="empty-state">No bottles match that search. Try a different word.</div>', unsafe_allow_html=True)
        return
    cols = st.columns(min(3, len(products)))
    for col, product in zip(cols, products):
        art = bottle_svg(product["accent"], product["dark"])
        with col:
            st.markdown(f'''<div class="product-shell"><div class="product-art" style="background:linear-gradient(145deg,{product["accent"]}55,#fff)"><img src="data:image/svg+xml;base64,{art}" alt="{product["name"]}" style="height:123px"></div><div class="product-tag">{product["tag"]}</div><div class="product-name">{product["name"]}</div><div class="product-detail">{product["detail"]}</div><div class="product-price">RM {product["price"]:.2f}</div><div style="font-size:11px;color:#71839A;line-height:1.35">{product["description"]}</div></div>''', unsafe_allow_html=True)
            first, second = st.columns(2)
            with first:
                if st.button("Add", key=f"add_{product['name']}", use_container_width=True):
                    add_to_cart(product); st.rerun()
            with second:
                if st.button("Buy now", key=f"buy_{product['name']}", type="primary", use_container_width=True):
                    st.session_state.cart = [{"name": product["name"], "price": product["price"], "qty": 1, "detail": product["detail"]}]
                    st.session_state.sub_page = "Cart"; st.rerun()


def render_cart():
    st.markdown('<div class="eyebrow">YOUR SELECTION</div><div class="section-title" style="margin-top:5px">The hydration edit</div><p class="section-copy">A few well-made things can make daily rituals feel better.</p>', unsafe_allow_html=True)
    if st.session_state.order_success:
        st.success("Order confirmed — your AquaSip is on its way. ✦")
        st.session_state.order_success = False
    if not st.session_state.cart:
        st.markdown('<div class="empty-state"><div style="font-size:30px">◌</div>Your cart is ready when you are.</div>', unsafe_allow_html=True)
        if st.button("← Explore bottles", type="primary", use_container_width=True):
            st.session_state.sub_page = None; st.rerun()
        return
    subtotal = 0.0
    for i, item in enumerate(st.session_state.cart):
        line_total = item["price"] * item["qty"]; subtotal += line_total
        st.markdown(f'<div class="app-card cart-item"><div style="display:flex;justify-content:space-between;gap:12px"><div><div class="cart-item-name">{item["name"]}</div><div class="alarm-sub">{item["detail"]} · RM {item["price"]:.2f} each</div></div><div class="log-amount">RM {line_total:.2f}</div></div></div>', unsafe_allow_html=True)
        less, qty, more, remove = st.columns([.8, 1.1, .8, 1.5])
        with less:
            if st.button("−", key=f"cart_less_{i}", use_container_width=True):
                if item["qty"] > 1: item["qty"] -= 1
                else: st.session_state.cart.pop(i)
                st.rerun()
        with qty: st.markdown(f'<div style="text-align:center;padding-top:10px;font-size:12px;font-weight:700">{item["qty"]} in cart</div>', unsafe_allow_html=True)
        with more:
            if st.button("+", key=f"cart_more_{i}", use_container_width=True): item["qty"] += 1; st.rerun()
        with remove:
            if st.button("Remove", key=f"cart_remove_{i}", use_container_width=True): st.session_state.cart.pop(i); st.rerun()
    discount = subtotal * .10 if subtotal > 50 else 0.0
    shipping = 5.00
    total = subtotal - discount + shipping
    st.markdown(f'<div class="app-card summary-card"><div class="log-time" style="margin-bottom:10px">Order summary</div><div class="summary-line"><span>Subtotal</span><span>RM {subtotal:.2f}</span></div><div class="summary-line"><span>Hydration club saving</span><span style="color:#15906C">− RM {discount:.2f}</span></div><div class="summary-line"><span>Shipping</span><span>RM {shipping:.2f}</span></div><div class="summary-total"><span>Total</span><span>RM {total:.2f}</span></div></div>', unsafe_allow_html=True)
    back, checkout = st.columns(2)
    with back:
        if st.button("← Keep exploring", use_container_width=True): st.session_state.sub_page = None; st.rerun()
    with checkout:
        if st.button("Secure checkout  →", type="primary", use_container_width=True):
            st.session_state.cart = []; st.session_state.order_success = True; st.balloons(); st.rerun()


def render_settings():
    st.markdown('<div class="eyebrow">YOUR RHYTHM, YOUR WAY</div><div class="section-title" style="margin-top:5px">Set up your flow</div><p class="section-copy">Build a hydration routine that works with your actual day.</p>', unsafe_allow_html=True)
    st.markdown('<div class="setting-card"><div class="log-time">Daily intention</div><div class="alarm-sub">A useful goal is one you will return to.</div></div>', unsafe_allow_html=True)
    goal = st.number_input("Daily water goal (ml)", min_value=500, max_value=10000, value=int(st.session_state.goal), step=100)
    st.session_state.goal = goal
    st.markdown('<div class="section-title">Gentle nudges</div><p class="section-copy">Your alarms live here — calm, clear and easy to change.</p>', unsafe_allow_html=True)
    if st.session_state.alarm_success_msg:
        st.success(st.session_state.alarm_success_msg); st.session_state.alarm_success_msg = None
    with st.expander("＋ Add a hydration reminder"):
        alarm = st.time_input("Time", value=time(8, 0), key="new_alarm")
        if st.button("Save reminder", type="primary", use_container_width=True):
            formatted = alarm.strftime("%I:%M %p")
            if formatted not in st.session_state.reminders:
                st.session_state.reminders.append(formatted)
                st.session_state.alarm_success_msg = f"Reminder set for {formatted}."
            else:
                st.session_state.alarm_success_msg = f"You already have a reminder at {formatted}."
            st.rerun()
    for i, alarm in enumerate(list(st.session_state.reminders)):
        card, delete = st.columns([3.6, 1])
        with card:
            st.markdown(f'<div class="setting-card"><div class="alarm-time">◷ {alarm}</div><div class="alarm-sub">Every day · a little nudge to refill</div></div>', unsafe_allow_html=True)
        with delete:
            st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
            if st.button("Delete", key=f"alarm_delete_{i}", use_container_width=True):
                st.session_state.reminders.pop(i); st.rerun()


def main():
    init_state()
    inject_styles()
    if not st.session_state.logged_in:
        render_auth()
        return
    render_draggable_avatar(current_percent())
    page = render_app_header()
    if page == "Home": render_home()
    elif page == "History": render_history()
    elif page == "Shop": render_shop()
    else: render_settings()


if __name__ == "__main__":
    main()
