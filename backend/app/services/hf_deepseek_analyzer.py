from PyPDF2 import PdfReader
import io
import logging
import os
import re
import json
import hashlib
from huggingface_hub import InferenceClient

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DeepSeekResumeAnalyzer:
    def __init__(self):
        self.client = None
        self.api_key = os.environ.get("HF_API_KEY") or os.environ.get("ACCESS_TOKEN", "")
        # Define important categories for resume evaluation
        self.keyword_categories = {
            'technical_skills': ['python', 'java', 'javascript', 'typescript', 'c++', 'ruby', 'php', 'sql', 'nosql', 
                             'react', 'angular', 'vue', 'node', 'django', 'flask', 'spring', 'aws', 'azure', 
                             'gcp', 'docker', 'kubernetes', 'terraform', 'git', 'machine learning', 'ai', 
                             'data science', 'analytics', 'tableau', 'powerbi', 'excel'],
            'soft_skills': ['communication', 'teamwork', 'leadership', 'problem solving', 'critical thinking',
                         'time management', 'adaptability', 'flexibility', 'creativity', 'collaboration',
                         'detail oriented', 'organization', 'project management', 'agile', 'scrum'],
            'education': ['degree', 'bachelor', 'master', 'phd', 'mba', 'certification', 'diploma', 'university',
                       'college', 'school', 'graduate', 'gpa', 'honors', 'thesis', 'dissertation'],
            'experience': ['experience', 'year', 'lead', 'manage', 'develop', 'implement', 'create', 'design',
                        'analyze', 'coordinate', 'improve', 'increase', 'decrease', 'achieve', 'responsible',
                        'team', 'client', 'project', 'product', 'application', 'system', 'solution']
        }

    def initialize_client(self):
        """Initialize the HuggingFace client with API key"""
        if not self.client and self.api_key:
            try:
                logger.info("Initializing HuggingFace client...")
                self.client = InferenceClient(
                    provider="novita",
                    api_key=self.api_key
                )
                logger.info("HuggingFace client initialized successfully")
                return True
            except Exception as e:
                logger.error(f"Failed to initialize HuggingFace client: {str(e)}")
                return False
        elif not self.api_key:
            logger.warning("No HuggingFace API key provided. Set HF_API_KEY environment variable.")
            return False
        return True if self.client else False

    def extract_text(self, file):
        """Extract text from PDF/DOCX"""
        try:
            logger.info(f"Extracting text from: {file.filename}")
            if file.filename.endswith('.pdf'):
                try:
                    file_bytes = io.BytesIO(file.read())
                    reader = PdfReader(file_bytes)
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
                try:
                    file.seek(0)
                    text = file.read().decode("utf-8", errors="replace")
                except Exception as e:
                    logger.error(f"Text extraction error: {str(e)}")
                    return f"Error extracting plain text: {str(e)}"

            text = re.sub(r'\s+', ' ', text).strip()
            truncated_text = text[:3000]
            logger.info(f"Extracted {len(text)} chars, truncated to {len(truncated_text)}")
            return truncated_text

        except Exception as e:
            logger.error(f"Unexpected error in extract_text: {str(e)}")
            return f"Error processing file: {str(e)}"

    def analyze_resume(self, text, job_desc=None):
        """Generate AI-powered suggestions using HuggingFace API"""
        try:
            client_ready = self.initialize_client()
            if not client_ready:
                logger.info("Using fallback analysis due to missing API client")
                return self._fallback_analysis(text, job_desc)

            system_prompt = "You are an expert resume reviewer. Analyze the resume text and provide specific, actionable improvements."

            user_prompt = f"Resume text:\n\n{text}"
            if job_desc:
                user_prompt += f"\n\nTarget Job Description:\n\n{job_desc[:1000]}"
            user_prompt += "\n\nProvide 3-5 specific improvements for this resume. For each improvement, explain why it matters and how to implement it. Focus on content, structure, and relevance to the job (if provided)."

            try:
                logger.info("Sending request to HuggingFace API")
                completion = self.client.chat.completions.create(
                    model="deepseek-ai/DeepSeek-Prover-V2-671B",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                )
                response = completion.choices[0].message.content
                logger.info("Received response from HuggingFace API")
                return response
            except Exception as e:
                logger.error(f"API call failed: {str(e)}")
                return f"Error calling AI service: {str(e)}\n\n" + self._fallback_analysis(text, job_desc)

        except Exception as e:
            logger.error(f"Error analyzing resume: {str(e)}")
            return f"Error analyzing resume: {str(e)}"

    def describe_and_rate_resume(self, text, job_desc=None):
        """Generate structured summary, name, skills, and match rating for a resume"""
        try:
            client_ready = self.initialize_client()
            if not client_ready:
                logger.info("Using fallback description and rating due to missing API client")
                return json.loads(self._fallback_description_and_rating(text, job_desc))

            # Prompts
            system_prompt = (
                "You are a professional resume evaluator. "
                "You must respond ONLY in strict JSON format with these keys: "
                "name, key_strengths, match_rating (out of 10), and summary. "
                "Do NOT include any markdown, extra text, or formatting around the JSON."
            )

            user_prompt = (
                f"Resume text:\n\n{text[:3000]}\n\n"
                f"Target Job Description:\n\n{job_desc[:1000] if job_desc else ''}\n\n"
                f"IMPORTANT: Only return valid JSON. No commentary or formatting."
            )

            logger.info("Sending resume structured request to HuggingFace API")
            completion = self.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-Prover-V2-671B",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            response = completion.choices[0].message.content
            logger.debug(f"Raw response from model: {response}")

            try:
                import re
                match = re.search(r'\{.*\}', response, re.DOTALL)
                if match:
                    result = json.loads(match.group())
                else:
                    raise json.JSONDecodeError("Could not find JSON object in response", response, 0)
                logger.info("Parsed structured resume analysis")
                
                # Override the AI model's match_rating with our deterministic calculation
                if job_desc:
                    match_rating = self._calculate_deterministic_match_rating(text, job_desc)
                    result['match_rating'] = match_rating
                    logger.info(f"Override match_rating with deterministic calculation: {match_rating}")
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON from response, falling back: {str(e)}")
                result = json.loads(self._fallback_description_and_rating(text, job_desc))

            result['truncated_text'] = text[:300] + "..." if len(text) > 300 else text
            return result

        except Exception as e:
            logger.error(f"Error describing and rating resume: {str(e)}")
            try:
                return json.loads(self._fallback_description_and_rating(text, job_desc))
            except Exception as fallback_error:
                logger.critical(f"Fallback also failed: {fallback_error}")
                return {
                    "name": "Unknown",
                    "key_strengths": [],
                    "match_rating": 0,
                    "summary": "Unable to process resume at this time.",
                    "truncated_text": text[:300] + "..." if len(text) > 300 else text
                }

    def _calculate_deterministic_match_rating(self, resume_text, job_desc):
        """
        Calculate a deterministic match rating based on weighted keyword matching
        that will return the same score for the same inputs every time.
        """
        resume_text = resume_text.lower()
        job_desc = job_desc.lower()
        
        # Create a hash of the inputs to ensure consistency across runs
        combined_input = resume_text + job_desc
        input_hash = int(hashlib.md5(combined_input.encode()).hexdigest(), 16)
        random_seed = input_hash % 1000 / 1000  # A consistent small random factor (0-1)
        
        # Extract key job requirement phrases
        job_req_patterns = [
            r'required skills?:?(.+?)(?:preferred skills|experience required|responsibilities|$)',
            r'qualifications?:?(.+?)(?:responsibilities|requirements|$)',
            r'experience:?(.+?)(?:education|skills|$)'
        ]
        
        job_key_phrases = []
        for pattern in job_req_patterns:
            matches = re.search(pattern, job_desc, re.IGNORECASE | re.DOTALL)
            if matches:
                section = matches.group(1)
                # Extract bullet point items or key phrases
                items = re.findall(r'(?:•|\*|\-|\d+\.)\s*([^•\*\-\d\.]+?)(?=(?:•|\*|\-|\d+\.)|$)', 
                                  section, re.DOTALL)
                if items:
                    job_key_phrases.extend([item.strip() for item in items])
        
        # If no structured requirements were found, create bigrams from job description
        if not job_key_phrases:
            words = re.findall(r'\b\w+\b', job_desc)
            job_key_phrases = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
            # Filter to only meaningful bigrams
            job_key_phrases = [phrase for phrase in job_key_phrases 
                              if not all(word in ['and', 'the', 'to', 'of', 'in', 'for', 'with'] 
                                        for word in phrase.split())]
            job_key_phrases = job_key_phrases[:20]  # Limit to 20 phrases
        
        # Calculate category-based matches
        category_scores = {}
        for category, keywords in self.keyword_categories.items():
            job_category_count = sum(1 for keyword in keywords if keyword in job_desc)
            resume_category_count = sum(1 for keyword in keywords if keyword in resume_text)
            
            if job_category_count > 0:
                category_scores[category] = min(1.0, resume_category_count / job_category_count)
            else:
                category_scores[category] = 0.5  # Neutral score if category not mentioned in job
        
        # Calculate phrase-based match
        phrase_matches = 0
        for phrase in job_key_phrases:
            if len(phrase) > 3 and phrase in resume_text:  # Only count meaningful phrases
                phrase_matches += 1
        
        phrase_score = min(1.0, phrase_matches / max(1, len(job_key_phrases)))
        
        # Weights for different components
        weights = {
            'technical_skills': 0.35,
            'soft_skills': 0.15,
            'education': 0.10,
            'experience': 0.20,
            'phrases': 0.20
        }
        
        # Calculate weighted score
        weighted_score = sum(
            weights[category] * score 
            for category, score in category_scores.items()
        ) + weights['phrases'] * phrase_score
        
        # Add a small random factor based on input hash to differentiate similar resumes
        adjusted_score = weighted_score * 0.95 + random_seed * 0.05
        
        # Convert to 1-10 rating scale with proper rounding
        rating = round(1 + adjusted_score * 9)
        
        logger.info(f"Match rating components - Categories: {category_scores}, Phrases: {phrase_score}, Final: {rating}")
        return rating

    def _fallback_description_and_rating(self, text, job_desc=None):
        """Simple fallback for resume description and rating when API isn't available"""
        name_match = re.search(r'([A-Z][a-z]+ [A-Z][a-z]+)', text[:200])
        name = name_match.group(1) if name_match else "Unknown Candidate"

        has_education = bool(re.search(r'education|university|college|degree|bachelor|master|phd', text.lower()))
        has_experience = bool(re.search(r'experience|work|employment|job|career', text.lower()))
        has_skills = bool(re.search(r'skills|proficiencies|abilities|competencies|qualifications', text.lower()))

        skills_list = re.findall(r'\b(?:Python|Java|JavaScript|SQL|AWS|Machine Learning|Data Analysis|Project Management)\b', text, re.I)
        skills_list = list(set(skills_list))[:5]

        if job_desc:
            # Use the deterministic match rating even in fallback mode
            rating = self._calculate_deterministic_match_rating(text, job_desc)
            rating_explanation = f"Based on keyword and phrase matching between resume and job description"
        else:
            # Calculate a deterministic rating based on resume content alone
            word_count = len(text.split())
            has_contact = bool(re.search(r'email|phone|linkedin|github', text.lower()))
            has_achievements = bool(re.search(r'achieve|accomplish|increase|decrease|improve|develop|lead|manage|create', text.lower()))
            
            base_score = 5  # Start at middle score
            if word_count > 300: base_score += 1
            if has_education: base_score += 1
            if has_experience: base_score += 1 
            if has_skills: base_score += 1
            if has_contact: base_score += 0.5
            if has_achievements: base_score += 0.5
            
            rating = min(10, max(1, round(base_score)))
            rating_explanation = "No specific job description provided for comparison"

        fallback_response = {
            "name": name,
            "summary": f"{name} has a professional profile that " +
                       (f"includes {'education, ' if has_education else ''}"
                        f"{'work experience, ' if has_experience else ''}"
                        f"{'and professional skills' if has_skills else ''})."),
            "match_rating": rating,
            "key_strengths": skills_list,
            "improvement_areas": [
                "Tailor resume to specific job requirements",
                "Add quantifiable achievements",
                "Ensure clear, concise formatting"
            ]
        }

        return json.dumps(fallback_response)

    def _fallback_analysis(self, text, job_desc=None):
        """Simple fallback when API isn't available"""
        word_count = len(text.split())
        suggestions = [
            f"## Resume Analysis\n\nYour resume contains approximately {word_count} words in the analyzed portion.",
            "### Improvement 1: Add Quantifiable Achievements\nConsider adding specific metrics and results to highlight your impact.",
            "### Improvement 2: Tailor Skills Section\nEnsure your skills clearly align with the job requirements."
        ]

        if job_desc:
            rating = self._calculate_deterministic_match_rating(text, job_desc)
            suggestions.append(f"### Improvement 3: Keyword Optimization\nYour resume matches the job description with a rating of {rating}/10.")
            
            # Find key terms in job description that aren't in the resume
            job_words = set(re.findall(r'\b[A-Za-z][A-Za-z0-9\+\#]+\b', job_desc.lower()))
            resume_words = set(re.findall(r'\b[A-Za-z][A-Za-z0-9\+\#]+\b', text.lower()))
            
            # Analyze common skill terms from job desc that aren't in resume
            common_skills = []
            for category, keywords in self.keyword_categories.items():
                for keyword in keywords:
                    if keyword in job_desc.lower() and keyword not in text.lower():
                        common_skills.append(keyword)
            
            if common_skills:
                suggestions.append(f"### Improvement 4: Add Missing Keywords\nConsider adding these key skills mentioned in the job description: {', '.join(common_skills[:8])}")

        return "\n\n".join(suggestions)

    def set_api_key(self, api_key):
        """Update the API key and reinitialize the client"""
        self.api_key = api_key
        self.client = None
        return self.initialize_client()


# Singleton instance
analyzer = DeepSeekResumeAnalyzer()