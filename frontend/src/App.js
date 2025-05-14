import React, { useState } from 'react';
import UploadResume from './components/resumeSuggestion';
import ResumeDescriptionAndRating from './components/rateResumes';
import { Typewriter } from 'react-simple-typewriter';

function App() {
  const [selectedModule, setSelectedModule] = useState(null);

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-blue-100 font-sans text-gray-800">
      {/* HERO SECTION */}
      <section className="text-center py-20 px-4">
        <h1 className="text-5xl font-extrabold mb-4">
          <span className="text-blue-600">AI Resume Analyzer</span>
        </h1>
        <h2 className="text-2xl font-semibold mb-6 text-gray-700">
          <Typewriter
            words={['Empowering Job Seekers.', 'Optimizing Recruitment.', 'AI-Powered Resume Insights.']}
            loop={true}
            cursor
            cursorStyle="_"
            typeSpeed={60}
            deleteSpeed={40}
            delaySpeed={2000}
          />
        </h2>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Whether you're refining your resume for your dream job or screening hundreds of applicants,
          our AI-driven platform gives you a smarter edge.
        </p>
      </section>

      {/* MODULE CARDS */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-6xl mx-auto px-4 mb-16">
        {/* Job Seeker Card */}
        <div
          onClick={() => setSelectedModule('jobseeker')}
          className="cursor-pointer bg-white/70 backdrop-blur-sm shadow-xl rounded-2xl p-8 hover:scale-105 transition-transform border border-blue-100"
        >
          <h2 className="text-2xl font-bold mb-2">👨‍💼 Job Seeker</h2>
          <p>
            Upload your CV and (optionally) a job description. Get AI-backed suggestions to improve and tailor your resume.
          </p>
        </div>

        {/* HR / Recruiter Card */}
        <div
          onClick={() => setSelectedModule('hr')}
          className="cursor-pointer bg-white/70 backdrop-blur-sm shadow-xl rounded-2xl p-8 hover:scale-105 transition-transform border border-blue-100"
        >
          <h2 className="text-2xl font-bold mb-2">🧑‍💻 HR / Recruiter</h2>
          <p>
            Upload multiple resumes and one job description. Our AI scores and ranks applicants based on relevance.
          </p>
        </div>
      </section>

      {/* CONDITIONAL RENDERING */}
      <section className="max-w-6xl mx-auto px-4 mb-20">
        {selectedModule === 'jobseeker' && (
          <div className="bg-white shadow-md rounded-xl p-6">
            <h3 className="text-xl font-bold mb-4 text-blue-600">Job Seeker Module</h3>
            <UploadResume />
          </div>
        )}
        {selectedModule === 'hr' && (
          <div className="bg-white shadow-md rounded-xl p-6">
            <h3 className="text-xl font-bold mb-4 text-indigo-600">HR / Recruiter Module</h3>
            <ResumeDescriptionAndRating />
          </div>
        )}
      </section>

      {/* FOOTER */}
      <footer className="text-center py-6 text-gray-500 text-sm">
       By LakhteHasnain
      </footer>
    </div>
  );
}

export default App;
