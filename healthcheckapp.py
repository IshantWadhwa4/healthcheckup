import streamlit as st
import openai
import pdfplumber  # PDF text extraction with layout preservation
import io
import requests
from datetime import datetime
import os
from typing import Optional, Dict, Any
import re

# Clean up any proxy-related environment variables that might interfere
if 'HTTP_PROXY' in os.environ:
    del os.environ['HTTP_PROXY']
if 'HTTPS_PROXY' in os.environ:
    del os.environ['HTTPS_PROXY']
if 'http_proxy' in os.environ:
    del os.environ['http_proxy']
if 'https_proxy' in os.environ:
    del os.environ['https_proxy']

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
        """Setup OpenAI API key - Always requires user input"""
        if 'openai_api_key' not in st.session_state:
            st.session_state.openai_api_key = ""
        
        # Clear any existing API key on app restart for security
        if not st.session_state.openai_api_key:
            st.session_state.openai_api_key = ""
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF using pdfplumber with layout preservation and table detection"""
        try:
            # Read PDF file bytes
            pdf_bytes = pdf_file.read()
            extracted_text = ""
            
            # Open PDF with pdfplumber
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                page_count = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages):
                    # Extract text with layout preservation
                    page_text = page.extract_text()
                    
                    if page_text and page_text.strip():
                        extracted_text += f"\n--- Page {page_num + 1} ---\n"
                        extracted_text += page_text + "\n"
                        
                        # Also extract tables if any
                        tables = page.extract_tables()
                        if tables:
                            extracted_text += "\n--- Tables on this page ---\n"
                            for table_num, table in enumerate(tables):
                                extracted_text += f"Table {table_num + 1}:\n"
                                for row in table:
                                    if row and any(cell for cell in row if cell):
                                        row_text = " | ".join(str(cell) if cell else "" for cell in row)
                                        extracted_text += row_text + "\n"
                                extracted_text += "\n"
            
            return extracted_text.strip()
            
        except Exception as e:
            st.error(f"Error extracting text from PDF: {str(e)}")
            return ""    
    
    def analyze_health_report(self, text: str, language: str) -> Dict[str, Any]:
        """Analyze health report using OpenAI GPT"""
        try:
            # Validate API key
            api_key = st.session_state.openai_api_key
            if not api_key:
                st.error("🔑 Please enter your OpenAI API key in the sidebar.")
                return None
            
            if not api_key.startswith('sk-') or len(api_key) < 20:
                st.error("❌ Invalid API key format. Please check your OpenAI API key.")
                return None
            
            if not text or not text.strip():
                st.error("📄 No text extracted from PDF to analyze.")
                return None
            
            language_instruction = self.language_prompts.get(language, self.language_prompts["English"])
            
            prompt = f"""You are a medical AI assistant specializing in health report analysis. 

Please carefully analyze the following health checkup report text and provide:

1. **SUMMARY**: A comprehensive summary of all test results across all pages
2. **KEY FINDINGS**: Important findings and abnormal values (highlight which are outside normal ranges)
3. **HEALTH STATUS**: Overall health assessment based on all available data
4. **LIFESTYLE RECOMMENDATIONS**: Specific lifestyle changes needed based on the results
5. **DIETARY SUGGESTIONS**: Nutritional recommendations tailored to the findings
6. **EXERCISE RECOMMENDATIONS**: Physical activity suggestions appropriate for the health status
7. **FOLLOW-UP ACTIONS**: Which tests to repeat, when to consult doctors, and urgency levels
8. **PREVENTIVE MEASURES**: Steps to prevent future health issues

{language_instruction}

Please analyze the health report text below. Look for:
- Lab test results and reference ranges
- Vital signs and measurements
- Any numerical values and their normal ranges
- Doctor's notes or recommendations
- Test dates and patient information
- Abnormal or concerning values

Provide a detailed, structured analysis that's easy to understand for a non-medical person.
Include specific actionable recommendations with clear priorities.
If any values are critical or require immediate attention, highlight them clearly.

Health Report Text:
{text}

