"""
DockGuard AI - Visual Storytelling Presentation Deck (Pixel-Perfect Polish)
Features:
- Native 4-stop deep navy-to-oceanic blue gradient background on cSld.
- Strict typography scale: Titles 30-38pt, Section headings 18-22pt, Body 15-18pt, Labels 14-16pt.
- No text overlaps, zero clipping, ample whitespace and breathing room.
- 60% visual storytelling, 40% text.
"""
import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml import parse_xml

def build_refined_presentation(output_paths=None):
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

    # Disciplined Palette
    COLOR_WHITE = RGBColor(255, 255, 255)         # Crisp White
    COLOR_CYAN = RGBColor(56, 189, 248)          # Electric Sky Cyan (#38BDF8)
    COLOR_CYAN_LIGHT = RGBColor(125, 211, 252)    # Soft Cyan (#7DD3FC)
    COLOR_SLATE_LIGHT = RGBColor(226, 232, 240)   # Light Slate (#E2E8F0)
    COLOR_SLATE_BODY = RGBColor(203, 213, 225)    # Slate Body (#CBD5E1)
    COLOR_SLATE_MUTED = RGBColor(148, 163, 184)   # Slate Muted (#94A3B8)
    
    SURFACE_BG = RGBColor(10, 25, 46)            # Translucent Dark Navy (#0A192E)
    SURFACE_ACTIVE = RGBColor(16, 44, 82)        # Active Navy (#102C52)
    SURFACE_BORDER = RGBColor(28, 62, 102)       # Subtle Border (#1C3E66)
    SURFACE_BORDER_CYAN = RGBColor(56, 189, 248) # Cyan Border

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
        """Clean header with single-line fit guarantee (30pt) and clear category micro-label."""
        # Top micro label
        lbl_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.42), Inches(6.5), Inches(0.3))
        tf_l = lbl_box.text_frame
        tf_l.margin_left = tf_l.margin_top = tf_l.margin_right = tf_l.margin_bottom = 0
        p_l = tf_l.paragraphs[0]
        p_l.text = f"{category_code}  /  {category_label.upper()}"
        p_l.font.name = "Segoe UI"
        p_l.font.size = Pt(13.5)
        p_l.font.bold = True
        p_l.font.color.rgb = COLOR_CYAN

        if top_tag:
            tag_box = slide.shapes.add_textbox(Inches(7.5), Inches(0.42), Inches(5.033), Inches(0.3))
            tf_t = tag_box.text_frame
            tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
            p_t = tf_t.paragraphs[0]
            p_t.text = top_tag.upper()
            p_t.font.name = "Segoe UI"
            p_t.font.size = Pt(12.5)
            p_t.font.bold = True
            p_t.font.color.rgb = COLOR_SLATE_MUTED
            p_t.alignment = PP_ALIGN.RIGHT

        # Main Title (30pt bold white, fits on one line)
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.733), Inches(0.55))
        tf = title_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = slide_title
        p.font.name = "Segoe UI"
        p.font.size = Pt(29)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE

        # Divider line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.733), Inches(0.015))
        line.fill.solid()
        line.fill.fore_color.rgb = SURFACE_BORDER
        line.line.fill.background()

    # =========================================================================
    # SLIDE 1: Make the Problem Visual
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    apply_native_gradient(s1)

    s1_brand = s1.shapes.add_textbox(Inches(0.8), Inches(0.52), Inches(11.733), Inches(0.3))
    tf_s1b = s1_brand.text_frame
    tf_s1b.margin_left = tf_s1b.margin_top = tf_s1b.margin_right = tf_s1b.margin_bottom = 0
    p_b = tf_s1b.paragraphs[0]
    p_b.text = "AUTONOMOUS WAREHOUSE CARGO INTELLIGENCE"
    p_b.font.name = "Segoe UI"
    p_b.font.size = Pt(13.5)
    p_b.font.bold = True
    p_b.font.color.rgb = COLOR_CYAN

    # Hero Title (38pt) + Value Prop (20pt)
    s1_title_box = s1.shapes.add_textbox(Inches(0.8), Inches(0.88), Inches(11.733), Inches(1.15))
    tf_s1t = s1_title_box.text_frame
    tf_s1t.word_wrap = True
    tf_s1t.margin_left = tf_s1t.margin_top = tf_s1t.margin_right = tf_s1t.margin_bottom = 0
    
    p_h = tf_s1t.paragraphs[0]
    p_h.text = "DockGuard AI"
    p_h.font.name = "Segoe UI"
    p_h.font.size = Pt(38)
    p_h.font.bold = True
    p_h.font.color.rgb = COLOR_WHITE

    p_tag = tf_s1t.add_paragraph()
    p_tag.text = "Because gravity shouldn't win on the warehouse loading dock."
    p_tag.font.name = "Segoe UI"
    p_tag.font.size = Pt(20)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_CYAN
    p_tag.space_before = Pt(3)

    # VISUAL PROBLEM FLOW (4 Nodes)
    pflow_y = Inches(2.28)
    pflow_steps = [
        ("WAREHOUSE DOCK", "4:00 PM trailer rush"),
        ("DROP / DRAG / TILT", "Cartons slip & pallets lean"),
        ("UNNOTICED DAMAGE", "Loaded into trucks blindly"),
        ("CUSTOMER RETURN", "$200+ claims & friction")
    ]
    pf_w = Inches(2.65)
    pf_gap = Inches(0.38)

    for i, (p_title, p_sub) in enumerate(pflow_steps):
        px = Inches(0.8) + i * (pf_w + pf_gap)
        
        p_block = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, px, pflow_y, pf_w, Inches(1.12))
        p_block.fill.solid()
        p_block.fill.fore_color.rgb = SURFACE_ACTIVE if i >= 2 else SURFACE_BG
        p_block.line.color.rgb = COLOR_CYAN if i >= 2 else SURFACE_BORDER
        p_block.line.width = Pt(1.5 if i >= 2 else 1)

        p_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, px, pflow_y, pf_w, Inches(0.035))
        p_bar.fill.solid()
        p_bar.fill.fore_color.rgb = COLOR_CYAN if i >= 2 else SURFACE_BORDER
        p_bar.line.fill.background()

        tb = s1.shapes.add_textbox(px + Inches(0.12), pflow_y + Inches(0.14), pf_w - Inches(0.24), Inches(0.85))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p1 = tf.paragraphs[0]
        p1.text = p_title
        p1.font.name = "Segoe UI"
        p1.font.size = Pt(15)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_WHITE

        p2 = tf.add_paragraph()
        p2.text = p_sub
        p2.font.name = "Segoe UI"
        p2.font.size = Pt(13)
        p2.font.color.rgb = COLOR_SLATE_LIGHT
        p2.space_before = Pt(3)

        if i < 3:
            arr = s1.shapes.add_textbox(px + pf_w + Inches(0.06), pflow_y + Inches(0.33), Inches(0.26), Inches(0.4))
            tf_a = arr.text_frame
            tf_a.margin_left = tf_a.margin_top = tf_a.margin_right = tf_a.margin_bottom = 0
            pa = tf_a.paragraphs[0]
            pa.text = "→"
            pa.font.name = "Segoe UI"
            pa.font.size = Pt(22)
            pa.font.bold = True
            pa.font.color.rgb = COLOR_CYAN

    # 3 LARGE STATISTICAL PROOFS (Taller cards: 2.15 in for ample breathing room)
    stats_y = Inches(3.72)
    stats_h = Inches(2.15)
    stats_data = [
        ("$50B+", "Annual Freight Loss", "Destroyed in warehouses each year before reaching highways—mostly unrecorded."),
        ("1 : 10", "Supervisor Blindspot", "1 supervisor managing 10 active bays and 40 fast-moving workers simultaneously."),
        ("< 1.5s", "Intervention Window", "Dockside repack costs $10. Letting cracked cargo reach customers costs $200+.")
    ]
    st_w = Inches(3.72)
    st_gap = Inches(0.28)

    for i, (big_stat, stat_lbl, stat_expl) in enumerate(stats_data):
        sx = Inches(0.8) + i * (st_w + st_gap)

        st_card = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, sx, stats_y, st_w, stats_h)
        st_card.fill.solid()
        st_card.fill.fore_color.rgb = SURFACE_BG
        st_card.line.color.rgb = SURFACE_BORDER
        st_card.line.width = Pt(1)

        st_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, sx, stats_y, st_w, Inches(0.035))
        st_bar.fill.solid()
        st_bar.fill.fore_color.rgb = COLOR_CYAN
        st_bar.line.fill.background()

        st_tb = s1.shapes.add_textbox(sx + Inches(0.2), stats_y + Inches(0.18), st_w - Inches(0.4), stats_h - Inches(0.35))
        tf_st = st_tb.text_frame
        tf_st.word_wrap = True
        tf_st.margin_left = tf_st.margin_top = tf_st.margin_right = tf_st.margin_bottom = 0

        p_num = tf_st.paragraphs[0]
        p_num.text = big_stat
        p_num.font.name = "Segoe UI"
        p_num.font.size = Pt(42)
        p_num.font.bold = True
        p_num.font.color.rgb = COLOR_WHITE

        p_lbl = tf_st.add_paragraph()
        p_lbl.text = stat_lbl.upper()
        p_lbl.font.name = "Segoe UI"
        p_lbl.font.size = Pt(15.5)
        p_lbl.font.bold = True
        p_lbl.font.color.rgb = COLOR_CYAN
        p_lbl.space_before = Pt(2)

        p_exp = tf_st.add_paragraph()
        p_exp.text = stat_expl
        p_exp.font.name = "Segoe UI"
        p_exp.font.size = Pt(13.5)
        p_exp.font.color.rgb = COLOR_SLATE_BODY
        p_exp.space_before = Pt(5)

    # Clean bottom team strip (15.5pt)
    team_box = s1.shapes.add_textbox(Inches(0.8), Inches(6.7), Inches(11.733), Inches(0.4))
    tf_team = team_box.text_frame
    tf_team.margin_left = tf_team.margin_top = tf_team.margin_right = tf_team.margin_bottom = 0
    p_tm = tf_team.paragraphs[0]
    p_tm.text = "Team VisionGuard: "
    p_tm.font.name = "Segoe UI"
    p_tm.font.size = Pt(15.5)
    p_tm.font.bold = True
    p_tm.font.color.rgb = COLOR_WHITE

    r1 = p_tm.add_run()
    r1.text = "Aastha Gupta (Computer Vision)   •   Lucky Lakhani (AI Pipeline)   •   Runjan Bawa (Dashboard & UX)"
    r1.font.bold = False
    r1.font.color.rgb = COLOR_CYAN

    # =========================================================================
    # SLIDE 2: Solution as a Visual Story (Pipeline + 2 Condensed Moments)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    apply_native_gradient(s2)
    add_header(s2, "02", "Problem, Solution & User Journey",
               "From Sensor to Prevention: The 6-Stage Loop")

    # Large Horizontal 6-Stage Pipeline (1.55 in tall, concise text)
    pipe_y = Inches(1.58)
    pipeline = [
        ("01", "CCTV Video", "1080p dock stream"),
        ("02", "YOLOv8", "Track boxes & crew"),
        ("03", "Physics", "vy > 2.5m/s or drag"),
        ("04", "Dock Chime", "Polite audio tone"),
        ("05", "Inspection", "Worker checks tape"),
        ("06", "Safe Transit", "100% verified cargo")
    ]
    p_w = Inches(1.82)
    p_gap = Inches(0.16)

    for i, (num, stage_t, stage_d) in enumerate(pipeline):
        px = Inches(0.8) + i * (p_w + p_gap)
        is_key = i in [1, 2, 3, 5]

        p_card = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, px, pipe_y, p_w, Inches(1.48))
        p_card.fill.solid()
        p_card.fill.fore_color.rgb = SURFACE_ACTIVE if is_key else SURFACE_BG
        p_card.line.color.rgb = COLOR_CYAN if is_key else SURFACE_BORDER
        p_card.line.width = Pt(1.5 if is_key else 1)

        p_line = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, px, pipe_y, p_w, Inches(0.04))
        p_line.fill.solid()
        p_line.fill.fore_color.rgb = COLOR_CYAN if is_key else SURFACE_BORDER
        p_line.line.fill.background()

        tb = s2.shapes.add_textbox(px + Inches(0.1), pipe_y + Inches(0.12), p_w - Inches(0.2), Inches(1.25))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_n = tf.paragraphs[0]
        p_n.text = num
        p_n.font.name = "Segoe UI"
        p_n.font.size = Pt(17)
        p_n.font.bold = True
        p_n.font.color.rgb = COLOR_CYAN

        p_title = tf.add_paragraph()
        p_title.text = stage_t
        p_title.font.name = "Segoe UI"
        p_title.font.size = Pt(16.5)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_WHITE
        p_title.space_before = Pt(2)

        p_desc = tf.add_paragraph()
        p_desc.text = stage_d
        p_desc.font.name = "Segoe UI"
        p_desc.font.size = Pt(13)
        p_desc.font.color.rgb = COLOR_SLATE_LIGHT
        p_desc.space_before = Pt(3)

    # TWO CONDENSED VISUAL MINI-STORIES (RAMESH VS POOJA)
    stories_y = Inches(3.38)
    st_panel_w = Inches(5.72)
    st_panel_h = Inches(3.65)

    # Left: Ramesh the Loader
    r_panel = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), stories_y, st_panel_w, st_panel_h)
    r_panel.fill.solid()
    r_panel.fill.fore_color.rgb = SURFACE_BG
    r_panel.line.color.rgb = SURFACE_BORDER
    r_panel.line.width = Pt(1)

    r_bar = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), stories_y, st_panel_w, Inches(0.04))
    r_bar.fill.solid()
    r_bar.fill.fore_color.rgb = COLOR_CYAN
    r_bar.line.fill.background()

    r_tb = s2.shapes.add_textbox(Inches(1.05), stories_y + Inches(0.18), st_panel_w - Inches(0.5), st_panel_h - Inches(0.3))
    tf_r = r_tb.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = tf_r.margin_top = tf_r.margin_right = tf_r.margin_bottom = 0

    p_rh = tf_r.paragraphs[0]
    p_rh.text = "OPERATOR MOMENT: RAMESH AT BAY 3"
    p_rh.font.name = "Segoe UI"
    p_rh.font.size = Pt(18)
    p_rh.font.bold = True
    p_rh.font.color.rgb = COLOR_CYAN

    p_rsub = tf_r.add_paragraph()
    p_rsub.text = "Supportive dockside coaching — not punitive surveillance."
    p_rsub.font.name = "Segoe UI"
    p_rsub.font.size = Pt(14)
    p_rsub.font.color.rgb = COLOR_SLATE_MUTED
    p_rsub.space_before = Pt(2)

    r_seq = [
        ("The Rush:", "4:15 PM container deadline; Ramesh lifts 25kg crate solo."),
        ("The Slip:", "Grip fails; carton drops 1.2 meters to concrete floor."),
        ("The Chime:", "Gentle microwave ping rings at Bay 3 (no panic siren)."),
        ("The Win:", "Calls teammate for 2-person lift; sets cracked item aside.")
    ]
    for step_h, step_t in r_seq:
        p = tf_r.add_paragraph()
        p.text = f"• {step_h} "
        p.font.name = "Segoe UI"
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.space_before = Pt(5)

        r_run = p.add_run()
        r_run.text = step_t
        r_run.font.bold = False
        r_run.font.color.rgb = COLOR_SLATE_BODY

    # Right: Pooja the Supervisor
    p_panel = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.813), stories_y, st_panel_w, st_panel_h)
    p_panel.fill.solid()
    p_panel.fill.fore_color.rgb = SURFACE_BG
    p_panel.line.color.rgb = SURFACE_BORDER
    p_panel.line.width = Pt(1)

    p_bar = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.813), stories_y, st_panel_w, Inches(0.04))
    p_bar.fill.solid()
    p_bar.fill.fore_color.rgb = COLOR_CYAN_LIGHT
    p_bar.line.fill.background()

    p_tb = s2.shapes.add_textbox(Inches(7.063), stories_y + Inches(0.18), st_panel_w - Inches(0.5), st_panel_h - Inches(0.3))
    tf_p = p_tb.text_frame
    tf_p.word_wrap = True
    tf_p.margin_left = tf_p.margin_top = tf_p.margin_right = tf_p.margin_bottom = 0

    p_ph = tf_p.paragraphs[0]
    p_ph.text = "SUPERVISOR MOMENT: POOJA ON HER IPAD"
    p_ph.font.name = "Segoe UI"
    p_ph.font.size = Pt(18)
    p_ph.font.bold = True
    p_ph.font.color.rgb = COLOR_CYAN_LIGHT

    p_psub = tf_p.add_paragraph()
    p_psub.text = "Replacing 45 minutes of manual video scrubbing with instant proof."
    p_psub.font.name = "Segoe UI"
    p_psub.font.size = Pt(14)
    p_psub.font.color.rgb = COLOR_SLATE_MUTED
    p_psub.space_before = Pt(2)

    p_seq = [
        ("The Old Way:", "Wasted 45 mins nightly hunting timestamps on blurry DVRs."),
        ("Instant Alert:", "iPad buzzes: 'Bay 3: High-Velocity Drop Detected (10:14 AM)'."),
        ("5-Second Replay:", "One tap plays fall trajectory and impact velocity vector."),
        ("Gemini Audit:", "Shift-end query: 'Summarize all Bay 3 drops today' in 1 click.")
    ]
    for step_h, step_t in p_seq:
        p = tf_p.add_paragraph()
        p.text = f"• {step_h} "
        p.font.name = "Segoe UI"
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.space_before = Pt(5)

        p_run = p.add_run()
        p_run.text = step_t
        p_run.font.bold = False
        p_run.font.color.rgb = COLOR_SLATE_BODY

    # =========================================================================
    # SLIDE 3: Architecture Should Be the Hero (Clean Flowchart)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    apply_native_gradient(s3)
    add_header(s3, "03", "Technical Architecture & Tech Stack",
               "Technical Architecture & Edge-to-Cloud Pipeline",
               top_tag="Confidential — Academic Project")

    nw = Inches(5.6)
    nh = Inches(1.18)
    left_x = Inches(0.8)
    right_x = Inches(6.933)

    # Row 1: CCTV Stream (Left) & YOLOv8 (Right)
    r1_y = Inches(1.58)

    cctv = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, left_x, r1_y, nw, nh)
    cctv.fill.solid()
    cctv.fill.fore_color.rgb = SURFACE_BG
    cctv.line.color.rgb = SURFACE_BORDER
    cctv.line.width = Pt(1)

    cctv_tb = s3.shapes.add_textbox(left_x + Inches(0.2), r1_y + Inches(0.12), nw - Inches(0.4), nh - Inches(0.24))
    tf_cctv = cctv_tb.text_frame
    tf_cctv.word_wrap = True
    p1 = tf_cctv.paragraphs[0]
    p1.text = "01 • CCTV VIDEO STREAM & RING BUFFER"
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(16.5)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE
    p2 = tf_cctv.add_paragraph()
    p2.text = "OpenCV + FFmpeg  |  1080p @ 15fps  |  In-Memory 15s FIFO Buffer"
    p2.font.name = "Segoe UI"
    p2.font.size = Pt(13.5)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_CYAN
    p2.space_before = Pt(3)

    yolo = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, right_x, r1_y, nw, nh)
    yolo.fill.solid()
    yolo.fill.fore_color.rgb = SURFACE_ACTIVE
    yolo.line.color.rgb = COLOR_CYAN
    yolo.line.width = Pt(1.5)

    yolo_tb = s3.shapes.add_textbox(right_x + Inches(0.2), r1_y + Inches(0.12), nw - Inches(0.4), nh - Inches(0.24))
    tf_yolo = yolo_tb.text_frame
    tf_yolo.word_wrap = True
    p1 = tf_yolo.paragraphs[0]
    p1.text = "02 • OBJECT DETECTION & TRACKING"
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(16.5)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE
    p2 = tf_yolo.add_paragraph()
    p2.text = "YOLOv8 + ByteTrack  |  Custom Carton, Pallet & Worker IDs  |  Zero Loss"
    p2.font.name = "Segoe UI"
    p2.font.size = Pt(13.5)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_CYAN
    p2.space_before = Pt(3)

    # Down Arrow between Row 1 & Row 2
    arr1 = s3.shapes.add_textbox(Inches(6.3), Inches(2.78), Inches(0.7), Inches(0.38))
    tf_a1 = arr1.text_frame
    tf_a1.margin_left = tf_a1.margin_top = tf_a1.margin_right = tf_a1.margin_bottom = 0
    pa1 = tf_a1.paragraphs[0]
    pa1.text = "↓"
    pa1.font.name = "Segoe UI"
    pa1.font.size = Pt(22)
    pa1.font.bold = True
    pa1.font.color.rgb = COLOR_CYAN
    pa1.alignment = PP_ALIGN.CENTER

    # Row 2: Kinematic Rules (Left) & FastAPI (Right)
    r2_y = Inches(3.18)

    rules = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, left_x, r2_y, nw, nh)
    rules.fill.solid()
    rules.fill.fore_color.rgb = SURFACE_BG
    rules.line.color.rgb = SURFACE_BORDER
    rules.line.width = Pt(1)

    rules_tb = s3.shapes.add_textbox(left_x + Inches(0.2), r2_y + Inches(0.12), nw - Inches(0.4), nh - Inches(0.24))
    tf_r = rules_tb.text_frame
    tf_r.word_wrap = True
    p1 = tf_r.paragraphs[0]
    p1.text = "03 • SPATIAL & KINEMATIC RULES"
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(16.5)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE
    p2 = tf_r.add_paragraph()
    p2.text = "Vector Math  |  Drop vy > 2.5m/s  |  Floor Drag > 2m  |  Tilt > 15°"
    p2.font.name = "Segoe UI"
    p2.font.size = Pt(13.5)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_CYAN
    p2.space_before = Pt(3)

    api = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, right_x, r2_y, nw, nh)
    api.fill.solid()
    api.fill.fore_color.rgb = SURFACE_ACTIVE
    api.line.color.rgb = COLOR_CYAN
    api.line.width = Pt(1.5)

    api_tb = s3.shapes.add_textbox(right_x + Inches(0.2), r2_y + Inches(0.12), nw - Inches(0.4), nh - Inches(0.24))
    tf_api = api_tb.text_frame
    tf_api.word_wrap = True
    p1 = tf_api.paragraphs[0]
    p1.text = "04 • EVENT DISPATCH & DATABASE"
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(16.5)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE
    p2 = tf_api.add_paragraph()
    p2.text = "FastAPI Core  |  < 50ms WebSockets  |  SQLite Telemetry Logs"
    p2.font.name = "Segoe UI"
    p2.font.size = Pt(13.5)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_CYAN
    p2.space_before = Pt(3)

    # Down Arrow between Row 2 & Row 3
    arr2 = s3.shapes.add_textbox(Inches(6.3), Inches(4.38), Inches(0.7), Inches(0.38))
    tf_a2 = arr2.text_frame
    tf_a2.margin_left = tf_a2.margin_top = tf_a2.margin_right = tf_a2.margin_bottom = 0
    pa2 = tf_a2.paragraphs[0]
    pa2.text = "↓"
    pa2.font.name = "Segoe UI"
    pa2.font.size = Pt(22)
    pa2.font.bold = True
    pa2.font.color.rgb = COLOR_CYAN
    pa2.alignment = PP_ALIGN.CENTER

    # Row 3: React Dashboard (Left) & Gemini RAG (Right)
    r3_y = Inches(4.78)
    nh3 = Inches(1.35)

    dash = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, left_x, r3_y, nw, nh3)
    dash.fill.solid()
    dash.fill.fore_color.rgb = SURFACE_BG
    dash.line.color.rgb = SURFACE_BORDER
    dash.line.width = Pt(1)

    dash_tb = s3.shapes.add_textbox(left_x + Inches(0.2), r3_y + Inches(0.12), nw - Inches(0.4), nh3 - Inches(0.24))
    tf_d = dash_tb.text_frame
    tf_d.word_wrap = True
    p1 = tf_d.paragraphs[0]
    p1.text = "05 • SUPERVISOR UI & AUDIO ENGINE"
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(16.5)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE
    p2 = tf_d.add_paragraph()
    p2.text = "React 18 + Tailwind CSS + Web Audio API"
    p2.font.name = "Segoe UI"
    p2.font.size = Pt(13.5)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_CYAN
    p2.space_before = Pt(2)
    p3 = tf_d.add_paragraph()
    p3.text = "Live KPI cards, 7-day risk trend curves & instant synthetic dock chimes."
    p3.font.name = "Segoe UI"
    p3.font.size = Pt(12.5)
    p3.font.color.rgb = COLOR_SLATE_BODY
    p3.space_before = Pt(3)

    gem = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, right_x, r3_y, nw, nh3)
    gem.fill.solid()
    gem.fill.fore_color.rgb = SURFACE_ACTIVE
    gem.line.color.rgb = COLOR_CYAN
    gem.line.width = Pt(1.5)

    gem_tb = s3.shapes.add_textbox(right_x + Inches(0.2), r3_y + Inches(0.12), nw - Inches(0.4), nh3 - Inches(0.24))
    tf_g = gem_tb.text_frame
    tf_g.word_wrap = True
    p1 = tf_g.paragraphs[0]
    p1.text = "06 • CONVERSATIONAL RAG ASSISTANT"
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(16.5)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE
    p2 = tf_g.add_paragraph()
    p2.text = "Google Gemini 2.5 Flash + Structured RAG"
    p2.font.name = "Segoe UI"
    p2.font.size = Pt(13.5)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_CYAN
    p2.space_before = Pt(2)
    p3 = tf_g.add_paragraph()
    p3.text = "Natural language shift queries without SQL; instant risk summaries & audit logs."
    p3.font.name = "Segoe UI"
    p3.font.size = Pt(12.5)
    p3.font.color.rgb = COLOR_SLATE_BODY
    p3.space_before = Pt(3)

    # Bottom Tag
    arch_tag = s3.shapes.add_textbox(Inches(0.8), Inches(6.75), Inches(11.733), Inches(0.35))
    tf_at = arch_tag.text_frame
    tf_at.margin_left = tf_at.margin_top = tf_at.margin_right = tf_at.margin_bottom = 0
    p_at = tf_at.paragraphs[0]
    p_at.text = "Key Design Decision: "
    p_at.font.name = "Segoe UI"
    p_at.font.size = Pt(14.5)
    p_at.font.bold = True
    p_at.font.color.rgb = COLOR_CYAN
    r_at = p_at.add_run()
    r_at.text = "Local spatial vector physics filter false alarms in <50ms → Only verified risk events reach Gemini & WebSockets."
    r_at.font.bold = False
    r_at.font.color.rgb = COLOR_SLATE_LIGHT

    # =========================================================================
    # SLIDE 4: Show, Don't Tell (Screenshots Are the Hero!)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    apply_native_gradient(s4)
    add_header(s4, "04", "Prototype Screenshots & Demo",
               "Field Prototype: Live Detection, Replay & Dashboard")

    # LEFT 58%: Large Computer Vision & Drop Replay Visuals
    right_meta_x = Inches(8.35)
    right_meta_w = Inches(4.18)

    if os.path.exists(IMG_CV_DRAGGING):
        s4.shapes.add_picture(IMG_CV_DRAGGING, Inches(0.8), Inches(1.55), width=Inches(3.5), height=Inches(2.55))
        b1 = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.55), Inches(2.2), Inches(0.32))
        b1.fill.solid()
        b1.fill.fore_color.rgb = SURFACE_ACTIVE
        b1.line.color.rgb = COLOR_CYAN
        b1_tb = s4.shapes.add_textbox(Inches(0.85), Inches(1.57), Inches(2.1), Inches(0.28))
        b1_tb.text_frame.paragraphs[0].text = "4.6m FLOOR DRAG DETECTED"
        b1_tb.text_frame.paragraphs[0].font.size = Pt(11)
        b1_tb.text_frame.paragraphs[0].font.bold = True
        b1_tb.text_frame.paragraphs[0].font.color.rgb = COLOR_WHITE

    if os.path.exists(IMG_DROP_HAZARD):
        s4.shapes.add_picture(IMG_DROP_HAZARD, Inches(4.45), Inches(1.55), width=Inches(3.55), height=Inches(2.55))
        b2 = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.45), Inches(1.55), Inches(2.2), Inches(0.32))
        b2.fill.solid()
        b2.fill.fore_color.rgb = SURFACE_ACTIVE
        b2.line.color.rgb = COLOR_CYAN
        b2_tb = s4.shapes.add_textbox(Inches(4.5), Inches(1.57), Inches(2.1), Inches(0.28))
        b2_tb.text_frame.paragraphs[0].text = "CRITICAL DROP REPLAY (5s)"
        b2_tb.text_frame.paragraphs[0].font.size = Pt(11)
        b2_tb.text_frame.paragraphs[0].font.bold = True
        b2_tb.text_frame.paragraphs[0].font.color.rgb = COLOR_WHITE

    if os.path.exists(IMG_DASHBOARD):
        s4.shapes.add_picture(IMG_DASHBOARD, Inches(0.8), Inches(4.25), width=Inches(7.2), height=Inches(2.55))
        b3 = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(4.25), Inches(2.6), Inches(0.32))
        b3.fill.solid()
        b3.fill.fore_color.rgb = SURFACE_ACTIVE
        b3.line.color.rgb = COLOR_CYAN
        b3_tb = s4.shapes.add_textbox(Inches(0.85), Inches(4.27), Inches(2.5), Inches(0.28))
        b3_tb.text_frame.paragraphs[0].text = "LIVE OPERATIONAL DASHBOARD"
        b3_tb.text_frame.paragraphs[0].font.size = Pt(11)
        b3_tb.text_frame.paragraphs[0].font.bold = True
        b3_tb.text_frame.paragraphs[0].font.color.rgb = COLOR_WHITE

    # RIGHT 42%: Concise Scenario Callouts + Live Verification
    sc_panel = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, right_meta_x, Inches(1.55), right_meta_w, Inches(5.25))
    sc_panel.fill.solid()
    sc_panel.fill.fore_color.rgb = SURFACE_BG
    sc_panel.line.color.rgb = SURFACE_BORDER
    sc_panel.line.width = Pt(1)

    sc_top_bar = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, right_meta_x, Inches(1.55), right_meta_w, Inches(0.04))
    sc_top_bar.fill.solid()
    sc_top_bar.fill.fore_color.rgb = COLOR_CYAN
    sc_top_bar.line.fill.background()

    sc_tb = s4.shapes.add_textbox(right_meta_x + Inches(0.25), Inches(1.72), right_meta_w - Inches(0.5), Inches(4.9))
    tf_sc = sc_tb.text_frame
    tf_sc.word_wrap = True
    tf_sc.margin_left = tf_sc.margin_top = tf_sc.margin_right = tf_sc.margin_bottom = 0

    p_sct = tf_sc.paragraphs[0]
    p_sct.text = "TESTED IN REAL FOOTAGE"
    p_sct.font.name = "Segoe UI"
    p_sct.font.size = Pt(18)
    p_sct.font.bold = True
    p_sct.font.color.rgb = COLOR_CYAN

    scenarios_condensed = [
        ("Drop from Staging (>1.2m)", "Freefall spike vy > 2.8 m/s triggers dock chime in 1.2s flat."),
        ("Wet-Floor Dragging (4.6m)", "Continuous floor displacement flagged as severe friction hazard."),
        ("Unstable Pallet Tilt (>17°)", "Stack angle warning alerts loaders before trailer loading."),
        ("Gemini AI Natural Query", "'Which bay had drops today?' resolved instantly from SQLite logs.")
    ]

    for s_title, s_detail in scenarios_condensed:
        p = tf_sc.add_paragraph()
        p.text = f"• {s_title}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(14.5)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.space_before = Pt(7)

        p_det = tf_sc.add_paragraph()
        p_det.text = f"  {s_detail}"
        p_det.font.name = "Segoe UI"
        p_det.font.size = Pt(12.5)
        p_det.font.color.rgb = COLOR_SLATE_BODY
        p_det.space_before = Pt(1)

    p_vl = tf_sc.add_paragraph()
    p_vl.text = "LIVE DEPLOYMENT:"
    p_vl.font.name = "Segoe UI"
    p_vl.font.size = Pt(14)
    p_vl.font.bold = True
    p_vl.font.color.rgb = COLOR_CYAN
    p_vl.space_before = Pt(10)

    p_url = tf_sc.add_paragraph()
    p_url.text = "smart-warehouse-system-rk8p.onrender.com"
    p_url.font.name = "Segoe UI"
    p_url.font.size = Pt(12.5)
    p_url.font.color.rgb = COLOR_WHITE
    p_url.space_before = Pt(1)

    p_gh = tf_sc.add_paragraph()
    p_gh.text = "github.com/Aastha008/Smart-Warehouse-System"
    p_gh.font.name = "Segoe UI"
    p_gh.font.size = Pt(12)
    p_gh.font.color.rgb = COLOR_SLATE_MUTED
    p_gh.space_before = Pt(1)

    # =========================================================================
    # SLIDE 5: Turn Results into Big Visual Proof
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    apply_native_gradient(s5)
    add_header(s5, "05", "Impact, Damage Prevention & Validation",
               "What Changed When We Put It Into Practice")

    # MIDDLE: 4 LARGE METRIC VISUALS (Cards height: 2.65 in)
    m_top = Inches(1.58)
    m_w = Inches(2.76)
    m_gap = Inches(0.23)
    m_h = Inches(2.65)

    metrics_showcase = [
        ("< 1.5s", Pt(38), "DETECTION → CHIME", "Sub-second vision catches drops before cartons are buried in trucks."),
        ("30m → 1m", Pt(32), "VERIFICATION SPEED", "5-second micro-replays replace 30 minutes of manual CCTV scrubbing."),
        ("89%", Pt(38), "UNREPORTED DROPS", "Intercepted 8 of 9 physical drop incidents never logged by workers."),
        ("100%", Pt(38), "AUDIT PROOF", "Timestamped video clips eliminate carrier-versus-warehouse liability disputes.")
    ]

    for i, (big_num, num_pt, num_label, num_desc) in enumerate(metrics_showcase):
        mx = Inches(0.8) + i * (m_w + m_gap)

        m_card = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, mx, m_top, m_w, m_h)
        m_card.fill.solid()
        m_card.fill.fore_color.rgb = SURFACE_BG
        m_card.line.color.rgb = SURFACE_BORDER
        m_card.line.width = Pt(1)

        m_bar = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, mx, m_top, m_w, Inches(0.04))
        m_bar.fill.solid()
        m_bar.fill.fore_color.rgb = COLOR_CYAN
        m_bar.line.fill.background()

        mtb = s5.shapes.add_textbox(mx + Inches(0.15), m_top + Inches(0.18), m_w - Inches(0.3), m_h - Inches(0.3))
        tf_m = mtb.text_frame
        tf_m.word_wrap = True
        tf_m.margin_left = tf_m.margin_top = tf_m.margin_right = tf_m.margin_bottom = 0

        p_bn = tf_m.paragraphs[0]
        p_bn.text = big_num
        p_bn.font.name = "Segoe UI"
        p_bn.font.size = num_pt
        p_bn.font.bold = True
        p_bn.font.color.rgb = COLOR_WHITE

        p_bl = tf_m.add_paragraph()
        p_bl.text = num_label
        p_bl.font.name = "Segoe UI"
        p_bl.font.size = Pt(14)
        p_bl.font.bold = True
        p_bl.font.color.rgb = COLOR_CYAN
        p_bl.space_before = Pt(3)

        p_bd = tf_m.add_paragraph()
        p_bd.text = num_desc
        p_bd.font.name = "Segoe UI"
        p_bd.font.size = Pt(13.5)
        p_bd.font.color.rgb = COLOR_SLATE_BODY
        p_bd.space_before = Pt(6)

    # BOTTOM: 3 SHORT USER FEEDBACK QUOTES
    q_top = Inches(4.45)
    q_w = Inches(3.75)
    q_gap = Inches(0.24)
    q_h = Inches(2.25)

    feedback_quotes = [
        ("Shift Supervisor", "I can't watch hours of CCTV while running across 6 active bays.",
         "→ Solution: 1-click 5-second replay with pre-buffered impact markers."),
        ("Dock Loader", "Your first alarm sounded like a fire siren. It made everyone defensive.",
         "→ Solution: Gentle microwave dock chime and coaching for 2-person lifts."),
        ("Logistics Director", "Carriers blame us for damaged goods discovered at destination.",
         "→ Solution: Tamper-evident video logs with velocity data end blame games.")
    ]

    for i, (q_role, q_quote, q_fix) in enumerate(feedback_quotes):
        qx = Inches(0.8) + i * (q_w + q_gap)

        q_card = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, qx, q_top, q_w, q_h)
        q_card.fill.solid()
        q_card.fill.fore_color.rgb = SURFACE_BG
        q_card.line.color.rgb = SURFACE_BORDER
        q_card.line.width = Pt(1)

        q_bar = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, qx, q_top, Inches(0.04), q_h)
        q_bar.fill.solid()
        q_bar.fill.fore_color.rgb = COLOR_CYAN_LIGHT
        q_bar.line.fill.background()

        q_tb = s5.shapes.add_textbox(qx + Inches(0.18), q_top + Inches(0.15), q_w - Inches(0.3), q_h - Inches(0.3))
        tf_q = q_tb.text_frame
        tf_q.word_wrap = True
        tf_q.margin_left = tf_q.margin_top = tf_q.margin_right = tf_q.margin_bottom = 0

        p_r = tf_q.paragraphs[0]
        p_r.text = q_role.upper()
        p_r.font.name = "Segoe UI"
        p_r.font.size = Pt(15)
        p_r.font.bold = True
        p_r.font.color.rgb = COLOR_CYAN

        p_qt = tf_q.add_paragraph()
        p_qt.text = f'"{q_quote}"'
        p_qt.font.name = "Segoe UI"
        p_qt.font.size = Pt(14)
        p_qt.font.italic = True
        p_qt.font.color.rgb = COLOR_WHITE
        p_qt.space_before = Pt(4)

        p_fx = tf_q.add_paragraph()
        p_fx.text = q_fix
        p_fx.font.name = "Segoe UI"
        p_fx.font.size = Pt(13)
        p_fx.font.color.rgb = COLOR_SLATE_LIGHT
        p_fx.space_before = Pt(5)

    # =========================================================================
    # SLIDE 6: Make the Ending Memorable (NOW -> BOTTLENECK -> NEXT)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    apply_native_gradient(s6)
    add_header(s6, "06", "Conclusion & Enterprise Roadmap",
               "Roadmap: Proven Today, Constraints & What's Next")

    prog_y = Inches(1.58)
    prog_w = Inches(3.68)
    prog_gap = Inches(0.34)
    prog_h = Inches(4.38)

    prog_stages = [
        ("01", "NOW", "PROVEN TODAY", SURFACE_BG, SURFACE_BORDER, COLOR_WHITE, [
            ("Live Full-Stack Cloud App", "Hosted 24/7 on Render (React + FastAPI + SQLite)."),
            ("YOLOv8 Video Inference", "Accurately detects cartons, pallets & drops in CCTV."),
            ("Real-Time Sound Chimes", "Zero-latency synthetic browser dock alerts."),
            ("Gemini 2.5 Flash RAG", "Answers natural language queries using real logs.")
        ]),
        ("02", "BOTTLENECK", "HONEST CONSTRAINTS", SURFACE_BG, SURFACE_BORDER, COLOR_SLATE_MUTED, [
            ("Cloud CPU Inference Latency", "Takes 5–8s per clip on free-tier; needs edge GPU."),
            ("Heavy Worker Crowding", "Occlusion when 3+ workers cluster tightly over boxes."),
            ("Morning Sunlight Glare", "Direct sun through bay doors lowers box confidence.")
        ]),
        ("03", "NEXT", "ENTERPRISE ROADMAP", SURFACE_ACTIVE, SURFACE_BORDER_CYAN, COLOR_CYAN, [
            ("NVIDIA Jetson Edge AI", "Run localized TensorRT models on-dock for <50ms speeds."),
            ("Barcode & WMS Sync", "Connect incident timestamps directly to package tracking."),
            ("Ergonomic Safety Coach", "Warn workers lifting with spine instead of knees.")
        ])
    ]

    for idx, (num, tag, title, bg_c, bord_c, h_color, items) in enumerate(prog_stages):
        x = Inches(0.8) + idx * (prog_w + prog_gap)
        is_dest = (idx == 2)

        p_box = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, prog_y, prog_w, prog_h)
        p_box.fill.solid()
        p_box.fill.fore_color.rgb = bg_c
        p_box.line.color.rgb = bord_c
        p_box.line.width = Pt(1.5 if is_dest else 1)

        p_bar = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, prog_y, prog_w, Inches(0.04))
        p_bar.fill.solid()
        p_bar.fill.fore_color.rgb = COLOR_CYAN if is_dest else SURFACE_BORDER
        p_bar.line.fill.background()

        tb = s6.shapes.add_textbox(x + Inches(0.2), prog_y + Inches(0.18), prog_w - Inches(0.4), prog_h - Inches(0.35))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_tag = tf.paragraphs[0]
        p_tag.text = f"{num}  —  {tag}"
        p_tag.font.name = "Segoe UI"
        p_tag.font.size = Pt(15.5)
        p_tag.font.bold = True
        p_tag.font.color.rgb = COLOR_CYAN if is_dest else COLOR_SLATE_MUTED

        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.name = "Segoe UI"
        p_t.font.size = Pt(18.5)
        p_t.font.bold = True
        p_t.font.color.rgb = h_color
        p_t.space_before = Pt(3)

        for head, body in items:
            p = tf.add_paragraph()
            p.text = f"• {head}"
            p.font.name = "Segoe UI"
            p.font.size = Pt(14.5)
            p.font.bold = True
            p.font.color.rgb = COLOR_WHITE
            p.space_before = Pt(7)

            p_sub = tf.add_paragraph()
            p_sub.text = f"  {body}"
            p_sub.font.name = "Segoe UI"
            p_sub.font.size = Pt(12.5)
            p_sub.font.color.rgb = COLOR_SLATE_BODY
            p_sub.space_before = Pt(1)

        if idx < 2:
            arr_x = x + prog_w + Inches(0.08)
            arr = s6.shapes.add_textbox(arr_x, prog_y + Inches(1.8), Inches(0.2), Inches(0.5))
            tf_a = arr.text_frame
            tf_a.margin_left = tf_a.margin_top = tf_a.margin_right = tf_a.margin_bottom = 0
            pa = tf_a.paragraphs[0]
            pa.text = "→"
            pa.font.name = "Segoe UI"
            pa.font.size = Pt(24)
            pa.font.bold = True
            pa.font.color.rgb = COLOR_CYAN
            pa.alignment = PP_ALIGN.CENTER

    # The Punchline: "From detecting risk -> to preventing it."
    close_bar = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.15), Inches(11.733), Inches(0.015))
    close_bar.fill.solid()
    close_bar.fill.fore_color.rgb = SURFACE_BORDER
    close_bar.line.fill.background()

    punch_tb = s6.shapes.add_textbox(Inches(0.8), Inches(6.25), Inches(11.733), Inches(0.42))
    tf_punch = punch_tb.text_frame
    tf_punch.margin_left = tf_punch.margin_top = tf_punch.margin_right = tf_punch.margin_bottom = 0
    p_pn = tf_punch.paragraphs[0]
    p_pn.text = "DockGuard AI: "
    p_pn.font.name = "Segoe UI"
    p_pn.font.size = Pt(20)
    p_pn.font.bold = True
    p_pn.font.color.rgb = COLOR_WHITE
    r_pn = p_pn.add_run()
    r_pn.text = "From detecting risk  →  to preventing it."
    r_pn.font.bold = True
    r_pn.font.color.rgb = COLOR_CYAN

    cred_tb = s6.shapes.add_textbox(Inches(0.8), Inches(6.75), Inches(11.733), Inches(0.35))
    tf_cr = cred_tb.text_frame
    tf_cr.margin_left = tf_cr.margin_top = tf_cr.margin_right = tf_cr.margin_bottom = 0
    p_cr = tf_cr.paragraphs[0]
    p_cr.text = "Team VisionGuard: Aastha Gupta, Lucky Lakhani, Runjan Bawa   |   smart-warehouse-system-rk8p.onrender.com   |   github.com/Aastha008/Smart-Warehouse-System"
    p_cr.font.name = "Segoe UI"
    p_cr.font.size = Pt(13)
    p_cr.font.color.rgb = COLOR_SLATE_MUTED

    for path in output_paths:
        prs.save(path)
        print(f"Saved polished presentation at: {path}")

if __name__ == "__main__":
    build_refined_presentation()
