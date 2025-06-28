import streamlit as st
import openai
from PIL import Image
import pytesseract
import pdf2image
import io
import base64
import requests
from datetime import datetime
import os
from typing import Optional, Dict, Any
import re

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
            st.session_state.openai_api_key = "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"
    
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
    
    def create_html_report(self, analysis_data: Dict[str, Any], patient_name: str = "Patient") -> str:
        """Create beautiful HTML report that users can print to PDF from browser"""
        try:
            # Process analysis text for better HTML formatting
            analysis_text = self.format_analysis_for_html(analysis_data['analysis'])
            
            # Create beautiful HTML content with print-friendly CSS
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Health Checkup Analysis Report - {patient_name}</title>
                <style>
                    /* Print-friendly styles */
                    @media print {{
                        @page {{
                            size: A4;
                            margin: 0.75in;
                        }}
                        
                        body {{
                            font-size: 12pt;
                            line-height: 1.4;
                        }}
                        
                        .no-print {{
                            display: none !important;
                        }}
                        
                        .section {{
                            page-break-inside: avoid;
                            break-inside: avoid;
                        }}
                        
                        .disclaimer {{
                            page-break-inside: avoid;
                        }}
                        
                        .header {{
                            page-break-after: avoid;
                        }}
                        
                        h1, h2, h3 {{
                            page-break-after: avoid;
                        }}
                    }}
                    
                    /* Screen styles */
                    body {{
                        font-family: 'Segoe UI', 'Arial', 'Helvetica', sans-serif;
                        line-height: 1.6;
                        color: #2c3e50;
                        margin: 0;
                        padding: 20px;
                        background: #f8f9fa;
                    }}
                    
                    .container {{
                        max-width: 210mm;
                        margin: 0 auto;
                        background: white;
                        padding: 40px;
                        border-radius: 12px;
                        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                    }}
                    
                    .print-button {{
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        border: none;
                        padding: 15px 25px;
                        border-radius: 50px;
                        font-size: 16px;
                        font-weight: bold;
                        cursor: pointer;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                        transition: all 0.3s ease;
                        z-index: 1000;
                    }}
                    
                    .print-button:hover {{
                        transform: translateY(-2px);
                        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
                    }}
                    
                    .header {{
                        text-align: center;
                        margin-bottom: 40px;
                        border-bottom: 4px solid #2E86AB;
                        padding-bottom: 25px;
                        position: relative;
                    }}
                    
                    .header::after {{
                        content: '';
                        position: absolute;
                        bottom: -4px;
                        left: 50%;
                        transform: translateX(-50%);
                        width: 100px;
                        height: 4px;
                        background: linear-gradient(90deg, #28a745, #17a2b8);
                        border-radius: 2px;
                    }}
                    
                    .header h1 {{
                        color: #2E86AB;
                        font-size: 32px;
                        margin: 0 0 10px 0;
                        font-weight: 700;
                        letter-spacing: -1px;
                    }}
                    
                    .header .subtitle {{
                        color: #6c757d;
                        font-size: 16px;
                        font-weight: 500;
                        margin: 0;
                    }}
                    
                    .patient-info {{
                        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                        padding: 25px;
                        border-radius: 15px;
                        margin: 25px 0;
                        border: 1px solid #90caf9;
                        position: relative;
                        overflow: hidden;
                    }}
                    
                    .patient-info::before {{
                        content: '📋';
                        position: absolute;
                        top: 20px;
                        right: 20px;
                        font-size: 24px;
                        opacity: 0.7;
                    }}
                    
                    .patient-info h3 {{
                        color: #1976d2;
                        margin: 0 0 20px 0;
                        font-size: 20px;
                        font-weight: 600;
                    }}
                    
                    .info-grid {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                        gap: 15px;
                    }}
                    
                    .info-item {{
                        background: rgba(255,255,255,0.8);
                        padding: 12px 16px;
                        border-radius: 8px;
                        border-left: 4px solid #1976d2;
                    }}
                    
                    .info-label {{
                        font-weight: 600;
                        color: #37474f;
                        display: block;
                        font-size: 14px;
                        margin-bottom: 4px;
                    }}
                    
                    .info-value {{
                        color: #1976d2;
                        font-weight: 500;
                    }}
                    
                    .analysis-section {{
                        margin: 40px 0;
                    }}
                    
                    .analysis-section h2 {{
                        color: #2E86AB;
                        font-size: 26px;
                        border-bottom: 3px solid #2E86AB;
                        padding-bottom: 12px;
                        margin-bottom: 25px;
                        font-weight: 600;
                        position: relative;
                    }}
                    
                    .analysis-section h2::after {{
                        content: '📊';
                        position: absolute;
                        right: 0;
                        top: 0;
                        font-size: 20px;
                    }}
                    
                    .section {{
                        margin: 30px 0;
                        padding: 25px;
                        background: #fff;
                        border-radius: 12px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                        border-left: 5px solid #28a745;
                        position: relative;
                    }}
                    
                    .section h3 {{
                        color: #28a745;
                        font-size: 20px;
                        margin: 0 0 18px 0;
                        font-weight: 600;
                        display: flex;
                        align-items: center;
                        gap: 10px;
                    }}
                    
                    .section h4 {{
                        color: #495057;
                        font-size: 16px;
                        margin: 20px 0 12px 0;
                        font-weight: 600;
                    }}
                    
                    .section p {{
                        margin: 12px 0;
                        line-height: 1.7;
                        text-align: justify;
                    }}
                    
                    /* Section type styling */
                    .section.summary {{
                        border-left-color: #17a2b8;
                        background: linear-gradient(135deg, #e0f7ff 0%, #b3e5fc 100%);
                    }}
                    
                    .section.summary h3 {{
                        color: #17a2b8;
                    }}
                    
                    .section.findings {{
                        border-left-color: #ffc107;
                        background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%);
                    }}
                    
                    .section.findings h3 {{
                        color: #f57c00;
                    }}
                    
                    .section.recommendations {{
                        border-left-color: #28a745;
                        background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
                    }}
                    
                    .section.lifestyle {{
                        border-left-color: #6f42c1;
                        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
                    }}
                    
                    .section.lifestyle h3 {{
                        color: #6f42c1;
                    }}
                    
                    ul {{
                        padding-left: 25px;
                        margin: 15px 0;
                    }}
                    
                    li {{
                        margin: 10px 0;
                        line-height: 1.6;
                        position: relative;
                    }}
                    
                    li::marker {{
                        color: #28a745;
                        font-weight: bold;
                    }}
                    
                    .highlight {{
                        background: linear-gradient(120deg, #fff3cd 0%, #ffeaa7 100%);
                        padding: 3px 6px;
                        border-radius: 4px;
                        font-weight: 500;
                        border: 1px solid #ffc107;
                    }}
                    
                    strong {{
                        color: #2c3e50;
                        font-weight: 600;
                    }}
                    
                    .disclaimer {{
                        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
                        border: 2px solid #e57373;
                        padding: 25px;
                        border-radius: 12px;
                        margin-top: 50px;
                        position: relative;
                    }}
                    
                    .disclaimer::before {{
                        content: '⚠️';
                        position: absolute;
                        top: 20px;
                        right: 20px;
                        font-size: 24px;
                    }}
                    
                    .disclaimer h3 {{
                        color: #c62828;
                        margin: 0 0 15px 0;
                        font-size: 18px;
                        font-weight: 700;
                    }}
                    
                    .disclaimer p {{
                        margin: 12px 0;
                        font-size: 14px;
                        line-height: 1.5;
                        color: #b71c1c;
                    }}
                    
                    .footer {{
                        text-align: center;
                        margin-top: 40px;
                        padding-top: 25px;
                        border-top: 2px solid #e9ecef;
                        font-size: 13px;
                        color: #6c757d;
                    }}
                    
                    .report-id {{
                        background: #f8f9fa;
                        padding: 8px 12px;
                        border-radius: 6px;
                        font-family: 'Courier New', monospace;
                        font-size: 11px;
                        margin-top: 10px;
                        display: inline-block;
                    }}
                    
                    /* Animations */
                    .section {{
                        animation: fadeInUp 0.6s ease-out;
                    }}
                    
                    @keyframes fadeInUp {{
                        from {{
                            opacity: 0;
                            transform: translateY(30px);
                        }}
                        to {{
                            opacity: 1;
                            transform: translateY(0);
                        }}
                    }}
                </style>
                <script>
                    function printReport() {{
                        window.print();
                    }}
                    
                    // Add print instructions
                    window.addEventListener('beforeprint', function() {{
                        console.log('Printing... For best results, use "Save as PDF" in print dialog');
                    }});
                </script>
            </head>
            <body>
                <button class="print-button no-print" onclick="printReport()">
                    🖨️ Print / Save as PDF
                </button>
                
                <div class="container">
                    <div class="header">
                        <h1>🏥 Health Checkup Analysis Report</h1>
                        <p class="subtitle">AI-Powered Comprehensive Health Assessment</p>
                    </div>
                    
                    <div class="patient-info">
                        <h3>Patient Information</h3>
                        <div class="info-grid">
                            <div class="info-item">
                                <span class="info-label">Patient Name</span>
                                <span class="info-value">{patient_name}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Report Generated</span>
                                <span class="info-value">{analysis_data['timestamp']}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Language</span>
                                <span class="info-value">{analysis_data['language']}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Analysis By</span>
                                <span class="info-value">AI Health Assistant</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="analysis-section">
                        <h2>Health Analysis & Recommendations</h2>
                        {analysis_text}
                    </div>
                    
                    <div class="disclaimer">
                        <h3>IMPORTANT MEDICAL DISCLAIMER</h3>
                        <p><strong>This analysis is generated by artificial intelligence and is for informational purposes only.</strong></p>
                        <p>This report should <strong>NOT</strong> replace professional medical advice, diagnosis, or treatment. Always seek the advice of qualified healthcare professionals regarding any medical condition or health concerns.</p>
                        <p><strong>In case of medical emergencies, contact emergency services immediately.</strong></p>
                        <p>The AI analysis may not identify all health conditions or risks. Regular consultation with healthcare providers is recommended for comprehensive health management.</p>
                    </div>
                    
                    <div class="footer">
                        <p><strong>Generated by Health Checkup Analyzer</strong><br>AI-Powered Medical Report Analysis</p>
                        <div class="report-id">Report ID: {analysis_data['timestamp'].replace(' ', '_').replace(':', '-')}</div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return html_content
            
        except Exception as e:
            st.error(f"Error creating HTML report: {str(e)}")
            return None
    
    def format_analysis_for_html(self, analysis_text: str) -> str:
        """Format the analysis text for better HTML presentation"""
        try:
            # Split into sections based on common patterns
            sections = []
            current_section = ""
            
            lines = analysis_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if line is a major heading (contains keywords like SUMMARY, FINDINGS, etc.)
                if any(keyword in line.upper() for keyword in [
                    'SUMMARY', 'FINDINGS', 'HEALTH STATUS', 'LIFESTYLE', 'DIETARY', 
                    'EXERCISE', 'FOLLOW-UP', 'PREVENTIVE', 'RECOMMENDATIONS'
                ]):
                    if current_section:
                        sections.append(current_section)
                    current_section = f"<div class='section'><h3>{line}</h3>"
                
                # Check if line starts with a number (like "1.", "2.", etc.)
                elif re.match(r'^\d+\.', line):
                    if current_section:
                        sections.append(current_section + "</div>")
                    current_section = f"<div class='section'><h3>{line}</h3>"
                
                # Regular content
                else:
                    if line.startswith('-') or line.startswith('•'):
                        # Convert bullet points to HTML list items
                        if '<ul>' not in current_section:
                            current_section += "<ul>"
                        current_section += f"<li>{line[1:].strip()}</li>"
                    else:
                        # Close any open list
                        if '<ul>' in current_section and '</ul>' not in current_section:
                            current_section += "</ul>"
                        current_section += f"<p>{line}</p>"
            
            # Close the last section
            if current_section:
                if '<ul>' in current_section and '</ul>' not in current_section:
                    current_section += "</ul>"
                current_section += "</div>"
                sections.append(current_section)
            
            # If no sections were created, format as simple paragraphs
            if not sections:
                paragraphs = [f"<p>{para.strip()}</p>" for para in analysis_text.split('\n\n') if para.strip()]
                return f"<div class='section'>{''.join(paragraphs)}</div>"
            
            return ''.join(sections)
            
        except Exception as e:
            # Fallback to simple formatting
            paragraphs = analysis_text.replace('\n\n', '</p><p>').replace('\n', '<br>')
            return f"<div class='section'><p>{paragraphs}</p></div>"
    


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
        - 📄 Beautiful HTML reports
        - 🖨️ Print-to-PDF ready
        - 👀 Live preview
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
                        
                        # Generate HTML Report
                        st.subheader("📥 Get Your Report")
                        
                        with st.spinner("📄 Generating beautiful HTML report..."):
                            html_content = analyzer.create_html_report(analysis_result, patient_name)
                        
                        if html_content:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"health_analysis_{patient_name}_{timestamp}.html"
                            
                            # Create two columns for different options
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.download_button(
                                    label="📥 Download HTML Report",
                                    data=html_content.encode('utf-8'),
                                    file_name=filename,
                                    mime="text/html",
                                    type="primary"
                                )
                            
                            with col2:
                                # Create a temporary display of the HTML
                                if st.button("👀 Preview Report", type="secondary"):
                                    st.session_state.show_preview = True
                            
                            st.markdown("""
                            <div class="success-box">
                                <b>✅ Success!</b><br/>
                                Your health report analysis is ready! 
                                <br><br>
                                <b>📥 Download HTML:</b> Save the file and open in your browser<br/>
                                <b>🖨️ Print to PDF:</b> Open the HTML file → Press Ctrl+P → Save as PDF<br/>
                                <b>👀 Preview:</b> See how the report looks before downloading
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Show preview if requested
                            if st.session_state.get('show_preview', False):
                                st.subheader("📄 Report Preview")
                                st.markdown("*This is how your report will look. Use the 'Download HTML Report' button above to save it.*")
                                
                                # Display the HTML in an iframe-like container
                                st.components.v1.html(html_content, height=800, scrolling=True)
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
