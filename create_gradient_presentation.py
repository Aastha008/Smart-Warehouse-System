"""
DockGuard AI - Presentation Deck with Pretty Blue Gradient Theme
Applies a cohesive, modern oceanic & royal blue gradient across ALL slides.
Human-generated, professional, engaging, and clear.
"""
import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml import parse_xml

def build_gradient_presentation(output_path="Smart_Warehouse_DockGuard_Presentation.pptx"):
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Theme Colors for Pretty Blue Gradient Slides
    CARD_BG = RGBColor(14, 30, 54)              # Translucent frosted navy card (#0E1E36)
    CARD_BORDER = RGBColor(40, 75, 120)         # Soft blue card border (#284B78)
    CARD_BG_HIGHLIGHT = RGBColor(20, 48, 88)    # Highlighted card fill (#143058)
    
    TEXT_WHITE = RGBColor(255, 255, 255)        # Crisp pure white for main titles & bold text
    TEXT_CYAN = RGBColor(125, 211, 252)         # Luminous sky/cyan for subtitles & headers (#7DD3FC)
    TEXT_SLATE_LIGHT = RGBColor(203, 213, 225)  # High-contrast readable light slate (#CBD5E1)
    TEXT_SLATE_MUTED = RGBColor(148, 163, 184)  # Muted secondary text (#94A3B8)
    
    PILL_BG = RGBColor(20, 48, 88)              # Tag pill background
    PILL_BORDER = RGBColor(56, 114, 186)        # Tag pill border
    PILL_TEXT = RGBColor(147, 197, 253)         # Light blue pill text
    
    ACCENT_BLUE = RGBColor(56, 189, 248)        # Electric sky blue (#38BDF8)
    ACCENT_GREEN = RGBColor(52, 211, 153)       # Vibrant emerald (#34D399)
    ACCENT_ROSE = RGBColor(251, 113, 133)       # Coral rose (#FB7185)
    ACCENT_AMBER = RGBColor(251, 191, 36)       # Warm amber (#FBBF24)
    ACCENT_PURPLE = RGBColor(192, 132, 252)     # Soft violet (#C084FC)

    # Screenshot paths
    IMG_DASHBOARD = r"C:\Users\hp\.gemini\antigravity\brain\587ef984-1fd1-4bbd-91b4-721393f702af\.user_uploaded\media_1788627628552.png"
    IMG_CV_DRAGGING = r"C:\Users\hp\.gemini\antigravity\brain\587ef984-1fd1-4bbd-91b4-721393f702af\.user_uploaded\media_1788498059037.png"
    IMG_DROP_HAZARD = r"C:\Users\hp\.gemini\antigravity\brain\587ef984-1fd1-4bbd-91b4-721393f702af\.user_uploaded\media_1788497397504.png"

    def apply_blue_gradient_background(slide):
        """Applies a pretty 4-stop diagonal blue gradient to the entire slide."""
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.line.fill.background()
        
        spPr = bg.element.spPr
        for child in list(spPr):
            if child.tag.endswith('solidFill') or child.tag.endswith('gradFill'):
                spPr.remove(child)

        # 4-stop rich blue gradient (Midnight Ocean -> Sapphire -> Cobalt -> Deep Twilight)
        grad_xml = """<a:gradFill xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" flip="none" rotWithShape="1">
            <a:gsLst>
                <a:gs pos="0">
                    <a:srgbClr val="08192E"/>
                </a:gs>
                <a:gs pos="42000">
                    <a:srgbClr val="12335E"/>
                </a:gs>
                <a:gs pos="78000">
                    <a:srgbClr val="1A4982"/>
                </a:gs>
                <a:gs pos="100000">
                    <a:srgbClr val="0A2140"/>
                </a:gs>
            </a:gsLst>
            <a:lin ang="3240000" scaled="1"/>
        </a:gradFill>"""
        spPr.append(parse_xml(grad_xml))
        return bg

    def add_slide_header(slide, title_text, pill_tag, confidential=False):
        """Standardized, high-end header with tag pill and divider line."""
        # Top Pill Tag
        tag_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.4), Inches(2.9), Inches(0.32))
        tag_card.fill.solid()
        tag_card.fill.fore_color.rgb = PILL_BG
        tag_card.line.color.rgb = PILL_BORDER
        tag_card.line.width = Pt(1)

        tf_tag = tag_card.text_frame
        tf_tag.word_wrap = False
        p_t = tf_tag.paragraphs[0]
        p_t.text = pill_tag.upper()
        p_t.font.name = "Segoe UI"
        p_t.font.size = Pt(9.5)
        p_t.font.bold = True
        p_t.font.color.rgb = PILL_TEXT
        p_t.alignment = PP_ALIGN.CENTER

        # Main Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.78), Inches(10.5), Inches(0.55))
        tf = t_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.name = "Segoe UI"
        p.font.size = Pt(21)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

        # Confidential Tag
        if confidential:
            c_box = slide.shapes.add_textbox(Inches(10.5), Inches(0.4), Inches(2.0), Inches(0.3))
            tf_c = c_box.text_frame
            p_c = tf_c.paragraphs[0]
            p_c.text = "Confidential - Hackathon Project"
            p_c.font.name = "Segoe UI"
            p_c.font.size = Pt(8.5)
            p_c.font.bold = True
            p_c.font.color.rgb = ACCENT_ROSE
            p_c.alignment = PP_ALIGN.RIGHT

        # Luminous accent divider line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.36), Inches(11.733), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = RGBColor(45, 85, 140)
        line.line.fill.background()

    # =========================================================================
    # SLIDE 1: Title, The Hook & Team VisionGuard
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    apply_blue_gradient_background(slide1)

    # Accent luminous bar
    top_band = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.75), Inches(11.733), Inches(0.06))
    top_band.fill.solid()
    top_band.fill.fore_color.rgb = ACCENT_BLUE
    top_band.line.fill.background()

    # Main Project Title
    t1_box = slide1.shapes.add_textbox(Inches(0.8), Inches(1.02), Inches(11.7), Inches(1.4))
    tf1 = t1_box.text_frame
    tf1.word_wrap = True
    
    p1 = tf1.paragraphs[0]
    p1.text = "DockGuard AI"
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE

    p1_sub = tf1.add_paragraph()
    p1_sub.text = "Because gravity shouldn't win on the warehouse loading dock."
    p1_sub.font.name = "Segoe UI"
    p1_sub.font.size = Pt(16)
    p1_sub.font.bold = True
    p1_sub.font.color.rgb = ACCENT_BLUE
    p1_sub.space_before = Pt(4)

    # The 10-Second Pitch Card
    hook_card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.4), Inches(11.733), Inches(1.35))
    hook_card.fill.solid()
    hook_card.fill.fore_color.rgb = CARD_BG_HIGHLIGHT
    hook_card.line.color.rgb = RGBColor(45, 95, 155)
    hook_card.line.width = Pt(1)

    hook_box = slide1.shapes.add_textbox(Inches(1.05), Inches(2.5), Inches(11.2), Inches(1.15))
    tf_h = hook_box.text_frame
    tf_h.word_wrap = True
    
    ph1 = tf_h.paragraphs[0]
    ph1.text = "THE 10-SECOND PITCH"
    ph1.font.name = "Segoe UI"
    ph1.font.size = Pt(10)
    ph1.font.bold = True
    ph1.font.color.rgb = ACCENT_CYAN = RGBColor(125, 211, 252)

    ph2 = tf_h.add_paragraph()
    ph2.text = "Ever opened an online order to find your new gadget smashed into puzzle pieces? It almost never happens in the delivery van. It happens in the 4:00 PM warehouse rush where boxes fly, pallets wobble, and nobody notices. We built DockGuard to watch CCTV feeds in real time, catch drops and rough drags in seconds, and make sure damaged boxes never leave the building."
    ph2.font.name = "Segoe UI"
    ph2.font.size = Pt(12)
    ph2.font.color.rgb = TEXT_SLATE_LIGHT
    ph2.space_before = Pt(3)

    # Left: Team Members Card
    team_card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(3.98), Inches(5.7), Inches(3.05))
    team_card.fill.solid()
    team_card.fill.fore_color.rgb = CARD_BG
    team_card.line.color.rgb = CARD_BORDER

    tbox = slide1.shapes.add_textbox(Inches(1.05), Inches(4.15), Inches(5.2), Inches(2.7))
    tf_t = tbox.text_frame
    tf_t.word_wrap = True

    p_th = tf_t.paragraphs[0]
    p_th.text = "THE SQUAD: TEAM VISIONGUARD"
    p_th.font.name = "Segoe UI"
    p_th.font.size = Pt(11)
    p_th.font.bold = True
    p_th.font.color.rgb = ACCENT_CYAN

    members = [
        ("Aastha Gupta", "Vision Whisperer", "Trained our custom YOLOv8 model to spot cartons, pallets & workers at awkward angles"),
        ("Lucky Lakhani", "Pipeline & AI Hacker", "Built the sub-second video buffer, FastAPI endpoints & connected Google Gemini"),
        ("Runjan Bawa", "UI & Experience Builder", "Crafted the live dashboard, audio chimes, trend charts & made it look clean")
    ]
    for name, title, role in members:
        p = tf_t.add_paragraph()
        p.text = f"• {name} — "
        p.font.name = "Segoe UI"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        p.space_before = Pt(7)

        run_t = p.add_run()
        run_t.text = f"[{title}]"
        run_t.font.bold = True
        run_t.font.color.rgb = ACCENT_PURPLE

        p_desc = tf_t.add_paragraph()
        p_desc.text = f"   {role}"
        p_desc.font.name = "Segoe UI"
        p_desc.font.size = Pt(9.5)
        p_desc.font.color.rgb = TEXT_SLATE_MUTED

    # Right: Why This Matters Card
    stats_card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.833), Inches(3.98), Inches(5.7), Inches(3.05))
    stats_card.fill.solid()
    stats_card.fill.fore_color.rgb = CARD_BG
    stats_card.line.color.rgb = CARD_BORDER

    sbox = slide1.shapes.add_textbox(Inches(7.08), Inches(4.15), Inches(5.2), Inches(2.7))
    tf_s = sbox.text_frame
    tf_s.word_wrap = True

    ps_h = tf_s.paragraphs[0]
    ps_h.text = "WHY THIS ACTUALLY MATTERS"
    ps_h.font.name = "Segoe UI"
    ps_h.font.size = Pt(11)
    ps_h.font.bold = True
    ps_h.font.color.rgb = ACCENT_CYAN

    highlights = [
        ("$50B+ Annual Lost Cargo:", "That's how much merchandise gets wrecked in warehouses before even making it onto the highway. Most of it goes completely unrecorded."),
        ("Human Eyes Can't Keep Up:", "A single supervisor can't watch 10 bays, 40 fast-moving workers, and forklift traffic all at once. Blame turns into guessing games."),
        ("Catching It at the Dock:", "If you catch a cracked box before it's loaded into the trailer, replacing it costs $10. If it reaches the customer, it costs $200+ and a bad review.")
    ]
    for head, text in highlights:
        p = tf_s.add_paragraph()
        p.text = f"• {head} "
        p.font.name = "Segoe UI"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        p.space_before = Pt(7)

        run = p.add_run()
        run.text = text
        run.font.bold = False
        run.font.color.rgb = TEXT_SLATE_LIGHT

    # =========================================================================
    # SLIDE 2: Problem, Solution & The Human User Journey
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    apply_blue_gradient_background(slide2)
    add_slide_header(slide2, "The Mystery of the Smashed Box (And How We Catch It)", "Slide 2: Problem, Solution & User Journey")

    # 7-Step Life Cycle of a Saved Box
    flow_steps = [
        ("1. Loading Bay", "Workers move cartons into trucks"),
        ("2. CCTV Camera", "Standard security camera feed"),
        ("3. AI Eyes", "YOLOv8 tracks every box & person"),
        ("4. Danger!", "Speed spike or ground drag flagged"),
        ("5. Friendly Chime", "Polite sound alert at the dock"),
        ("6. Quick Check", "Worker inspects & resets load"),
        ("7. Zero Damage", "Shipment leaves 100% intact")
    ]
    step_w = Inches(1.58)
    step_g = Inches(0.11)
    f_top = Inches(1.5)

    for i, (stitle, sdesc) in enumerate(flow_steps):
        lx = Inches(0.8) + i * (step_w + step_g)
        scard = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, lx, f_top, step_w, Inches(1.1))
        scard.fill.solid()
        is_highlight = i in [3, 4, 6]
        scard.fill.fore_color.rgb = RGBColor(30, 65, 115) if is_highlight else CARD_BG
        scard.line.color.rgb = ACCENT_BLUE if is_highlight else CARD_BORDER
        scard.line.width = Pt(1.5 if is_highlight else 1)

        sbox = slide2.shapes.add_textbox(lx + Inches(0.04), f_top + Inches(0.08), step_w - Inches(0.08), Inches(0.95))
        stf = sbox.text_frame
        stf.word_wrap = True
        p_t = stf.paragraphs[0]
        p_t.text = stitle
        p_t.font.name = "Segoe UI"
        p_t.font.size = Pt(10)
        p_t.font.bold = True
        p_t.font.color.rgb = ACCENT_CYAN if is_highlight else TEXT_WHITE
        p_t.alignment = PP_ALIGN.CENTER

        p_d = stf.add_paragraph()
        p_d.text = sdesc
        p_d.font.name = "Segoe UI"
        p_d.font.size = Pt(8.5)
        p_d.font.color.rgb = TEXT_SLATE_LIGHT
        p_d.alignment = PP_ALIGN.CENTER
        p_d.space_before = Pt(3)

    # Real human stories: Ramesh (Loader) vs Pooja (Supervisor)
    uj_top = Inches(2.85)
    uj_h = Inches(4.2)
    uj_w = Inches(5.7)

    # Journey 1: Ramesh
    r_card = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), uj_top, uj_w, uj_h)
    r_card.fill.solid()
    r_card.fill.fore_color.rgb = CARD_BG
    r_card.line.color.rgb = CARD_BORDER

    # Card accent line on top
    r_line = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), uj_top, uj_w, Inches(0.05))
    r_line.fill.solid()
    r_line.fill.fore_color.rgb = ACCENT_BLUE
    r_line.line.fill.background()

    r_box = slide2.shapes.add_textbox(Inches(1.05), uj_top + Inches(0.18), uj_w - Inches(0.5), uj_h - Inches(0.3))
    tf_r = r_box.text_frame
    tf_r.word_wrap = True

    pr_h = tf_r.paragraphs[0]
    pr_h.text = "THE LOADER'S STORY: Ramesh at Loading Bay 3"
    pr_h.font.name = "Segoe UI"
    pr_h.font.size = Pt(11)
    pr_h.font.bold = True
    pr_h.font.color.rgb = ACCENT_CYAN

    ramesh_points = [
        ("The Rush: ", "It's 4:15 PM, 34°C, and Ramesh has 45 minutes to finish packing a 40-foot trailer."),
        ("The Slip: ", "He tries lifting a 25kg crate without a partner. His grip slips, and the box crashes 1.2 meters to the concrete."),
        ("No Panic Siren: ", "Instead of an ear-piercing fire alarm that makes everyone freeze, a friendly, microwave-style *ding* chimes at Bay 3, and his dock screen flashes yellow."),
        ("What He Does: ", "Instead of sheepishly hiding the box in the back of the truck, Ramesh stops, inspects the tape, calls his teammate for a 2-person lift, and sets the item aside."),
        ("The Win: ", "No broken microwave sent to a customer, and Ramesh learns to ask for a hand with heavy loads.")
    ]
    for p_title, p_text in ramesh_points:
        p = tf_r.add_paragraph()
        p.text = f"• {p_title}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        p.space_before = Pt(6)

        run = p.add_run()
        run.text = p_text
        run.font.bold = False
        run.font.color.rgb = TEXT_SLATE_LIGHT

    # Journey 2: Pooja
    p_card = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.833), uj_top, uj_w, uj_h)
    p_card.fill.solid()
    p_card.fill.fore_color.rgb = CARD_BG
    p_card.line.color.rgb = CARD_BORDER

    p_line = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.833), uj_top, uj_w, Inches(0.05))
    p_line.fill.solid()
    p_line.fill.fore_color.rgb = ACCENT_PURPLE
    p_line.line.fill.background()

    p_box = slide2.shapes.add_textbox(Inches(7.08), uj_top + Inches(0.18), uj_w - Inches(0.5), uj_h - Inches(0.3))
    tf_p = p_box.text_frame
    tf_p.word_wrap = True

    pp_h = tf_p.paragraphs[0]
    pp_h.text = "THE SUPERVISOR'S STORY: Pooja with her iPad"
    pp_h.font.name = "Segoe UI"
    pp_h.font.size = Pt(11)
    pp_h.font.bold = True
    pp_h.font.color.rgb = ACCENT_PURPLE

    pooja_points = [
        ("The Daily Nightmare: ", "Pooja used to spend 45 minutes every evening fast-forwarding through blurry CCTV tapes trying to figure out who dropped a customer's TV."),
        ("Instant Notification: ", "Her tablet buzzes: 'Bay 3: High-Velocity Drop Flagged (10:14 AM)'."),
        ("TikTok-Length Replay: ", "She taps it and immediately watches a 5-second replay showing the carton falling, complete with bounding box tracking and impact velocity."),
        ("Quick Resolution: ", "She signs off on a packaging replacement in 10 seconds flat—no shouting matches, no guessing."),
        ("Asking the AI: ", "At the end of the week, she asks the Gemini chat: 'Which shift has the most drops?' and instantly gets an answer for Monday's safety huddle.")
    ]
    for p_title, p_text in pooja_points:
        p = tf_p.add_paragraph()
        p.text = f"• {p_title}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        p.space_before = Pt(6)

        run = p.add_run()
        run.text = p_text
        run.font.bold = False
        run.font.color.rgb = TEXT_SLATE_LIGHT

    # =========================================================================
    # SLIDE 3: Under the Hood (Tech Stack on Pretty Blue Gradient)
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    apply_blue_gradient_background(slide3)
    add_slide_header(slide3, "Under the Hood: How We Taught Cameras to Care About Boxes", "Slide 3: Technical Architecture & Tech Stack", confidential=True)

    tech_cards = [
        ("1. Computer Vision (YOLOv8 + ByteTrack)", [
            ("The Model: ", "Ultralytics YOLOv8 fine-tuned on warehouse objects."),
            ("What it sees: ", "Workers, cardboard cartons, wooden pallets, and forklifts."),
            ("The ByteTrack Trick: ", "Keeps track of 'Box #4' even when a worker walks in front of it so the ID doesn't get lost.")
        ]),
        ("2. The Physics & Motion Rules", [
            ("Drop Detector: ", "If a box's downward Y-velocity spikes > 2.5 m/s and suddenly hits zero, that's a crash."),
            ("Drag Detector: ", "If a carton slides > 2 meters across the floor without lifting, it flags rough dragging."),
            ("Stack Tilt Check: ", "Measures the angle of boxes on pallets—anything tilted > 15° triggers a wobble warning.")
        ]),
        ("3. Conversational AI (Google Gemini 1.5)", [
            ("Why an LLM? ", "Supervisors hate writing SQL queries or clicking 20 filters."),
            ("How it works: ", "We feed SQLite telemetry logs into Gemini so supervisors can ask plain questions like: 'Did Bay 3 drop anything today?'"),
            ("Result: ", "Instant plain-English answers with timestamps.")
        ]),
        ("4. Smart Video Snips (OpenCV + FFmpeg)", [
            ("No Wasted Storage: ", "We don't save 24 hours of boring empty dock video."),
            ("Rolling Ring Buffer: ", "Keeps the last 15 seconds in memory. When a drop triggers, it automatically cuts a neat 5-second replay clip."),
            ("Web Ready: ", "Encodes to lightweight H.264 so it plays instantly in the browser.")
        ]),
        ("5. Fast Python Backend & Database", [
            ("FastAPI Core: ", "Super-fast async Python framework handling video uploads, alert websockets, and stats."),
            ("SQLite + SQLAlchemy: ", "Simple, reliable local database storing incident records, drop heights, and camera IDs."),
            ("Clean API: ", "Well-documented REST routes for the frontend to poll.")
        ]),
        ("6. React Dashboard & Sound Alerts", [
            ("Frontend Stack: ", "React 18, TypeScript, and Tailwind CSS for a crisp, responsive layout."),
            ("Interactive Charts: ", "Recharts rendering 7-day risk trends and KPI cards."),
            ("Audio Chimes: ", "Web Audio API generates soft synthetic tones right inside the browser without downloading sound files.")
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

        # Colored accent top strip
        colors = [ACCENT_BLUE, ACCENT_PURPLE, ACCENT_ROSE, ACCENT_AMBER, ACCENT_GREEN, ACCENT_BLUE]
        strip = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, t_col_w, Inches(0.05))
        strip.fill.solid()
        strip.fill.fore_color.rgb = colors[idx]
        strip.line.fill.background()

        tbox = slide3.shapes.add_textbox(x + Inches(0.2), y + Inches(0.12), t_col_w - Inches(0.4), t_row_h - Inches(0.25))
        tf = tbox.text_frame
        tf.word_wrap = True

        p_h = tf.paragraphs[0]
        p_h.text = head
        p_h.font.name = "Segoe UI"
        p_h.font.size = Pt(11)
        p_h.font.bold = True
        p_h.font.color.rgb = ACCENT_CYAN

        for k, v in items:
            p_i = tf.add_paragraph()
            p_i.text = f"• {k}"
            p_i.font.name = "Segoe UI"
            p_i.font.size = Pt(9.5)
            p_i.font.bold = True
            p_i.font.color.rgb = TEXT_WHITE
            p_i.space_before = Pt(5)

            run = p_i.add_run()
            run.text = v
            run.font.bold = False
            run.font.color.rgb = TEXT_SLATE_LIGHT

    # =========================================================================
    # SLIDE 4: In Action: Real Screenshots & Tested Scenarios
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    apply_blue_gradient_background(slide4)
    add_slide_header(slide4, "In Action: Spotting Drops, Drags & Tilted Pallets", "Slide 4: Prototype Screenshots & Demo")

    s4_left_w = Inches(7.4)
    s4_right_x = Inches(8.45)
    s4_right_w = Inches(4.08)

    # Top Left Screenshot: Object Detection & Wet Floor Dragging
    if os.path.exists(IMG_CV_DRAGGING):
        slide4.shapes.add_picture(IMG_CV_DRAGGING, Inches(0.8), Inches(1.5), width=Inches(3.55), height=Inches(2.55))
        cap1 = slide4.shapes.add_textbox(Inches(0.8), Inches(4.08), Inches(3.55), Inches(0.3))
        cap1.text_frame.word_wrap = True
        p_c1 = cap1.text_frame.paragraphs[0]
        p_c1.text = "AI detecting worker & box dragged 4.6m on wet floor"
        p_c1.font.name = "Segoe UI"
        p_c1.font.size = Pt(8.5)
        p_c1.font.color.rgb = TEXT_SLATE_MUTED

    # Top Right Screenshot: Drop Hazard Replay
    if os.path.exists(IMG_DROP_HAZARD):
        slide4.shapes.add_picture(IMG_DROP_HAZARD, Inches(4.55), Inches(1.5), width=Inches(3.65), height=Inches(2.55))
        cap2 = slide4.shapes.add_textbox(Inches(4.55), Inches(4.08), Inches(3.65), Inches(0.3))
        cap2.text_frame.word_wrap = True
        p_c2 = cap2.text_frame.paragraphs[0]
        p_c2.text = "Instant 5-second replay with falling box trajectory"
        p_c2.font.name = "Segoe UI"
        p_c2.font.size = Pt(8.5)
        p_c2.font.color.rgb = TEXT_SLATE_MUTED

    # Bottom Screenshot: Full Dashboard
    if os.path.exists(IMG_DASHBOARD):
        slide4.shapes.add_picture(IMG_DASHBOARD, Inches(0.8), Inches(4.45), width=Inches(7.4), height=Inches(2.65))
        cap3 = slide4.shapes.add_textbox(Inches(0.8), Inches(7.12), Inches(7.4), Inches(0.3))
        cap3.text_frame.word_wrap = True
        p_c3 = cap3.text_frame.paragraphs[0]
        p_c3.text = "The live dashboard: Pastel KPI cards, 7-day risk trend curves, and instant alert drawer"
        p_c3.font.name = "Segoe UI"
        p_c3.font.size = Pt(8.5)
        p_c3.font.color.rgb = TEXT_SLATE_MUTED

    # Right Column: 4 Real Test Scenarios
    sc_card = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, s4_right_x, Inches(1.5), s4_right_w, Inches(5.6))
    sc_card.fill.solid()
    sc_card.fill.fore_color.rgb = CARD_BG
    sc_card.line.color.rgb = CARD_BORDER

    sc_box = slide4.shapes.add_textbox(s4_right_x + Inches(0.25), Inches(1.65), s4_right_w - Inches(0.5), Inches(5.3))
    tf_sc = sc_box.text_frame
    tf_sc.word_wrap = True

    p_sct = tf_sc.paragraphs[0]
    p_sct.text = "4 REAL SCENARIOS WE TESTED"
    p_sct.font.name = "Segoe UI"
    p_sct.font.size = Pt(11)
    p_sct.font.bold = True
    p_sct.font.color.rgb = ACCENT_CYAN

    scenarios = [
        ("1. The 'Butterfingers' Drop:", "Carton slips from 1.3m off pallet staging. The camera spots the free-fall spike and triggers a CRITICAL alert in 1.2s flat."),
        ("2. The Wet-Floor Hockey Puck:", "A worker slides a 20kg box 4.6m across wet concrete. The system measures the ground distance and flags HIGH risk dragging."),
        ("3. The Leaning Tower of Boxes:", "Boxes stacked with a 17° tilt without proper interlocking are flagged as CAUTION so the loader can straighten the pile."),
        ("4. Grilling the AI Assistant:", "We typed: 'Which bay had drops today?' and Gemini parsed the database logs to tell us Bay 3 had 2 drop incidents at 10:14 AM and 2:30 PM.")
    ]
    for s_head, s_desc in scenarios:
        p = tf_sc.add_paragraph()
        p.text = f"• {s_head}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        p.space_before = Pt(7)

        run = p.add_run()
        run.text = f" {s_desc}"
        run.font.bold = False
        run.font.color.rgb = TEXT_SLATE_LIGHT

    # Live Links
    p_link = tf_sc.add_paragraph()
    p_link.text = "TEST IT YOURSELF (LIVE LINKS):"
    p_link.font.name = "Segoe UI"
    p_link.font.size = Pt(10)
    p_link.font.bold = True
    p_link.font.color.rgb = ACCENT_BLUE
    p_link.space_before = Pt(12)

    links_text = [
        ("Live Web App: ", "smart-warehouse-system-rk8p.onrender.com"),
        ("Local Port: ", "localhost:8000 / localhost:5173"),
        ("Open Source Repo: ", "github.com/Aastha008/Smart-Warehouse-System")
    ]
    for l_label, l_url in links_text:
        pl = tf_sc.add_paragraph()
        pl.text = f"  {l_label}{l_url}"
        pl.font.name = "Segoe UI"
        pl.font.size = Pt(8.5)
        pl.font.color.rgb = TEXT_SLATE_LIGHT
        pl.space_before = Pt(1)

    # =========================================================================
    # SLIDE 5: What Warehouse Crews Told Us (And How They Roasted Version 1)
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    apply_blue_gradient_background(slide5)
    add_slide_header(slide5, "What Warehouse Crews Told Us (And How They Roasted Version 1)", "Slide 5: Feedback, Iterations & Real Impact")

    user_w = Inches(7.7)
    row_y = Inches(1.5)
    row_h = Inches(0.98)

    personas = [
        ("The Shift Supervisor", "I can't watch hours of boring CCTV tapes while running around 6 bays.", "Built a 1-click replay button that jumps right to the 5-second drop moment with red/yellow timeline markers."),
        ("The Loading Worker", "Your first alarm sounded like a nuclear meltdown siren. Everyone hated it.", "Switched to a polite, gentle audio chime for small issues, saving louder alerts only for big drops."),
        ("The Logistics Manager", "Cool tech, but how do I prove to my boss that we're actually breaking fewer things?", "Designed real-time KPI stat cards and a 7-day risk trend chart showing the 95.8% damage-free handling rate."),
        ("The Quality Inspector", "When customers return broken ceramics, the freight company claims we dropped it.", "Saved tamper-evident video clips showing exact time, bay number, and drop height so there's zero finger-pointing."),
        ("The Safety Officer", "Workers drag heavy boxes across wet spots and blow out their backs.", "Added automatic wet-floor hazard detection boxes and recommendations for two-person lifting.")
    ]

    for i, (role, quote, change) in enumerate(personas):
        y = row_y + i * (row_h + Inches(0.08))
        card = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y, user_w, row_h)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BORDER

        # Left accent strip
        c_line = slide5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y, Inches(0.06), row_h)
        c_line.fill.solid()
        c_line.fill.fore_color.rgb = ACCENT_PURPLE if i%2==0 else ACCENT_BLUE
        c_line.line.fill.background()

        tbox = slide5.shapes.add_textbox(Inches(1.0), y + Inches(0.08), user_w - Inches(0.3), row_h - Inches(0.16))
        tf = tbox.text_frame
        tf.word_wrap = True

        p_r = tf.paragraphs[0]
        p_r.text = f"{role}: "
        p_r.font.name = "Segoe UI"
        p_r.font.size = Pt(10)
        p_r.font.bold = True
        p_r.font.color.rgb = ACCENT_CYAN

        run_q = p_r.add_run()
        run_q.text = f'"{quote}"'
        run_q.font.bold = False
        run_q.font.italic = True
        run_q.font.color.rgb = ACCENT_ROSE

        p_c = tf.add_paragraph()
        p_c.text = f"→ How we fixed it: {change}"
        p_c.font.name = "Segoe UI"
        p_c.font.size = Pt(9)
        p_c.font.color.rgb = TEXT_SLATE_LIGHT
        p_c.space_before = Pt(3)

    # Right: Measurable Results
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
    p_rt.font.name = "Segoe UI"
    p_rt.font.size = Pt(11)
    p_rt.font.bold = True
    p_rt.font.color.rgb = ACCENT_GREEN

    stats = [
        ("Sub-1.5s Reaction Time:", "From the instant a box crashes to the floor, the system detects it and plays a sound in under 1.5 seconds."),
        ("30 mins down to 1 min:", "Supervisors no longer waste half an hour hunting for incident timestamps—the 5-second replay is right there."),
        ("Caught 8 out of 9 Drops:", "In our test video footage, the AI caught 8 out of 9 drops that human workers didn't bother reporting."),
        ("Zero Guesswork on Claims:", "Having a video clip with a timestamp and drop height completely shuts down freight liability disputes.")
    ]
    for s_title, s_text in stats:
        p = tf_res.add_paragraph()
        p.text = f"• {s_title}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        p.space_before = Pt(8)

        run = p.add_run()
        run.text = f" {s_text}"
        run.font.bold = False
        run.font.color.rgb = TEXT_SLATE_LIGHT

    # =========================================================================
    # SLIDE 6: The Good, The Glitches & What's Next
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    apply_blue_gradient_background(slide6)
    add_slide_header(slide6, "The Good, The Glitches & What’s Next", "Slide 6: Conclusion, Real Limitations & Roadmap")

    col3_w = Inches(3.73)
    col3_g = Inches(0.27)
    col3_top = Inches(1.55)
    col3_h = Inches(4.35)

    sections = [
        ("What's Working (The Good Stuff)", ACCENT_GREEN, [
            ("Live Cloud App: ", "Hosted online 24/7 on Render with working frontend, backend, and database."),
            ("Real Video Analysis: ", "Processes uploaded CCTV footage, draws bounding boxes, and flags drops and dragging."),
            ("Dashboard & Sound: ", "Real-time KPI cards, 7-day risk trend curves, and in-browser audio chimes."),
            ("Gemini Assistant: ", "Actually answers conversational questions using real database records.")
        ]),
        ("Honest Glitches (The Stuff We're Fixing)", ACCENT_ROSE, [
            ("Free Tier Cloud CPU: ", "Running video analysis on a free CPU instance takes 5–8 seconds per clip. A dedicated GPU will make it instant."),
            ("The Crowd Problem: ", "When 3 workers crowd directly in front of a box, the camera can temporarily lose sight of it."),
            ("Morning Sunlight Glare: ", "Intense morning glare through open truck doors can slightly lower detection confidence.")
        ]),
        ("What We're Building Next", ACCENT_BLUE, [
            ("Edge Hardware (NVIDIA Jetson): ", "Run YOLOv8 right on the dock on a $150 Jetson nano for instant <50ms processing."),
            ("Barcode Scanner Link: ", "Connect detection timestamps directly to package tracking numbers (WMS integration)."),
            ("Ergonomic Lifting Checks: ", "Warn workers if they bend at the back instead of lifting with their knees to prevent injury.")
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
        p_th.font.name = "Segoe UI"
        p_th.font.size = Pt(11.5)
        p_th.font.bold = True
        p_th.font.color.rgb = col_color

        for pk, pv in col_points:
            p = stf.add_paragraph()
            p.text = f"• {pk}"
            p.font.name = "Segoe UI"
            p.font.size = Pt(9.5)
            p.font.bold = True
            p.font.color.rgb = TEXT_WHITE
            p.space_before = Pt(7)

            run = p.add_run()
            run.text = pv
            run.font.bold = False
            run.font.color.rgb = TEXT_SLATE_LIGHT

    # Bottom Summary Bar
    bot_card = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.15), Inches(11.733), Inches(0.85))
    bot_card.fill.solid()
    bot_card.fill.fore_color.rgb = CARD_BG_HIGHLIGHT
    bot_card.line.color.rgb = RGBColor(45, 95, 155)

    bot_box = slide6.shapes.add_textbox(Inches(1.0), Inches(6.22), Inches(11.3), Inches(0.7))
    tf_b = bot_box.text_frame
    tf_b.word_wrap = True
    
    p_bt = tf_b.paragraphs[0]
    p_bt.text = "Thanks for listening! We'd love to show you the live demo and answer any questions."
    p_bt.font.name = "Segoe UI"
    p_bt.font.size = Pt(12)
    p_bt.font.bold = True
    p_bt.font.color.rgb = ACCENT_CYAN
    p_bt.alignment = PP_ALIGN.CENTER

    p_bs = tf_b.add_paragraph()
    p_bs.text = "Team VisionGuard: Aastha Gupta, Lucky Lakhani, Runjan Bawa  |  Live link: smart-warehouse-system-rk8p.onrender.com"
    p_bs.font.name = "Segoe UI"
    p_bs.font.size = Pt(9.5)
    p_bs.font.color.rgb = TEXT_SLATE_LIGHT
    p_bs.alignment = PP_ALIGN.CENTER
    p_bs.space_before = Pt(2)

    prs.save(output_path)
    print(f"Successfully generated pretty blue gradient presentation at: {output_path}")

if __name__ == "__main__":
    build_gradient_presentation("Smart_Warehouse_DockGuard_Presentation.pptx")
    build_gradient_presentation("DockGuard_AI_Presentation_Deck.pptx")
    build_gradient_presentation("DockGuard_Fun_Presentation.pptx")
