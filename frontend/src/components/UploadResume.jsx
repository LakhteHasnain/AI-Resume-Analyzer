import React, { useState } from 'react';  
import axios from 'axios';  

const UploadResume = () => {  
  const [file, setFile] = useState(null);  

  const handleUpload = async (e) => {  
    e.preventDefault();  
    const formData = new FormData();  
    formData.append('resume', file);  

    try {  
      const res = await axios.post('http://localhost:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });  
      alert(res.data.message);  
    } catch (err) {  
      console.error("Upload error:", err.response ? err.response.data : err.message);
      alert(err.response?.data?.error || "Upload failed!");  
    }  
  };  

  return (  
    <div>  
      <h2>Upload Your Resume</h2>  
      <form onSubmit={handleUpload}>  
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />  
        <button type="submit">Analyze</button>  
      </form>  
    </div>  
  );  
};  

export default UploadResume;