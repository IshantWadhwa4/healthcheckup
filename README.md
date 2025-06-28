# 🏥 Health Checkup Analyzer

An AI-powered Streamlit application that analyzes health checkup reports and provides personalized recommendations in multiple languages.

## ✨ Features

- **📤 File Upload**: Support for PDF and image files (PNG, JPG, JPEG)
- **🔍 OCR Text Extraction**: Automatic text extraction from health reports
- **🤖 AI Analysis**: Advanced health report analysis using OpenAI GPT
- **🌐 Multi-language Support**: English, Hindi, and Hinglish output
- **📊 Comprehensive Reports**: Detailed analysis with lifestyle recommendations
- **📋 PDF Generation**: Downloadable PDF reports with professional formatting
- **🎨 Modern UI**: Beautiful and responsive user interface

## 🚀 Quick Start

### Prerequisites

Before running the application, ensure you have:

1. **Python 3.8+** installed
2. **Tesseract OCR** installed on your system
3. **OpenAI API Key** (get it from [OpenAI Platform](https://platform.openai.com/api-keys))

### Installation

1. **Clone or download the project**
   ```bash
   cd health_check
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Tesseract OCR**
   
   **On macOS:**
   ```bash
   brew install tesseract
   ```
   
   **On Ubuntu/Debian:**
   ```bash
   sudo apt-get install tesseract-ocr
   sudo apt-get install libtesseract-dev
   ```
   
   **On Windows:**
   - Download Tesseract from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - Add Tesseract to your PATH environment variable

4. **Run the application**
   ```bash
   streamlit run healthcheckapp.py
   ```

5. **Open your browser** and navigate to `http://localhost:8501`

## 📋 Usage Guide

### Step 1: Configuration
1. **Enter OpenAI API Key**: In the sidebar, enter your OpenAI API key
2. **Select Language**: Choose from English, Hindi, or Hinglish
3. **Patient Name**: Optionally enter the patient's name for the PDF report

### Step 2: Upload Health Report
1. **Choose File**: Upload your health checkup report (PDF or image)
2. **Preview**: View the uploaded file and extracted text
3. **Analyze**: Click "Analyze Health Report" to get AI-powered insights

### Step 3: Get Results
1. **View Analysis**: Read the comprehensive health analysis
2. **Download PDF**: Get a professionally formatted PDF report
3. **Follow Recommendations**: Implement the suggested lifestyle changes

## 🔧 System Requirements

- **Python**: 3.8 or higher
- **Memory**: At least 2GB RAM
- **Storage**: 500MB free space
- **Internet**: Required for OpenAI API calls

## 📊 Analysis Features

The AI provides detailed analysis including:

- **📈 Summary**: Comprehensive overview of test results
- **🔍 Key Findings**: Important abnormal values and concerns
- **💚 Health Status**: Overall health assessment
- **🏃‍♂️ Lifestyle Recommendations**: Specific lifestyle changes
- **🥗 Dietary Suggestions**: Nutritional guidance
- **💪 Exercise Recommendations**: Physical activity plans
- **🩺 Follow-up Actions**: When to consult doctors
- **🛡️ Preventive Measures**: Health prevention strategies

## 🌐 Language Support

- **English**: Professional medical terminology
- **Hindi**: Complete analysis in Hindi (हिंदी में विश्लेषण)
- **Hinglish**: Hindi-English mix for easy understanding

## 🔒 Security & Privacy

- **API Key Security**: Your OpenAI API key is stored locally in session
- **No Data Storage**: Uploaded files are processed temporarily
- **Privacy First**: No health data is permanently stored

## ⚠️ Important Disclaimers

1. **Medical Advice**: This tool is for informational purposes only
2. **Professional Consultation**: Always consult healthcare professionals
3. **AI Limitations**: AI analysis may not catch all medical conditions
4. **Emergency Situations**: Seek immediate medical attention for emergencies

## 🛠️ Troubleshooting

### Common Issues

**1. Tesseract not found**
```
Error: Tesseract is not installed or not in your PATH
```
**Solution**: Install Tesseract OCR and add it to your system PATH

**2. OpenAI API Error**
```
Error: Invalid API key
```
**Solution**: Verify your OpenAI API key is correct and has available credits

**3. PDF Processing Error**
```
Error extracting text from PDF
```
**Solution**: Ensure the PDF is not password-protected and contains readable text

**4. Poor OCR Results**
```
No text extracted from image
```
**Solution**: Use high-quality, clear images with good contrast

### Performance Tips

- **Image Quality**: Use high-resolution, clear images for better OCR
- **PDF Format**: Text-based PDFs work better than scanned images
- **File Size**: Keep files under 10MB for faster processing
- **Internet Speed**: Stable internet connection for OpenAI API calls

## 📝 File Format Support

### Supported Formats
- **Images**: PNG, JPG, JPEG
- **Documents**: PDF

### Best Practices
- **Resolution**: At least 300 DPI for images
- **Clarity**: Ensure text is clearly visible
- **Orientation**: Keep documents properly oriented
- **Language**: Works best with English and Hindi text

## 🔄 Updates & Maintenance

To update the application:

1. **Update dependencies**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Check for updates**: Regularly update OpenAI and Streamlit packages

3. **Backup**: Keep backups of important analysis results

## 📞 Support

For issues or questions:

1. **Check the troubleshooting section** above
2. **Verify all dependencies** are properly installed
3. **Test with a simple, clear health report** first
4. **Ensure stable internet connection** for API calls

## 🤝 Contributing

To contribute to this project:

1. **Fork the repository**
2. **Create a feature branch**
3. **Add your improvements**
4. **Test thoroughly**
5. **Submit a pull request**

## 📄 License

This project is for educational and informational purposes. Please ensure compliance with medical regulations in your jurisdiction.

---

**⚠️ Medical Disclaimer**: This application is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of qualified health providers with any questions regarding medical conditions. 