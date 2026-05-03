import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, File, X, AlertCircle, CheckCircle } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export default function UploadView() {
  const [categories, setCategories] = useState({
    IDENTIFICATION: [],
    ADDRESS: [],
    NON_ECR: []
  });
  
  const [uploads, setUploads] = useState({
    IDENTIFICATION: [],
    ADDRESS: [],
    NON_ECR: []
  });

  const [selectedTypes, setSelectedTypes] = useState({
    IDENTIFICATION: '',
    ADDRESS: '',
    NON_ECR: ''
  });

  const [sessionId, setSessionId] = useState(null);
  const [error, setError] = useState(null);
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        console.log("Sending request to : ", `${API_BASE_URL}/categories`)
        const response = await axios.get(`${API_BASE_URL}/categories`);
        setCategories(response.data);
      } catch (err) {
        console.error("Failed to fetch categories", err);
        setError("Failed to load document categories. Please refresh.");
      }
    };
    fetchCategories();
  }, []);

  const handleFileSelect = async (e, category) => {
    const newFiles = Array.from(e.target.files);
    if (newFiles.length === 0) return;

    const docType = selectedTypes[category];
    if (!docType) {
      setError(`Please select a document type for ${category} before uploading.`);
      return;
    }

    const file = newFiles[0];
    if (!['application/pdf', 'image/jpeg', 'image/png'].includes(file.type)) {
      setError("Only PDF, JPG, JPEG, and PNG files are allowed.");
      return;
    }

    setError(null);
    setUploading(true);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);
    formData.append('document_type', docType);
    if (sessionId) {
      formData.append('session_id', sessionId);
    }

    try {
      const response = await axios.post(`${API_BASE_URL}/upload/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setSessionId(response.data.session_id);
      
      setUploads(prev => ({
        ...prev,
        [category]: [...prev[category], { file: file.name, documentType: docType, size: file.size }]
      }));
      
      setSelectedTypes(prev => ({ ...prev, [category]: '' }));
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
    
    e.target.value = null;
  };

  const removeUpload = (category, index) => {
    setUploads(prev => ({
      ...prev,
      [category]: prev[category].filter((_, i) => i !== index)
    }));
  };

  const isVerifyReady = () => {
    return uploads.IDENTIFICATION.length >= 3 &&
           uploads.ADDRESS.length >= 1 &&
           uploads.NON_ECR.length >= 1;
  };

  const handleVerify = () => {
    if (!isVerifyReady() || !sessionId) return;
    navigate(`/processing/${sessionId}`);
  };

  const categoryConfigs = [
    { key: 'IDENTIFICATION', title: 'Identification Proof', min: 3 },
    { key: 'ADDRESS', title: 'Address Proof', min: 1 },
    { key: 'NON_ECR', title: 'Non-ECR Proof', min: 1 }
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-100 p-8">
        <h2 className="text-3xl font-bold text-slate-800 mb-2">Upload Documents</h2>
        <p className="text-slate-500 mb-8">
          Upload required documents for each category to proceed with verification.
        </p>

        {error && (
          <div className="mb-6 bg-red-50 text-red-600 p-4 rounded-xl flex items-start border border-red-100">
            <AlertCircle className="w-5 h-5 mr-3 flex-shrink-0 mt-0.5" />
            <p className="font-medium">{error}</p>
          </div>
        )}

        <div className="space-y-8">
          {categoryConfigs.map(({ key, title, min }) => (
            <div key={key} className="border border-slate-200 rounded-2xl p-6 bg-slate-50">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-semibold text-slate-800">{title}</h3>
                <span className={`px-3 py-1 rounded-full text-sm font-bold ${uploads[key].length >= min ? 'bg-emerald-100 text-emerald-700' : 'bg-blue-100 text-blue-700'}`}>
                  {uploads[key].length} / {min} Minimum
                </span>
              </div>

              <div className="flex gap-4 mb-6">
                <select 
                  className="flex-1 rounded-xl border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 p-3"
                  value={selectedTypes[key]}
                  onChange={(e) => setSelectedTypes(prev => ({ ...prev, [key]: e.target.value }))}
                >
                  <option value="">Select Document Type...</option>
                  {categories[key]?.map(type => (
                    <option key={type} value={type}>{type.replace(/_/g, ' ')}</option>
                  ))}
                </select>

                <div className="relative">
                  <input 
                    type="file" 
                    id={`upload-${key}`}
                    className="hidden"
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={(e) => handleFileSelect(e, key)}
                    disabled={!selectedTypes[key] || uploading}
                  />
                  <label 
                    htmlFor={`upload-${key}`}
                    className={`flex items-center justify-center px-6 py-3 rounded-xl font-bold transition-all ${
                      !selectedTypes[key] || uploading 
                        ? 'bg-slate-200 text-slate-400 cursor-not-allowed' 
                        : 'bg-indigo-600 text-white hover:bg-indigo-700 cursor-pointer shadow-sm hover:shadow'
                    }`}
                  >
                    <UploadCloud className="w-5 h-5 mr-2" />
                    Upload
                  </label>
                </div>
              </div>

              {uploads[key].length > 0 && (
                <div className="space-y-3">
                  {uploads[key].map((item, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-white border border-slate-200 rounded-xl">
                      <div className="flex items-center overflow-hidden">
                        <File className="w-5 h-5 text-indigo-400 mr-3 flex-shrink-0" />
                        <div className="truncate">
                          <p className="font-semibold text-sm text-slate-800 truncate">{item.file}</p>
                          <p className="text-xs text-slate-500 font-medium">{item.documentType.replace(/_/g, ' ')}</p>
                        </div>
                      </div>
                      <button 
                        onClick={() => removeUpload(key, idx)}
                        className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
        
        <div className="mt-8 pt-6 border-t border-slate-200 flex justify-end">
          <button
            onClick={handleVerify}
            disabled={!isVerifyReady() || uploading}
            className={`px-8 py-4 rounded-xl font-bold text-white transition-all ${
              !isVerifyReady() || uploading 
                ? 'bg-slate-300 cursor-not-allowed' 
                : 'bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-emerald-500/30'
            }`}
          >
            {uploading ? 'Processing...' : 'Verify All Documents'}
          </button>
        </div>
      </div>
    </div>
  );
}

