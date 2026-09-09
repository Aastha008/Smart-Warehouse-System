"""
DockGuard AI - Premium Human-Crafted Presentation Deck
Restores 100% of the authentic project content, stories, personas, and technical depth from before,
while presenting it with high-impact visual design:
- Native 4-stop deep navy-to-oceanic blue gradient background on cSld.
- Clean card surfaces with generous margins (no text-heavy walls of plain prose).
- Bold keyword lead-ins on every bullet point for effortless visual scanning.
- Distinct slide visual identities:
  Slide 1: Asymmetrical Pitch & Team Showcase + The 10-Second Pitch + Economic Reality
  Slide 2: 7-Step Life Cycle Flow + Frontline Stories (Ramesh at Bay 3 vs Pooja on iPad)
  Slide 3: 6-Module Full Architecture Grid (Under the Hood: How We Taught Cameras to Care About Boxes)
  Slide 4: Prototype Screenshots in Action (CV Dragging, Drop Replay, Live Dashboard) + 4 Tested Scenarios
  Slide 5: What Warehouse Crews Told Us (5 Frontline Personas with Quotes & Fixes) + Testing Results
  Slide 6: 3-Stage Progressive Roadmap (01 What's Working -> 02 Honest Glitches -> 03 What's Next) + Closing Punchline
"""
import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml import parse_xml

