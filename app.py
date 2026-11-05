import streamlit as st
import json
import io
import re
from openai import OpenAI
from pptx import Presentation
from pptx.util import Inches, Pt
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="AI Presentation Maker",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(circle at top left, #24104f 0%, transparent 35%),
        radial-gradient(circle at bottom right, #101d52 0%, transparent 40%),
        #080d24;
    color: white;
}

.main-title {
    font-size: 52px;
    font-weight: 800;
    text-align: center;
    margin-top: 20px;
    background: linear-gradient(90deg, #7c3aed, #3b82f6, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    text-align: center;
    color: #b8bfd8;
    font-size: 18px;
    margin-bottom: 35px;
}

.card {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px;
    padding: 25px;
    margin-bottom: 20px;
    backdrop-filter: blur(15px);
}

.slide-card {
    background: linear-gradient(
        135deg,
        rgba(124,58,237,0.18),
        rgba(37,99,235,0.12)
    );
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 20px;
}

.slide-number {
    color: #a78bfa;
    font-weight: bold;
    font-size: 14px;
}

.slide-title {
    font-size: 26px;
    font-weight: 700;
    color: white;
}

.small-text {
    color: #aeb7d5;
}

div.stButton > button {
    width: 100%;
    border: none;
    border-radius: 12px;
    padding: 12px 20px;
    font-weight: 700;
    color: white;
    background: linear-gradient(90deg, #7c3aed, #2563eb);
    transition: 0.3s;
}

div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0px 8px 25px rgba(124,58,237,0.35);
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "slides" not in st.session_state:
    st.session_state.slides = []

if "generated" not in st.session_state:
    st.session_state.generated = False


# --------------------------------------------------
# OPENAI CLIENT
# --------------------------------------------------

def get_client():

    api_key = st.secrets.get("OPENAI_API_KEY", "")

    if not api_key:
        return None

    return OpenAI(api_key=api_key)


# --------------------------------------------------
# AI GENERATION
# --------------------------------------------------

def generate_presentation(topic, number_of_slides, language, template):

    client = get_client()

    if client is None:
        st.error(
            "OPENAI_API_KEY nahi mili. Streamlit Secrets mein API key add karein."
        )
        return []

    prompt = f"""
Create a professional presentation.

Topic: {topic}

Number of slides: {number_of_slides}

Language: {language}

Template style: {template}

Return ONLY valid JSON.

Format:

{{
  "slides": [
    {{
      "title": "Slide title",
      "content": [
        "Point 1",
        "Point 2",
        "Point 3",
        "Point 4"
      ]
    }}
  ]
}}

Requirements:
- Make the presentation professional.
- Use clear and useful information.
- Avoid very long paragraphs.
- Each slide should contain 3-5 important points.
- Create a logical flow.
- Include an introduction and conclusion.
- Write everything in the requested language.
"""

    try:

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional presentation designer."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7
        )

        result = response.choices[0].message.content

        # Remove possible markdown JSON fences
        result = re.sub(r"```json|```", "", result).strip()

        data = json.loads(result)

        return data.get("slides", [])

    except Exception as e:

        st.error(f"AI generation error: {e}")
        return []


# --------------------------------------------------
# PPTX EXPORT
# --------------------------------------------------

def create_pptx(slides, topic):

    prs = Presentation()

    # 16:9
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    for index, slide_data in enumerate(slides):

        slide = prs.slides.add_slide(
            prs.slide_layouts[6]
        )

        # Background
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = __import__(
            "pptx"
        ).dml.color.RGBColor(10, 15, 40)

        # Slide number
        box = slide.shapes.add_textbox(
            Inches(0.6),
            Inches(0.4),
            Inches(1.5),
            Inches(0.4)
        )

        p = box.text_frame.paragraphs[0]
        p.text = f"SLIDE {index + 1}"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = __import__(
            "pptx"
        ).dml.color.RGBColor(167, 139, 250)

        # Title
        title_box = slide.shapes.add_textbox(
            Inches(0.6),
            Inches(1.0),
            Inches(12),
            Inches(1.2)
        )

        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = slide_data["title"]
        p.font.size = Pt(30)
        p.font.bold = True
        p.font.color.rgb = __import__(
            "pptx"
        ).dml.color.RGBColor(255, 255, 255)

        # Content
        content_box = slide.shapes.add_textbox(
            Inches(0.8),
            Inches(2.3),
            Inches(11.8),
            Inches(4.5)
        )

        tf = content_box.text_frame
        tf.word_wrap = True

        for i, point in enumerate(slide_data["content"]):

            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()

            p.text = "• " + point
            p.font.size = Pt(20)
            p.font.color.rgb = __import__(
                "pptx"
            ).dml.color.RGBColor(220, 225, 245)

            p.space_after = Pt(15)

    output = io.BytesIO()
    prs.save(output)
    output.seek(0)

    return output


# --------------------------------------------------
# PDF EXPORT
# --------------------------------------------------

def create_pdf(slides, topic):

    output = io.BytesIO()

    c = canvas.Canvas(
        output,
        pagesize=landscape(A4)
    )

    width, height = landscape(A4)

    for index, slide_data in enumerate(slides):

        # Dark background
        c.setFillColorRGB(0.04, 0.06, 0.16)
        c.rect(0, 0, width, height, fill=1)

        # Slide number
        c.setFillColorRGB(0.65, 0.55, 0.98)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(
            45,
            height - 45,
            f"SLIDE {index + 1}"
        )

        # Title
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 25)

        c.drawString(
            45,
            height - 90,
            slide_data["title"]
        )

        # Content
        y = height - 145

        c.setFont("Helvetica", 16)

        for point in slide_data["content"]:

            # Simple line wrapping
            words = point.split()
            line = ""

            lines = []

            for word in words:

                test_line = line + word + " "

                if c.stringWidth(test_line, "Helvetica", 16) < width - 100:
                    line = test_line

                else:
                    lines.append(line)
                    line = word + " "

            if line:
                lines.append(line)

            for line in lines:

                c.setFillColorRGB(
                    0.85,
                    0.87,
                    0.95
                )

                c.drawString(
                    60,
                    y,
                    "• " + line
                )

                y -= 25

            y -= 10

        c.showPage()

    c.save()

    output.seek(0)

    return output


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown("## 🎨 AI Presentation Maker")

    st.markdown("---")

    st.markdown("### ⚙️ Presentation Settings")

    number_of_slides = st.slider(
        "Number of slides",
        min_value=3,
        max_value=15,
        value=6
    )

    language = st.selectbox(
        "Presentation Language",
        [
            "English",
            "Urdu",
            "Roman Urdu",
            "Arabic",
            "French",
            "Spanish"
        ]
    )

    template = st.selectbox(
        "Choose Template",
        [
            "Modern Dark",
            "Corporate Blue",
            "Creative Purple",
            "Minimal Professional",
            "Technology",
            "Education"
        ]
    )

    st.markdown("---")

    st.info(
        "💡 Tip: Topic ko specific rakhein taake AI zyada useful presentation generate kare."
    )


# --------------------------------------------------
# HOMEPAGE
# --------------------------------------------------

st.markdown(
    '<div class="main-title">AI Presentation Maker</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Create professional presentations with AI in seconds.</div>',
    unsafe_allow_html=True
)


# --------------------------------------------------
# INPUT SECTION
# --------------------------------------------------

st.markdown(
    '<div class="card">',
    unsafe_allow_html=True
)

st.markdown("### ✨ Create Your Presentation")

topic = st.text_input(
    "Presentation Topic",
    placeholder="Example: Artificial Intelligence in Education"
)

generate_button = st.button(
    "🚀 Generate Presentation"
)

st.markdown("</div>", unsafe_allow_html=True)


# --------------------------------------------------
# GENERATE
# --------------------------------------------------

if generate_button:

    if not topic.strip():

        st.warning("Please enter a presentation topic.")

    else:

        with st.spinner("AI presentation generate kar raha hai..."):

            slides = generate_presentation(
                topic,
                number_of_slides,
                language,
                template
            )

        if slides:

            st.session_state.slides = slides
            st.session_state.generated = True

            st.success("🎉 Presentation successfully generated!")


# --------------------------------------------------
# DISPLAY SLIDES
# --------------------------------------------------

if st.session_state.generated:

    st.markdown("## 📑 Your Presentation")

    for index, slide in enumerate(
        st.session_state.slides
    ):

        st.markdown(
            f"""
            <div class="slide-card">
                <div class="slide-number">
                    SLIDE {index + 1}
                </div>
                <div class="slide-title">
                    {slide["title"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        new_title = st.text_input(
            f"Slide {index + 1} Title",
            value=slide["title"],
            key=f"title_{index}"
        )

        new_content = st.text_area(
            f"Slide {index + 1} Content",
            value="\n".join(slide["content"]),
            height=150,
            key=f"content_{index}"
        )

        slide["title"] = new_title

        slide["content"] = [
            line.strip()
            for line in new_content.split("\n")
            if line.strip()
        ]


    # --------------------------------------------------
    # EXPORT
    # --------------------------------------------------

    st.markdown("---")

    st.markdown("## 📥 Export Presentation")

    col1, col2 = st.columns(2)

    with col1:

        pptx_file = create_pptx(
            st.session_state.slides,
            topic
        )

        st.download_button(
            label="📊 Download PowerPoint",
            data=pptx_file,
            file_name="AI_Presentation.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )

    with col2:

        pdf_file = create_pdf(
            st.session_state.slides,
            topic
        )

        st.download_button(
            label="📄 Download PDF",
            data=pdf_file,
            file_name="AI_Presentation.pdf",
            mime="application/pdf"
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown(
    """
    <br><br>
    <div style="text-align:center;color:#7f89aa;">
        AI Presentation Maker • Built with Python + Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
