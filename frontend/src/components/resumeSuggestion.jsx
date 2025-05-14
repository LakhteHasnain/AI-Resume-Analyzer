import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import './rateResume.css'; // Reusing the same CSS file

const ResumeAnalyzer = ({ onBack }) => {
  const [file, setFile] = useState(null);
  const [jobDesc, setJobDesc] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [savedApiKey, setSavedApiKey] = useState('');
  const [showApiForm, setShowApiForm] = useState(false);
  const [error, setError] = useState('');

  // Load saved API key from localStorage on component mount
  useEffect(() => {
    const savedKey = localStorage.getItem('hf_api_key');
    if (savedKey) {
      setSavedApiKey(savedKey);
      setApiKey(savedKey);
    }
  }, []);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setResults(null);

    if (!file) {
      setError('Please upload a resume file');
      setIsLoading(false);
      return;
    }

    const formData = new FormData();
    formData.append('resume', file);
    if (jobDesc) formData.append('job_desc', jobDesc);
    if (apiKey) formData.append('api_key', apiKey);

    try {
      const res = await axios.post('http://localhost:5000/analyze', formData);
      setResults(res.data);
      // Save API key to localStorage if it was used successfully
      if (apiKey) {
        localStorage.setItem('hf_api_key', apiKey);
        setSavedApiKey(apiKey);
      }
    } catch (err) {
      setError(err.response?.data?.error || "Analysis failed");
    } finally {
      setIsLoading(false);
    }
  };

  const handleApiKeySubmit = async (e) => {
    e.preventDefault();
    if (!apiKey) {
      setError('Please enter an API key');
      return;
    }

    try {
      await axios.post('http://localhost:5000/set-api-key', { api_key: apiKey });
      localStorage.setItem('hf_api_key', apiKey);
      setSavedApiKey(apiKey);
      setShowApiForm(false);
    } catch (err) {
      setError(err.response?.data?.error || "Failed to update API key");
    }
  };

  return (
    <div className="resume-analyzer-container">
      <div className="analyzer-header">
       
        <h1 className="app-title">Resume Analyzer</h1>
      </div>

      <div className="content-wrapper">
        {/* API Key Management */}
        <div className="form-card" style={{ marginBottom: '20px' }}>
          <div className="api-key-section">
            {savedApiKey ? (
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>✅ Hugging Face API key is set</span>
                <button 
                  onClick={() => setShowApiForm(!showApiForm)}
                  className="view-details-button"
                >
                  Change API Key
                </button>
              </div>
            ) : (
              <div>
                <p style={{ color: '#6b7280', marginBottom: '12px' }}>⚠️ No Hugging Face API key set. Analysis will use the fallback method.</p>
                <button 
                  onClick={() => setShowApiForm(!showApiForm)}
                  className="submit-button"
                  style={{ marginTop: 0 }}
                >
                  Set API Key
                </button>
              </div>
            )}
            
            {showApiForm && (
              <form onSubmit={handleApiKeySubmit} className="analyzer-form" style={{ marginTop: '16px' }}>
                <div className="form-group">
                  <label htmlFor="api-key" className="form-label">
                    Hugging Face API Key
                  </label>
                  <input
                    id="api-key"
                    type="password" 
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="Enter Hugging Face API key"
                    className="api-key-input"
                  />
                  <div className="form-hint">API key will be saved in your browser for future use.</div>
                </div>
                <button 
                  type="submit"
                  className="submit-button"
                >
                  Save API Key
                </button>
              </form>
            )}
          </div>
        </div>

        <div className="form-card">
          <form onSubmit={handleSubmit} className="analyzer-form">
            <div className="form-group">
              <label htmlFor="resume-file" className="form-label">
                Upload Resume <span className="required-mark">*</span>
              </label>
              <div className="file-input-container">
                <div className="file-input-wrapper">
                  <input
                    id="resume-file"
                    type="file"
                    onChange={handleFileChange}
                    className="file-input"
                    accept=".pdf,.docx"
                    required
                  />
                  <div className="file-input-placeholder">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                      <polyline points="14 2 14 8 20 8" />
                      <path d="M12 18v-6" />
                      <path d="M9 15h6" />
                    </svg>
                    <span>Drop resume here or click to browse</span>
                  </div>
                </div>
                {file && (
                  <div className="file-count">
                    {file.name}
                  </div>
                )}
              </div>
              <div className="form-hint">PDF or DOCX formats accepted</div>
            </div>

            <div className="form-group">
              <label htmlFor="job-description" className="form-label">
                Job Description (Optional)
              </label>
              <textarea
                id="job-description"
                value={jobDesc}
                onChange={(e) => setJobDesc(e.target.value)}
                className="job-description-input"
                placeholder="Paste the job description here to get targeted resume improvement suggestions"
              />
              <div className="form-hint">Adding a job description improves analysis accuracy</div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="submit-button"
            >
              {isLoading ? (
                <>
                  <div className="spinner"></div>
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M2 12h20M16 6l6 6-6 6"/>
                  </svg>
                  Analyze Resume
                </>
              )}
            </button>
          </form>
        </div>

        {error && (
          <div className="error-message">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12" y2="16" />
            </svg>
            <p>{error}</p>
          </div>
        )}

        {results?.data?.suggestions && (
          <div className="results-container">
            <div className="results-header">
              <h2>Analysis Results</h2>
              {jobDesc && (
                <div className="job-description-display">
                  <div className="job-label">
                    <span className="job-label-text">Job Description:</span>
                    <span className="job-title">{jobDesc.substring(0, 150)}...</span>
                  </div>
                </div>
              )}
            </div>
            
            {results.data.skills && results.data.skills.length > 0 && (
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ fontSize: '1.2rem', fontWeight: '600', marginBottom: '0.75rem' }}>Detected Skills</h3>
                <div className="skills-container">
                  {results.data.skills.map((skill, index) => (
                    <span key={index} className="skill-tag">{skill}</span>
                  ))}
                </div>
              </div>
            )}
            
            <div className="details-panel">
              <h4>Improvement Suggestions</h4>
              <div className="analysis-text markdown-content">
                <ReactMarkdown>
                  {results.data.suggestions}
                </ReactMarkdown>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResumeAnalyzer;