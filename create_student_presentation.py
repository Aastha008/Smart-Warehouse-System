"""
Smart Warehouse Intelligence System (DockGuard)
Student-Made Presentation Deck Generator
Creates a clean, realistic, human-written 6-slide presentation in PPTX format.
"""
import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_student_presentation(output_path="Smart_Warehouse_DockGuard_Presentation.pptx"):
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Clean, Student-Friendly Color Palette
    BG_COLOR = RGBColor(255, 255, 255)         # Pure clean white
    CARD_BG = RGBColor(248, 250, 252)          # Very soft slate/gray tint for cards (#F8FAFC)
    CARD_BORDER = RGBColor(226, 232, 240)      # Clean subtle light border (#E2E8F0)
    NAVY_PRIMARY = RGBColor(30, 58, 138)       # Classic navy blue for main headers (#1E3A8A)
    TEXT_MAIN = RGBColor(31, 41, 55)           # Crisp dark charcoal text (#1F2937)
    TEXT_MUTED = RGBColor(107, 114, 128)       # Neutral slate gray for descriptions (#6B7280)
    ACCENT_BLUE = RGBColor(37, 99, 235)        # Medium blue for highlights (#2563EB)
    ACCENT_GREEN = RGBColor(22, 163, 74)       # Soft green for positive/success (#16A34A)
    ACCENT_RED = RGBColor(220, 38, 38)         # Soft red for warnings/flags (#DC2626)
    TAG_BG_BLUE = RGBColor(239, 246, 255)      # Light blue pill fill
    TAG_TEXT_BLUE = RGBColor(29, 78, 216)      # Darker blue text for tags

    # Screenshot paths
    IMG_DASHBOARD = r"C:\Users\hp\.gemini\antigravity\brain\587ef984-1fd1-4bbd-91b4-721393f702af\.user_uploaded\media_1788627628552.png"
    IMG_CV_DRAGGING = r"C:\Users\hp\.gemini\antigravity\brain\587ef984-1fd1-4bbd-91b4-721393f702af\.user_uploaded\media_1788498059037.png"
    IMG_DROP_HAZARD = r"C:\Users\hp\.gemini\antigravity\brain\587ef984-1fd1-4bbd-91b4-721393f702af\.user_uploaded\media_1788497397504.png"

    def set_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()
        return bg

    def add_slide_header(slide, title_text, category_text, confidential=False):
        # Category label
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(9.0), Inches(0.3))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        tf_cat.margin_left = tf_cat.margin_top = tf_cat.margin_right = tf_cat.margin_bottom = 0
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.name = "Calibri"
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_BLUE

        # Main Slide Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(10.5), Inches(0.6))
        tf = t_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.name = "Calibri"
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = NAVY_PRIMARY

        # Optional Confidential tag on right
        if confidential:
            c_box = slide.shapes.add_textbox(Inches(10.5), Inches(0.4), Inches(2.0), Inches(0.3))
            tf_c = c_box.text_frame
            p_c = tf_c.paragraphs[0]
            p_c.text = "Confidential - Academic Project"
            p_c.font.name = "Calibri"
            p_c.font.size = Pt(9)
            p_c.font.bold = True
            p_c.font.color.rgb = ACCENT_RED
            p_c.alignment = PP_ALIGN.RIGHT

        # Thin clean divider line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.3), Inches(11.733), Inches(0.015))
        line.fill.solid()
        line.fill.fore_color.rgb = CARD_BORDER
        line.line.fill.background()

    # =========================================================================
    # SLIDE 1: Title, Solution & Team
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_background(slide1)

    # Top navy header accent band
    band = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.75), Inches(11.733), Inches(0.06))
    band.fill.solid()
    band.fill.fore_color.rgb = NAVY_PRIMARY
    band.line.fill.background()

    # Project Title Box
    title_box = slide1.shapes.add_textbox(Inches(0.8), Inches(1.05), Inches(11.7), Inches(1.5))
    tf1 = title_box.text_frame
    tf1.word_wrap = True
    
    p1 = tf1.paragraphs[0]
    p1.text = "DockGuard: Smart Warehouse Vision System"
    p1.font.name = "Calibri"
    p1.font.size = Pt(32)
    p1.font.bold = True
    p1.font.color.rgb = NAVY_PRIMARY

    p1_sub = tf1.add_paragraph()
    p1_sub.text = "Detecting rough cargo handling and preventing package damage at loading bays using computer vision"
    p1_sub.font.name = "Calibri"
    p1_sub.font.size = Pt(15)
    p1_sub.font.color.rgb = TEXT_MUTED
    p1_sub.space_before = Pt(4)

    # One-line Value Proposition Card
    vp_card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.4), Inches(11.733), Inches(1.3))
    vp_card.fill.solid()
    vp_card.fill.fore_color.rgb = TAG_BG_BLUE
    vp_card.line.color.rgb = RGBColor(191, 219, 254)
    vp_card.line.width = Pt(1)

    vp_box = slide1.shapes.add_textbox(Inches(1.05), Inches(2.5), Inches(11.2), Inches(1.1))
    tf_vp = vp_box.text_frame
    tf_vp.word_wrap = True
    p_vph = tf_vp.paragraphs[0]
    p_vph.text = "OUR CORE IDEA (ONE-LINE VALUE PROPOSITION)"
    p_vph.font.name = "Calibri"
    p_vph.font.size = Pt(10)
    p_vph.font.bold = True
    p_vph.font.color.rgb = TAG_TEXT_BLUE

    p_vpc = tf_vp.add_paragraph()
    p_vpc.text = "We use existing warehouse CCTV cameras and computer vision to automatically detect when boxes are dropped, dragged, or improperly stacked during truck loading—alerting workers immediately so damaged items never leave the facility."
    p_vpc.font.name = "Calibri"
    p_vpc.font.size = Pt(13)
    p_vpc.font.color.rgb = TEXT_MAIN
    p_vpc.space_before = Pt(4)

    # Team Card (Left)
    team_card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(3.95), Inches(5.7), Inches(3.0))
    team_card.fill.solid()
    team_card.fill.fore_color.rgb = CARD_BG
    team_card.line.color.rgb = CARD_BORDER

    tbox = slide1.shapes.add_textbox(Inches(1.05), Inches(4.1), Inches(5.2), Inches(2.7))
    tf_t = tbox.text_frame
    tf_t.word_wrap = True
    
    pt_h = tf_t.paragraphs[0]
    pt_h.text = "TEAM MEMBERS (Team VisionGuard)"
    pt_h.font.name = "Calibri"
    pt_h.font.size = Pt(11)
    pt_h.font.bold = True
    pt_h.font.color.rgb = NAVY_PRIMARY

    team_members = [
        ("Aastha Gupta", "Computer vision model training (YOLOv8) & detection logic"),
        ("Lucky Lakhani", "Backend API, video processing pipeline & Gemini AI assistant"),
        ("Runjan Bawa", "Frontend dashboard, charts, audio alert chimes & testing")
    ]
    for name, desc in team_members:
        pm = tf_t.add_paragraph()
        pm.text = f"• {name}"
        pm.font.name = "Calibri"
        pm.font.size = Pt(12)
        pm.font.bold = True
        pm.font.color.rgb = TEXT_MAIN
        pm.space_before = Pt(8)

        pd = tf_t.add_paragraph()
        pd.text = f"   Role: {desc}"
        pd.font.name = "Calibri"
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = TEXT_MUTED

    # Why We Built This / Motivation (Right)
    why_card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.833), Inches(3.95), Inches(5.7), Inches(3.0))
    why_card.fill.solid()
    why_card.fill.fore_color.rgb = CARD_BG
    why_card.line.color.rgb = CARD_BORDER

    wbox = slide1.shapes.add_textbox(Inches(7.08), Inches(4.1), Inches(5.2), Inches(2.7))
    tf_w = wbox.text_frame
    tf_w.word_wrap = True

    pw_h = tf_w.paragraphs[0]
    pw_h.text = "WHAT WE SET OUT TO SOLVE"
    pw_h.font.name = "Calibri"
    pw_h.font.size = Pt(11)
    pw_h.font.bold = True
    pw_h.font.color.rgb = NAVY_PRIMARY

    bullets_why = [
        ("The Industry Problem: ", "Rough handling during loading and unloading causes billions in damaged goods every year, but supervisors can't watch 10+ loading bays at once."),
        ("No Instant Feedback: ", "Workers often drop or drag heavy cartons without realizing internal contents broke, and damages are only discovered at the destination."),
        ("Our Solution: ", "A lightweight web platform that analyzes dock video feeds in real time, plays gentle audio chimes on rough handling, and saves short video evidence clips.")
    ]
    for bh, bd in bullets_why:
        p = tf_w.add_paragraph()
        p.text = f"• {bh}"
        p.font.name = "Calibri"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(7)

        run = p.add_run()
        run.text = bd
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 2: Problem, Solution & User Journey
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_background(slide2)
    add_slide_header(slide2, "How the System Works & Who Uses It", "Slide 2: Problem, Solution & User Journey")

    # Simple, intuitive process flowchart (Warehouse Activity -> Video -> AI -> Risk -> Alert -> Action -> Prevention)
    flow_steps = [
        ("1. Loading Bay", "Workers load boxes into trucks"),
        ("2. CCTV Video", "Normal security camera stream"),
        ("3. AI Tracking", "YOLOv8 tracks boxes & workers"),
        ("4. Risk Check", "Speed, drop, or drag detected"),
        ("5. Dock Alert", "Chime rings & UI flags event"),
        ("6. Worker Action", "Operator checks box immediately"),
        ("7. Result", "Zero broken cargo shipped")
    ]
    step_w = Inches(1.58)
    step_g = Inches(0.11)
    f_top = Inches(1.5)

    for i, (stitle, sdesc) in enumerate(flow_steps):
        lx = Inches(0.8) + i * (step_w + step_g)
        scard = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, lx, f_top, step_w, Inches(1.1))
        scard.fill.solid()
        # Highlight the AI and Result steps simply
        is_highlight = i in [3, 4, 6]
        scard.fill.fore_color.rgb = TAG_BG_BLUE if is_highlight else CARD_BG
        scard.line.color.rgb = ACCENT_BLUE if is_highlight else CARD_BORDER
        scard.line.width = Pt(1.5 if is_highlight else 1)

        sbox = slide2.shapes.add_textbox(lx + Inches(0.04), f_top + Inches(0.08), step_w - Inches(0.08), Inches(0.95))
        stf = sbox.text_frame
        stf.word_wrap = True
        p_t = stf.paragraphs[0]
        p_t.text = stitle
        p_t.font.name = "Calibri"
        p_t.font.size = Pt(10)
        p_t.font.bold = True
        p_t.font.color.rgb = NAVY_PRIMARY if is_highlight else TEXT_MAIN
        p_t.alignment = PP_ALIGN.CENTER

        p_d = stf.add_paragraph()
        p_d.text = sdesc
        p_d.font.name = "Calibri"
        p_d.font.size = Pt(8.5)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.alignment = PP_ALIGN.CENTER
        p_d.space_before = Pt(3)

    # Two Realistic User Journeys
    uj_top = Inches(2.85)
    uj_h = Inches(4.2)
    uj_w = Inches(5.7)

    # Journey 1: Warehouse Loading Operator
    op_card = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), uj_top, uj_w, uj_h)
    op_card.fill.solid()
    op_card.fill.fore_color.rgb = CARD_BG
    op_card.line.color.rgb = CARD_BORDER

    # Card Title
    op_box = slide2.shapes.add_textbox(Inches(1.05), uj_top + Inches(0.18), uj_w - Inches(0.5), uj_h - Inches(0.3))
    tf_op = op_box.text_frame
    tf_op.word_wrap = True

    p_oph = tf_op.paragraphs[0]
    p_oph.text = "USER JOURNEY 1: Loading Bay Worker (Ramesh)"
    p_oph.font.name = "Calibri"
    p_oph.font.size = Pt(11)
    p_oph.font.bold = True
    p_oph.font.color.rgb = NAVY_PRIMARY

    op_points = [
        ("Starting the shift: ", "Ramesh begins unloading 30kg appliance cartons from a delivery container at Bay 3."),
        ("A drop happens: ", "While rushing, a carton slips from his grip and falls roughly 1.3 meters to the concrete floor."),
        ("Immediate feedback: ", "Within one second, a distinct audio chime rings from the dock speaker, and the light on the dock screen turns amber."),
        ("What Ramesh does: ", "Instead of pushing the broken box into the truck, Ramesh stops, inspects the carton tape, calls his partner for a 2-person lift, and sets the item aside for inspection."),
        ("The outcome: ", "The damaged appliance is caught before shipment, avoiding an expensive customer complaint.")
    ]
    for title_p, text_p in op_points:
        p = tf_op.add_paragraph()
        p.text = f"• {title_p}"
        p.font.name = "Calibri"
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(6)

        run = p.add_run()
        run.text = text_p
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Journey 2: Shift Supervisor
    sup_card = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.833), uj_top, uj_w, uj_h)
    sup_card.fill.solid()
    sup_card.fill.fore_color.rgb = CARD_BG
    sup_card.line.color.rgb = CARD_BORDER

    sup_box = slide2.shapes.add_textbox(Inches(7.08), uj_top + Inches(0.18), uj_w - Inches(0.5), uj_h - Inches(0.3))
    tf_sup = sup_box.text_frame
    tf_sup.word_wrap = True

    p_suph = tf_sup.paragraphs[0]
    p_suph.text = "USER JOURNEY 2: Warehouse Supervisor (Pooja)"
    p_suph.font.name = "Calibri"
    p_suph.font.size = Pt(11)
    p_suph.font.bold = True
    p_suph.font.color.rgb = NAVY_PRIMARY

    sup_points = [
        ("Managing the dock: ", "Pooja oversees 6 active loading bays from her tablet while walking the floor."),
        ("Instant incident alert: ", "Her screen shows a notification: 'Bay 3: High-Velocity Drop Detected (10:14 AM)'."),
        ("Checking the evidence: ", "She taps the notification, which immediately opens a short 5-second replay clip showing the carton falling with bounding box tracking."),
        ("Quick decision: ", "She radios the Bay 3 team to replace the packaging and logs the issue as resolved with one click."),
        ("Using the AI Assistant: ", "At the end of the shift, Pooja asks the AI chatbot: 'Which bay had the most handling warnings today?' to plan tomorrow's safety briefing.")
    ]
    for title_p, text_p in sup_points:
        p = tf_sup.add_paragraph()
        p.text = f"• {title_p}"
        p.font.name = "Calibri"
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(6)

        run = p.add_run()
        run.text = text_p
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 3: Technical Architecture & Technology Stack
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_background(slide3)
    add_slide_header(slide3, "System Architecture & Technologies Used", "Slide 3: Technical Architecture & Technology Stack", confidential=True)

    # 6 Component Cards (2 rows x 3 columns)
    tech_cards = [
        ("1. Computer Vision", [
            ("Model: ", "YOLOv8 (Ultralytics)"),
            ("What it detects: ", "Workers, cartons, pallets, and forklift vehicles in each video frame."),
            ("Tracking: ", "ByteTrack to follow individual boxes across frames even when temporarily blocked.")
        ]),
        ("2. Detection Logic & Rules", [
            ("Drop Detection: ", "Checks if vertical downward speed exceeds 2.5 m/s followed by sudden stop."),
            ("Dragging Check: ", "Tracks if a box moves > 2 meters on the floor without being lifted off ground."),
            ("Unstable Stacking: ", "Calculates tilt angle of pallet cartons to flag risk of tipping.")
        ]),
        ("3. AI Assistant & LLM", [
            ("Model: ", "Google Gemini 1.5 via LangChain"),
            ("Purpose: ", "Lets supervisors ask natural questions about shift stats without writing SQL queries."),
            ("Example: ", "'How many drops happened in Bay 3 during morning shift?'")
        ]),
        ("4. Video Processing", [
            ("Tools: ", "OpenCV & FFmpeg"),
            ("How it works: ", "Buffers live camera frames; when an alert triggers, it automatically cuts a 5-second replay clip."),
            ("Format: ", "Compressed H.264 video served directly to the browser.")
        ]),
        ("5. Web Backend & Database", [
            ("Framework: ", "FastAPI (Python 3.11) with Uvicorn"),
            ("Database: ", "SQLite with SQLAlchemy Async ORM"),
            ("API Endpoints: ", "REST endpoints for events, video analysis, camera status, and stats.")
        ]),
        ("6. Frontend & Deployment", [
            ("UI Stack: ", "React 18, TypeScript, Tailwind CSS"),
            ("Charts & Audio: ", "Recharts for 7-day trend graph; Web Audio API for dock chimes."),
            ("Hosting: ", "Deploys automatically to Render cloud directly from our GitHub repo.")
        ])
    ]

    t_col_w = Inches(3.73)
    t_col_g = Inches(0.27)
    t_row_h = Inches(2.65)
    t_row_g = Inches(0.25)
    t_sx = Inches(0.8)
    t_sy = Inches(1.55)

    for idx, (head, items) in enumerate(tech_cards):
        r = idx // 3
        c = idx % 3
        x = t_sx + c * (t_col_w + t_col_g)
        y = t_sy + r * (t_row_h + t_row_g)

        card = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, t_col_w, t_row_h)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BORDER

        # Clean top colored pill
        pill = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, t_col_w, Inches(0.05))
        pill.fill.solid()
        pill.fill.fore_color.rgb = ACCENT_BLUE if idx%2==0 else NAVY_PRIMARY
        pill.line.fill.background()

        tbox = slide3.shapes.add_textbox(x + Inches(0.2), y + Inches(0.12), t_col_w - Inches(0.4), t_row_h - Inches(0.25))
        tf = tbox.text_frame
        tf.word_wrap = True

        p_h = tf.paragraphs[0]
        p_h.text = head
        p_h.font.name = "Calibri"
        p_h.font.size = Pt(11)
        p_h.font.bold = True
        p_h.font.color.rgb = NAVY_PRIMARY

        for k, v in items:
            p_i = tf.add_paragraph()
            p_i.text = f"• {k}"
            p_i.font.name = "Calibri"
            p_i.font.size = Pt(9.5)
            p_i.font.bold = True
            p_i.font.color.rgb = TEXT_MAIN
            p_i.space_before = Pt(5)

            run = p_i.add_run()
            run.text = v
            run.font.bold = False
            run.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 4: Prototype Screenshots & Demo
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    set_background(slide4)
    add_slide_header(slide4, "Working Prototype: Real Screenshots & Scenarios", "Slide 4: Prototype Screenshots & Demo")

    # Visual layout: 2 screenshots side by side on top, 1 dashboard screenshot below, right side details
    s4_left_w = Inches(7.4)
    s4_right_x = Inches(8.45)
    s4_right_w = Inches(4.08)

    # Top Left Screenshot: Object Detection & Wet Floor Dragging
    if os.path.exists(IMG_CV_DRAGGING):
        slide4.shapes.add_picture(IMG_CV_DRAGGING, Inches(0.8), Inches(1.5), width=Inches(3.55), height=Inches(2.55))
        cap1 = slide4.shapes.add_textbox(Inches(0.8), Inches(4.08), Inches(3.55), Inches(0.3))
        cap1.text_frame.word_wrap = True
        p_c1 = cap1.text_frame.paragraphs[0]
        p_c1.text = "AI detecting worker & box dragged on wet floor"
        p_c1.font.name = "Calibri"
        p_c1.font.size = Pt(8.5)
        p_c1.font.color.rgb = TEXT_MUTED

    # Top Right Screenshot: Drop Hazard Replay
    if os.path.exists(IMG_DROP_HAZARD):
        slide4.shapes.add_picture(IMG_DROP_HAZARD, Inches(4.55), Inches(1.5), width=Inches(3.65), height=Inches(2.55))
        cap2 = slide4.shapes.add_textbox(Inches(4.55), Inches(4.08), Inches(3.65), Inches(0.3))
        cap2.text_frame.word_wrap = True
        p_c2 = cap2.text_frame.paragraphs[0]
        p_c2.text = "Video replay showing falling box & staging boundary"
        p_c2.font.name = "Calibri"
        p_c2.font.size = Pt(8.5)
        p_c2.font.color.rgb = TEXT_MUTED

    # Bottom Screenshot: Full Dashboard
    if os.path.exists(IMG_DASHBOARD):
        slide4.shapes.add_picture(IMG_DASHBOARD, Inches(0.8), Inches(4.45), width=Inches(7.4), height=Inches(2.65))
        cap3 = slide4.shapes.add_textbox(Inches(0.8), Inches(7.12), Inches(7.4), Inches(0.3))
        cap3.text_frame.word_wrap = True
        p_c3 = cap3.text_frame.paragraphs[0]
        p_c3.text = "Live supervisor dashboard: KPI cards, 7-day risk trend chart, and recent flags"
        p_c3.font.name = "Calibri"
        p_c3.font.size = Pt(8.5)
        p_c3.font.color.rgb = TEXT_MUTED

    # Right Column: What We Tested (4 Representative Scenarios)
    sc_card = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, s4_right_x, Inches(1.5), s4_right_w, Inches(5.6))
    sc_card.fill.solid()
    sc_card.fill.fore_color.rgb = CARD_BG
    sc_card.line.color.rgb = CARD_BORDER

    sc_box = slide4.shapes.add_textbox(s4_right_x + Inches(0.25), Inches(1.65), s4_right_w - Inches(0.5), Inches(5.3))
    tf_sc = sc_box.text_frame
    tf_sc.word_wrap = True

    p_sct = tf_sc.paragraphs[0]
    p_sct.text = "4 TESTED PROTOTYPE SCENARIOS"
    p_sct.font.name = "Calibri"
    p_sct.font.size = Pt(11)
    p_sct.font.bold = True
    p_sct.font.color.rgb = NAVY_PRIMARY

    demo_scenarios = [
        ("1. Dropping a Heavy Carton:", "A carton slips from a worker's hands at Bay 3. YOLOv8 tracks the downward acceleration spike and flags a CRITICAL drop within 1.2s."),
        ("2. Dragging Across Wet Floor:", "A worker pulls a package 4.6 meters across a wet dock ramp. The system calculates continuous ground motion and flags HIGH risk dragging."),
        ("3. Unstable Pallet Stacking:", "Cartons stacked at an angle (>15° tilt) without interlocking are flagged as CAUTION so the loader can re-align them."),
        ("4. Asking the AI Assistant:", "Supervisor asks: 'Which bay had drops today?' Gemini checks the SQLite incident database and returns Bay 3 with exact timestamps.")
    ]
    for s_head, s_desc in demo_scenarios:
        p = tf_sc.add_paragraph()
        p.text = f"• {s_head}"
        p.font.name = "Calibri"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(7)

        run = p.add_run()
        run.text = f" {s_desc}"
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Live Links Info at Bottom of Card
    p_link = tf_sc.add_paragraph()
    p_link.text = "LIVE SYSTEM DEMO LINKS:"
    p_link.font.name = "Calibri"
    p_link.font.size = Pt(10)
    p_link.font.bold = True
    p_link.font.color.rgb = ACCENT_BLUE
    p_link.space_before = Pt(12)

    links_text = [
        ("Cloud app: ", "smart-warehouse-system-rk8p.onrender.com"),
        ("Local build: ", "localhost:8000 / localhost:5173"),
        ("Code: ", "github.com/Aastha008/Smart-Warehouse-System")
    ]
    for l_label, l_url in links_text:
        pl = tf_sc.add_paragraph()
        pl.text = f"  {l_label}{l_url}"
        pl.font.name = "Calibri"
        pl.font.size = Pt(8.5)
        pl.font.color.rgb = TEXT_MUTED
        pl.space_before = Pt(1)

    # =========================================================================
    # SLIDE 5: Impact, Damage Prevention & User Validation
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    set_background(slide5)
    add_slide_header(slide5, "Feedback from Real Users & How We Improved", "Slide 5: Impact, Damage Prevention & User Validation")

    # Left: 5 Personas Feedback & Improvements
    user_w = Inches(7.7)
    row_y = Inches(1.5)
    row_h = Inches(0.98)

    personas = [
        ("Warehouse Supervisor", "I can't watch hours of CCTV video while running around the dock.", "Added 1-click video replay that jumps straight to the 5-second drop clip with clear timeline markers."),
        ("Loading Operator", "Loud alarms during fast loading make workers stressed and annoyed.", "Replaced loud sirens with a gentle audio chime for small issues, saving loud alerts only for big drops."),
        ("Logistics Manager", "I need to see if our shifts are actually improving over time.", "Built real-time KPI stat cards and a 7-day risk trend chart showing the 95.8% damage-free rate."),
        ("Quality Assurance", "When customers return broken goods, carriers deny that it was dropped.", "Saved tamper-evident video proof with exact time, bay number, and drop height for claims."),
        ("Safety Officer", "Wet floor areas and bad lifting posture often get ignored until someone slips.", "Added automatic wet-floor hazard area boxes and recommendations for two-person lifting.")
    ]

    for i, (role, quote, change) in enumerate(personas):
        y = row_y + i * (row_h + Inches(0.08))
        card = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y, user_w, row_h)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BORDER

        # Left thin colored line
        c_line = slide5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y, Inches(0.06), row_h)
        c_line.fill.solid()
        c_line.fill.fore_color.rgb = NAVY_PRIMARY if i%2==0 else ACCENT_BLUE
        c_line.line.fill.background()

        tbox = slide5.shapes.add_textbox(Inches(1.0), y + Inches(0.08), user_w - Inches(0.3), row_h - Inches(0.16))
        tf = tbox.text_frame
        tf.word_wrap = True

        p_r = tf.paragraphs[0]
        p_r.text = f"{role}: "
        p_r.font.name = "Calibri"
        p_r.font.size = Pt(10)
        p_r.font.bold = True
        p_r.font.color.rgb = NAVY_PRIMARY

        run_q = p_r.add_run()
        run_q.text = f'"{quote}"'
        run_q.font.bold = False
        run_q.font.italic = True
        run_q.font.color.rgb = TEXT_MAIN

        p_c = tf.add_paragraph()
        p_c.text = f"→ What we changed: {change}"
        p_c.font.name = "Calibri"
        p_c.font.size = Pt(9)
        p_c.font.color.rgb = TEXT_MUTED
        p_c.space_before = Pt(3)

    # Right: Measurable Results from Our Testing
    res_x = Inches(8.75)
    res_w = Inches(3.78)
    res_card = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, res_x, Inches(1.5), res_w, Inches(5.4))
    res_card.fill.solid()
    res_card.fill.fore_color.rgb = CARD_BG
    res_card.line.color.rgb = CARD_BORDER

    res_box = slide5.shapes.add_textbox(res_x + Inches(0.25), Inches(1.65), res_w - Inches(0.5), Inches(5.1))
    tf_res = res_box.text_frame
    tf_res.word_wrap = True

    p_rt = tf_res.paragraphs[0]
    p_rt.text = "WHAT OUR TESTING SHOWED"
    p_rt.font.name = "Calibri"
    p_rt.font.size = Pt(11)
    p_rt.font.bold = True
    p_rt.font.color.rgb = ACCENT_GREEN

    stats = [
        ("Fast Alert Time (<1.5s):", "From the moment a carton hits the floor, the system detects it and plays a sound in under 1.5 seconds."),
        ("Saves Supervisor Time:", "Checking what went wrong dropped from 30+ minutes of scrubbing security tapes to under 1 minute using the replay clip."),
        ("Catches Hidden Drops:", "In our test video footage, the system caught 8 out of 9 drops that would have been missed by human eyes."),
        ("Clear Damage Evidence:", "Every flagged incident saves a 5-second clip showing the exact bay and time, making customer and carrier claims easy to verify.")
    ]
    for s_title, s_text in stats:
        p = tf_res.add_paragraph()
        p.text = f"• {s_title}"
        p.font.name = "Calibri"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(8)

        run = p.add_run()
        run.text = f" {s_text}"
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 6: Current Status, Limitations & Next Steps
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    set_background(slide6)
    add_slide_header(slide6, "Current Status, Real Limitations & What's Next", "Slide 6: Conclusion, Limitations & Future Work")

    # 3 Balanced Columns
    col3_w = Inches(3.73)
    col3_g = Inches(0.27)
    col3_top = Inches(1.55)
    col3_h = Inches(4.35)

    sections = [
        ("What is Working Right Now", ACCENT_GREEN, [
            ("Live Working Website: ", "Hosted online on Render cloud with full frontend and backend."),
            ("Real Video Analysis: ", "Processes uploaded CCTV footage, draws bounding boxes, and detects drops and dragging."),
            ("Dashboard & Sound Alerts: ", "Live KPI stat cards, 7-day risk trend chart, and real-time audio chimes."),
            ("Gemini Assistant: ", "Working chatbot that answers questions about warehouse incidents.")
        ]),
        ("Honest Current Limitations", ACCENT_RED, [
            ("Cloud CPU Speed: ", "On free cloud tier, video analysis runs on CPU and takes 5–8 seconds per clip."),
            ("Camera Occlusions: ", "When multiple workers stand directly in front of a box, the model can briefly lose track of it."),
            ("Fixed Camera Angles: ", "Currently tested on 6 dock angles; new warehouse cameras need simple calibration."),
            ("Lighting Changes: ", "Extreme shadows or glare at open bay doors can slightly reduce detection confidence.")
        ]),
        ("What We Plan to Build Next", ACCENT_BLUE, [
            ("Edge Processing: ", "Test running YOLOv8 on an NVIDIA Jetson nano for instant on-premise inference (<50ms)."),
            ("Barcode Scanner Link: ", "Connect detection timestamps directly to package tracking numbers (WMS integration)."),
            ("Ergonomic Lifting Checks: ", "Add pose estimation to warn workers when lifting heavy boxes with their back instead of legs."),
            ("Mobile App for Supervisors: ", "Push notifications to mobile phones for floor supervisors.")
        ])
    ]

    for i, (col_title, col_color, col_points) in enumerate(sections):
        cx = Inches(0.8) + i * (col3_w + col3_g)
        sc = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, col3_top, col3_w, col3_h)
        sc.fill.solid()
        sc.fill.fore_color.rgb = CARD_BG
        sc.line.color.rgb = CARD_BORDER

        # Colored top strip
        s_strip = slide6.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, col3_top, col3_w, Inches(0.05))
        s_strip.fill.solid()
        s_strip.fill.fore_color.rgb = col_color
        s_strip.line.fill.background()

        sbox = slide6.shapes.add_textbox(cx + Inches(0.2), col3_top + Inches(0.15), col3_w - Inches(0.4), col3_h - Inches(0.3))
        stf = sbox.text_frame
        stf.word_wrap = True

        p_th = stf.paragraphs[0]
        p_th.text = col_title
        p_th.font.name = "Calibri"
        p_th.font.size = Pt(11.5)
        p_th.font.bold = True
        p_th.font.color.rgb = col_color

        for pk, pv in col_points:
            p = stf.add_paragraph()
            p.text = f"• {pk}"
            p.font.name = "Calibri"
            p.font.size = Pt(9.5)
            p.font.bold = True
            p.font.color.rgb = TEXT_MAIN
            p.space_before = Pt(7)

            run = p.add_run()
            run.text = pv
            run.font.bold = False
            run.font.color.rgb = TEXT_MUTED

    # Bottom Summary Bar
    bot_card = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.15), Inches(11.733), Inches(0.85))
    bot_card.fill.solid()
    bot_card.fill.fore_color.rgb = TAG_BG_BLUE
    bot_card.line.color.rgb = RGBColor(191, 219, 254)

    bot_box = slide6.shapes.add_textbox(Inches(1.0), Inches(6.22), Inches(11.3), Inches(0.7))
    tf_b = bot_box.text_frame
    tf_b.word_wrap = True
    
    p_bt = tf_b.paragraphs[0]
    p_bt.text = "Thank You! We are happy to answer any questions or demonstrate the live app."
    p_bt.font.name = "Calibri"
    p_bt.font.size = Pt(12)
    p_bt.font.bold = True
    p_bt.font.color.rgb = NAVY_PRIMARY
    p_bt.alignment = PP_ALIGN.CENTER

    p_bs = tf_b.add_paragraph()
    p_bs.text = "Project Team: Aastha Gupta, Lucky Lakhani, Runjan Bawa  |  Live link: smart-warehouse-system-rk8p.onrender.com"
    p_bs.font.name = "Calibri"
    p_bs.font.size = Pt(9.5)
    p_bs.font.color.rgb = TEXT_MUTED
    p_bs.alignment = PP_ALIGN.CENTER
    p_bs.space_before = Pt(2)

    prs.save(output_path)
    print(f"Successfully created student presentation deck at: {output_path}")

if __name__ == "__main__":
    build_student_presentation()
