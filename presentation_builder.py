from io import BytesIO

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.colors import HexColor


# =========================================================
# PROFESSIONAL THEMES
# =========================================================

THEMES = {

    "Modern Blue": {
        "background": "F5F8FF",
        "primary": "2563EB",
        "secondary": "DBEAFE",
        "text": "172033",
        "muted": "64748B",
        "accent": "0EA5E9",
    },

    "Elegant Purple": {
        "background": "FAF7FF",
        "primary": "7C3AED",
        "secondary": "EDE9FE",
        "text": "24163B",
        "muted": "6B6280",
        "accent": "C026D3",
    },

    "Professional Green": {
        "background": "F5FBF7",
        "primary": "15803D",
        "secondary": "DCFCE7",
        "text": "12301E",
        "muted": "64746A",
        "accent": "0F766E",
    },

    "Minimal Dark": {
        "background": "111827",
        "primary": "60A5FA",
        "secondary": "1F2937",
        "text": "F9FAFB",
        "muted": "CBD5E1",
        "accent": "22D3EE",
    },
}


# =========================================================
# COLOR HELPER
# =========================================================

def hex_to_rgb(hex_color):

    hex_color = hex_color.replace("#", "")

    return RGBColor(
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16)
    )


# =========================================================
# ADD TEXT TO POWERPOINT
# =========================================================

def add_text(
    slide,
    text,
    x,
    y,
    width,
    height,
    font_size,
    color,
    bold=False,
    alignment=PP_ALIGN.LEFT
):

    textbox = slide.shapes.add_textbox(
        Inches(x),
        Inches(y),
        Inches(width),
        Inches(height)
    )

    text_frame = textbox.text_frame

    text_frame.clear()

    text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

    paragraph = text_frame.paragraphs[0]

    paragraph.alignment = alignment

    run = paragraph.add_run()

    run.text = str(text)

    run.font.name = "Aptos"

    run.font.size = Pt(font_size)

    run.font.bold = bold

    run.font.color.rgb = hex_to_rgb(color)

    return textbox


# =========================================================
# CREATE POWERPOINT
# =========================================================

def build_pptx(
    slides,
    topic,
    theme="Modern Blue"
):

    colors = THEMES.get(
        theme,
        THEMES["Modern Blue"]
    )

    presentation = Presentation()

    # 16:9 widescreen

    presentation.slide_width = Inches(13.333)

    presentation.slide_height = Inches(7.5)

    # Remove default slide

    while len(presentation.slides) > 0:

        slide_id = presentation.slides._sldIdLst[0]

        presentation.slides._sldIdLst.remove(slide_id)

    # -----------------------------------------------------
    # CREATE EACH SLIDE
    # -----------------------------------------------------

    for index, slide_data in enumerate(slides):

        slide = presentation.slides.add_slide(
            presentation.slide_layouts[6]
        )

        # Background

        background = slide.background.fill

        background.solid()

        background.fore_color.rgb = hex_to_rgb(
            colors["background"]
        )

        # -------------------------------------------------
        # LEFT ACCENT BAR
        # -------------------------------------------------

        accent_bar = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0),
            Inches(0),
            Inches(0.18),
            Inches(7.5)
        )

        accent_bar.fill.solid()

        accent_bar.fill.fore_color.rgb = hex_to_rgb(
            colors["primary"]
        )

        accent_bar.line.fill.background()

        # -------------------------------------------------
        # DECORATIVE CIRCLE
        # -------------------------------------------------

        circle = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(11.8),
            Inches(-0.65),
            Inches(2.2),
            Inches(2.2)
        )

        circle.fill.solid()

        circle.fill.fore_color.rgb = hex_to_rgb(
            colors["secondary"]
        )

        circle.line.fill.background()

        # -------------------------------------------------
        # SLIDE TITLE
        # -------------------------------------------------

        add_text(
            slide,
            slide_data.get("title", "Untitled Slide"),
            0.8,
            0.65,
            10.5,
            0.65,
            28,
            colors["text"],
            bold=True
        )

        # -------------------------------------------------
        # SUBTITLE
        # -------------------------------------------------

        subtitle = slide_data.get(
            "subtitle",
            ""
        )

        if subtitle:

            add_text(
                slide,
                subtitle,
                0.82,
                1.32,
                10.3,
                0.45,
                13,
                colors["muted"]
            )

        # -------------------------------------------------
        # BULLET POINTS
        # -------------------------------------------------

        bullets = slide_data.get(
            "bullets",
            []
        )

        y_position = 2.0

        for bullet in bullets[:5]:

            # Bullet circle

            bullet_circle = slide.shapes.add_shape(
                MSO_SHAPE.OVAL,
                Inches(0.85),
                Inches(y_position + 0.12),
                Inches(0.13),
                Inches(0.13)
            )

            bullet_circle.fill.solid()

            bullet_circle.fill.fore_color.rgb = hex_to_rgb(
                colors["accent"]
            )

            bullet_circle.line.fill.background()

            # Bullet text

            add_text(
                slide,
                bullet,
                1.15,
                y_position,
                10.7,
                0.65,
                17,
                colors["text"]
            )

            y_position += 0.85

        # -------------------------------------------------
        # SLIDE NUMBER
        # -------------------------------------------------

        add_text(
            slide,
            f"{index + 1:02d}",
            11.7,
            6.75,
            0.8,
            0.3,
            10,
            colors["muted"],
            bold=True,
            alignment=PP_ALIGN.RIGHT
        )

    # -----------------------------------------------------
    # SAVE PPTX
    # -----------------------------------------------------

    output = BytesIO()

    presentation.save(output)

    output.seek(0)

    return output.getvalue()


