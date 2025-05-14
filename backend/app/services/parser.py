import re

class ResumeParser:
    """
    A simple parser to extract basic information from resume text
    """
    
    @staticmethod
    def parse_resume(text):
        """
        Extract structured data from resume text
        """
        if not text:
            return {"error": "No text to parse"}
            
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        # Extract phone numbers (simple pattern)
        phone_pattern = r'(\+\d{1,3}[-\.\s]??)?\(?\d{3}\)?[-\.\s]?\d{3}[-\.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        
        # Extract education (simple approach)
        education_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college', 'school']
        education_lines = []
        
        for line in text.split('\n'):
            if any(keyword in line.lower() for keyword in education_keywords):
                education_lines.append(line.strip())
        
        # Extract skills (very basic)
        common_skills = [
            'python', 'java', 'javascript', 'html', 'css', 'react', 'angular',
            'vue', 'node', 'express', 'flask', 'django', 'sql', 'nosql', 'mongodb',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'agile', 'scrum',
            'machine learning', 'data science', 'ai', 'deep learning', 'nlp',
            'leadership', 'management', 'communication', 'teamwork', 'problem solving'
        ]
        
        skills = []
        for skill in common_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text.lower()):
                skills.append(skill)
        
        # Create structured data
        parsed_data = {
            "emails": emails,
            "phone_numbers": phones,
            "education": education_lines[:3],  # Limit to top 3
            "skills": skills,
            "word_count": len(text.split())
        }
        
        return parsed_data