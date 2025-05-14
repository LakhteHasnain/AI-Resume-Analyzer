from transformers import AutoTokenizer, AutoModelForCausalLM
from PyPDF2 import PdfReader
import io
import torch
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeepSeekResumeAnalyzer:
    def __init__(self):
        # Initialize model (loads on first call)
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
    def load_model(self):
        """Lazy-load model to conserve memory"""
        if self.model is None:
            try:
                logger.info("Loading DeepSeek-Prover model...")
                
                # Check if model is available locally first
                try:
                    self.tokenizer = AutoTokenizer.from_pretrained(
                        "deepseek-ai/DeepSeek-Prover-V2-671B", 
                        trust_remote_code=True
                    )
                    self.model = AutoModelForCausalLM.from_pretrained(
                        "deepseek-ai/DeepSeek-Prover-V2-671B",
                        torch_dtype=torch.float16,
                        device_map="auto",
                        trust_remote_code=True
                    )
                    logger.info("Model loaded successfully")
                except Exception as e:
                    # If model loading fails, use a fallback approach
                    logger.warning(f"Failed to load DeepSeek model: {str(e)}")
                    logger.warning("Using simple text processing instead")
                    self.tokenizer = "FALLBACK"
                    self.model = "FALLBACK"
            except Exception as e:
                logger.error(f"Critical error loading model: {str(e)}")
                raise

    def extract_text(self, file):
        """Extract text from PDF/DOCX"""
        try:
            logger.info(f"Extracting text from: {file.filename}")
            
            if file.filename.endswith('.pdf'):
                try:
                    # Create a BytesIO object from the file's binary data
                    file_bytes = io.BytesIO(file.read())
                    
                    # Create PdfReader with BytesIO object
                    reader = PdfReader(file_bytes)
                    
                    # Extract text from pages
                    text = ""
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + " "
                            
                except Exception as e:
                    logger.error(f"PDF extraction error: {str(e)}")
                    return f"Error extracting PDF text: {str(e)}"
                    
            elif file.filename.endswith('.docx'):
                try:
                    # For DOCX files, need to use python-docx library
                    try:
                        from docx import Document
                        doc = Document(io.BytesIO(file.read()))
                        text = " ".join([para.text for para in doc.paragraphs])
                    except ImportError:
                        logger.warning("python-docx not installed, extracting as plain text")
                        text = file.read().decode("utf-8", errors="replace")
                except Exception as e:
                    logger.error(f"DOCX extraction error: {str(e)}")
                    return f"Error extracting DOCX text: {str(e)}"
            else:
                # For plain text files
                try:
                    file.seek(0)  # Make sure we're at the start of the file
                    text = file.read().decode("utf-8", errors="replace")
                except Exception as e:
                    logger.error(f"Text extraction error: {str(e)}")
                    return f"Error extracting plain text: {str(e)}"

            # Truncate for token limits
            truncated = text[:3000]
            logger.info(f"Extracted {len(text)} chars, truncated to {len(truncated)}")
            return truncated
            
        except Exception as e:
            logger.error(f"Unexpected error in extract_text: {str(e)}")
            return f"Error processing file: {str(e)}"

    def analyze_resume(self, text, job_desc=None):
        """Generate AI-powered suggestions"""
        try:
            self.load_model()  # Ensure model is loaded
            
            # If we're in fallback mode, provide a basic analysis
            if self.model == "FALLBACK":
                logger.info("Using fallback analysis")
                return self._fallback_analysis(text, job_desc)
            
            # Otherwise use the actual model
            prompt = f"""
            Analyze this resume and provide 3 specific improvements:
            {text}
            """
            if job_desc:
                prompt += f"\n\nTarget Job Requirements:\n{job_desc[:1000]}"

            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=500,
                    temperature=0.7,
                    do_sample=True
                )
            
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
        except Exception as e:
            logger.error(f"Error analyzing resume: {str(e)}")
            return f"Error analyzing resume: {str(e)}"
            
    def _fallback_analysis(self, text, job_desc=None):
        """Simple fallback when model isn't available"""
        # Count words in resume
        word_count = len(text.split())
        
        suggestions = [
            f"Your resume contains approximately {word_count} words in the analyzed portion.",
            "Consider adding more quantifiable achievements to highlight your impact.",
            "Ensure your skills section aligns with the job requirements."
        ]
        
        if job_desc:
            # Do very basic keyword matching
            job_words = set(job_desc.lower().split())
            resume_words = set(text.lower().split())
            common_words = job_words.intersection(resume_words)
            
            keyword_match = len(common_words) / len(job_words) if job_words else 0
            suggestions.append(f"Your resume matches approximately {keyword_match:.0%} of keywords from the job description.")
        
        return "\n\n".join(suggestions)

# Create singleton instance
analyzer = DeepSeekResumeAnalyzer()