Please provide a thorough analysis based on the extracted text content."""

            # Use OpenAI API directly with requests to bypass client initialization issues
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a helpful medical AI assistant that provides health report analysis and recommendations."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2500,
                "temperature": 0.7
            }
            
            # Make the API request
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code != 200:
                st.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return None
            
            response_data = response.json()
            analysis = response_data['choices'][0]['message']['content']
            
            # Count pages from text (rough estimate)
            pages_analyzed = text.count("--- Page") if "--- Page" in text else 1
            
            return {
                "analysis": analysis,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "language": language,
                "pages_analyzed": pages_analyzed,
                "extracted_text_length": len(text)
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
                    /* Medical Report Professional Styles */
                    :root {{
                        --primary-blue: #1e40af;
                        --secondary-blue: #3b82f6;
                        --success-green: #059669;
                        --warning-orange: #d97706;
                        --danger-red: #dc2626;
                        --info-cyan: #0891b2;
                        --gray-50: #f9fafb;
                        --gray-100: #f3f4f6;
                        --gray-200: #e5e7eb;
                        --gray-300: #d1d5db;
                        --gray-600: #4b5563;
                        --gray-700: #374151;
                        --gray-800: #1f2937;
                        --gray-900: #111827;
                    }}
                    
                    /* Print-Optimized Styles */
                    @media print {{
                        @page {{
                            size: A4;
                            margin: 0.5in 0.75in;
                        }}
                        
                        * {{
                            -webkit-print-color-adjust: exact !important;
                            color-adjust: exact !important;
                            print-color-adjust: exact !important;
                        }}
                        
                        body {{
                            font-size: 11pt;
                            line-height: 1.3;
                            color: #000;
                            background: white;
                        }}
                        
                        .no-print {{
                            display: none !important;
                        }}
                        
                        .medical-section {{
                            page-break-inside: avoid;
                            break-inside: avoid;
                            margin-bottom: 20px;
                        }}
                        
                        .section-header {{
                            page-break-after: avoid;
                        }}
                        
                        .patient-info {{
                            page-break-after: avoid;
                        }}
                        
                        .header {{
                            page-break-after: avoid;
                        }}
                        
                        h1, h2, h3, h4 {{
                            page-break-after: avoid;
                        }}
                        
                        .container {{
                            box-shadow: none;
                            border-radius: 0;
                            margin: 0;
                            padding: 0;
                        }}
                    }}
                    
                    /* Base Styles */
                    * {{
                        box-sizing: border-box;
                    }}
                    
                    body {{
                        font-family: 'Inter', 'Segoe UI', 'system-ui', -apple-system, sans-serif;
                        line-height: 1.6;
                        color: var(--gray-800);
                        margin: 0;
                        padding: 20px;
                        background: var(--gray-50);
                        font-size: 14px;
                    }}
                    
                    .container {{
                        max-width: 21cm;
                        margin: 0 auto;
                        background: white;
                        padding: 40px;
                        border-radius: 8px;
                        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
                        position: relative;
                    }}
                    
                    /* Print Button */
                    .print-button {{
                        position: fixed;
                        top: 30px;
                        right: 30px;
                        background: var(--primary-blue);
                        color: white;
                        border: none;
                        padding: 12px 24px;
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: 600;
                        cursor: pointer;
                        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.4);
                        transition: all 0.2s ease;
                        z-index: 1000;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    }}
                    
                    .print-button:hover {{
                        background: #1d4ed8;
                        transform: translateY(-1px);
                        box-shadow: 0 6px 16px rgba(30, 64, 175, 0.5);
                    }}
                    
                    /* Header Section */
                    .header {{
                        text-align: center;
                        margin-bottom: 40px;
                        padding-bottom: 30px;
                        border-bottom: 3px solid var(--primary-blue);
                        position: relative;
                    }}
                    
                    .header h1 {{
                        color: var(--primary-blue);
                        font-size: 28px;
                        font-weight: 700;
                        margin: 0 0 8px 0;
                        letter-spacing: -0.5px;
                    }}
                    
                    .header .subtitle {{
                        color: var(--gray-600);
                        font-size: 16px;
                        font-weight: 500;
                        margin: 0;
                    }}
                    
                    /* Patient Information Section */
                    .patient-info {{
                        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
                        border: 1px solid #bfdbfe;
                        padding: 30px;
                        border-radius: 12px;
                        margin: 30px 0;
                        position: relative;
                    }}
                    
                    .patient-info h3 {{
                        color: var(--primary-blue);
                        margin: 0 0 20px 0;
                        font-size: 18px;
                        font-weight: 600;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    }}
                    
                    .info-grid {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                        gap: 16px;
                    }}
                    
                    .info-item {{
                        background: rgba(255, 255, 255, 0.9);
                        padding: 16px 20px;
                        border-radius: 8px;
                        border-left: 4px solid var(--primary-blue);
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                    }}
                    
                    .info-label {{
                        font-weight: 600;
                        color: var(--gray-700);
                        display: block;
                        font-size: 12px;
                        margin-bottom: 4px;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                    }}
                    
                    .info-value {{
                        color: var(--primary-blue);
                        font-weight: 600;
                        font-size: 14px;
                    }}
                    
                    /* Medical Sections */
                    .medical-section {{
                        margin: 30px 0;
                        background: white;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                        border: 1px solid var(--gray-200);
                    }}
                    
                    .section-header {{
                        padding: 20px 30px;
                        background: linear-gradient(135deg, var(--gray-50) 0%, white 100%);
                        border-bottom: 2px solid var(--gray-200);
                    }}
                    
                    .section-header h3 {{
                        margin: 0;
                        font-size: 18px;
                        font-weight: 700;
                        color: var(--gray-800);
                        display: flex;
                        align-items: center;
                        gap: 12px;
                    }}
                    
                    .section-icon {{
                        font-size: 20px;
                        display: inline-block;
                    }}
                    
                    .section-content {{
                        padding: 30px;
                    }}
                    
                    /* Section Type Specific Styling */
                    .medical-section.summary .section-header {{
                        background: linear-gradient(135deg, #ecfeff 0%, #cffafe 100%);
                        border-bottom-color: var(--info-cyan);
                    }}
                    
                    .medical-section.summary .section-header h3 {{
                        color: var(--info-cyan);
                    }}
                    
                    .medical-section.findings .section-header {{
                        background: linear-gradient(135deg, #fef3c7 0%, #fed7aa 100%);
                        border-bottom-color: var(--warning-orange);
                    }}
                    
                    .medical-section.findings .section-header h3 {{
                        color: var(--warning-orange);
                    }}
                    
                    .medical-section.health-status .section-header {{
                        background: linear-gradient(135deg, #fecaca 0%, #fca5a5 100%);
                        border-bottom-color: var(--danger-red);
                    }}
                    
                    .medical-section.health-status .section-header h3 {{
                        color: var(--danger-red);
                    }}
                    
                    .medical-section.lifestyle .section-header,
                    .medical-section.dietary .section-header,
                    .medical-section.exercise .section-header {{
                        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
                        border-bottom-color: var(--success-green);
                    }}
                    
                    .medical-section.lifestyle .section-header h3,
                    .medical-section.dietary .section-header h3,
                    .medical-section.exercise .section-header h3 {{
                        color: var(--success-green);
                    }}
                    
                    .medical-section.follow-up .section-header,
                    .medical-section.preventive .section-header {{
                        background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
                        border-bottom-color: var(--secondary-blue);
                    }}
                    
                    .medical-section.follow-up .section-header h3,
                    .medical-section.preventive .section-header h3 {{
                        color: var(--secondary-blue);
                    }}
                    
                    /* Typography */
                    .sub-heading {{
                        color: var(--gray-700);
                        font-size: 16px;
                        font-weight: 600;
                        margin: 25px 0 15px 0;
                        padding-bottom: 8px;
                        border-bottom: 1px solid var(--gray-200);
                    }}
                    
                    p {{
                        margin: 16px 0;
                        line-height: 1.7;
                        color: var(--gray-700);
                        text-align: justify;
                    }}
                    
                    /* Lists */
                    .medical-list {{
                        padding-left: 0;
                        margin: 20px 0;
                        list-style: none;
                    }}
                    
                    .medical-list li {{
                        position: relative;
                        padding: 12px 0 12px 35px;
                        margin: 8px 0;
                        line-height: 1.6;
                        border-left: 3px solid var(--gray-200);
                        padding-left: 20px;
                        margin-left: 15px;
                        background: var(--gray-50);
                        border-radius: 4px;
                        padding: 12px 15px 12px 35px;
                    }}
                    
                    .medical-list li::before {{
                        content: '▸';
                        position: absolute;
                        left: 15px;
                        top: 12px;
                        color: var(--success-green);
                        font-weight: bold;
                        font-size: 14px;
                    }}
                    
                    /* Medical Value Highlighting */
                    .medical-value {{
                        background: linear-gradient(135deg, #fef3c7 0%, #fed7aa 100%);
                        color: var(--warning-orange);
                        padding: 2px 6px;
                        border-radius: 4px;
                        font-weight: 600;
                        font-family: 'Monaco', 'Menlo', monospace;
                        font-size: 13px;
                        border: 1px solid #f59e0b;
                    }}
                    
                    .medical-term {{
                        padding: 2px 6px;
                        border-radius: 4px;
                        font-weight: 600;
                        font-size: 12px;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                    }}
                    
                    .medical-term.high,
                    .medical-term.elevated,
                    .medical-term.critical {{
                        background: #fecaca;
                        color: var(--danger-red);
                        border: 1px solid #f87171;
                    }}
                    
                    .medical-term.low,
                    .medical-term.decreased {{
                        background: #fed7aa;
                        color: var(--warning-orange);
                        border: 1px solid #fb923c;
                    }}
                    
                    .medical-term.normal,
                    .medical-term.optimal,
                    .medical-term.good {{
                        background: #bbf7d0;
                        color: var(--success-green);
                        border: 1px solid #4ade80;
                    }}
                    
                    .medical-term.recommended,
                    .medical-term.maintain {{
                        background: #dbeafe;
                        color: var(--primary-blue);
                        border: 1px solid #60a5fa;
                    }}
                    
                    strong {{
                        color: var(--gray-800);
                        font-weight: 700;
                    }}
                    
                    /* Disclaimer Section */
                    .disclaimer {{
                        background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%);
                        border: 2px solid #fca5a5;
                        padding: 30px;
                        border-radius: 12px;
                        margin-top: 50px;
                        position: relative;
                    }}
                    
                    .disclaimer::before {{
                        content: '⚠️';
                        position: absolute;
                        top: 25px;
                        right: 25px;
                        font-size: 24px;
                    }}
                    
                    .disclaimer h3 {{
                        color: var(--danger-red);
                        margin: 0 0 20px 0;
                        font-size: 18px;
                        font-weight: 700;
                    }}
                    
                    .disclaimer p {{
                        margin: 12px 0;
                        font-size: 14px;
                        line-height: 1.6;
                        color: #7f1d1d;
                    }}
                    
                    /* Footer */
                    .footer {{
                        text-align: center;
                        margin-top: 50px;
                        padding-top: 30px;
                        border-top: 2px solid var(--gray-200);
                        color: var(--gray-600);
                    }}
                    
                    .report-id {{
                        background: var(--gray-100);
                        padding: 8px 16px;
                        border-radius: 6px;
                        font-family: 'Monaco', 'Menlo', monospace;
                        font-size: 11px;
                        margin-top: 15px;
                        display: inline-block;
                        color: var(--gray-600);
                    }}
                    
                    /* Responsive Design */
                    @media (max-width: 768px) {{
                        .container {{
                            padding: 20px;
                            margin: 10px;
                        }}
                        
                        .info-grid {{
                            grid-template-columns: 1fr;
                        }}
                        
                        .section-content {{
                            padding: 20px;
                        }}
                        
                        .print-button {{
                            top: 20px;
                            right: 20px;
                            padding: 10px 16px;
                            font-size: 12px;
                        }}
                    }}
                    
                    /* Animation */
                    .medical-section {{
                        animation: slideInUp 0.6s ease-out;
                    }}
                    
                    @keyframes slideInUp {{
                        from {{
                            opacity: 0;
                            transform: translateY(20px);
                        }}
                        to {{
                            opacity: 1;
                            transform: translateY(0);
                        }}
                    }}
                </style>
                <script>
                    // Print functionality with user feedback
                    function printReport() {{
                        // Show loading state
                        const button = document.querySelector('.print-button');
                        const originalText = button.innerHTML;
                        button.innerHTML = '🔄 Preparing...';
                        button.disabled = true;
                        
                        // Trigger print after short delay
                        setTimeout(function() {{
                            window.print();
                            // Reset button
                            setTimeout(function() {{
                                button.innerHTML = originalText;
                                button.disabled = false;
                            }}, 1000);
                        }}, 500);
                    }}
                    
                    // Enhanced print event handling
                    window.addEventListener('beforeprint', function() {{
                        console.log('🖨️ Printing Health Report - Use "Save as PDF" for best results');
                        
                        // Optimize for print
                        document.body.style.backgroundColor = 'white';
                        
                        // Show print tips
                        const printTips = document.createElement('div');
                        printTips.className = 'print-tips no-print';
                        printTips.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border-radius: 8px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); z-index: 10000; border: 2px solid #3b82f6;';
                        printTips.innerHTML = '<h4 style="margin: 0 0 10px 0; color: #1e40af;">📄 Print Tips</h4><ul style="margin: 0; padding-left: 20px; font-size: 14px;"><li>Use "Save as PDF" instead of printing</li><li>Select "More settings" → "Background graphics"</li><li>Choose A4 paper size for best layout</li></ul>';
                        document.body.appendChild(printTips);
                        
                        // Remove tips after 3 seconds
                        setTimeout(function() {{
                            if (printTips.parentNode) {{
                                printTips.parentNode.removeChild(printTips);
                            }}
                        }}, 3000);
                    }});
                    
                    window.addEventListener('afterprint', function() {{
                        console.log('✅ Print dialog closed');
                    }});
                    
                    // Smooth scroll to sections (if we add navigation later)
                    function scrollToSection(sectionId) {{
                        const element = document.getElementById(sectionId);
                        if (element) {{
                            element.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                        }}
                    }}
                    
                    // Add loading animation when page loads
                    document.addEventListener('DOMContentLoaded', function() {{
                        // Animate sections on load
                        const sections = document.querySelectorAll('.medical-section');
                        sections.forEach(function(section, index) {{
                            section.style.opacity = '0';
                            section.style.transform = 'translateY(20px)';
                            
                            setTimeout(function() {{
                                section.style.transition = 'all 0.6s ease-out';
                                section.style.opacity = '1';
                                section.style.transform = 'translateY(0)';
                            }}, index * 200);
                        }});
                        
                        // Add hover effects to medical values
                        const medicalValues = document.querySelectorAll('.medical-value');
                        medicalValues.forEach(function(value) {{
                            value.addEventListener('mouseenter', function() {{
                                this.style.transform = 'scale(1.05)';
                                this.style.transition = 'transform 0.2s ease';
                            }});
                            
                            value.addEventListener('mouseleave', function() {{
                                this.style.transform = 'scale(1)';
                            }});
                        }});
                        
                        console.log('📊 Health Report loaded successfully');
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
                        <h3><span class="section-icon">👤</span> Patient Information</h3>
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
                                <span class="info-value">AI Health Assistant (GPT-3.5)</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Pages Analyzed</span>
                                <span class="info-value">{analysis_data.get('pages_analyzed', 'N/A')}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Text Length</span>
                                <span class="info-value">{analysis_data.get('extracted_text_length', 0):,} characters</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Executive Summary Box -->
                    <div class="executive-summary" style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border: 2px solid #bbf7d0; padding: 25px; border-radius: 12px; margin: 25px 0;">
                        <h3 style="color: #059669; margin: 0 0 15px 0; display: flex; align-items: center; gap: 8px;">
                            <span style="font-size: 20px;">📋</span> Report Overview
                        </h3>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; font-size: 13px;">
                            <div><strong>Analysis Scope:</strong> Comprehensive health assessment</div>
                            <div><strong>Data Source:</strong> Medical report PDF</div>
                            <div><strong>Processing:</strong> AI-powered analysis</div>
                            <div><strong>Recommendations:</strong> Lifestyle, dietary, medical</div>
                        </div>
                    </div>
                    
                    <div class="analysis-section">
                        <div class="section-header" style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); padding: 20px 30px; border-bottom: 2px solid #0ea5e9; border-radius: 12px 12px 0 0; margin-bottom: 0;">
                            <h2 style="margin: 0; font-size: 20px; font-weight: 700; color: #0ea5e9; display: flex; align-items: center; gap: 12px;">
                                <span class="section-icon">📊</span> Health Analysis & Recommendations
                            </h2>
                        </div>
                        <div style="background: white; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); border: 1px solid #e2e8f0; border-top: none;">
                            {analysis_text}
                        </div>
                    </div>
                    
                    <div class="disclaimer">
                        <h3>⚠️ IMPORTANT MEDICAL DISCLAIMER</h3>
                        <div style="background: rgba(255,255,255,0.8); padding: 20px; border-radius: 8px; margin: 15px 0;">
                            <p><strong>🤖 AI-Generated Analysis:</strong> This report is generated by artificial intelligence (GPT-3.5-turbo) and is for <strong>informational purposes only</strong>.</p>
                            
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 20px 0;">
                                <div style="background: #fef2f2; padding: 15px; border-radius: 6px; border-left: 4px solid #dc2626;">
                                    <strong style="color: #dc2626;">❌ NOT a Substitute</strong><br>
                                    <small>This does NOT replace professional medical advice, diagnosis, or treatment.</small>
                                </div>
                                <div style="background: #fef3c7; padding: 15px; border-radius: 6px; border-left: 4px solid #d97706;">
                                    <strong style="color: #d97706;">🏥 Consult Professionals</strong><br>
                                    <small>Always seek advice from qualified healthcare professionals.</small>
                                </div>
                                <div style="background: #fecaca; padding: 15px; border-radius: 6px; border-left: 4px solid #dc2626;">
                                    <strong style="color: #dc2626;">🚨 Emergencies</strong><br>
                                    <small>For medical emergencies, contact emergency services immediately.</small>
                                </div>
                                <div style="background: #dbeafe; padding: 15px; border-radius: 6px; border-left: 4px solid #3b82f6;">
                                    <strong style="color: #3b82f6;">🔍 Limitations</strong><br>
                                    <small>AI may not identify all health conditions or risks.</small>
                                </div>
                            </div>
                            
                            <p style="text-align: center; margin-top: 20px; font-size: 12px; color: #7f1d1d;">
                                <strong>Regular consultation with healthcare providers is recommended for comprehensive health management.</strong>
                            </p>
                        </div>
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
        """Enhanced format analysis text for professional medical report HTML presentation"""
        try:
            # Define section mapping with icons and CSS classes
            section_config = {
                'SUMMARY': {'icon': '📋', 'class': 'summary', 'title': 'Executive Summary'},
                'KEY FINDINGS': {'icon': '🔍', 'class': 'findings', 'title': 'Key Findings'},
                'HEALTH STATUS': {'icon': '💓', 'class': 'health-status', 'title': 'Health Status Assessment'},
                'LIFESTYLE RECOMMENDATIONS': {'icon': '🏃', 'class': 'lifestyle', 'title': 'Lifestyle Recommendations'},
                'DIETARY SUGGESTIONS': {'icon': '🥗', 'class': 'dietary', 'title': 'Dietary Suggestions'},
                'EXERCISE RECOMMENDATIONS': {'icon': '💪', 'class': 'exercise', 'title': 'Exercise Recommendations'},
                'FOLLOW-UP ACTIONS': {'icon': '🏥', 'class': 'follow-up', 'title': 'Follow-up Actions'},
                'PREVENTIVE MEASURES': {'icon': '🛡️', 'class': 'preventive', 'title': 'Preventive Measures'}
            }
            
            lines = analysis_text.split('\n')
            formatted_sections = []
            current_section = None
            current_content = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for section headers
                section_found = None
                for key, config in section_config.items():
                    if key in line.upper() or any(word in line.upper() for word in key.split()):
                        section_found = key
                        break
                
                # Check for numbered sections (1., 2., etc.)
                numbered_match = re.match(r'^(\d+\.)\s*(.+)', line)
                if numbered_match:
                    number, title = numbered_match.groups()
                    section_found = title.upper().strip()
                
                if section_found:
                    # Save previous section
                    if current_section and current_content:
                        formatted_sections.append(self._create_section_html(current_section, current_content, section_config))
                    
                    # Start new section
                    current_section = section_found
                    current_content = []
                else:
                    # Add content to current section
                    if line:
                        current_content.append(line)
            
            # Add final section
            if current_section and current_content:
                formatted_sections.append(self._create_section_html(current_section, current_content, section_config))
            
            # If no sections found, create a general analysis section
            if not formatted_sections:
                tt = analysis_text.split('\n')
                return f"""
                <div class="medical-section general">
                    <div class="section-header">
                        <h3><span class="section-icon">📊</span> Health Analysis</h3>
                    </div>
                    <div class="section-content">
                        {self._format_content_to_html(tt)}
                    </div>
                </div>
                """
            
            return ''.join(formatted_sections)
            
        except Exception as e:
            # Enhanced fallback formatting
            paragraphs = []
            for para in analysis_text.split('\n\n'):
                if para.strip():
                    formatted_para = para.replace('\n', '<br>')
                    paragraphs.append(f"<p>{formatted_para}</p>")
            
            return f"""
            <div class="medical-section general">
                <div class="section-header">
                    <h3><span class="section-icon">📊</span> Health Analysis</h3>
                </div>
                <div class="section-content">
                    {''.join(paragraphs)}
                </div>
            </div>
            """
    
    def _create_section_html(self, section_key: str, content_lines: list, section_config: dict) -> str:
        """Create professional HTML section with proper styling"""
        # Get section configuration
        config = section_config.get(section_key, {
            'icon': '📄', 
            'class': 'general',
            'title': section_key.title()
        })
        
        # Format content
        formatted_content = self._format_content_to_html(content_lines)
        
        return f"""
        <div class="medical-section {config['class']}">
            <div class="section-header">
                <h3><span class="section-icon">{config['icon']}</span> {config['title']}</h3>
            </div>
            <div class="section-content">
                {formatted_content}
            </div>
        </div>
        """
    
    def _format_content_to_html(self, content_lines: list) -> str:
        """Format content lines into proper HTML with lists, emphasis, etc."""
        html_content = []
        current_list = []
        in_list = False
        
        for line in content_lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for bullet points
            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                if not in_list:
                    in_list = True
                    current_list = []
                
                # Clean up bullet point
                clean_line = line[1:].strip()
                # Highlight important values and ranges
                clean_line = self._highlight_medical_values(clean_line)
                current_list.append(f"<li>{clean_line}</li>")
            
            else:
                # Close current list if we were in one
                if in_list:
                    html_content.append(f"<ul class='medical-list'>{''.join(current_list)}</ul>")
                    current_list = []
                    in_list = False
                
                # Format regular paragraph
                formatted_line = self._highlight_medical_values(line)
                
                # Check if it's a sub-heading
                if line.isupper() or line.endswith(':'):
                    html_content.append(f"<h4 class='sub-heading'>{formatted_line}</h4>")
                else:
                    html_content.append(f"<p>{formatted_line}</p>")
        
        # Close any remaining list
        if in_list and current_list:
            html_content.append(f"<ul class='medical-list'>{''.join(current_list)}</ul>")
        
        return ''.join(html_content)
    
    def _highlight_medical_values(self, text: str) -> str:
        """Highlight medical values, ranges, and important terms"""
        # Highlight numerical values and ranges
        text = re.sub(r'(\d+(?:\.\d+)?(?:\s*[-–]\s*\d+(?:\.\d+)?)?(?:\s*(?:mg|g|kg|lb|cm|mm|%|bpm|mmHg|mg/dL|g/dL|mL|L|units?|IU)\b)?)', 
                     r'<span class="medical-value">\1</span>', text)
        
        # Highlight important medical terms
        important_terms = [
            'HIGH', 'LOW', 'NORMAL', 'ABNORMAL', 'CRITICAL', 'URGENT', 'IMMEDIATE',
            'ELEVATED', 'DECREASED', 'BORDERLINE', 'OPTIMAL', 'GOOD', 'POOR',
            'RECOMMENDED', 'AVOID', 'INCREASE', 'DECREASE', 'MAINTAIN', 'MONITOR'
        ]
        
        for term in important_terms:
            text = re.sub(f'\\b{term}\\b', f'<span class="medical-term {term.lower()}">{term}</span>', text, flags=re.IGNORECASE)
        
        # Bold important phrases
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        
        return text
    


def main():
    analyzer = HealthCheckupAnalyzer()
    
    # Header
    st.markdown('<div class="main-header">🏥 Health Checkup Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered Health Report Analysis with Personalized Recommendations</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # OpenAI API Key Input
        st.markdown("### 🔐 API Configuration")
        
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.get('openai_api_key', ''),
            placeholder="sk-proj-...",
            help="🔑 Enter your OpenAI API key to enable AI analysis"
        )
        
        # API Key validation and feedback
        if api_key:
            if api_key.startswith('sk-') and len(api_key) > 20:
                st.success("✅ API Key format looks valid")
                st.session_state.openai_api_key = api_key
            else:
                st.error("❌ Invalid API key format. Should start with 'sk-'")
                st.session_state.openai_api_key = ""
        else:
            st.session_state.openai_api_key = ""
            
        # API Key Instructions
        if not api_key:
            st.info("""
            **🚀 Get Your Free OpenAI API Key:**
            1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
            2. Sign up or log in to your account
            3. Click "Create new secret key"
            4. Copy and paste the key above
            
            **💰 Cost:** ~$0.01-0.05 per health report analysis
            """)
        
        # Security notice
        if api_key:
            st.caption("🔒 Your API key is stored securely in this session only")
        
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
        - 📄 Upload PDF health reports
        - 🔤 **pdfplumber extraction**: Superior layout preservation
        - 📊 **Automatic table detection** and extraction
        - 🤖 GPT-3.5-turbo analysis
        - 🌐 Multi-language support  
        - 📋 Multi-page text analysis
        - 💡 Detailed recommendations
        - 📄 Beautiful HTML reports
        - 🖨️ Print-to-PDF ready
        - 👀 Live preview
        """)
        
        # Extraction method info
        st.info("📊 pdfplumber provides excellent layout preservation and table detection!")
    
    # Main content - Continue without blocking if no API key
    
    # File upload section
    st.header("📤 Upload Health Report PDF")
    
    uploaded_file = st.file_uploader(
        "Choose your health checkup report (PDF only)",
        type=['pdf'],
        help="Upload your health report in PDF format. pdfplumber will extract text and tables from all pages."
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
            st.write("📄 PDF file uploaded successfully")
            st.info("🤖 pdfplumber will extract text and tables from all pages for AI analysis!")
        
        # Extract text from PDF using pdfplumber
        with st.spinner("📄 Extracting text and tables from PDF using pdfplumber..."):
            extracted_text = analyzer.extract_text_from_pdf(uploaded_file)
        
        if extracted_text and extracted_text.strip():
            st.success(f"✅ Successfully extracted text from PDF ({len(extracted_text)} characters)")
            
            # Show extracted text preview
            with st.expander("📝 Preview Extracted Text"):
                st.text_area(
                    "Extracted Content", 
                    extracted_text[:2000] + ("..." if len(extracted_text) > 2000 else ""), 
                    height=300, 
                    disabled=True
                )
                if len(extracted_text) > 2000:
                    st.info(f"Showing first 2000 characters. Total extracted: {len(extracted_text)} characters")
            
            # Analyze button
            if st.button("🔬 Analyze Health Report", type="primary"):
                if not st.session_state.openai_api_key:
                    st.error("Please enter your OpenAI API key in the sidebar.")
                else:
                    with st.spinner("🤖 Analyzing your health report with AI..."):
                        analysis_result = analyzer.analyze_health_report(extracted_text, language)
                    
                    if analysis_result:
                        st.success(f"✅ Analysis completed successfully! Analyzed {analysis_result['pages_analyzed']} pages ({analysis_result['extracted_text_length']} characters).")
                        
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
                            
                            st.markdown(f"""
                            <div class="success-box">
                                <b>✅ Success!</b><br/>
                                Your health report analysis is ready! 
                                <br><br>
                                <b>📥 Download HTML:</b> Save the file and open in your browser<br/>
                                <b>🖨️ Print to PDF:</b> Open the HTML file → Press Ctrl+P → Save as PDF<br/>
                                <b>👀 Preview:</b> See how the report looks before downloading<br/>
                                <b>📊 Analysis:</b> {analysis_result['pages_analyzed']} pages analyzed with GPT-3.5-turbo
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Show preview if requested
                            if st.session_state.get('show_preview', False):
                                st.subheader("📄 Report Preview")
                                st.markdown("*This is how your report will look. Use the 'Download HTML Report' button above to save it.*")
                                
                                # Display the HTML in an iframe-like container
                                st.components.v1.html(html_content, height=800, scrolling=True)
        else:
            st.error("❌ Could not extract text from PDF. The PDF might be image-based, password-protected, or corrupted. Please ensure the PDF contains extractable text.")
    
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
