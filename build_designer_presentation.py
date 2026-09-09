"""
DockGuard AI - High-End Human-Designed Presentation Deck
Rebuilt from scratch with a bespoke, polished technology/startup deck aesthetic.
Features:
- Sophisticated 4-stop deep navy-to-oceanic blue gradient background on all slides.
- Disciplined color system: Crisp White + Electric Sky Cyan (#38BDF8) accents + Light Slate body text.
- No repetitive card templates or generic AI rounded boxes.
- Slide 6 built as a horizontal progressive story: 01 WHAT'S WORKING -> 02 CURRENT LIMITATIONS -> 03 WHAT'S NEXT.
- Minimalist, elegant footer line instead of giant bottom rectangles.
- Fully preserved content, real prototype screenshots, and accurate technical details.
"""
import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml import parse_xml

def build_designer_presentation(output_paths=None):
    if output_paths is None:
        output_paths = [
            "Smart_Warehouse_DockGuard_Presentation.pptx",
            "DockGuard_AI_Presentation_Deck.pptx"
        ]

    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Premium Brand Palette (Disciplined Blue & Sky Cyan)
    COLOR_WHITE = RGBColor(255, 255, 255)         # Crisp pure white
    COLOR_CYAN = RGBColor(56, 189, 248)          # Electric sky cyan (#38BDF8)
    COLOR_CYAN_SOFT = RGBColor(125, 211, 252)     # Soft cyan (#7DD3FC)
    COLOR_SLATE_LIGHT = RGBColor(226, 232, 240)   # High legibility slate (#E2E8F0)
    COLOR_SLATE_BODY = RGBColor(203, 213, 225)    # Standard body text slate (#CBD5E1)
    COLOR_SLATE_MUTED = RGBColor(148, 163, 184)   # Subtle metadata / secondary (#94A3B8)
    
    SURFACE_BG = RGBColor(10, 25, 46)            # Elegant translucent dark navy surface (#0A192E)
    SURFACE_BG_ACTIVE = RGBColor(16, 44, 82)     # Highlighted forward destination surface (#102C52)
    SURFACE_BORDER = RGBColor(28, 62, 102)       # Clean hairline border (#1C3E66)
    SURFACE_BORDER_CYAN = RGBColor(56, 189, 248) # Active border cyan

    # Screenshots
    IMG_DASHBOARD = r"C:\Users\hp\.gemini\antigravity\brain\587ef984-1fd1-4bbd-91b4-721393f702af\.user_uploaded\media_1788627628552.png"
    IMG_CV_DRAGGING = r"C:\Users\hp\.gemini\antigravity\brain\587ef984-1fd1-4bbd-91b4-721393f702af\.user_uploaded\media_1788498059037.png"
    IMG_DROP_HAZARD = r"C:\Users\hp\.gemini\antigravity\brain\587ef984-1fd1-4bbd-91b4-721393f702af\.user_uploaded\media_1788497397504.png"

    def apply_background(slide):
        """Native 4-stop diagonal blue gradient canvas applied directly to slide background."""
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
        # Insert as first child of cSld as mandated by OpenXML schema
        existing_bg = cSld.find('{http://schemas.openxmlformats.org/presentationml/2006/main}bg')
        if existing_bg is not None:
            cSld.remove(existing_bg)
        cSld.insert(0, parse_xml(bg_xml))

    def add_top_nav(slide, category_code, category_label, slide_title, top_right_text=""):
        """Clean modern top navigation bar without bulky boxes."""
        # Top micro category tracker
        nav_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.42), Inches(7.0), Inches(0.3))
        tf_n = nav_box.text_frame
        tf_n.word_wrap = False
        tf_n.margin_left = tf_n.margin_top = tf_n.margin_right = tf_n.margin_bottom = 0
        p_n = tf_n.paragraphs[0]
        p_n.text = f"{category_code}  /  {category_label.upper()}"
        p_n.font.name = "Segoe UI"
        p_n.font.size = Pt(9.5)
        p_n.font.bold = True
        p_n.font.color.rgb = COLOR_CYAN

        # Top right tag if specified
        if top_right_text:
            tag_box = slide.shapes.add_textbox(Inches(7.8), Inches(0.42), Inches(4.733), Inches(0.3))
            tf_t = tag_box.text_frame
            tf_t.word_wrap = False
            tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
            p_t = tf_t.paragraphs[0]
            p_t.text = top_right_text.upper()
            p_t.font.name = "Segoe UI"
            p_t.font.size = Pt(8.5)
            p_t.font.bold = True
            p_t.font.color.rgb = COLOR_SLATE_MUTED
            p_t.alignment = PP_ALIGN.RIGHT

        # Primary Slide Heading
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.733), Inches(0.55))
        tf = t_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = slide_title
        p.font.name = "Segoe UI"
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE

        # Fine accent rule
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.36), Inches(11.733), Inches(0.015))
        line.fill.solid()
        line.fill.fore_color.rgb = SURFACE_BORDER
        line.line.fill.background()

    # =========================================================================
    # SLIDE 1: Solution & Team (Asymmetrical Startup Pitch Architecture)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    apply_background(s1)

    # Top brand bar
    brand_box = s1.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.733), Inches(0.3))
    tf_b = brand_box.text_frame
    tf_b.margin_left = tf_b.margin_top = tf_b.margin_right = tf_b.margin_bottom = 0
    pb = tf_b.paragraphs[0]
    pb.text = "AUTONOMOUS WAREHOUSE CARGO INTELLIGENCE"
    pb.font.name = "Segoe UI"
    pb.font.size = Pt(10)
    pb.font.bold = True
    pb.font.color.rgb = COLOR_CYAN

    # Left Column: Hero Title, Proposition & Team
    left_x = Inches(0.8)
    left_w = Inches(6.8)

    h_box = s1.shapes.add_textbox(left_x, Inches(0.95), left_w, Inches(1.3))
    tf_h = h_box.text_frame
    tf_h.word_wrap = True
    tf_h.margin_left = tf_h.margin_top = tf_h.margin_right = tf_h.margin_bottom = 0
    p_hero = tf_h.paragraphs[0]
    p_hero.text = "DockGuard AI"
    p_hero.font.name = "Segoe UI"
    p_hero.font.size = Pt(36)
    p_hero.font.bold = True
    p_hero.font.color.rgb = COLOR_WHITE

    p_prop = tf_h.add_paragraph()
    p_prop.text = "Because gravity shouldn't win on the warehouse loading dock."
    p_prop.font.name = "Segoe UI"
    p_prop.font.size = Pt(15)
    p_prop.font.bold = True
    p_prop.font.color.rgb = COLOR_CYAN
    p_prop.space_before = Pt(4)

    # Narrative callout block with sleek cyan accent bar (NOT a bloated rounded card)
    narrative_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, left_x, Inches(2.42), Inches(0.04), Inches(1.2))
    narrative_bar.fill.solid()
    narrative_bar.fill.fore_color.rgb = COLOR_CYAN
    narrative_bar.line.fill.background()

    narrative_bg = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, left_x + Inches(0.04), Inches(2.42), left_w - Inches(0.04), Inches(1.2))
    narrative_bg.fill.solid()
    narrative_bg.fill.fore_color.rgb = SURFACE_BG
    narrative_bg.line.fill.background()

    nar_box = s1.shapes.add_textbox(left_x + Inches(0.2), Inches(2.48), left_w - Inches(0.35), Inches(1.08))
    tf_nar = nar_box.text_frame
    tf_nar.word_wrap = True
    tf_nar.margin_left = tf_nar.margin_top = tf_nar.margin_right = tf_nar.margin_bottom = 0
    
    p_nh = tf_nar.paragraphs[0]
    p_nh.text = "THE PROBLEM IN 10 SECONDS"
    p_nh.font.name = "Segoe UI"
    p_nh.font.size = Pt(9)
    p_nh.font.bold = True
    p_nh.font.color.rgb = COLOR_CYAN_SOFT

    p_nt = tf_nar.add_paragraph()
    p_nt.text = "Ever opened an online delivery to find a shattered product? It rarely breaks in the van. It happens in the 4:00 PM warehouse rush where cartons slip, pallets wobble, and nobody notices. DockGuard watches CCTV in real time to catch drops, rough drags, and stack collapses before goods ever leave the bay."
    p_nt.font.name = "Segoe UI"
    p_nt.font.size = Pt(10.5)
    p_nt.font.color.rgb = COLOR_SLATE_BODY
    p_nt.space_before = Pt(3)

    # Team section header
    team_lbl = s1.shapes.add_textbox(left_x, Inches(3.85), left_w, Inches(0.3))
    tf_tl = team_lbl.text_frame
    tf_tl.margin_left = tf_tl.margin_top = tf_tl.margin_right = tf_tl.margin_bottom = 0
    p_tl = tf_tl.paragraphs[0]
    p_tl.text = "THE BUILDERS  —  TEAM VISIONGUARD"
    p_tl.font.name = "Segoe UI"
    p_tl.font.size = Pt(10)
    p_tl.font.bold = True
    p_tl.font.color.rgb = COLOR_CYAN

    # Team Members (Structured clean rows with hairline borders)
    team_members = [
        ("Aastha Gupta", "Computer Vision Whisperer", "Trained custom YOLOv8 model for carton, pallet & worker detection under complex dock occlusions"),
        ("Lucky Lakhani", "Pipeline & AI Hacker", "Built low-latency video ring buffer, async FastAPI backend, and Gemini 2.5 RAG integration"),
        ("Runjan Bawa", "UI & Operational Experience", "Crafted the live dashboard, Web Audio chimes, 7-day risk charts, and supervisor workflows")
    ]

    for idx, (name, role_title, role_desc) in enumerate(team_members):
        ty = Inches(4.25) + idx * Inches(0.92)
        # Background plate
        t_row = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, left_x, ty, left_w, Inches(0.82))
        t_row.fill.solid()
        t_row.fill.fore_color.rgb = SURFACE_BG
        t_row.line.color.rgb = SURFACE_BORDER
        t_row.line.width = Pt(1)

        # Left subtle cyan highlight dot
        t_dot = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, left_x, ty, Inches(0.03), Inches(0.82))
        t_dot.fill.solid()
        t_dot.fill.fore_color.rgb = COLOR_CYAN
        t_dot.line.fill.background()

        t_box = s1.shapes.add_textbox(left_x + Inches(0.18), ty + Inches(0.08), left_w - Inches(0.3), Inches(0.66))
        tf_tm = t_box.text_frame
        tf_tm.word_wrap = True
        tf_tm.margin_left = tf_tm.margin_top = tf_tm.margin_right = tf_tm.margin_bottom = 0

        p_name = tf_tm.paragraphs[0]
        p_name.text = name
        p_name.font.name = "Segoe UI"
        p_name.font.size = Pt(11)
        p_name.font.bold = True
        p_name.font.color.rgb = COLOR_WHITE

        r_role = p_name.add_run()
        r_role.text = f"   •   {role_title}"
        r_role.font.size = Pt(9.5)
        r_role.font.bold = True
        r_role.font.color.rgb = COLOR_CYAN

        p_td = tf_tm.add_paragraph()
        p_td.text = role_desc
        p_td.font.name = "Segoe UI"
        p_td.font.size = Pt(9)
        p_td.font.color.rgb = COLOR_SLATE_MUTED
        p_td.space_before = Pt(2)

    # Right Column: High-Impact Industry Numbers & Reality Cards
    right_x = Inches(8.0)
    right_w = Inches(4.533)

    r_lbl = s1.shapes.add_textbox(right_x, Inches(0.95), right_w, Inches(0.3))
    tf_rl = r_lbl.text_frame
    tf_rl.margin_left = tf_rl.margin_top = tf_rl.margin_right = tf_rl.margin_bottom = 0
    p_rl = tf_rl.paragraphs[0]
    p_rl.text = "INDUSTRY REALITY & ECONOMIC IMPACT"
    p_rl.font.name = "Segoe UI"
    p_rl.font.size = Pt(10)
    p_rl.font.bold = True
    p_rl.font.color.rgb = COLOR_CYAN

    impact_cards = [
        ("01", "$50B+", "Annual Global Freight Damage",
         "Over $50 billion of merchandise is destroyed in warehouses each year before reaching highways. The majority goes entirely unrecorded at the loading dock."),
        ("02", "1 : 10", "Supervisor Blindspot Ratio",
         "A single dock supervisor oversees up to 10 active bays, 40 fast-moving workers, and forklift traffic. Blame turns into speculation and customer friction."),
        ("03", "< 1.5s", "Intervention Window",
         "Catching cracked goods at the dock costs ~$10 to repackage. Letting damaged goods ship to a customer costs $200+ in return logistics and lost account goodwill.")
    ]

    for idx, (num, metric, metric_title, detail) in enumerate(impact_cards):
        cy = Inches(1.4) + idx * Inches(1.78)

        card = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, right_x, cy, right_w, Inches(1.62))
        card.fill.solid()
        card.fill.fore_color.rgb = SURFACE_BG
        card.line.color.rgb = SURFACE_BORDER
        card.line.width = Pt(1)

        c_box = s1.shapes.add_textbox(right_x + Inches(0.22), cy + Inches(0.14), right_w - Inches(0.44), Inches(1.35))
        tf_c = c_box.text_frame
        tf_c.word_wrap = True
        tf_c.margin_left = tf_c.margin_top = tf_c.margin_right = tf_c.margin_bottom = 0

        p_m = tf_c.paragraphs[0]
        p_m.text = f"{num}   "
        p_m.font.name = "Segoe UI"
        p_m.font.size = Pt(11)
        p_m.font.bold = True
        p_m.font.color.rgb = COLOR_SLATE_MUTED

        r_big = p_m.add_run()
        r_big.text = f"{metric}  "
        r_big.font.name = "Segoe UI"
        r_big.font.size = Pt(17)
        r_big.font.bold = True
        r_big.font.color.rgb = COLOR_WHITE

        r_sub = p_m.add_run()
        r_sub.text = metric_title
        r_sub.font.name = "Segoe UI"
        r_sub.font.size = Pt(10)
        r_sub.font.bold = True
        r_sub.font.color.rgb = COLOR_CYAN

        p_det = tf_c.add_paragraph()
        p_det.text = detail
        p_det.font.name = "Segoe UI"
        p_det.font.size = Pt(9.5)
        p_det.font.color.rgb = COLOR_SLATE_BODY
        p_det.space_before = Pt(5)

    # Subtle bottom branding line
    s1_line = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(7.1), Inches(11.733), Inches(0.015))
    s1_line.fill.solid()
    s1_line.fill.fore_color.rgb = SURFACE_BORDER
    s1_line.line.fill.background()

    s1_foot = s1.shapes.add_textbox(Inches(0.8), Inches(7.15), Inches(11.733), Inches(0.25))
    tf_s1f = s1_foot.text_frame
    tf_s1f.margin_left = tf_s1f.margin_top = tf_s1f.margin_right = tf_s1f.margin_bottom = 0
    p_s1f = tf_s1f.paragraphs[0]
    p_s1f.text = "DockGuard AI  •  Autonomous Video Intelligence for Warehouse Loading Bays  •  Slide 1 of 6"
    p_s1f.font.name = "Segoe UI"
    p_s1f.font.size = Pt(8.5)
    p_s1f.font.color.rgb = COLOR_SLATE_MUTED

    # =========================================================================
    # SLIDE 2: Problem, Solution & Human User Journey
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    apply_background(s2)
    add_top_nav(s2, "02", "Problem, Solution & User Journey",
                "The Anatomy of a Saved Carton: From Sensor to Safe Shipment")

    # Section 1: 7-Step Operational Pipeline Flow
    flow_steps = [
        ("01", "Bay Activity", "Cartons loaded into 40ft trailer"),
        ("02", "CCTV Stream", "1080p camera captures bay frames"),
        ("03", "YOLOv8 Vision", "Spatial tracking of boxes & workers"),
        ("04", "Risk Detector", "Free-fall acceleration or drag flag"),
        ("05", "Dock Chime", "Subtle audible ping at Bay 3"),
        ("06", "Inspection", "Worker checks tape & sets aside"),
        ("07", "Zero Defect", "Shipment leaves 100% verified")
    ]

    p_w = Inches(1.58)
    p_gap = Inches(0.11)
    p_top = Inches(1.55)

    for i, (num, title, desc) in enumerate(flow_steps):
        px = Inches(0.8) + i * (p_w + p_gap)
        is_hero = i in [3, 4, 6]

        pipe_box = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, px, p_top, p_w, Inches(1.02))
        pipe_box.fill.solid()
        pipe_box.fill.fore_color.rgb = SURFACE_BG_ACTIVE if is_hero else SURFACE_BG
        pipe_box.line.color.rgb = COLOR_CYAN if is_hero else SURFACE_BORDER
        pipe_box.line.width = Pt(1.5 if is_hero else 1)

        # Top micro highlight line for hero steps
        if is_hero:
            h_line = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, px, p_top, p_w, Inches(0.03))
            h_line.fill.solid()
            h_line.fill.fore_color.rgb = COLOR_CYAN
            h_line.line.fill.background()

        tb = s2.shapes.add_textbox(px + Inches(0.08), p_top + Inches(0.08), p_w - Inches(0.16), Inches(0.88))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p1 = tf.paragraphs[0]
        p1.text = f"{num} • {title}"
        p1.font.name = "Segoe UI"
        p1.font.size = Pt(9.5)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_CYAN if is_hero else COLOR_WHITE

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = "Segoe UI"
        p2.font.size = Pt(8.2)
        p2.font.color.rgb = COLOR_SLATE_LIGHT
        p2.space_before = Pt(3)

    # Section 2: Dual Human Journeys (Ramesh the Loader vs Pooja the Supervisor)
    j_top = Inches(2.78)
    j_w = Inches(5.7)
    j_h = Inches(4.15)

    # Left Track: Ramesh
    r_panel = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), j_top, j_w, j_h)
    r_panel.fill.solid()
    r_panel.fill.fore_color.rgb = SURFACE_BG
    r_panel.line.color.rgb = SURFACE_BORDER
    r_panel.line.width = Pt(1)

    r_top_bar = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), j_top, j_w, Inches(0.03))
    r_top_bar.fill.solid()
    r_top_bar.fill.fore_color.rgb = COLOR_CYAN
    r_top_bar.line.fill.background()

    r_tb = s2.shapes.add_textbox(Inches(1.05), j_top + Inches(0.18), j_w - Inches(0.5), j_h - Inches(0.35))
    tf_r = r_tb.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = tf_r.margin_top = tf_r.margin_right = tf_r.margin_bottom = 0

    p_rh = tf_r.paragraphs[0]
    p_rh.text = "OPERATOR JOURNEY: RAMESH AT BAY 3"
    p_rh.font.name = "Segoe UI"
    p_rh.font.size = Pt(11)
    p_rh.font.bold = True
    p_rh.font.color.rgb = COLOR_CYAN

    p_rs = tf_r.add_paragraph()
    p_rs.text = "How DockGuard supports rather than polices dockworkers under pressure."
    p_rs.font.name = "Segoe UI"
    p_rs.font.size = Pt(9)
    p_rs.font.color.rgb = COLOR_SLATE_MUTED
    p_rs.space_before = Pt(2)

    ramesh_steps = [
        ("The Rush Window", "It's 4:15 PM, 34°C, and Ramesh has 45 minutes to finish packing a 40-foot container before driver cutoff."),
        ("The Accidental Drop", "Lifting a heavy 25kg crate solo, his grip slips. The carton crashes 1.2 meters directly onto the concrete floor."),
        ("Non-Punitive Chime", "Instead of a harsh alarm that triggers fear or panic, a polite, microwave-style chime pings at Bay 3 as the dock tablet pulses amber."),
        ("Immediate Correction", "Ramesh pauses, inspects the seal, requests assistance for a 2-person lift, and places the suspect carton on the audit cart."),
        ("The Outcome", "A broken high-value appliance never reaches the consumer, and Ramesh avoids back injury on subsequent lifts.")
    ]

    for title, desc in ramesh_steps:
        p = tf_r.add_paragraph()
        p.text = f"• {title}: "
        p.font.name = "Segoe UI"
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.space_before = Pt(6)

        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = COLOR_SLATE_BODY

    # Right Track: Pooja
    p_panel = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.833), j_top, j_w, j_h)
    p_panel.fill.solid()
    p_panel.fill.fore_color.rgb = SURFACE_BG
    p_panel.line.color.rgb = SURFACE_BORDER
    p_panel.line.width = Pt(1)

    p_top_bar = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.833), j_top, j_w, Inches(0.03))
    p_top_bar.fill.solid()
    p_top_bar.fill.fore_color.rgb = COLOR_CYAN_SOFT
    p_top_bar.line.fill.background()

    p_tb = s2.shapes.add_textbox(Inches(7.08), j_top + Inches(0.18), j_w - Inches(0.5), j_h - Inches(0.35))
    tf_p = p_tb.text_frame
    tf_p.word_wrap = True
    tf_p.margin_left = tf_p.margin_top = tf_p.margin_right = tf_p.margin_bottom = 0

    p_ph = tf_p.paragraphs[0]
    p_ph.text = "SUPERVISOR JOURNEY: POOJA WITH HER TABLET"
    p_ph.font.name = "Segoe UI"
    p_ph.font.size = Pt(11)
    p_ph.font.bold = True
    p_ph.font.color.rgb = COLOR_CYAN_SOFT

    p_ps = tf_p.add_paragraph()
    p_ps.text = "Replacing 45 minutes of manual video scrubbing with instant actionable proof."
    p_ps.font.name = "Segoe UI"
    p_ps.font.size = Pt(9)
    p_ps.font.color.rgb = COLOR_SLATE_MUTED
    p_ps.space_before = Pt(2)

    pooja_steps = [
        ("The Daily Grind", "Pooja previously wasted 45 minutes every evening scrubbing grainy DVR tapes trying to verify freight claims."),
        ("Real-Time Dispatch", "Her tablet buzzes instantly: 'Bay 3: High-Velocity Drop Detected (10:14 AM)' with classified severity."),
        ("5-Second Micro Replay", "One tap launches a lightweight 5-second video clip displaying the carton trajectory, bounding box, and impact velocity."),
        ("Decisive Sign-Off", "She verifies the incident, authorizes repackaging in 15 seconds, and logs the package barcode without friction."),
        ("Natural Language Audit", "At shift handover, she asks Gemini: 'Summarize all high-velocity drops today' and receives an instant breakdown for the safety briefing.")
    ]

    for title, desc in pooja_steps:
        p = tf_p.add_paragraph()
        p.text = f"• {title}: "
        p.font.name = "Segoe UI"
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.space_before = Pt(6)

        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = COLOR_SLATE_BODY

    # Footer
    s2_line = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(7.1), Inches(11.733), Inches(0.015))
    s2_line.fill.solid()
    s2_line.fill.fore_color.rgb = SURFACE_BORDER
    s2_line.line.fill.background()

    s2_foot = s2.shapes.add_textbox(Inches(0.8), Inches(7.15), Inches(11.733), Inches(0.25))
    tf_s2f = s2_foot.text_frame
    tf_s2f.margin_left = tf_s2f.margin_top = tf_s2f.margin_right = tf_s2f.margin_bottom = 0
    p_s2f = tf_s2f.paragraphs[0]
    p_s2f.text = "DockGuard AI  •  Dual User Journey & 7-Stage Prevention Flow  •  Slide 2 of 6"
    p_s2f.font.name = "Segoe UI"
    p_s2f.font.size = Pt(8.5)
    p_s2f.font.color.rgb = COLOR_SLATE_MUTED

    # =========================================================================
    # SLIDE 3: Technical Architecture & Technology Stack
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    apply_background(s3)
    add_top_nav(s3, "03", "Technical Architecture & Stack",
                "Full-Stack Architecture: Computer Vision, Spatial Physics & LLM RAG",
                top_right_text="Confidential — Academic & Prototype Project")

    # Subtitle narrative
    arch_sub = s3.shapes.add_textbox(Inches(0.8), Inches(1.42), Inches(11.733), Inches(0.3))
    tf_as = arch_sub.text_frame
    tf_as.margin_left = tf_as.margin_top = tf_as.margin_right = tf_as.margin_bottom = 0
    p_as = tf_as.paragraphs[0]
    p_as.text = "End-to-end edge-to-cloud intelligence pipeline combining computer vision, kinematic rules, and conversational RAG."
    p_as.font.name = "Segoe UI"
    p_as.font.size = Pt(10)
    p_as.font.color.rgb = COLOR_CYAN

    # 6-Component Architecture Grid (3 columns x 2 rows)
    tech_modules = [
        ("01", "Computer Vision & Object Tracking", "YOLOv8 + ByteTrack (Ultralytics)", [
            ("Custom Weight Fine-Tuning: ", "Trained specifically on warehouse cartons, wooden pallets, personnel, and forklifts."),
            ("Persistent Identity Tracking: ", "ByteTrack maintains box IDs across frames even during temporary worker occlusion.")
        ]),
        ("02", "Spatial & Kinematic Physics Rules", "Real-Time Vector Math", [
            ("Free-Fall Acceleration: ", "Monitors downward velocity spikes (vy > 2.5 m/s -> 0 m/s sudden impact) to flag drop crashes."),
            ("Friction & Drag Distance: ", "Flags sustained lateral displacement (>2m on floor) without vertical lift to catch rough dragging."),
            ("Stack Tilt Calculation: ", "Measures bounding box tilt angles; orientations exceeding 15° trigger unstable stack warnings.")
        ]),
        ("03", "Conversational AI & Audit Assistant", "Google Gemini 2.5 Flash + RAG", [
            ("Natural Language RAG: ", "Ingests SQLite telemetry logs so supervisors can query history in plain English without SQL."),
            ("Shift Summaries: ", "Generates instant structured executive reports on bay risk hotspots and incident timestamps.")
        ]),
        ("04", "Rolling Video Snip Buffer", "OpenCV + FFmpeg Subprocess", [
            ("Zero Storage Waste: ", "Avoids saving hours of empty dock feeds; maintains a lightweight 15-second FIFO memory buffer."),
            ("5-Second Micro Replays: ", "Upon alert trigger, automatically transcodes a lightweight 5s H.264 clip for instant browser streaming.")
        ]),
        ("05", "High-Throughput API & Database", "FastAPI + SQLAlchemy + SQLite", [
            ("Asynchronous Event Loop: ", "Ultra-fast REST API handling CCTV video uploads, metric polling, and telemetry ingestion."),
            ("Live WebSocket Feeds: ", "Broadcasts sub-50ms incident events and danger alerts to connected dock clients.")
        ]),
        ("06", "Operational Frontend & Audio Engine", "React 18 + Tailwind + Web Audio API", [
            ("Responsive Supervisory UI: ", "Interactive KPI metrics, 7-day handling risk charts, and instant alert slide-out drawers."),
            ("Synthetic Audio Synthesis: ", "Web Audio API generates dock chimes on client devices without external audio file latency.")
        ])
    ]

    col_w = Inches(3.73)
    col_gap = Inches(0.27)
    row_h = Inches(2.45)
    row_gap = Inches(0.22)
    s_x = Inches(0.8)
    s_y = Inches(1.8)

    for idx, (num, mod_name, tech_sub, items) in enumerate(tech_modules):
        r = idx // 3
        c = idx % 3
        x = s_x + c * (col_w + col_gap)
        y = s_y + r * (row_h + row_gap)

        card = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, col_w, row_h)
        card.fill.solid()
        card.fill.fore_color.rgb = SURFACE_BG
        card.line.color.rgb = SURFACE_BORDER
        card.line.width = Pt(1)

        # Micro top accent line
        top_accent = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, col_w, Inches(0.025))
        top_accent.fill.solid()
        top_accent.fill.fore_color.rgb = COLOR_CYAN
        top_accent.line.fill.background()

        tb = s3.shapes.add_textbox(x + Inches(0.18), y + Inches(0.12), col_w - Inches(0.36), row_h - Inches(0.2))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_h = tf.paragraphs[0]
        p_h.text = f"{num} • {mod_name}"
        p_h.font.name = "Segoe UI"
        p_h.font.size = Pt(10)
        p_h.font.bold = True
        p_h.font.color.rgb = COLOR_WHITE

        p_sub = tf.add_paragraph()
        p_sub.text = tech_sub
        p_sub.font.name = "Segoe UI"
        p_sub.font.size = Pt(8.5)
        p_sub.font.bold = True
        p_sub.font.color.rgb = COLOR_CYAN
        p_sub.space_before = Pt(1)

        for k, v in items:
            p = tf.add_paragraph()
            p.text = f"• {k}"
            p.font.name = "Segoe UI"
            p.font.size = Pt(8.5)
            p.font.bold = True
            p.font.color.rgb = COLOR_WHITE
            p.space_before = Pt(4)

            run = p.add_run()
            run.text = v
            run.font.bold = False
            run.font.color.rgb = COLOR_SLATE_BODY

    # Footer
    s3_line = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(7.1), Inches(11.733), Inches(0.015))
    s3_line.fill.solid()
    s3_line.fill.fore_color.rgb = SURFACE_BORDER
    s3_line.line.fill.background()

    s3_foot = s3.shapes.add_textbox(Inches(0.8), Inches(7.15), Inches(11.733), Inches(0.25))
    tf_s3f = s3_foot.text_frame
    tf_s3f.margin_left = tf_s3f.margin_top = tf_s3f.margin_right = tf_s3f.margin_bottom = 0
    p_s3f = tf_s3f.paragraphs[0]
    p_s3f.text = "DockGuard AI  •  Full-Stack Architecture & Implementation Stack  •  Slide 3 of 6"
    p_s3f.font.name = "Segoe UI"
    p_s3f.font.size = Pt(8.5)
    p_s3f.font.color.rgb = COLOR_SLATE_MUTED

    # =========================================================================
    # SLIDE 4: Prototype Screenshots & Demo (Clean Visual Showcase)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    apply_background(s4)
    add_top_nav(s4, "04", "Prototype Screenshots & Demo",
                "Field Prototype: Live Object Detection, Replay & Supervisory Dashboard")

    left_screen_w = Inches(7.35)
    right_meta_x = Inches(8.4)
    right_meta_w = Inches(4.133)

    # Frame 1: CV Dragging Detection
    if os.path.exists(IMG_CV_DRAGGING):
        # Framing border
        f1 = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(3.55), Inches(2.5))
        f1.fill.solid()
        f1.fill.fore_color.rgb = SURFACE_BG
        f1.line.color.rgb = SURFACE_BORDER
        f1.line.width = Pt(1)
        s4.shapes.add_picture(IMG_CV_DRAGGING, Inches(0.81), Inches(1.51), width=Inches(3.53), height=Inches(2.48))

        cap1 = s4.shapes.add_textbox(Inches(0.8), Inches(4.03), Inches(3.55), Inches(0.28))
        tf_c1 = cap1.text_frame
        tf_c1.word_wrap = True
        tf_c1.margin_left = tf_c1.margin_top = tf_c1.margin_right = tf_c1.margin_bottom = 0
        p_c1 = tf_c1.paragraphs[0]
        p_c1.text = "AI tracking worker & carton dragged 4.6m on wet floor"
        p_c1.font.name = "Segoe UI"
        p_c1.font.size = Pt(8.5)
        p_c1.font.color.rgb = COLOR_CYAN

    # Frame 2: Drop Replay
    if os.path.exists(IMG_DROP_HAZARD):
        f2 = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.55), Inches(1.5), Inches(3.6), Inches(2.5))
        f2.fill.solid()
        f2.fill.fore_color.rgb = SURFACE_BG
        f2.line.color.rgb = SURFACE_BORDER
        f2.line.width = Pt(1)
        s4.shapes.add_picture(IMG_DROP_HAZARD, Inches(4.56), Inches(1.51), width=Inches(3.58), height=Inches(2.48))

        cap2 = s4.shapes.add_textbox(Inches(4.55), Inches(4.03), Inches(3.6), Inches(0.28))
        tf_c2 = cap2.text_frame
        tf_c2.word_wrap = True
        tf_c2.margin_left = tf_c2.margin_top = tf_c2.margin_right = tf_c2.margin_bottom = 0
        p_c2 = tf_c2.paragraphs[0]
        p_c2.text = "5-second incident replay with falling velocity vectors"
        p_c2.font.name = "Segoe UI"
        p_c2.font.size = Pt(8.5)
        p_c2.font.color.rgb = COLOR_CYAN

    # Frame 3: Live Dashboard Wide
    if os.path.exists(IMG_DASHBOARD):
        f3 = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(4.38), left_screen_w, Inches(2.62))
        f3.fill.solid()
        f3.fill.fore_color.rgb = SURFACE_BG
        f3.line.color.rgb = SURFACE_BORDER
        f3.line.width = Pt(1)
        s4.shapes.add_picture(IMG_DASHBOARD, Inches(0.81), Inches(4.39), width=Inches(7.33), height=Inches(2.35))

        cap3 = s4.shapes.add_textbox(Inches(0.8), Inches(6.78), left_screen_w, Inches(0.25))
        tf_c3 = cap3.text_frame
        tf_c3.word_wrap = True
        tf_c3.margin_left = tf_c3.margin_top = tf_c3.margin_right = tf_c3.margin_bottom = 0
        p_c3 = tf_c3.paragraphs[0]
        p_c3.text = "Production UI: Pastel KPI cards, 7-day risk trend curves, and real-time incident drawer"
        p_c3.font.name = "Segoe UI"
        p_c3.font.size = Pt(8.5)
        p_c3.font.color.rgb = COLOR_SLATE_MUTED

    # Right Column: 4 Real Test Scenarios + Deployment Links
    sc_panel = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, right_meta_x, Inches(1.5), right_meta_w, Inches(5.5))
    sc_panel.fill.solid()
    sc_panel.fill.fore_color.rgb = SURFACE_BG
    sc_panel.line.color.rgb = SURFACE_BORDER
    sc_panel.line.width = Pt(1)

    sc_top_bar = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, right_meta_x, Inches(1.5), right_meta_w, Inches(0.03))
    sc_top_bar.fill.solid()
    sc_top_bar.fill.fore_color.rgb = COLOR_CYAN
    sc_top_bar.line.fill.background()

    sc_tb = s4.shapes.add_textbox(right_meta_x + Inches(0.22), Inches(1.65), right_meta_w - Inches(0.44), Inches(5.2))
    tf_sc = sc_tb.text_frame
    tf_sc.word_wrap = True
    tf_sc.margin_left = tf_sc.margin_top = tf_sc.margin_right = tf_sc.margin_bottom = 0

    p_sct = tf_sc.paragraphs[0]
    p_sct.text = "EMPIRICAL TEST SCENARIOS"
    p_sct.font.name = "Segoe UI"
    p_sct.font.size = Pt(10.5)
    p_sct.font.bold = True
    p_sct.font.color.rgb = COLOR_CYAN

    scenarios = [
        ("01", "Carton Free-Fall Drop (>1.2m)", "Carton slips from staging pallet. Camera spots velocity spike (vy > 2.8 m/s) and triggers dock chime in 1.2s flat."),
        ("02", "Rough Wet-Floor Dragging", "Worker slides a 20kg box 4.6m across damp concrete. System calculates floor displacement and issues high-risk friction alert."),
        ("03", "Unstable Pallet Tilt (>17°)", "Boxes stacked at a 17° lean without interlock flagged as caution before transit collapse could occur."),
        ("04", "Gemini Natural Language Audit", "Asked 'Which bay had drops today?' Gemini parsed logs to confirm Bay 3 had 2 incidents at 10:14 AM and 2:30 PM.")
    ]

    for num, s_title, s_desc in scenarios:
        p = tf_sc.add_paragraph()
        p.text = f"{num} • {s_title}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(9.2)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.space_before = Pt(6)

        p_body = tf_sc.add_paragraph()
        p_body.text = s_desc
        p_body.font.name = "Segoe UI"
        p_body.font.size = Pt(8.5)
        p_body.font.color.rgb = COLOR_SLATE_BODY
        p_body.space_before = Pt(1)

    # Live Verification Links
    p_links_head = tf_sc.add_paragraph()
    p_links_head.text = "LIVE DEPLOYMENT & REPOSITORIES"
    p_links_head.font.name = "Segoe UI"
    p_links_head.font.size = Pt(9.5)
    p_links_head.font.bold = True
    p_links_head.font.color.rgb = COLOR_CYAN
    p_links_head.space_before = Pt(12)

    links_info = [
        ("Live Web App", "smart-warehouse-system-rk8p.onrender.com"),
        ("Local Port", "localhost:8000 / localhost:5173"),
        ("Open Source Repo", "github.com/Aastha008/Smart-Warehouse-System")
    ]
    for label, url in links_info:
        pl = tf_sc.add_paragraph()
        pl.text = f"• {label}: "
        pl.font.name = "Segoe UI"
        pl.font.size = Pt(8.5)
        pl.font.bold = True
        pl.font.color.rgb = COLOR_WHITE
        pl.space_before = Pt(2)

        r_u = pl.add_run()
        r_u.text = url
        r_u.font.bold = False
        r_u.font.color.rgb = COLOR_SLATE_MUTED

    # Footer
    s4_line = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(7.1), Inches(11.733), Inches(0.015))
    s4_line.fill.solid()
    s4_line.fill.fore_color.rgb = SURFACE_BORDER
    s4_line.line.fill.background()

    s4_foot = s4.shapes.add_textbox(Inches(0.8), Inches(7.15), Inches(11.733), Inches(0.25))
    tf_s4f = s4_foot.text_frame
    tf_s4f.margin_left = tf_s4f.margin_top = tf_s4f.margin_right = tf_s4f.margin_bottom = 0
    p_s4f = tf_s4f.paragraphs[0]
    p_s4f.text = "DockGuard AI  •  Field Prototypes, Test Scenarios & Verified Deployments  •  Slide 4 of 6"
    p_s4f.font.name = "Segoe UI"
    p_s4f.font.size = Pt(8.5)
    p_s4f.font.color.rgb = COLOR_SLATE_MUTED

    # =========================================================================
    # SLIDE 5: Impact, Damage Prevention & User Validation
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    apply_background(s5)
    add_top_nav(s5, "05", "Impact & User Validation",
                "Operational Feedback: How Warehouse Teams Shaped Our Iterations")

    stakeholder_w = Inches(7.5)
    metrics_x = Inches(8.55)
    metrics_w = Inches(3.983)

    personas = [
        ("The Shift Supervisor", "I can't watch hours of CCTV while running across 6 active bays.",
         "Engineered 1-click 5s replay clips with pre-buffered impact markers so reviews take <10 seconds."),
        ("The Dock Loader", "Your first alarm sounded like an evacuation siren. It made everyone defensive.",
         "Replaced harsh sirens with soft dock chimes and educational recommendations for 2-person lifts."),
        ("The Logistics Director", "How do I prove to executive leadership that we are actually breaking less freight?",
         "Designed real-time KPI stat cards and a 7-day risk trend chart showing the 95.8% damage-free handling rate."),
        ("The Quality Auditor", "Carriers always blame the warehouse for cracked goods discovered at destination.",
         "Saved tamper-evident video clips showing exact time, bay number, and drop height to eliminate liability debates."),
        ("The Safety Compliance Officer", "Workers repeatedly drag heavy goods over wet surfaces causing ergonomic injury.",
         "Added spatial wet-zone detection and automatic heavy carton weight warnings.")
    ]

    s5_y = Inches(1.5)
    card_h = Inches(0.98)

    for i, (role, quote, solution) in enumerate(personas):
        cy = s5_y + i * (card_h + Inches(0.1))

        c_panel = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), cy, stakeholder_w, card_h)
        c_panel.fill.solid()
        c_panel.fill.fore_color.rgb = SURFACE_BG
        c_panel.line.color.rgb = SURFACE_BORDER
        c_panel.line.width = Pt(1)

        # Subtle left accent bar
        l_bar = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), cy, Inches(0.03), card_h)
        l_bar.fill.solid()
        l_bar.fill.fore_color.rgb = COLOR_CYAN
        l_bar.line.fill.background()

        tb = s5.shapes.add_textbox(Inches(1.0), cy + Inches(0.08), stakeholder_w - Inches(0.3), card_h - Inches(0.16))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_r = tf.paragraphs[0]
        p_r.text = f"{role}: "
        p_r.font.name = "Segoe UI"
        p_r.font.size = Pt(10)
        p_r.font.bold = True
        p_r.font.color.rgb = COLOR_CYAN

        run_q = p_r.add_run()
        run_q.text = f'"{quote}"'
        run_q.font.bold = False
        run_q.font.italic = True
        run_q.font.color.rgb = COLOR_WHITE

        p_sol = tf.add_paragraph()
        p_sol.text = f"→ Iteration Implemented: {solution}"
        p_sol.font.name = "Segoe UI"
        p_sol.font.size = Pt(8.8)
        p_sol.font.color.rgb = COLOR_SLATE_BODY
        p_sol.space_before = Pt(3)

    # Right: Measurable Impact & Test Performance
    m_panel = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, metrics_x, Inches(1.5), metrics_w, Inches(5.3))
    m_panel.fill.solid()
    m_panel.fill.fore_color.rgb = SURFACE_BG
    m_panel.line.color.rgb = SURFACE_BORDER
    m_panel.line.width = Pt(1)

    m_top_bar = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, metrics_x, Inches(1.5), metrics_w, Inches(0.03))
    m_top_bar.fill.solid()
    m_top_bar.fill.fore_color.rgb = COLOR_CYAN
    m_top_bar.line.fill.background()

    m_tb = s5.shapes.add_textbox(metrics_x + Inches(0.22), Inches(1.65), metrics_w - Inches(0.44), Inches(5.0))
    tf_m = m_tb.text_frame
    tf_m.word_wrap = True
    tf_m.margin_left = tf_m.margin_top = tf_m.margin_right = tf_m.margin_bottom = 0

    p_mt = tf_m.paragraphs[0]
    p_mt.text = "MEASURED PROTOTYPE RESULTS"
    p_mt.font.name = "Segoe UI"
    p_mt.font.size = Pt(10.5)
    p_mt.font.bold = True
    p_mt.font.color.rgb = COLOR_CYAN

    kpis = [
        ("< 1.5s", "Detection-to-Chime Latency",
         "Sub-second CV inference flags drops and issues audio alerts before cartons can be covered up or loaded deep into trailers."),
        ("30m -> 1m", "Incident Verification Speed",
         "Supervisors access pre-buffered 5s clips in under 60 seconds, eliminating half-hour searches through manual DVR recordings."),
        ("89% (8/9)", "Unreported Drops Captured",
         "In blind test video runs, the vision pipeline intercepted 8 of 9 physical drop incidents that workers never logged manually."),
        ("100%", "Liability Audit Proof",
         "Timestamped clips with measured impact velocity resolve carrier-versus-warehouse liability disputes instantly.")
    ]

    for stat, stat_label, stat_desc in kpis:
        p_stat = tf_m.add_paragraph()
        p_stat.text = f"{stat} • "
        p_stat.font.name = "Segoe UI"
        p_stat.font.size = Pt(13)
        p_stat.font.bold = True
        p_stat.font.color.rgb = COLOR_WHITE
        p_stat.space_before = Pt(8)

        r_sl = p_stat.add_run()
        r_sl.text = stat_label
        r_sl.font.size = Pt(9.5)
        r_sl.font.bold = True
        r_sl.font.color.rgb = COLOR_CYAN

        p_desc = tf_m.add_paragraph()
        p_desc.text = stat_desc
        p_desc.font.name = "Segoe UI"
        p_desc.font.size = Pt(8.5)
        p_desc.font.color.rgb = COLOR_SLATE_BODY
        p_desc.space_before = Pt(2)

    # Footer
    s5_line = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(7.1), Inches(11.733), Inches(0.015))
    s5_line.fill.solid()
    s5_line.fill.fore_color.rgb = SURFACE_BORDER
    s5_line.line.fill.background()

    s5_foot = s5.shapes.add_textbox(Inches(0.8), Inches(7.15), Inches(11.733), Inches(0.25))
    tf_s5f = s5_foot.text_frame
    tf_s5f.margin_left = tf_s5f.margin_top = tf_s5f.margin_right = tf_s5f.margin_bottom = 0
    p_s5f = tf_s5f.paragraphs[0]
    p_s5f.text = "DockGuard AI  •  User Validation, Real Operational Feedback & Metrics  •  Slide 5 of 6"
    p_s5f.font.name = "Segoe UI"
    p_s5f.font.size = Pt(8.5)
    p_s5f.font.color.rgb = COLOR_SLATE_MUTED

    # =========================================================================
    # SLIDE 6: 3-Stage Progressive Roadmap (01 -> 02 -> 03) & Understated Footer
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    apply_background(s6)
    add_top_nav(s6, "06", "Conclusion & Roadmap",
                "The Honest Reality: Current Capabilities, Engineering Constraints & What's Next")

    # 3-Stage Progressive Story Horizontal Columns
    # 01 WHAT'S WORKING -> 02 CURRENT LIMITATIONS -> 03 WHAT'S NEXT
    col_width = Inches(3.68)
    col_gap_6 = Inches(0.34)
    s6_top = Inches(1.55)
    s6_height = Inches(4.75)

    stages = [
        ("01", "WHAT'S WORKING TODAY", "PROVEN CAPABILITIES", SURFACE_BG, SURFACE_BORDER, COLOR_WHITE, [
            ("Live Full-Stack Cloud App: ", "Hosted online 24/7 on Render with working frontend, FastAPI backend, and SQLite telemetry database."),
            ("Real Video Analysis: ", "Processes uploaded CCTV footage, draws accurate bounding boxes, and flags drops and dragging."),
            ("Dashboard & Audio Chimes: ", "Real-time KPI cards, 7-day risk trend curves, and zero-latency in-browser Web Audio chimes."),
            ("Gemini Conversational RAG: ", "Accurately answers natural language supervisor questions using live database records.")
        ]),
        ("02", "CURRENT LIMITATIONS", "HONEST CONSTRAINTS", SURFACE_BG, SURFACE_BORDER, COLOR_SLATE_MUTED, [
            ("Cloud CPU Latency: ", "Running deep video inference on free-tier cloud CPUs takes 5–8 seconds per clip. A dedicated GPU will make it instantaneous."),
            ("Heavy Crowding Occlusion: ", "When 3+ workers cluster tightly around a carton, bounding box tracking can temporarily lose continuity."),
            ("Morning Sunlight Glare: ", "Intense direct morning glare through open loading bay doors can slightly lower detection confidence.")
        ]),
        ("03", "WHAT'S NEXT", "ENTERPRISE ROADMAP", SURFACE_BG_ACTIVE, SURFACE_BORDER_CYAN, COLOR_CYAN, [
            ("Edge Hardware (NVIDIA Jetson): ", "Deploy localized TensorRT models on $150 dockside Jetson hardware for true <50ms processing."),
            ("Barcode Scanner Integration: ", "Synchronize AI incident timestamps directly with handheld barcode scans and WMS manifests."),
            ("Ergonomic Safety Coaching: ", "Warn workers if they bend at the spine instead of lifting with their knees to prevent chronic injury.")
        ])
    ]

    for idx, (num, stage_tag, stage_title, bg_clr, border_clr, header_clr, items) in enumerate(stages):
        x = Inches(0.8) + idx * (col_width + col_gap_6)
        is_dest = (idx == 2)

        # Stage Column Card
        card = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, s6_top, col_width, s6_height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_clr
        card.line.color.rgb = border_clr
        card.line.width = Pt(1.5 if is_dest else 1)

        # Top accent strip
        accent_strip = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, s6_top, col_width, Inches(0.035))
        accent_strip.fill.solid()
        accent_strip.fill.fore_color.rgb = COLOR_CYAN if is_dest else SURFACE_BORDER
        accent_strip.line.fill.background()

        # Text Frame
        tb = s6.shapes.add_textbox(x + Inches(0.22), s6_top + Inches(0.18), col_width - Inches(0.44), s6_height - Inches(0.35))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        # Stage Number + Tag
        p_num = tf.paragraphs[0]
        p_num.text = f"{num}  —  {stage_tag}"
        p_num.font.name = "Segoe UI"
        p_num.font.size = Pt(9.5)
        p_num.font.bold = True
        p_num.font.color.rgb = COLOR_CYAN if is_dest else COLOR_SLATE_MUTED

        # Stage Subtitle
        p_st = tf.add_paragraph()
        p_st.text = stage_title
        p_st.font.name = "Segoe UI"
        p_st.font.size = Pt(12)
        p_st.font.bold = True
        p_st.font.color.rgb = header_clr
        p_st.space_before = Pt(3)

        # Hairline separator inside card
        p_sep = tf.add_paragraph()
        p_sep.text = "—" * 28
        p_sep.font.name = "Segoe UI"
        p_sep.font.size = Pt(6)
        p_sep.font.color.rgb = SURFACE_BORDER
        p_sep.space_before = Pt(2)

        # Items
        for k, v in items:
            p = tf.add_paragraph()
            p.text = f"• {k}"
            p.font.name = "Segoe UI"
            p.font.size = Pt(9.2)
            p.font.bold = True
            p.font.color.rgb = COLOR_WHITE
            p.space_before = Pt(7)

            run = p.add_run()
            run.text = v
            run.font.bold = False
            run.font.color.rgb = COLOR_SLATE_BODY

        # Connector arrow between stage 1->2 and stage 2->3
        if idx < 2:
            arrow_x = x + col_width + Inches(0.08)
            arrow_tb = s6.shapes.add_textbox(arrow_x, s6_top + Inches(2.2), Inches(0.2), Inches(0.4))
            tf_a = arrow_tb.text_frame
            tf_a.margin_left = tf_a.margin_top = tf_a.margin_right = tf_a.margin_bottom = 0
            pa = tf_a.paragraphs[0]
            pa.text = "→"
            pa.font.name = "Segoe UI"
            pa.font.size = Pt(16)
            pa.font.bold = True
            pa.font.color.rgb = COLOR_CYAN
            pa.alignment = PP_ALIGN.CENTER

    # Elegant, Understated Footer Line (Replaces the giant bottom rectangle!)
    foot_line = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.6), Inches(11.733), Inches(0.015))
    foot_line.fill.solid()
    foot_line.fill.fore_color.rgb = SURFACE_BORDER
    foot_line.line.fill.background()

    foot_box = s6.shapes.add_textbox(Inches(0.8), Inches(6.72), Inches(11.733), Inches(0.45))
    tf_f = foot_box.text_frame
    tf_f.word_wrap = True
    tf_f.margin_left = tf_f.margin_top = tf_f.margin_right = tf_f.margin_bottom = 0

    pf1 = tf_f.paragraphs[0]
    pf1.text = "Team VisionGuard: Aastha Gupta, Lucky Lakhani, Runjan Bawa  •  Thank you for listening!"
    pf1.font.name = "Segoe UI"
    pf1.font.size = Pt(10.5)
    pf1.font.bold = True
    pf1.font.color.rgb = COLOR_WHITE

    pf2 = tf_f.add_paragraph()
    pf2.text = "Live Web App: smart-warehouse-system-rk8p.onrender.com   |   GitHub: github.com/Aastha008/Smart-Warehouse-System"
    pf2.font.name = "Segoe UI"
    pf2.font.size = Pt(9)
    pf2.font.color.rgb = COLOR_CYAN
    pf2.space_before = Pt(2)

    # Save to all target presentation files
    for path in output_paths:
        prs.save(path)
        print(f"Successfully generated designer presentation at: {path}")

if __name__ == "__main__":
    build_designer_presentation([
        "Smart_Warehouse_DockGuard_Presentation.pptx",
        "DockGuard_AI_Presentation_Deck.pptx",
        "DockGuard_Fun_Presentation.pptx"
    ])
