import React, { useState, useEffect } from 'react';
import './rateResume.css';

const ResumeDescriptionAndRating = ({ onBack }) => {
  const [files, setFiles] = useState([]);
  const [jobDescription, setJobDescription] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [expandedRow, setExpandedRow] = useState(null);
  const [savedApiKey, setSavedApiKey] = useState('');
  const [showApiForm, setShowApiForm] = useState(false);

  // Load saved API key from localStorage on component mount
  useEffect(() => {
    const savedKey = localStorage.getItem('hf_api_key');
    if (savedKey) {
      setSavedApiKey(savedKey);
      setApiKey(savedKey);
    }
  }, []);

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setResults(null);

    if (files.length === 0) {
      setError('Please select at least one resume file');
      setIsLoading(false);
      return;
    }

    if (!jobDescription.trim()) {
      setError('Job description is required for accurate analysis');
      setIsLoading(false);
      return;
    }

    const formData = new FormData();
    files.forEach(file => formData.append('resumes[]', file));
    formData.append('job_desc', jobDescription);
    if (apiKey) formData.append('api_key', apiKey);

    try {
      const response = await fetch('http://localhost:5000/batch-analyze', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('Server returned an error');
      }
      
      const data = await response.json();
      setResults(data);
      
      // Save API key to localStorage if it was used successfully
      if (apiKey) {
        localStorage.setItem('hf_api_key', apiKey);
        setSavedApiKey(apiKey);
      }
    } catch (err) {
      setError(err.message || 'An error occurred while processing resumes');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApiKeySubmit = () => {
    if (!apiKey) {
      setError('Please enter an API key');
      return;
    }

    localStorage.setItem('hf_api_key', apiKey);
    setSavedApiKey(apiKey);
    setShowApiForm(false);
  };

  const toggleExpand = (index) => {
    setExpandedRow(expandedRow === index ? null : index);
  };

  return (
    <div className="resume-analyzer-container">
      <div className="analyzer-header">
        <button onClick={onBack} className="back-button">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
          Back
        </button>
        <h1 className="app-title">Resume Analyzer</h1>
      </div>

      <div className="content-wrapper">
        {/* API Key Management */}
        <div className="form-card mb-5">
          <div className="api-key-section">
            {savedApiKey ? (
              <div className="flex justify-between items-center">
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
                <p className="text-gray-500 mb-3">⚠️ No Hugging Face API key set. Analysis will use the fallback method.</p>
                <button 
                  onClick={() => setShowApiForm(!showApiForm)}
                  className="submit-button mt-0"
                >
                  Set API Key
                </button>
              </div>
            )}
            
            {showApiForm && (
              <div className="analyzer-form mt-4">
                <div className="form-group">
                  <label htmlFor="api-key-input" className="form-label">
                    Hugging Face API Key
                  </label>
                  <input
                    id="api-key-input"
                    type="password" 
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="Enter Hugging Face API key"
                    className="api-key-input"
                  />
                  <div className="form-hint">API key will be saved in your browser for future use.</div>
                </div>
                <button 
                  onClick={handleApiKeySubmit}
                  className="submit-button"
                >
                  Save API Key
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="form-card">
          <div className="analyzer-form">
            <div className="form-group">
              <label htmlFor="resume-files" className="form-label">
                Upload Resumes <span className="required-mark">*</span>
              </label>
              <div className="file-input-container">
                <div className="file-input-wrapper">
                  <input
                    id="resume-files"
                    type="file"
                    multiple
                    onChange={handleFileChange}
                    className="file-input"
                    accept=".pdf,.docx,.txt"
                  />
                  <div className="file-input-placeholder">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                      <polyline points="14 2 14 8 20 8" />
                      <path d="M12 18v-6" />
                      <path d="M9 15h6" />
                    </svg>
                    <span>Drop files here or click to browse</span>
                  </div>
                </div>
                {files.length > 0 && (
                  <div className="file-count">
                    {files.length} file{files.length !== 1 ? 's' : ''} selected
                  </div>
                )}
              </div>
              <div className="form-hint">PDF, DOCX, or TXT formats accepted</div>
            </div>

            <div className="form-group">
              <label htmlFor="job-description" className="form-label">
                Job Description <span className="required-mark">*</span>
              </label>
              <textarea
                id="job-description"
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                className="job-description-input"
                placeholder="Paste the job description here for targeted analysis..."
              />
              <div className="form-hint">Required for accurate candidate matching</div>
            </div>

            <button
              onClick={handleSubmit}
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
                    <path d="M22 12l-4 4-4-4" />
                    <path d="M12 12v9" />
                    <path d="M8 17l-4-4 4-4" />
                    <path d="M16 3l4 4-4 4" />
                    <path d="M2 7h10" />
                  </svg>
                  Analyze Resumes
                </>
              )}
            </button>
          </div>
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

        {results && (
          <div className="results-container">
            <div className="results-header">
              <h2>Analysis Results</h2>
              <div className="job-description-display">
                <div className="job-label">
                  <span className="job-label-text">Job Description:</span>
                  <span className="job-title">
                    {jobDescription && jobDescription.length > 150 
                      ? `${jobDescription.substring(0, 150)}...` 
                      : jobDescription || 'Not specified'}
                  </span>
                </div>
              </div>
            </div>
            
            <div className="table-responsive">
              <table className="results-table">
                <thead>
                  <tr>
                    <th className="rank-header">Rank</th>
                    <th className="name-header">Applicant</th>
                    <th className="skills-header">Key Skills</th>
                    <th className="score-header">Score</th>
                    <th className="actions-header">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {results.results.map((result, index) => (
                    <React.Fragment key={index}>
                      <tr className={expandedRow === index ? 'expanded-row' : ''}>
                        <td className="rank-cell">
                          <div className="rank-badge">{index + 1}</div>
                        </td>
                        <td className="name-cell">{result.name || result.filename}</td>
                        <td className="skills-cell">
                          <div className="skills-container">
                            {result.skills?.slice(0, 3).map((skill, i) => (
                              <span key={i} className="skill-tag">{skill}</span>
                            ))}
                            {result.skills?.length > 3 && (
                              <span className="more-skills">+{result.skills.length - 3} more</span>
                            )}
                          </div>
                        </td>
                        <td className="score-cell">
                          <span className="score-badge" style={{
                            color: result.score > 7 ? 'green' : result.score > 5 ? 'orange' : 'crimson',
                          }}>
                            {result.score || 0}
                          </span>
                        </td>
                        <td className="actions-cell">
                          <button 
                            className="view-details-button"
                            onClick={() => toggleExpand(index)}
                            aria-expanded={expandedRow === index}
                          >
                            {expandedRow === index ? 'Hide' : 'View'}
                          </button>
                        </td>
                      </tr>
                      {expandedRow === index && (
                        <tr className="details-row">
                          <td colSpan="5">
                            <div className="details-panel">
                              <h4>Analysis Summary</h4>
                              <p className="analysis-text">{result.analysis || 'No analysis available'}</p>
                              
                              <h4>All Skills</h4>
                              <div className="all-skills-container">
                                {result.skills?.map((skill, i) => (
                                  <span key={i} className="skill-tag">{skill}</span>
                                ))}
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResumeDescriptionAndRating;