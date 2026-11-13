"""Page background and CSS for the Streamlit app."""
import base64

SVG_BG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#4FC3F7"/>
      <stop offset="38%" stop-color="#81D4FA"/>
      <stop offset="68%" stop-color="#C8ECA0"/>
      <stop offset="100%" stop-color="#A8D868"/>
    </linearGradient>
    <radialGradient id="sunGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#FFFDE7" stop-opacity="0.85"/>
      <stop offset="55%"  stop-color="#FFF9C4" stop-opacity="0.38"/>
      <stop offset="100%" stop-color="#FFFDE7" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="sunBody" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="#FFE082"/>
      <stop offset="100%" stop-color="#FFCA28"/>
    </linearGradient>
    <linearGradient id="hillFar" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="#B8DFA0"/>
      <stop offset="100%" stop-color="#8AC878"/>
    </linearGradient>
    <linearGradient id="hillNear" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="#7CBB58"/>
      <stop offset="100%" stop-color="#5AA840"/>
    </linearGradient>
    <linearGradient id="field" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="#90D060"/>
      <stop offset="100%" stop-color="#4CAF50"/>
    </linearGradient>
  </defs>

  <!-- Sky -->
  <rect width="1440" height="900" fill="url(#sky)"/>

  <!-- Sun halo -->
  <ellipse cx="155" cy="148" rx="130" ry="130" fill="url(#sunGlow)"/>
  <!-- Sun disc -->
  <circle cx="155" cy="148" r="55" fill="url(#sunBody)"/>
  <!-- Sun rays -->
  <g stroke="#FFD54F" stroke-width="3" stroke-linecap="round" opacity="0.60">
    <line x1="155" y1="80"  x2="155" y2="58"/>
    <line x1="155" y1="216" x2="155" y2="238"/>
    <line x1="87"  y1="148" x2="65"  y2="148"/>
    <line x1="223" y1="148" x2="245" y2="148"/>
    <line x1="107" y1="100" x2="91"  y2="84"/>
    <line x1="203" y1="196" x2="219" y2="212"/>
    <line x1="203" y1="100" x2="219" y2="84"/>
    <line x1="107" y1="196" x2="91"  y2="212"/>
    <line x1="130" y1="88"  x2="120" y2="68"/>
    <line x1="180" y1="208" x2="190" y2="228"/>
  </g>

  <!-- Cloud 1 (large, left-centre) -->
  <g opacity="0.92">
    <ellipse cx="432" cy="168" rx="100" ry="38" fill="white"/>
    <ellipse cx="490" cy="152" rx="72"  ry="31" fill="white"/>
    <ellipse cx="370" cy="174" rx="62"  ry="28" fill="white"/>
    <ellipse cx="520" cy="171" rx="50"  ry="24" fill="white"/>
  </g>

  <!-- Cloud 2 (medium, right) -->
  <g opacity="0.85">
    <ellipse cx="1022" cy="126" rx="114" ry="41" fill="white"/>
    <ellipse cx="1096" cy="110" rx="80"  ry="34" fill="white"/>
    <ellipse cx="950"  cy="133" rx="67"  ry="30" fill="white"/>
    <ellipse cx="1132" cy="129" rx="54"  ry="25" fill="white"/>
  </g>

  <!-- Cloud 3 (small, top-right) -->
  <g opacity="0.74">
    <ellipse cx="1302" cy="88"  rx="80" ry="28" fill="white"/>
    <ellipse cx="1355" cy="76"  rx="56" ry="23" fill="white"/>
    <ellipse cx="1260" cy="94"  rx="50" ry="21" fill="white"/>
  </g>

  <!-- Cloud 4 (wispy, centre-top) -->
  <g opacity="0.60">
    <ellipse cx="702" cy="105" rx="64" ry="22" fill="white"/>
    <ellipse cx="746" cy="94"  rx="46" ry="18" fill="white"/>
  </g>

  <!-- Far hills -->
  <ellipse cx="720"  cy="792" rx="1150" ry="332" fill="url(#hillFar)"/>
  <!-- Near hill left -->
  <ellipse cx="40"   cy="872" rx="608"  ry="252" fill="url(#hillNear)"/>
  <!-- Near hill right -->
  <ellipse cx="1400" cy="858" rx="628"  ry="262" fill="url(#hillNear)"/>
  <!-- Centre mound -->
  <ellipse cx="720"  cy="878" rx="688"  ry="198" fill="#7cbb58"/>

  <!-- Foreground field -->
  <rect x="0" y="770" width="1440" height="130" fill="url(#field)"/>

  <!-- Crop rows -->
  <g stroke="#3d8025" stroke-width="1.5" opacity="0.20">
    <line x1="0" y1="797" x2="1440" y2="797"/>
    <line x1="0" y1="817" x2="1440" y2="817"/>
    <line x1="0" y1="837" x2="1440" y2="837"/>
    <line x1="0" y1="857" x2="1440" y2="857"/>
    <line x1="0" y1="877" x2="1440" y2="877"/>
  </g>

  <!-- Wheat stalks – left -->
  <g stroke="#8BC34A" stroke-width="2.2">
    <line x1="68"  y1="900" x2="74"  y2="758"/><ellipse cx="74"  cy="749" rx="9" ry="15" fill="#F9A825"/>
    <line x1="94"  y1="900" x2="101" y2="754"/><ellipse cx="101" cy="745" rx="9" ry="15" fill="#F9A825"/>
    <line x1="120" y1="900" x2="126" y2="760"/><ellipse cx="126" cy="751" rx="9" ry="15" fill="#F9A825"/>
    <line x1="146" y1="900" x2="152" y2="755"/><ellipse cx="152" cy="746" rx="9" ry="15" fill="#F9A825"/>
    <line x1="170" y1="900" x2="176" y2="762"/><ellipse cx="176" cy="753" rx="9" ry="15" fill="#F9A825"/>
    <line x1="194" y1="900" x2="200" y2="757"/><ellipse cx="200" cy="748" rx="9" ry="15" fill="#F9A825"/>
  </g>

  <!-- Wheat stalks – right -->
  <g stroke="#8BC34A" stroke-width="2.2">
    <line x1="1246" y1="900" x2="1252" y2="757"/><ellipse cx="1252" cy="748" rx="9" ry="15" fill="#F9A825"/>
    <line x1="1270" y1="900" x2="1277" y2="761"/><ellipse cx="1277" cy="752" rx="9" ry="15" fill="#F9A825"/>
    <line x1="1294" y1="900" x2="1300" y2="755"/><ellipse cx="1300" cy="746" rx="9" ry="15" fill="#F9A825"/>
    <line x1="1318" y1="900" x2="1324" y2="761"/><ellipse cx="1324" cy="752" rx="9" ry="15" fill="#F9A825"/>
    <line x1="1342" y1="900" x2="1348" y2="756"/><ellipse cx="1348" cy="747" rx="9" ry="15" fill="#F9A825"/>
    <line x1="1366" y1="900" x2="1372" y2="762"/><ellipse cx="1372" cy="753" rx="9" ry="15" fill="#F9A825"/>
  </g>

  <!-- Tree – far left tall -->
  <rect x="24"  y="638" width="17" height="108" fill="#6D4C41" rx="3"/>
  <ellipse cx="33"  cy="618" rx="52" ry="68" fill="#2E7D32"/>
  <ellipse cx="16"  cy="638" rx="34" ry="50" fill="#388E3C"/>
  <ellipse cx="52"  cy="635" rx="34" ry="48" fill="#1B5E20"/>

  <!-- Tree – left shorter -->
  <rect x="200" y="662" width="14" height="86" fill="#6D4C41" rx="2"/>
  <ellipse cx="207" cy="645" rx="42" ry="56" fill="#33691E"/>
  <ellipse cx="192" cy="658" rx="27" ry="40" fill="#558B2F"/>
  <ellipse cx="224" cy="655" rx="27" ry="40" fill="#1B5E20"/>

  <!-- Tree – far right tall -->
  <rect x="1400" y="630" width="17" height="115" fill="#6D4C41" rx="3"/>
  <ellipse cx="1409" cy="612" rx="54" ry="70" fill="#2E7D32"/>
  <ellipse cx="1392" cy="630" rx="36" ry="52" fill="#388E3C"/>
  <ellipse cx="1428" cy="628" rx="36" ry="50" fill="#1B5E20"/>

  <!-- Tree – right shorter -->
  <rect x="1228" y="655" width="14" height="90" fill="#6D4C41" rx="2"/>
  <ellipse cx="1235" cy="638" rx="44" ry="58" fill="#33691E"/>
  <ellipse cx="1220" cy="652" rx="29" ry="42" fill="#558B2F"/>
  <ellipse cx="1252" cy="650" rx="29" ry="42" fill="#1B5E20"/>

  <!-- Birds -->
  <g stroke="#0D47A1" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.55">
    <path d="M 580 228 Q 586 222 592 228"/>
    <path d="M 602 220 Q 608 214 614 220"/>
    <path d="M 626 234 Q 632 228 638 234"/>
    <path d="M 660 214 Q 666 208 672 214"/>
    <path d="M 680 226 Q 686 220 692 226"/>
  </g>

  <!-- Farmhouse -->
  <rect x="638" y="706" width="64" height="50" fill="#FFCCBC" stroke="#BF360C" stroke-width="1.5" rx="2"/>
  <polygon points="628,706 712,706 670,672" fill="#D32F2F"/>
  <rect x="659" y="722" width="16" height="34" fill="#795548" rx="2"/>
  <rect x="641" y="714" width="13" height="11" fill="#B3E5FC" rx="1"/>
  <rect x="686" y="714" width="13" height="11" fill="#B3E5FC" rx="1"/>
  <rect x="694" y="668" width="8"  height="22" fill="#8D6E63"/>
  <circle cx="698" cy="660" r="5"  fill="rgba(200,200,200,0.50)"/>
  <circle cx="702" cy="648" r="7"  fill="rgba(200,200,200,0.38)"/>
  <circle cx="698" cy="636" r="9"  fill="rgba(200,200,200,0.26)"/>

  <!-- Fence left of house -->
  <g fill="#8D6E63" stroke="#795548" stroke-width="0.5">
    <rect x="578" y="750" width="5" height="24" rx="1"/>
    <rect x="593" y="750" width="5" height="24" rx="1"/>
    <rect x="608" y="750" width="5" height="24" rx="1"/>
    <rect x="623" y="750" width="5" height="24" rx="1"/>
    <line x1="578" y1="758" x2="628" y2="758" stroke="#8D6E63" stroke-width="2"/>
    <line x1="578" y1="766" x2="628" y2="766" stroke="#8D6E63" stroke-width="2"/>
  </g>
  <!-- Fence right of house -->
  <g fill="#8D6E63" stroke="#795548" stroke-width="0.5">
    <rect x="714" y="750" width="5" height="24" rx="1"/>
    <rect x="729" y="750" width="5" height="24" rx="1"/>
    <rect x="744" y="750" width="5" height="24" rx="1"/>
    <rect x="759" y="750" width="5" height="24" rx="1"/>
    <line x1="714" y1="758" x2="764" y2="758" stroke="#8D6E63" stroke-width="2"/>
    <line x1="714" y1="766" x2="764" y2="766" stroke="#8D6E63" stroke-width="2"/>
  </g>
