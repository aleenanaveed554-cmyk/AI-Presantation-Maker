import streamlit as st
from openai import OpenAI
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit
from io import BytesIO
import json

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Presentation Maker",
    page_icon="🎓",
    layout="wide"
)

# ---------------- DESIGN ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0b1024, #172554, #312e81);
    color: white;
}
h1, h2, h3, p, label {
    color: white !important;
}
.block-container {
    padding-top: 2rem;
}
.stButton > button {
    background: linear-gradient(90deg, #6366f1, #a855f7);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 24px;
    font-weight: bold;
}
.stButton > button:hover {
    background: #818cf8;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.title("🎓 AI Presentation Maker")
st.markdown(
    "Create professional presentations in seconds with the power of AI."
)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("⚙️ Presentation Settings")

    language = st.selectbox(
        "Presentation Language",
        ["English", "Urdu", "Roman Urdu"]
    )

    slide_count = st.slider(
        "Number of Slides",
        min_value=3,
        max_value=15,
        value=6
    )

    audience = st.selectbox(
        "Presentation Audience",
        ["University Students", "Teachers", "Professionals"]
    )

    style = st.selectbox(
        "Presentation Style",
        ["Modern", "Academic", "Minimal", "Creative"]
    )

    st.info("Enter a topic to generate your presentation.")

# ---------------- TOPIC INPUT ----------------
topic = st.text_input(
    "Enter Your Presentation Topic",
    placeholder="e.g. Artificial Intelligence in Education"
)

# ---------------- GENERATE PRESENTATION ----------------
if st.button("✨ Generate Presentation", use_container_width=True):

    if not topic.strip():
        st.warning("Please enter a presentation topic.")
        st.stop()

    if "OPENAI_API_KEY" not in st.secrets:
        st.error(
            "OpenAI API key nahi mili. "
            "Streamlit Secrets mein OPENAI_API_KEY add karein."
        )
        st.stop()

    client = OpenAI(
        api_key=st.secrets["OPENAI_API_KEY"]
    )

    prompt = f"""
    Create a professional presentation for {audience}.

    Topic: {topic}
    Number of slides: {slide_count}
    Language: {language}
    Style: {style}

    Return ONLY valid JSON in this format:
    {{
        "title": "Presentation title",
        "slides": [
            {{
                "title": "Slide title",
                "points": [
                    "Point 1",
                    "Point 2",
                    "Point 3"
                ]
            }}
        ]
    }}

    Requirements:
    - Include an introduction slide.
    - Explain the topic clearly.
    - Use short, meaningful bullet points.
    - Include examples where useful.
    - Include a conclusion slide.
    - Do not use markdown.
    - Keep the presentation suitable for a university audience.
    """

    try:
        with st.spinner("AI is creating your presentation..."):

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
                response_format={"type": "json_object"}
            )

            result = json.loads(
                response.choices[0].message.content
            )

            st.session_state["presentation"] = result

    except Exception as e:
        st.error(f"Presentation generate nahi hui: {e}")

# ---------------- DISPLAY & EDIT SLIDES ----------------
if "presentation" in st.session_state:

    presentation = st.session_state["presentation"]

    st.success("Your presentation is ready!")

    st.subheader("📝 Edit Your Presentation")

    presentation["title"] = st.text_input(
        "Presentation Title",
        value=presentation.get("title", topic)
    )

    for index, slide in enumerate(presentation["slides"]):

        with st.expander(
            f"Slide {index + 1}: {slide.get('title', '')}",
            expanded=False
        ):

            slide["title"] = st.text_input(
                "Slide Title",
                value=slide.get("title", ""),
                key=f"title_{index}"
            )

            points_text = st.text_area(
                "Slide Points (one point per line)",
                value="\n".join(slide.get("points", [])),
                height=150,
                key=f"points_{index}"
            )

            slide["points"] = [
                point.strip()
                for point in points_text.split("\n")
                if point.strip()
            ]

    # ---------------- POWERPOINT EXPORT ----------------
    def create_pptx(data):
        prs = Presentation()

        for index, slide_data in enumerate(data["slides"]):

            if index == 0:
                slide = prs.slides.add_slide(
                    prs.slide_layouts[0]
                )
                slide.shapes.title.text = data["title"]
                slide.placeholders[1].text = (
                    slide_data.get("title", "")
                )
            else:
                slide = prs.slides.add_slide(
                    prs.slide_layouts[1]
                )

                slide.shapes.title.text = slide_data.get(
                    "title", ""
                )

                body = slide.placeholders[1].text_frame
                body.clear()

                for point in slide_data.get("points", []):
                    paragraph = body.add_paragraph()
                    paragraph.text = point
                    paragraph.level = 0
                    paragraph.font.size = Pt(22)

            # Professional colors
            background = slide.background
            background.fill.solid()
            background.fill.fore_color.rgb = RGBColor(
                15, 23, 42
            )

            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        for run in paragraph.runs:
                            run.font.color.rgb = RGBColor(
                                255, 255, 255
                            )

        output = BytesIO()
        prs.save(output)
        output.seek(0)
        return output

    # ---------------- PDF EXPORT ----------------
    def create_pdf(data):
        output = BytesIO()
        pdf = canvas.Canvas(output, pagesize=A4)

        width, height = A4

        for slide_data in data["slides"]:

            pdf.setFillColorRGB(0.05, 0.08, 0.20)
            pdf.rect(0, 0, width, height, fill=1)

            pdf.setFillColorRGB(1, 1, 1)
            pdf.setFont("Helvetica-Bold", 22)

            y = height - 80

            for line in simpleSplit(
                slide_data.get("title", ""),
                "Helvetica-Bold",
                22,
                width - 100
            ):
                pdf.drawString(50, y, line)
                y -= 30

            y -= 25

            pdf.setFont("Helvetica", 14)

            for point in slide_data.get("points", []):

                lines = simpleSplit(
                    "• " + point,
                    "Helvetica",
                    14,
                    width - 100
                )

                for line in lines:
                    if y < 70:
                        pdf.showPage()
                        pdf.setFillColorRGB(0.05, 0.08, 0.20)
                        pdf.rect(0, 0, width, height, fill=1)
                        pdf.setFillColorRGB(1, 1, 1)
                        y = height - 70

                    pdf.drawString(50, y, line)
                    y -= 25

                y -= 10

            pdf.showPage()

        pdf.save()
        output.seek(0)
        return output

    # ---------------- DOWNLOAD BUTTONS ----------------
    st.subheader("📥 Download Presentation")

    col1, col2 = st.columns(2)

    with col1:
        pptx_file = create_pptx(presentation)

        st.download_button(
            "📊 Download PowerPoint",
            data=pptx_file,
            file_name="AI_Presentation.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True
        )

    with col2:
        pdf_file = create_pdf(presentation)

        st.download_button(
            "📄 Download PDF",
            data=pdf_file,
            file_name="AI_Presentation.pdf",
            mime="application/pdf",
            use_container_width=True
        )

st.markdown("---")
st.caption("AI Presentation Maker | Powered by Streamlit and OpenAI")