def build_perfect_presentation(output_paths=None):
    if output_paths is None:
        output_paths = [
            "Smart_Warehouse_DockGuard_Presentation.pptx",
            "DockGuard_AI_Presentation_Deck.pptx",
            "DockGuard_Fun_Presentation.pptx"
        ]

    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Cohesive Blue & Sky Cyan Identity
    COLOR_WHITE = RGBColor(255, 255, 255)         # Crisp White
    COLOR_CYAN = RGBColor(56, 189, 248)          # Electric Sky Cyan (#38BDF8)
    COLOR_CYAN_SOFT = RGBColor(125, 211, 252)     # Soft Cyan (#7DD3FC)
    COLOR_SLATE_LIGHT = RGBColor(226, 232, 240)   # Light Slate (#E2E8F0)
    COLOR_SLATE_BODY = RGBColor(203, 213, 225)    # Slate Body (#CBD5E1)
    COLOR_SLATE_MUTED = RGBColor(148, 163, 184)   # Slate Muted (#94A3B8)
    
    SURFACE_BG = RGBColor(10, 25, 46)            # Deep Translucent Navy (#0A192E)
    SURFACE_ACTIVE = RGBColor(16, 44, 82)        # Active Navy (#102C52)
    SURFACE_BORDER = RGBColor(28, 62, 102)       # Subtle Card Border (#1C3E66)
    SURFACE_BORDER_CYAN = RGBColor(56, 189, 248) # Cyan Accent Border

    # Screenshots
    IMG_DASHBOARD = r"C:\Users\hp\.gemini\antigravity\brain\587ef984-1fd1-4bbd-91b4-721393f702af\.user_uploaded\media_1788627628552.png"
    IMG_CV_DRAGGING = r"C:\Users\hp\.gemini\antigravity\brain\587ef984-1fd1-4bbd-91b4-721393f702af\.user_uploaded\media_1788498059037.png"
    IMG_DROP_HAZARD = r"C:\Users\hp\.gemini\antigravity\brain\587ef984-1fd1-4bbd-91b4-721393f702af\.user_uploaded\media_1788497397504.png"

    def apply_native_gradient(slide):
        """Native OpenXML 4-stop deep navy-to-oceanic blue gradient on cSld."""
        bg_xml = """<p:bg xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
          <p:bgPr>
            <a:gradFill flip="none" rotWithShape="1">
              <a:gsLst>
                <a:gs pos="0"><a:srgbClr val="060F1E"/></a:gs>
                <a:gs pos="38000"><a:srgbClr val="0A213D"/></a:gs>
                <a:gs pos="75000"><a:srgbClr val="113665"/></a:gs>
                <a:gs pos="100000"><a:srgbClr val="07182E"/></a:gs>
              </a:gsLst>
              <a:lin ang="3240000" scaled="1"/>
            </a:gradFill>
            <a:effectLst/>
          </p:bgPr>
        </p:bg>"""
        cSld = slide._element.find('{http://schemas.openxmlformats.org/presentationml/2006/main}cSld')
        existing_bg = cSld.find('{http://schemas.openxmlformats.org/presentationml/2006/main}bg')
        if existing_bg is not None:
            cSld.remove(existing_bg)
        cSld.insert(0, parse_xml(bg_xml))

    def add_header(slide, category_code, category_label, slide_title, top_tag=""):
        """Refined header with micro-category tag, prominent white title, and subtle line."""
        lbl_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.38), Inches(6.5), Inches(0.28))
        tf_l = lbl_box.text_frame
        tf_l.margin_left = tf_l.margin_top = tf_l.margin_right = tf_l.margin_bottom = 0
        p_l = tf_l.paragraphs[0]
        p_l.text = f"{category_code}  /  {category_label.upper()}"
        p_l.font.name = "Segoe UI"
        p_l.font.size = Pt(11)
        p_l.font.bold = True
        p_l.font.color.rgb = COLOR_CYAN

        if top_tag:
            tag_box = slide.shapes.add_textbox(Inches(7.5), Inches(0.38), Inches(5.033), Inches(0.28))
            tf_t = tag_box.text_frame
            tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
            p_t = tf_t.paragraphs[0]
            p_t.text = top_tag.upper()
            p_t.font.name = "Segoe UI"
            p_t.font.size = Pt(10.5)
            p_t.font.bold = True
            p_t.font.color.rgb = COLOR_CYAN_SOFT
            p_t.alignment = PP_ALIGN.RIGHT

        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(11.733), Inches(0.55))
        tf = title_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = slide_title
        p.font.name = "Segoe UI"
        p.font.size = Pt(25)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE

        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.28), Inches(11.733), Inches(0.015))
        line.fill.solid()
        line.fill.fore_color.rgb = SURFACE_BORDER
        line.line.fill.background()

    # =========================================================================
    # SLIDE 1: Title, The Hook & Team VisionGuard
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    apply_native_gradient(s1)

    # Top Brand Bar
    s1_brand = s1.shapes.add_textbox(Inches(0.8), Inches(0.48), Inches(11.733), Inches(0.28))
    tf_s1b = s1_brand.text_frame
    tf_s1b.margin_left = tf_s1b.margin_top = tf_s1b.margin_right = tf_s1b.margin_bottom = 0
    p_b = tf_s1b.paragraphs[0]
    p_b.text = "AUTONOMOUS WAREHOUSE CARGO INTELLIGENCE"
    p_b.font.name = "Segoe UI"
    p_b.font.size = Pt(11)
    p_b.font.bold = True
    p_b.font.color.rgb = COLOR_CYAN

    # Main Project Title & Tagline
    s1_title_box = s1.shapes.add_textbox(Inches(0.8), Inches(0.82), Inches(11.733), Inches(1.1))
    tf_s1t = s1_title_box.text_frame
    tf_s1t.word_wrap = True
    tf_s1t.margin_left = tf_s1t.margin_top = tf_s1t.margin_right = tf_s1t.margin_bottom = 0
    
    p_h = tf_s1t.paragraphs[0]
    p_h.text = "DockGuard AI"
    p_h.font.name = "Segoe UI"
    p_h.font.size = Pt(36)
    p_h.font.bold = True
    p_h.font.color.rgb = COLOR_WHITE

    p_tag = tf_s1t.add_paragraph()
    p_tag.text = "Because gravity shouldn't win on the warehouse loading dock."
    p_tag.font.name = "Segoe UI"
    p_tag.font.size = Pt(16.5)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_CYAN
    p_tag.space_before = Pt(3)

    # The 10-Second Pitch Card (Full Width Callout, Elegant & Punchy)
    pitch_card = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(2.08), Inches(11.733), Inches(1.28))
    pitch_card.fill.solid()
    pitch_card.fill.fore_color.rgb = SURFACE_ACTIVE
    pitch_card.line.color.rgb = COLOR_CYAN
    pitch_card.line.width = Pt(1.5)

    p_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(2.08), Inches(0.04), Inches(1.28))
    p_bar.fill.solid()
    p_bar.fill.fore_color.rgb = COLOR_CYAN
    p_bar.line.fill.background()

    pitch_tb = s1.shapes.add_textbox(Inches(1.05), Inches(2.18), Inches(11.25), Inches(1.08))
    tf_p = pitch_tb.text_frame
    tf_p.word_wrap = True
    tf_p.margin_left = tf_p.margin_top = tf_p.margin_right = tf_p.margin_bottom = 0

    p_ph = tf_p.paragraphs[0]
    p_ph.text = "THE 10-SECOND PITCH"
    p_ph.font.name = "Segoe UI"
    p_ph.font.size = Pt(11)
    p_ph.font.bold = True
    p_ph.font.color.rgb = COLOR_CYAN_SOFT

    p_pt = tf_p.add_paragraph()
    p_pt.text = "Ever opened an online order to find your new gadget smashed into puzzle pieces? It almost never happens in the delivery van. It happens in the 4:00 PM warehouse rush where boxes fly, pallets wobble, and nobody notices. We built DockGuard to watch CCTV feeds in real time, catch drops and rough drags in seconds, and make sure damaged boxes never leave the building."
    p_pt.font.name = "Segoe UI"
    p_pt.font.size = Pt(11.5)
    p_pt.font.color.rgb = COLOR_SLATE_LIGHT
    p_pt.space_before = Pt(4)

    # Left: Team Members Card (Squad)
    left_w = Inches(5.72)
    right_w = Inches(5.72)
    s1_cards_y = Inches(3.52)
    s1_cards_h = Inches(3.62)

    team_card = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), s1_cards_y, left_w, s1_cards_h)
    team_card.fill.solid()
    team_card.fill.fore_color.rgb = SURFACE_BG
    team_card.line.color.rgb = SURFACE_BORDER
    team_card.line.width = Pt(1)

    t_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), s1_cards_y, left_w, Inches(0.035))
    t_bar.fill.solid()
    t_bar.fill.fore_color.rgb = COLOR_CYAN
    t_bar.line.fill.background()

    team_tb = s1.shapes.add_textbox(Inches(1.05), s1_cards_y + Inches(0.18), left_w - Inches(0.5), s1_cards_h - Inches(0.35))
    tf_t = team_tb.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0

    p_th = tf_t.paragraphs[0]
    p_th.text = "THE SQUAD: TEAM VISIONGUARD"
    p_th.font.name = "Segoe UI"
    p_th.font.size = Pt(14)
    p_th.font.bold = True
    p_th.font.color.rgb = COLOR_CYAN

    members = [
        ("Aastha Gupta", "Vision Whisperer", "Trained our custom YOLOv8 model to spot cartons, pallets & workers at awkward angles"),
        ("Lucky Lakhani", "Pipeline & AI Hacker", "Built the sub-second video buffer, FastAPI endpoints & connected Google Gemini"),
        ("Runjan Bawa", "UI & Experience Builder", "Crafted the live dashboard, audio chimes, trend charts & made it look clean")
    ]

    for name, title, role in members:
        p = tf_t.add_paragraph()
        p.text = f"• {name}  —  "
        p.font.name = "Segoe UI"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.space_before = Pt(8)

        run_t = p.add_run()
        run_t.text = f"[{title}]"
        run_t.font.bold = True
        run_t.font.color.rgb = COLOR_CYAN

        p_desc = tf_t.add_paragraph()
        p_desc.text = f"   {role}"
        p_desc.font.name = "Segoe UI"
        p_desc.font.size = Pt(10.5)
        p_desc.font.color.rgb = COLOR_SLATE_BODY
        p_desc.space_before = Pt(1)

    # Right: Why This Matters Card (Large Impact Stats & Explanations)
    stats_card = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.813), s1_cards_y, right_w, s1_cards_h)
    stats_card.fill.solid()
    stats_card.fill.fore_color.rgb = SURFACE_BG
    stats_card.line.color.rgb = SURFACE_BORDER
    stats_card.line.width = Pt(1)

    s_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.813), s1_cards_y, right_w, Inches(0.035))
    s_bar.fill.solid()
    s_bar.fill.fore_color.rgb = COLOR_CYAN_SOFT
    s_bar.line.fill.background()

    stats_tb = s1.shapes.add_textbox(Inches(7.063), s1_cards_y + Inches(0.18), right_w - Inches(0.5), s1_cards_h - Inches(0.35))
    tf_s = stats_tb.text_frame
    tf_s.word_wrap = True
    tf_s.margin_left = tf_s.margin_top = tf_s.margin_right = tf_s.margin_bottom = 0

    ps_h = tf_s.paragraphs[0]
    ps_h.text = "WHY THIS ACTUALLY MATTERS"
    ps_h.font.name = "Segoe UI"
    ps_h.font.size = Pt(14)
    ps_h.font.bold = True
    ps_h.font.color.rgb = COLOR_CYAN_SOFT

    highlights = [
        ("$50B+ Annual Lost Cargo:", "That's how much merchandise gets wrecked in warehouses before even making it onto the highway. Most of it goes completely unrecorded."),
        ("Human Eyes Can't Keep Up:", "A single supervisor can't watch 10 bays, 40 fast-moving workers, and forklift traffic all at once. Blame turns into guessing games."),
        ("Catching It at the Dock:", "If you catch a cracked box before it's loaded into the trailer, replacing it costs $10. If it reaches the customer, it costs $200+ and a bad review.")
    ]

    for head, text in highlights:
        p = tf_s.add_paragraph()
        p.text = f"• {head} "
        p.font.name = "Segoe UI"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.space_before = Pt(8)

        run = p.add_run()
        run.text = text
        run.font.bold = False
        run.font.color.rgb = COLOR_SLATE_BODY

    # =========================================================================
    # SLIDE 2: Problem, Solution & The Human User Journey
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    apply_native_gradient(s2)
    add_header(s2, "02", "Problem, Solution & User Journey",
               "The Mystery of the Smashed Box (And How We Catch It)")

    # 7-Step Life Cycle of a Saved Box (Horizontal Flow)
    flow_steps = [
        ("1. Loading Bay", "Cartons loaded into trucks"),
        ("2. CCTV Camera", "Standard security camera"),
        ("3. AI Eyes", "YOLOv8 tracks every box"),
        ("4. Danger!", "Speed spike or drag flagged"),
        ("5. Friendly Chime", "Polite sound alert at bay"),
        ("6. Quick Check", "Worker inspects & resets"),
        ("7. Zero Damage", "Shipment leaves 100% intact")
    ]
    step_w = Inches(1.58)
    step_g = Inches(0.11)
    f_top = Inches(1.48)

    for i, (stitle, sdesc) in enumerate(flow_steps):
        lx = Inches(0.8) + i * (step_w + step_g)
        is_highlight = i in [3, 4, 6]

        scard = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, lx, f_top, step_w, Inches(1.22))
        scard.fill.solid()
        scard.fill.fore_color.rgb = SURFACE_ACTIVE if is_highlight else SURFACE_BG
        scard.line.color.rgb = COLOR_CYAN if is_highlight else SURFACE_BORDER
        scard.line.width = Pt(1.5 if is_highlight else 1)

        s_bar = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, lx, f_top, step_w, Inches(0.035))
        s_bar.fill.solid()
        s_bar.fill.fore_color.rgb = COLOR_CYAN if is_highlight else SURFACE_BORDER
        s_bar.line.fill.background()

        sbox = s2.shapes.add_textbox(lx + Inches(0.06), f_top + Inches(0.1), step_w - Inches(0.12), Inches(1.05))
        stf = sbox.text_frame
        stf.word_wrap = True
        stf.margin_left = stf.margin_top = stf.margin_right = stf.margin_bottom = 0

        p_t = stf.paragraphs[0]
        p_t.text = stitle
        p_t.font.name = "Segoe UI"
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_CYAN if is_highlight else COLOR_WHITE
        p_t.alignment = PP_ALIGN.CENTER

        p_d = stf.add_paragraph()
        p_d.text = sdesc
        p_d.font.name = "Segoe UI"
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = COLOR_SLATE_LIGHT
        p_d.alignment = PP_ALIGN.CENTER
        p_d.space_before = Pt(3)

    # Real human stories: Ramesh (Loader) vs Pooja (Supervisor)
    uj_top = Inches(2.88)
    uj_h = Inches(4.35)
    uj_w = Inches(5.72)

    # Journey 1: Ramesh
    r_card = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), uj_top, uj_w, uj_h)
    r_card.fill.solid()
    r_card.fill.fore_color.rgb = SURFACE_BG
    r_card.line.color.rgb = SURFACE_BORDER
    r_card.line.width = Pt(1)

    r_line = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), uj_top, uj_w, Inches(0.04))
    r_line.fill.solid()
    r_line.fill.fore_color.rgb = COLOR_CYAN
    r_line.line.fill.background()

    r_box = s2.shapes.add_textbox(Inches(1.05), uj_top + Inches(0.18), uj_w - Inches(0.5), uj_h - Inches(0.35))
    tf_r = r_box.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = tf_r.margin_top = tf_r.margin_right = tf_r.margin_bottom = 0

    pr_h = tf_r.paragraphs[0]
    pr_h.text = "THE LOADER'S STORY: Ramesh at Loading Bay 3"
    pr_h.font.name = "Segoe UI"
    pr_h.font.size = Pt(14)
    pr_h.font.bold = True
    pr_h.font.color.rgb = COLOR_CYAN

    ramesh_points = [
        ("The Rush:", "It's 4:15 PM, 34°C, and Ramesh has 45 minutes to finish packing a 40-foot trailer."),
        ("The Slip:", "He tries lifting a 25kg crate without a partner. His grip slips, and the box crashes 1.2 meters to the concrete."),
        ("No Panic Siren:", "Instead of an ear-piercing fire alarm that makes everyone freeze, a friendly, microwave-style *ding* chimes at Bay 3, and his dock screen flashes yellow."),
        ("What He Does:", "Instead of sheepishly hiding the box in the back of the truck, Ramesh stops, inspects the tape, calls his teammate for a 2-person lift, and sets the item aside."),
        ("The Win:", "No broken microwave sent to a customer, and Ramesh learns to ask for a hand with heavy loads.")
    ]
    for p_title, p_text in ramesh_points:
        p = tf_r.add_paragraph()
        p.text = f"• {p_title} "
        p.font.name = "Segoe UI"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.space_before = Pt(6)

        run = p.add_run()
        run.text = p_text
        run.font.bold = False
        run.font.color.rgb = COLOR_SLATE_BODY

    # Journey 2: Pooja
    p_card = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.813), uj_top, uj_w, uj_h)
    p_card.fill.solid()
    p_card.fill.fore_color.rgb = SURFACE_BG
    p_card.line.color.rgb = SURFACE_BORDER
    p_card.line.width = Pt(1)

    p_line = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.813), uj_top, uj_w, Inches(0.04))
    p_line.fill.solid()
    p_line.fill.fore_color.rgb = COLOR_CYAN_SOFT
    p_line.line.fill.background()

    p_box = s2.shapes.add_textbox(Inches(7.063), uj_top + Inches(0.18), uj_w - Inches(0.5), uj_h - Inches(0.35))
    tf_p = p_box.text_frame
    tf_p.word_wrap = True
    tf_p.margin_left = tf_p.margin_top = tf_p.margin_right = tf_p.margin_bottom = 0

    pp_h = tf_p.paragraphs[0]
    pp_h.text = "THE SUPERVISOR'S STORY: Pooja with her iPad"
    pp_h.font.name = "Segoe UI"
    pp_h.font.size = Pt(14)
    pp_h.font.bold = True
    pp_h.font.color.rgb = COLOR_CYAN_SOFT

    pooja_points = [
        ("The Daily Nightmare:", "Pooja used to spend 45 minutes every evening fast-forwarding through blurry CCTV tapes trying to figure out who dropped a customer's TV."),
        ("Instant Notification:", "Her tablet buzzes: 'Bay 3: High-Velocity Drop Flagged (10:14 AM)'."),
        ("TikTok-Length Replay:", "She taps it and immediately watches a 5-second replay showing the carton falling, complete with bounding box tracking and impact velocity."),
        ("Quick Resolution:", "She signs off on a packaging replacement in 10 seconds flat—no shouting matches, no guessing."),
        ("Asking the AI:", "At the end of the week, she asks the Gemini chat: 'Which shift has the most drops?' and instantly gets an answer for Monday's safety huddle.")
    ]
    for p_title, p_text in pooja_points:
        p = tf_p.add_paragraph()
        p.text = f"• {p_title} "
        p.font.name = "Segoe UI"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.space_before = Pt(6)

        run = p.add_run()
        run.text = p_text
        run.font.bold = False
        run.font.color.rgb = COLOR_SLATE_BODY

    # =========================================================================
    # SLIDE 3: Under the Hood (Tech Stack)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    apply_native_gradient(s3)
    add_header(s3, "03", "Technical Architecture & Tech Stack",
               "Under the Hood: How We Taught Cameras to Care About Boxes",
               top_tag="Confidential — Hackathon Project")

    tech_cards = [
        ("1. Computer Vision (YOLOv8 + ByteTrack)", [
            ("The Model:", "Ultralytics YOLOv8 fine-tuned on warehouse objects."),
            ("What it sees:", "Workers, cardboard cartons, wooden pallets, and forklifts."),
            ("The ByteTrack Trick:", "Keeps track of 'Box #4' even when a worker walks in front of it so the ID doesn't get lost.")
        ]),
        ("2. The Physics & Motion Rules", [
            ("Drop Detector:", "If a box's downward Y-velocity spikes > 2.5 m/s and suddenly hits zero, that's a crash."),
            ("Drag Detector:", "If a carton slides > 2 meters across the floor without lifting, it flags rough dragging."),
            ("Stack Tilt Check:", "Measures the angle of boxes on pallets—anything tilted > 15° triggers a wobble warning.")
        ]),
        ("3. Conversational AI (Google Gemini 2.5)", [
            ("Why an LLM?", "Supervisors hate writing SQL queries or clicking through 20 filter dropdowns."),
            ("How it works:", "Feeds SQLite telemetry into Gemini to answer plain questions: 'Did Bay 3 drop anything today?'"),
            ("Result:", "Instant plain-English answers with timestamps.")
        ]),
        ("4. Smart Video Snips (OpenCV + FFmpeg)", [
            ("No Wasted Storage:", "We don't save 24 hours of boring empty dock video."),
            ("Rolling Ring Buffer:", "Keeps last 15 seconds in memory; automatically cuts a neat 5-second replay clip on alert."),
            ("Web Ready:", "Encodes to lightweight H.264 so it plays instantly in the browser.")
        ]),
        ("5. Fast Python Backend & Database", [
            ("FastAPI Core:", "Super-fast async framework handling video uploads, alert WebSockets, and stats."),
            ("SQLite + SQLAlchemy:", "Simple, reliable local database storing incident records, drop heights, and camera IDs."),
            ("Clean API:", "Well-documented REST routes for the frontend to poll.")
        ]),
        ("6. React Dashboard & Sound Alerts", [
            ("Frontend Stack:", "React 18, TypeScript, and Tailwind CSS for a crisp, responsive layout."),
            ("Interactive Charts:", "Recharts rendering 7-day risk trends and KPI cards."),
            ("Audio Chimes:", "Web Audio API generates soft synthetic tones in-browser without downloading sound files.")
        ])
    ]

    t_col_w = Inches(3.73)
    t_col_g = Inches(0.27)
    t_row_h = Inches(2.78)
    t_row_g = Inches(0.22)
    t_sx = Inches(0.8)
    t_sy = Inches(1.48)

    for idx, (head, items) in enumerate(tech_cards):
        r = idx // 3
        c = idx % 3
        x = t_sx + c * (t_col_w + t_col_g)
        y = t_sy + r * (t_row_h + t_row_g)

        card = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, t_col_w, t_row_h)
        card.fill.solid()
        card.fill.fore_color.rgb = SURFACE_BG
        card.line.color.rgb = SURFACE_BORDER
        card.line.width = Pt(1)

        strip = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, t_col_w, Inches(0.04))
        strip.fill.solid()
        strip.fill.fore_color.rgb = COLOR_CYAN
        strip.line.fill.background()

        tbox = s3.shapes.add_textbox(x + Inches(0.18), y + Inches(0.14), t_col_w - Inches(0.36), t_row_h - Inches(0.28))
        tf = tbox.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_h = tf.paragraphs[0]
        p_h.text = head
        p_h.font.name = "Segoe UI"
        p_h.font.size = Pt(12)
        p_h.font.bold = True
        p_h.font.color.rgb = COLOR_CYAN

        for k, v in items:
            p_i = tf.add_paragraph()
            p_i.text = f"• {k} "
            p_i.font.name = "Segoe UI"
            p_i.font.size = Pt(10.5)
            p_i.font.bold = True
            p_i.font.color.rgb = COLOR_WHITE
            p_i.space_before = Pt(6)

            run = p_i.add_run()
            run.text = v
            run.font.bold = False
            run.font.color.rgb = COLOR_SLATE_BODY

    # =========================================================================
    # SLIDE 4: In Action: Real Screenshots & Tested Scenarios
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    apply_native_gradient(s4)
    add_header(s4, "04", "Prototype Screenshots & Demo",
               "In Action: Spotting Drops, Drags & Tilted Pallets")

    s4_right_x = Inches(8.35)
    s4_right_w = Inches(4.18)

    # Top Left Screenshot: Object Detection & Dragging
    if os.path.exists(IMG_CV_DRAGGING):
        s4.shapes.add_picture(IMG_CV_DRAGGING, Inches(0.8), Inches(1.48), width=Inches(3.55), height=Inches(2.55))
        cap1 = s4.shapes.add_textbox(Inches(0.8), Inches(4.06), Inches(3.55), Inches(0.3))
        cap1.text_frame.word_wrap = True
        cap1.text_frame.margin_left = cap1.text_frame.margin_top = cap1.text_frame.margin_right = cap1.text_frame.margin_bottom = 0
        p_c1 = cap1.text_frame.paragraphs[0]
        p_c1.text = "AI detecting worker & box dragged 4.6m on wet floor"
        p_c1.font.name = "Segoe UI"
        p_c1.font.size = Pt(9.5)
        p_c1.font.color.rgb = COLOR_CYAN

    # Top Right Screenshot: Drop Hazard Replay
    if os.path.exists(IMG_DROP_HAZARD):
        s4.shapes.add_picture(IMG_DROP_HAZARD, Inches(4.55), Inches(1.48), width=Inches(3.6), height=Inches(2.55))
        cap2 = s4.shapes.add_textbox(Inches(4.55), Inches(4.06), Inches(3.6), Inches(0.3))
        cap2.text_frame.word_wrap = True
        cap2.text_frame.margin_left = cap2.text_frame.margin_top = cap2.text_frame.margin_right = cap2.text_frame.margin_bottom = 0
        p_c2 = cap2.text_frame.paragraphs[0]
        p_c2.text = "Instant 5-second replay with falling box trajectory"
        p_c2.font.name = "Segoe UI"
        p_c2.font.size = Pt(9.5)
        p_c2.font.color.rgb = COLOR_CYAN

    # Bottom Screenshot: Full Dashboard
    if os.path.exists(IMG_DASHBOARD):
        s4.shapes.add_picture(IMG_DASHBOARD, Inches(0.8), Inches(4.42), width=Inches(7.35), height=Inches(2.45))
        cap3 = s4.shapes.add_textbox(Inches(0.8), Inches(6.92), Inches(7.35), Inches(0.3))
        cap3.text_frame.word_wrap = True
        cap3.text_frame.margin_left = cap3.text_frame.margin_top = cap3.text_frame.margin_right = cap3.text_frame.margin_bottom = 0
        p_c3 = cap3.text_frame.paragraphs[0]
        p_c3.text = "The live dashboard: Pastel KPI cards, 7-day risk trend curves, and instant alert drawer"
        p_c3.font.name = "Segoe UI"
        p_c3.font.size = Pt(9.5)
        p_c3.font.color.rgb = COLOR_SLATE_MUTED

    # Right Column: 4 Real Test Scenarios + Live Links
    sc_card = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, s4_right_x, Inches(1.48), s4_right_w, Inches(5.72))
    sc_card.fill.solid()
    sc_card.fill.fore_color.rgb = SURFACE_BG
    sc_card.line.color.rgb = SURFACE_BORDER
    sc_card.line.width = Pt(1)

    sc_bar = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, s4_right_x, Inches(1.48), s4_right_w, Inches(0.04))
    sc_bar.fill.solid()
    sc_bar.fill.fore_color.rgb = COLOR_CYAN
    sc_bar.line.fill.background()

    sc_box = s4.shapes.add_textbox(s4_right_x + Inches(0.22), Inches(1.65), s4_right_w - Inches(0.44), Inches(5.4))
    tf_sc = sc_box.text_frame
    tf_sc.word_wrap = True
    tf_sc.margin_left = tf_sc.margin_top = tf_sc.margin_right = tf_sc.margin_bottom = 0

    p_sct = tf_sc.paragraphs[0]
    p_sct.text = "4 REAL SCENARIOS WE TESTED"
    p_sct.font.name = "Segoe UI"
    p_sct.font.size = Pt(13)
    p_sct.font.bold = True
    p_sct.font.color.rgb = COLOR_CYAN

    scenarios = [
        ("1. The 'Butterfingers' Drop:", "Carton slips from 1.3m off pallet staging. The camera spots the free-fall spike and triggers a CRITICAL alert in 1.2s flat."),
        ("2. The Wet-Floor Hockey Puck:", "A worker slides a 20kg box 4.6m across wet concrete. The system measures the ground distance and flags HIGH risk dragging."),
        ("3. The Leaning Tower of Boxes:", "Boxes stacked with a 17° tilt without proper interlocking are flagged as CAUTION so the loader can straighten the pile."),
        ("4. Grilling the AI Assistant:", "We typed: 'Which bay had drops today?' and Gemini parsed the database logs to tell us Bay 3 had 2 drop incidents at 10:14 AM and 2:30 PM.")
    ]
    for s_head, s_desc in scenarios:
        p = tf_sc.add_paragraph()
        p.text = f"• {s_head} "
        p.font.name = "Segoe UI"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.space_before = Pt(7)

        run = p.add_run()
        run.text = s_desc
        run.font.bold = False
        run.font.color.rgb = COLOR_SLATE_BODY

    p_link = tf_sc.add_paragraph()
    p_link.text = "TEST IT YOURSELF (LIVE LINKS):"
    p_link.font.name = "Segoe UI"
    p_link.font.size = Pt(11)
    p_link.font.bold = True
    p_link.font.color.rgb = COLOR_CYAN
    p_link.space_before = Pt(12)

    links_text = [
        ("Live Web App:", "smart-warehouse-system-rk8p.onrender.com"),
        ("Local Port:", "localhost:8000 / localhost:5173"),
        ("Open Source Repo:", "github.com/Aastha008/Smart-Warehouse-System")
    ]
    for l_label, l_url in links_text:
        pl = tf_sc.add_paragraph()
        pl.text = f"  • {l_label} "
        pl.font.name = "Segoe UI"
        pl.font.size = Pt(10)
        pl.font.bold = True
        pl.font.color.rgb = COLOR_WHITE
        pl.space_before = Pt(2)

        run_u = pl.add_run()
        run_u.text = l_url
        run_u.font.bold = False
        run_u.font.color.rgb = COLOR_SLATE_MUTED

    # =========================================================================
    # SLIDE 5: Feedback, Iterations & Real Impact
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    apply_native_gradient(s5)
    add_header(s5, "05", "Feedback, Iterations & Real Impact",
               "What Warehouse Crews Told Us (And How They Roasted Version 1)")

    user_w = Inches(7.5)
    row_y = Inches(1.48)
    row_h = Inches(1.02)

    personas = [
        ("The Shift Supervisor", "I can't watch hours of boring CCTV tapes while running around 6 bays.",
         "Built a 1-click replay button that jumps right to the 5-second drop moment with red/yellow timeline markers."),
        ("The Loading Worker", "Your first alarm sounded like a nuclear meltdown siren. Everyone hated it.",
         "Switched to a polite, gentle audio chime for small issues, saving louder alerts only for big drops."),
        ("The Logistics Manager", "Cool tech, but how do I prove to my boss that we're actually breaking fewer things?",
         "Designed real-time KPI stat cards and a 7-day risk trend chart showing the 95.8% damage-free handling rate."),
        ("The Quality Inspector", "When customers return broken ceramics, the freight company claims we dropped it.",
         "Saved tamper-evident video clips showing exact time, bay number, and drop height so there's zero finger-pointing."),
        ("The Safety Officer", "Workers drag heavy boxes across wet spots and blow out their backs.",
         "Added automatic wet-floor hazard detection boxes and recommendations for two-person lifting.")
    ]

    for i, (role, quote, change) in enumerate(personas):
        y = row_y + i * (row_h + Inches(0.1))
        card = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y, user_w, row_h)
        card.fill.solid()
        card.fill.fore_color.rgb = SURFACE_BG
        card.line.color.rgb = SURFACE_BORDER
        card.line.width = Pt(1)

        c_line = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y, Inches(0.04), row_h)
        c_line.fill.solid()
        c_line.fill.fore_color.rgb = COLOR_CYAN if i%2==0 else COLOR_CYAN_SOFT
        c_line.line.fill.background()

        tbox = s5.shapes.add_textbox(Inches(0.98), y + Inches(0.08), user_w - Inches(0.28), row_h - Inches(0.16))
        tf = tbox.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_r = tf.paragraphs[0]
        p_r.text = f"{role}: "
        p_r.font.name = "Segoe UI"
        p_r.font.size = Pt(11)
        p_r.font.bold = True
        p_r.font.color.rgb = COLOR_CYAN

        run_q = p_r.add_run()
        run_q.text = f'"{quote}"'
        run_q.font.bold = False
        run_q.font.italic = True
        run_q.font.color.rgb = COLOR_WHITE

        p_c = tf.add_paragraph()
        p_c.text = f"→ How we fixed it: {change}"
        p_c.font.name = "Segoe UI"
        p_c.font.size = Pt(10)
        p_c.font.color.rgb = COLOR_SLATE_LIGHT
        p_c.space_before = Pt(3)

    # Right: Measurable Results
    res_x = Inches(8.55)
    res_w = Inches(3.98)
    res_card = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, res_x, Inches(1.48), res_w, Inches(5.5))
    res_card.fill.solid()
    res_card.fill.fore_color.rgb = SURFACE_BG
    res_card.line.color.rgb = SURFACE_BORDER
    res_card.line.width = Pt(1)

    res_bar = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, res_x, Inches(1.48), res_w, Inches(0.04))
    res_bar.fill.solid()
    res_bar.fill.fore_color.rgb = COLOR_CYAN
    res_bar.line.fill.background()

    res_box = s5.shapes.add_textbox(res_x + Inches(0.22), Inches(1.65), res_w - Inches(0.44), Inches(5.2))
    tf_res = res_box.text_frame
    tf_res.word_wrap = True
    tf_res.margin_left = tf_res.margin_top = tf_res.margin_right = tf_res.margin_bottom = 0

    p_rt = tf_res.paragraphs[0]
    p_rt.text = "WHAT OUR TESTING SHOWED"
    p_rt.font.name = "Segoe UI"
    p_rt.font.size = Pt(13)
    p_rt.font.bold = True
    p_rt.font.color.rgb = COLOR_CYAN

    stats = [
        ("Sub-1.5s Reaction Time:", "From the instant a box crashes to the floor, the system detects it and plays a sound in under 1.5 seconds."),
        ("30 mins down to 1 min:", "Supervisors no longer waste half an hour hunting for incident timestamps—the 5-second replay is right there."),
        ("Caught 8 out of 9 Drops:", "In our test video footage, the AI caught 8 out of 9 drops that human workers didn't bother reporting."),
        ("Zero Guesswork on Claims:", "Having a video clip with a timestamp and drop height completely shuts down freight liability disputes.")
    ]
    for s_title, s_text in stats:
        p = tf_res.add_paragraph()
        p.text = f"• {s_title} "
        p.font.name = "Segoe UI"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.space_before = Pt(8)

        run = p.add_run()
        run.text = s_text
        run.font.bold = False
        run.font.color.rgb = COLOR_SLATE_BODY

    # =========================================================================
    # SLIDE 6: The Good, The Glitches & What's Next (3-Stage Progression)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    apply_native_gradient(s6)
    add_header(s6, "06", "Conclusion, Real Limitations & Roadmap",
               "The Good, The Glitches & What’s Next")

    col3_w = Inches(3.68)
    col3_g = Inches(0.34)
    col3_top = Inches(1.48)
    col3_h = Inches(4.55)

    sections = [
        ("01 — WHAT'S WORKING", "The Good Stuff", SURFACE_BG, SURFACE_BORDER, COLOR_WHITE, [
            ("Live Cloud App:", "Hosted online 24/7 on Render with working frontend, backend, and database."),
            ("Real Video Analysis:", "Processes uploaded CCTV footage, draws bounding boxes, and flags drops and dragging."),
            ("Dashboard & Sound:", "Real-time KPI cards, 7-day risk trend curves, and in-browser audio chimes."),
            ("Gemini Assistant:", "Actually answers conversational questions using real database records.")
        ]),
        ("02 — CURRENT LIMITATIONS", "Honest Glitches", SURFACE_BG, SURFACE_BORDER, COLOR_SLATE_MUTED, [
            ("Free Tier Cloud CPU:", "Running video analysis on a free CPU instance takes 5–8 seconds per clip. A dedicated GPU will make it instant."),
            ("The Crowd Problem:", "When 3 workers crowd directly in front of a box, the camera can temporarily lose sight of it."),
            ("Morning Sunlight Glare:", "Intense morning glare through open truck doors can slightly lower detection confidence.")
        ]),
        ("03 — WHAT'S NEXT", "Enterprise Roadmap", SURFACE_ACTIVE, SURFACE_BORDER_CYAN, COLOR_CYAN, [
            ("Edge Hardware (NVIDIA Jetson):", "Run YOLOv8 right on the dock on a $150 Jetson nano for instant <50ms processing."),
            ("Barcode Scanner Link:", "Connect detection timestamps directly to package tracking numbers (WMS integration)."),
            ("Ergonomic Lifting Checks:", "Warn workers if they bend at the back instead of lifting with their knees to prevent injury.")
        ])
    ]

    for i, (col_num, col_title, bg_c, bord_c, h_color, col_points) in enumerate(sections):
        cx = Inches(0.8) + i * (col3_w + col3_g)
        is_dest = (i == 2)

        sc = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, col3_top, col3_w, col3_h)
        sc.fill.solid()
        sc.fill.fore_color.rgb = bg_c
        sc.line.color.rgb = bord_c
        sc.line.width = Pt(1.5 if is_dest else 1)

        s_strip = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, col3_top, col3_w, Inches(0.04))
        s_strip.fill.solid()
        s_strip.fill.fore_color.rgb = COLOR_CYAN if is_dest else SURFACE_BORDER
        s_strip.line.fill.background()

        sbox = s6.shapes.add_textbox(cx + Inches(0.2), col3_top + Inches(0.18), col3_w - Inches(0.4), col3_h - Inches(0.35))
        stf = sbox.text_frame
        stf.word_wrap = True
        stf.margin_left = stf.margin_top = stf.margin_right = stf.margin_bottom = 0

        p_th = stf.paragraphs[0]
        p_th.text = col_num
        p_th.font.name = "Segoe UI"
        p_th.font.size = Pt(14)
        p_th.font.bold = True
        p_th.font.color.rgb = COLOR_CYAN if is_dest else COLOR_SLATE_MUTED

        p_sub = stf.add_paragraph()
        p_sub.text = col_title
        p_sub.font.name = "Segoe UI"
        p_sub.font.size = Pt(16.5)
        p_sub.font.bold = True
        p_sub.font.color.rgb = h_color
        p_sub.space_before = Pt(2)

        for pk, pv in col_points:
            p = stf.add_paragraph()
            p.text = f"• {pk} "
            p.font.name = "Segoe UI"
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = COLOR_WHITE
            p.space_before = Pt(7)

            run = p.add_run()
            run.text = pv
            run.font.bold = False
            run.font.color.rgb = COLOR_SLATE_BODY

        if i < 2:
            arr_x = cx + col3_w + Inches(0.08)
            arr = s6.shapes.add_textbox(arr_x, col3_top + Inches(1.8), Inches(0.2), Inches(0.5))
            tf_a = arr.text_frame
            tf_a.margin_left = tf_a.margin_top = tf_a.margin_right = tf_a.margin_bottom = 0
            pa = tf_a.paragraphs[0]
            pa.text = "→"
            pa.font.name = "Segoe UI"
            pa.font.size = Pt(24)
            pa.font.bold = True
            pa.font.color.rgb = COLOR_CYAN
            pa.alignment = PP_ALIGN.CENTER

    # Elegant Bottom Footer (Punchline + Team Credits)
    foot_line = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.22), Inches(11.733), Inches(0.015))
    foot_line.fill.solid()
    foot_line.fill.fore_color.rgb = SURFACE_BORDER
    foot_line.line.fill.background()

    foot_box = s6.shapes.add_textbox(Inches(0.8), Inches(6.32), Inches(11.733), Inches(0.8))
    tf_b = foot_box.text_frame
    tf_b.word_wrap = True
    tf_b.margin_left = tf_b.margin_top = tf_b.margin_right = tf_b.margin_bottom = 0

    p_bt = tf_b.paragraphs[0]
    p_bt.text = "DockGuard AI: "
    p_bt.font.name = "Segoe UI"
    p_bt.font.size = Pt(15)
    p_bt.font.bold = True
    p_bt.font.color.rgb = COLOR_WHITE
    
    r_punch = p_bt.add_run()
    r_punch.text = "From detecting risk  →  to preventing it."
    r_punch.font.bold = True
    r_punch.font.color.rgb = COLOR_CYAN

    p_bs = tf_b.add_paragraph()
    p_bs.text = "Team VisionGuard: Aastha Gupta, Lucky Lakhani, Runjan Bawa   |   smart-warehouse-system-rk8p.onrender.com   |   github.com/Aastha008/Smart-Warehouse-System"
    p_bs.font.name = "Segoe UI"
    p_bs.font.size = Pt(10.5)
    p_bs.font.color.rgb = COLOR_SLATE_MUTED
    p_bs.space_before = Pt(3)

    for path in output_paths:
        prs.save(path)
        print(f"Saved perfect presentation at: {path}")

if __name__ == "__main__":
    build_perfect_presentation()