</svg>
"""

_svg_b64 = base64.b64encode(SVG_BG.encode("utf-8")).decode("utf-8")
_bg_url  = f"data:image/svg+xml;base64,{_svg_b64}"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Nunito:wght@300;400;600;700&display=swap');

/* Background scenery */
.stApp {{
    background-image: url("{_bg_url}") !important;
    background-size: cover !important;
    background-attachment: fixed !important;
    min-height: 100vh;
}}

/* Content above background */
.main .block-container {{
    position: relative;
    z-index: 1;
    padding-top: 2rem;
    max-width: 730px;
}}

/* Title */
h1 {{
    font-family: 'Playfair Display', serif !important;
    color: #1b4d0a !important;
    font-size: 2.65rem !important;
    text-align: center;
    letter-spacing: 0.5px;
    text-shadow: 0 2px 14px rgba(255,255,255,0.95), 0 1px 4px rgba(0,0,0,0.10);
    margin-bottom: 0.15rem !important;
}}

/* Subtitle / paragraphs */
p {{
    font-family: 'Nunito', sans-serif !important;
    color: #2d5a14 !important;
    text-align: center;
    font-size: 1rem;
    text-shadow: 0 1px 6px rgba(255,255,255,0.85);
}}

/* Input field */
.stTextInput > div > div > input {{
    background: rgba(255,255,255,0.90) !important;
    border: 2px solid #7bc150 !important;
    border-radius: 14px !important;
    color: #1a3d0a !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 1rem !important;
    padding: 14px 18px !important;
    box-shadow: 0 4px 18px rgba(100,170,60,0.14), inset 0 1px 3px rgba(255,255,255,0.5) !important;
    transition: all 0.3s ease;
}}
.stTextInput > div > div > input:focus {{
    border-color: #4a8f2a !important;
    background: rgba(255,255,255,0.97) !important;
    box-shadow: 0 4px 26px rgba(74,143,42,0.24) !important;
}}
.stTextInput > div > div > input::placeholder {{
    color: #9dc870 !important;
    font-style: italic;
}}

/* Input label */
.stTextInput label {{
    font-family: 'Nunito', sans-serif !important;
    color: #235510 !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    letter-spacing: 1.2px !important;
    text-transform: uppercase;
    text-shadow: 0 1px 5px rgba(255,255,255,0.8);
}}

/* Button */
.stButton > button {{
    width: 100%;
    background: linear-gradient(135deg, #5db33a 0%, #3a8520 100%) !important;
    color: #ffffff !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase;
    border: none !important;
    border-radius: 14px !important;
    padding: 14px 0 !important;
    box-shadow: 0 5px 22px rgba(90,180,58,0.42), 0 2px 6px rgba(0,0,0,0.08) !important;
    transition: all 0.28s cubic-bezier(.4,0,.2,1) !important;
}}
.stButton > button:hover {{
    background: linear-gradient(135deg, #6ec44a 0%, #4a9530 100%) !important;
    transform: translateY(-2px) scale(1.015) !important;
    box-shadow: 0 8px 30px rgba(90,180,58,0.52) !important;
}}
.stButton > button:active {{
    transform: translateY(0) scale(0.99) !important;
}}

/* Answer box */
.answer-box {{
    background: rgba(255,255,255,0.88);
    border: 1.5px solid #a0d87a;
    border-left: 5px solid #5db33a;
    border-radius: 14px;
    padding: 22px 26px;
    margin-top: 1.5rem;
    font-family: 'Nunito', sans-serif;
    color: #1e3d0e;
    font-size: 1.06rem;
    line-height: 1.80;
    box-shadow: 0 6px 26px rgba(90,170,60,0.13), 0 2px 8px rgba(255,255,255,0.55);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    animation: slideUp 0.45s cubic-bezier(.4,0,.2,1);
}}
@keyframes slideUp {{
    from {{ opacity: 0; transform: translateY(18px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

/* Example tags */
.example-tag {{
    display: inline-block;
    background: rgba(255,255,255,0.78);
    border: 1.5px solid #88c85e;
    color: #2a5e12;
    border-radius: 24px;
    padding: 5px 16px;
    font-size: 0.82rem;
    font-family: 'Nunito', sans-serif;
    font-weight: 600;
    margin: 4px;
    box-shadow: 0 2px 8px rgba(90,170,58,0.12);
    cursor: pointer;
    transition: all 0.2s;
}}
.example-tag:hover {{
    background: rgba(255,255,255,0.96);
    border-color: #5db33a;
}}

/* Section label above example tags */
.try-label {{
    font-size: 0.76rem;
    color: rgba(35,85,16,0.65);
    text-align: center;
    font-family: 'Nunito', sans-serif;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
    text-shadow: 0 1px 4px rgba(255,255,255,0.7);
}}

/* Divider */
hr {{
    border: none !important;
    border-top: 1.5px solid rgba(90,170,58,0.22) !important;
    margin: 1.5rem 0 !important;
}}

/* Alert / warning */
.stAlert {{
    background: rgba(255,252,220,0.92) !important;
    border: 1.5px solid #e8c840 !important;
    color: #6b5000 !important;
    border-radius: 12px !important;
    font-family: 'Nunito', sans-serif !important;
}}

/* Spinner */
.stSpinner > div {{
    border-top-color: #5db33a !important;
}}

/* Hide Streamlit chrome */
#MainMenu, footer, header {{ visibility: hidden; }}

/* Scrollbar */
::-webkit-scrollbar {{ width: 6px; }}
::-webkit-scrollbar-track {{ background: rgba(180,230,140,0.15); }}
::-webkit-scrollbar-thumb {{ background: #88c85e; border-radius: 4px; }}
</style>
"""
