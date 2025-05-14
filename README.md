# AI Resume Analyzer

A powerful resume analysis tool leveraging the Deep Seek model with RAG (Retrieval-Augmented Generation) techniques to help both job seekers and HR professionals optimize the recruitment process.

## 🚀 Features

### For Job Seekers

- **Resume Analysis**: Upload your CV/resume and receive detailed feedback
- **Improvement Suggestions**: Get actionable tips to enhance your resume
- **Keyword Optimization**: Identify missing keywords and skills based on industry standards
- **Format Checking**: Ensure your resume follows best practices in structure and presentation

### For HR Professionals

- **Bulk CV Processing**: Upload multiple resumes simultaneously
- **Job Description Matching**: Enter job requirements and get ranked candidates
- **Candidate Summaries**: Generate concise summaries of each applicant
- **Skills Gap Analysis**: Identify the strengths and weaknesses of each candidate
- **Automated Ranking**: Sort candidates based on job description relevance

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: React.js
- **Styling**: Tailwind CSS
- **AI Model**: Deep Seek with RAG implementation
- **Database**: MongoDB (for storing analysis results)
- **Authentication**: JWT-based auth system

## 📋 Prerequisites

- Python 3.8+
- Node.js 14+
- MongoDB
- Deep Seek API credentials

## 🔧 Installation

### Clone the repository

```bash
git clone [https://github.com/yourusername/ai-resume-analyzer.git](https://github.com/LakhteHasnain/AI-Resume-Analyzer.git)
cd ai-resume-analyzer
```

### Backend Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your Deep Seek API credentials and MongoDB connection string

# Run the Flask server
flask run --debug
```

### Frontend Setup

```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm run dev
```

## 🚀 Usage

### Job Seeker Module

1. Navigate to the "Job Seeker" section
2. Upload your resume/CV (PDF, DOCX formats supported)
3. Review the analysis results:
   - Overall score
   - Sections that need improvement
   - Keyword suggestions
   - Format recommendations
4. Download the improved version or suggestions report

### HR Module

1. Navigate to the "HR Professional" section
2. Enter job description or select from templates
3. Upload multiple resumes (batch processing available)
4. View analysis results:
   - Ranked candidates based on job match
   - Individual candidate summaries
   - Side-by-side comparison of top candidates
   - Skills gap visualization

## 📊 API Reference

The backend exposes the following main endpoints:

```
POST /analyze - Analyze a single resume
POST /analyze-batch - Analyze multiple resumes against a job description

```



## 🧠 How It Works

### RAG Implementation

The AI Resume Analyzer uses Retrieval-Augmented Generation (RAG) techniques to enhance the Deep Seek model's capabilities:

1. **Document Processing**: Resumes are parsed and converted into embeddings
2. **Knowledge Base**: Industry-specific requirements and best practices are stored in a vector database
3. **Retrieval**: Relevant information is retrieved based on the resume content or job description
4. **Generation**: The Deep Seek model generates insights by combining retrieved information with its trained knowledge

### Resume Analysis Flow

1. Document parsing and text extraction
2. Section identification and classification
3. Skills and experience extraction
4. Comparison against industry standards
5. Generation of improvement suggestions

### HR Matching Flow

1. Job description parsing and requirement extraction
2. Resume batch processing
3. Semantic matching between requirements and qualifications
4. Candidate ranking and summary generation

### Thankyouu
