import React, { useState } from 'react';
import axios from 'axios';
import './App.css'; // Make sure to import the CSS file

function App() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    education: '',
    experience: '',
    skills: ''
  });
  const [resumeContent, setResumeContent] = useState('');
  const [pdfLink, setPdfLink] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(''); // Reset error state
    try {
      // Generate resume content
      const resumeResponse = await axios.post('http://localhost:8000/generate_resume/', formData);
      setResumeContent(resumeResponse.data.resume_content);

      // Generate PDF
      const pdfResponse = await axios.post('http://localhost:8000/generate_pdf/', formData, {
        responseType: 'blob'  // Important for handling binary data
      });

      // Create a URL for the PDF
      const pdfBlob = new Blob([pdfResponse.data], { type: 'application/pdf' });
      const pdfUrl = URL.createObjectURL(pdfBlob);
      setPdfLink(pdfUrl);

    } catch (error) {
      console.error('Error generating resume or PDF:', error);
      setError('Failed to generate resume or PDF. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <Header />
      <main>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Name</label>
            <input 
              type="text" 
              id="name" 
              name="name" 
              placeholder="Enter your name" 
              onChange={handleChange} 
              value={formData.name} 
              aria-required="true"
            />
          </div>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input 
              type="email" 
              id="email" 
              name="email" 
              placeholder="Enter your email" 
              onChange={handleChange} 
              value={formData.email} 
              aria-required="true"
            />
          </div>
          <div className="form-group">
            <label htmlFor="phone">Phone</label>
            <input 
              type="tel" 
              id="phone" 
              name="phone" 
              placeholder="Enter your phone number" 
              onChange={handleChange} 
              value={formData.phone} 
              aria-required="true"
            />
          </div>
          <div className="form-group">
            <label htmlFor="education">Education</label>
            <textarea 
              id="education" 
              name="education" 
              placeholder="Enter your education details" 
              onChange={handleChange} 
              value={formData.education} 
              aria-required="true"
            />
          </div>
          <div className="form-group">
            <label htmlFor="experience">Experience</label>
            <textarea 
              id="experience" 
              name="experience" 
              placeholder="Enter your work experience" 
              onChange={handleChange} 
              value={formData.experience} 
              aria-required="true"
            />
          </div>
          <div className="form-group">
            <label htmlFor="skills">Skills</label>
            <textarea 
              id="skills" 
              name="skills" 
              placeholder="Enter your skills" 
              onChange={handleChange} 
              value={formData.skills} 
              aria-required="true"
            />
          </div>
          <button type="submit" disabled={loading}>
            {loading ? 'Generating...' : 'Generate Resume'}
          </button>
        </form>
        {error && <div className="error-message">{error}</div>}
        {resumeContent && (
          <div className="resume-preview">
            <h2>Resume Preview</h2>
            <pre>{resumeContent}</pre>
          </div>
        )}
        {pdfLink && <a href={pdfLink} download="resume.pdf" className="pdf-link">Download PDF</a>}
      </main>
    </div>
  );
}

function Header() {
  return (
    <header className="App-header">
      <h1>Resume Builder</h1>
      <p>Create and download your resume easily!</p>
    </header>
  );
}

export default App;
