import streamlit as st
import openai
from PIL import Image
import pytesseract
import pdf2image
import io
import base64
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfutils
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import requests
from datetime import datetime
import os
from typing import Optional, Dict, Any

# Set page configuration
st.set_page_config(
    page_title="Health Checkup Analyzer",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .analysis-result {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class HealthCheckupAnalyzer:
    def __init__(self):
        self.setup_openai()
        self.language_prompts = {
            "English": "Provide the analysis in clear, professional English.",
            "Hindi": "कृपया विश्लेषण स्पष्ट और व्यावसायिक हिंदी में प्रदान करें।",
            "Hinglish": "Please provide the analysis in Hinglish (Hindi-English mix) that's easy to understand for Indian users."
        }
    
    def setup_openai(self):
        """Setup OpenAI API key"""
        if 'openai_api_key' not in st.session_state:
            st.session_state.openai_api_key = ""
    
    def extract_text_from_image(self, image) -> str:
        """Extract text from uploaded image using OCR"""
        try:
            # Convert PIL image to text using pytesseract
            text = pytesseract.image_to_string(image, lang='eng+hin')
            return text
        except Exception as e:
            st.error(f"Error extracting text from image: {str(e)}")
            return ""
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from uploaded PDF"""
        try:
            # Convert PDF to images
            images = pdf2image.convert_from_bytes(pdf_file.read())
            
            extracted_text = ""
            for image in images:
                # Extract text from each page
                page_text = pytesseract.image_to_string(image, lang='eng+hin')
                extracted_text += page_text + "\n\n"
            
            return extracted_text
        except Exception as e:
            st.error(f"Error extracting text from PDF: {str(e)}")
            return ""
    
    def analyze_health_report(self, text: str, language: str) -> Dict[str, Any]:
        """Analyze health report using OpenAI"""
        try:
            if not st.session_state.openai_api_key:
                st.error("Please enter your OpenAI API key in the sidebar.")
                return None
            
            client = openai.OpenAI(api_key=st.session_state.openai_api_key)
            
            language_instruction = self.language_prompts.get(language, self.language_prompts["English"])
            
            prompt = f"""
            You are a medical AI assistant specializing in health report analysis. 
            Please analyze the following health checkup report and provide:

            1. **SUMMARY**: A comprehensive summary of the test results
            2. **KEY FINDINGS**: Important findings and abnormal values
            3. **HEALTH STATUS**: Overall health assessment
            4. **LIFESTYLE RECOMMENDATIONS**: Specific lifestyle changes needed
            5. **DIETARY SUGGESTIONS**: Nutritional recommendations
            6. **EXERCISE RECOMMENDATIONS**: Physical activity suggestions
            7. **FOLLOW-UP ACTIONS**: When to consult doctors or repeat tests
            8. **PREVENTIVE MEASURES**: Steps to prevent future health issues

            {language_instruction}

            Health Report Text:
            {text}

            Please provide a detailed, structured analysis that's easy to understand for a non-medical person.
            Include specific actionable recommendations.
            """

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful medical AI assistant that provides health report analysis and recommendations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            analysis = response.choices[0].message.content
            
            return {
                "analysis": analysis,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "language": language
            }
            
        except Exception as e:
            st.error(f"Error analyzing health report: {str(e)}")
            return None
    
    def create_pdf_report(self, analysis_data: Dict[str, Any], patient_name: str = "Patient") -> bytes:
        """Create PDF report from analysis data"""
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                spaceAfter=30,
                textColor=colors.darkblue,
                alignment=1  # Center alignment
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                textColor=colors.darkgreen
            )
            
            # Title
            title = Paragraph(f"Health Checkup Analysis Report", title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Patient info
            patient_info = f"""
            <b>Patient Name:</b> {patient_name}<br/>
            <b>Report Generated:</b> {analysis_data['timestamp']}<br/>
            <b>Language:</b> {analysis_data['language']}<br/>
            <b>Analysis By:</b> AI Health Assistant
            """
            story.append(Paragraph(patient_info, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Analysis content
            analysis_heading = Paragraph("Health Analysis & Recommendations", heading_style)
            story.append(analysis_heading)
            
            # Split analysis into paragraphs for better formatting
            analysis_paragraphs = analysis_data['analysis'].split('\n\n')
            for para in analysis_paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), styles['Normal']))
                    story.append(Spacer(1, 12))
            
            # Disclaimer
            disclaimer_style = ParagraphStyle(
                'Disclaimer',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.red,
                spaceAfter=12
            )
            
            disclaimer = """
            <b>IMPORTANT DISCLAIMER:</b><br/>
            This analysis is generated by AI and is for informational purposes only. 
            It should not replace professional medical advice, diagnosis, or treatment. 
            Always consult with qualified healthcare professionals for medical concerns.
            """
            story.append(Spacer(1, 30))
            story.append(Paragraph(disclaimer, disclaimer_style))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            st.error(f"Error creating PDF: {str(e)}")
            return None
    
    def get_download_link(self, pdf_bytes: bytes, filename: str) -> str:
        """Generate download link for PDF"""
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" class="download-link">📥 Download PDF Report</a>'
        return href

def main():
    analyzer = HealthCheckupAnalyzer()
    
    # Header
    st.markdown('<div class="main-header">🏥 Health Checkup Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered Health Report Analysis with Personalized Recommendations</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # OpenAI API Key
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.get('openai_api_key', ''),
            help="Enter your OpenAI API key to enable health report analysis"
        )
        st.session_state.openai_api_key = api_key
        
        # Language selection
        language = st.selectbox(
            "Select Language",
            ["English", "Hindi", "Hinglish"],
            help="Choose the language for analysis output"
        )
        
        # Patient name
        patient_name = st.text_input(
            "Patient Name (Optional)",
            value="Patient",
            help="Enter patient name for the PDF report"
        )
        
        st.divider()
        
        # Features info
        st.markdown("""
        ### 🎯 Features
        - 📤 Upload health reports (PDF/Image)
        - 🤖 AI-powered analysis
        - 🌐 Multi-language support
        - 📊 Detailed recommendations
        - 📋 PDF report generation
        - 💡 Lifestyle suggestions
        """)
    
    # Main content
    if not st.session_state.get('openai_api_key'):
        st.markdown("""
        <div class="warning-box">
            <b>⚠️ Setup Required:</b><br/>
            Please enter your OpenAI API key in the sidebar to get started.
            You can get your API key from <a href="https://platform.openai.com/api-keys" target="_blank">OpenAI Platform</a>.
        </div>
        """, unsafe_allow_html=True)
    
    # File upload section
    st.header("📤 Upload Health Report")
    
    uploaded_file = st.file_uploader(
        "Choose your health checkup report",
        type=['pdf', 'png', 'jpg', 'jpeg'],
        help="Upload your health report in PDF or image format"
    )
    
    if uploaded_file is not None:
        # Display file info
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size} bytes",
            "File type": uploaded_file.type
        }
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("📄 File Details")
            for key, value in file_details.items():
                st.write(f"**{key}:** {value}")
        
        with col2:
            # Display preview
            if uploaded_file.type.startswith('image'):
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)
            else:
                st.write("📄 PDF file uploaded successfully")
        
        # Extract text
        with st.spinner("🔍 Extracting text from your report..."):
            if uploaded_file.type.startswith('image'):
                image = Image.open(uploaded_file)
                extracted_text = analyzer.extract_text_from_image(image)
            else:
                extracted_text = analyzer.extract_text_from_pdf(uploaded_file)
        
        if extracted_text:
            # Show extracted text (collapsible)
            with st.expander("📝 Extracted Text Preview"):
                st.text_area("Extracted Content", extracted_text, height=200, disabled=True)
            
            # Analyze button
            if st.button("🔬 Analyze Health Report", type="primary"):
                if not st.session_state.openai_api_key:
                    st.error("Please enter your OpenAI API key in the sidebar.")
                else:
                    with st.spinner("🤖 Analyzing your health report..."):
                        analysis_result = analyzer.analyze_health_report(extracted_text, language)
                    
                    if analysis_result:
                        st.success("✅ Analysis completed successfully!")
                        
                        # Display analysis
                        st.markdown('<div class="analysis-result">', unsafe_allow_html=True)
                        st.markdown("## 📊 Health Analysis Results")
                        st.markdown(analysis_result['analysis'])
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Generate PDF
                        st.subheader("📥 Download Report")
                        
                        with st.spinner("📄 Generating PDF report..."):
                            pdf_bytes = analyzer.create_pdf_report(analysis_result, patient_name)
                        
                        if pdf_bytes:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"health_analysis_{patient_name}_{timestamp}.pdf"
                            
                            st.download_button(
                                label="📥 Download PDF Report",
                                data=pdf_bytes,
                                file_name=filename,
                                mime="application/pdf",
                                type="primary"
                            )
                            
                            st.markdown("""
                            <div class="success-box">
                                <b>✅ Success!</b><br/>
                                Your health report analysis is ready for download. 
                                The PDF contains detailed analysis and recommendations.
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.error("❌ Could not extract text from the uploaded file. Please ensure the image/PDF is clear and readable.")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p><b>🏥 Health Checkup Analyzer</b> - AI-Powered Health Report Analysis</p>
        <p><small>⚠️ This tool is for informational purposes only. Always consult healthcare professionals for medical advice.</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