# =========================================================
# TEXT WRAPPING FOR PDF
# =========================================================

def wrap_text(
    text,
    max_characters=78
):

    words = str(text).split()

    lines = []

    current_line = ""

    for word in words:

        test_line = (
            current_line + " " + word
        ).strip()

        if len(test_line) <= max_characters:

            current_line = test_line

        else:

            if current_line:

                lines.append(
                    current_line
                )

            current_line = word

    if current_line:

        lines.append(
            current_line
        )

    return lines


# =========================================================
# CREATE PDF
# =========================================================

def build_pdf(
    slides,
    topic,
    theme="Modern Blue"
):

    colors = THEMES.get(
        theme,
        THEMES["Modern Blue"]
    )

    page_width, page_height = landscape(A4)

    output = BytesIO()

    pdf = canvas.Canvas(
        output,
        pagesize=(
            page_width,
            page_height
        )
    )

    # -----------------------------------------------------
    # CREATE EACH PDF PAGE
    # -----------------------------------------------------

    for index, slide_data in enumerate(slides):

        # Background

        pdf.setFillColor(
            HexColor(
                colors["background"]
            )
        )

        pdf.rect(
            0,
            0,
            page_width,
            page_height,
            fill=1,
            stroke=0
        )

        # -------------------------------------------------
        # LEFT ACCENT BAR
        # -------------------------------------------------

        pdf.setFillColor(
            HexColor(
                colors["primary"]
            )
        )

        pdf.rect(
            0,
            0,
            10,
            page_height,
            fill=1,
            stroke=0
        )

        # -------------------------------------------------
        # DECORATIVE CIRCLE
        # -------------------------------------------------

        pdf.setFillColor(
            HexColor(
                colors["secondary"]
            )
        )

        pdf.circle(
            page_width - 35,
            page_height + 5,
            70,
            fill=1,
            stroke=0
        )

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        pdf.setFillColor(
            HexColor(
                colors["text"]
            )
        )

        pdf.setFont(
            "Helvetica-Bold",
            24
        )

        pdf.drawString(
            55,
            page_height - 60,
            str(
                slide_data.get(
                    "title",
                    "Untitled Slide"
                )
            )
        )

        # -------------------------------------------------
        # SUBTITLE
        # -------------------------------------------------

        subtitle = slide_data.get(
            "subtitle",
            ""
        )

        if subtitle:

            pdf.setFillColor(
                HexColor(
                    colors["muted"]
                )
            )

            pdf.setFont(
                "Helvetica",
                11
            )

            pdf.drawString(
                57,
                page_height - 82,
                str(subtitle)
            )

        # -------------------------------------------------
        # BULLETS
        # -------------------------------------------------

        y_position = page_height - 125

        bullets = slide_data.get(
            "bullets",
            []
        )

        for bullet in bullets[:5]:

            # Bullet

            pdf.setFillColor(
                HexColor(
                    colors["accent"]
                )
            )

            pdf.circle(
                66,
                y_position + 4,
                3.5,
                fill=1,
                stroke=0
            )

            # Text

            pdf.setFillColor(
                HexColor(
                    colors["text"]
                )
            )

            pdf.setFont(
                "Helvetica",
                13
            )

            lines = wrap_text(
                bullet
            )

            for line in lines:

                pdf.drawString(
                    82,
                    y_position,
                    line
                )

                y_position -= 18

            y_position -= 12

        # -------------------------------------------------
        # PAGE NUMBER
        # -------------------------------------------------

        pdf.setFillColor(
            HexColor(
                colors["muted"]
            )
        )

        pdf.setFont(
            "Helvetica-Bold",
            9
        )

        pdf.drawRightString(
            page_width - 35,
            25,
            f"{index + 1:02d}"
        )

        pdf.showPage()

    # -----------------------------------------------------
    # SAVE PDF
    # -----------------------------------------------------

    pdf.save()

    output.seek(0)

    return output.getvalue()
