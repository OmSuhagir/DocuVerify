import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Loader2 } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export default function ProcessingView() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [error, setError] = useState(null);
  const calledRef = useRef(false); // prevent React StrictMode double-call

  useEffect(() => {
    if (calledRef.current) return;
    calledRef.current = true;

    const processDocuments = async () => {
      try {
        console.log("Sending post request to ", `${API_BASE_URL}/verify/${sessionId}`)
        await axios.post(`${API_BASE_URL}/verify/${sessionId}`);
        navigate(`/results/${sessionId}`);
      } catch (err) {
        setError(err.response?.data?.detail || "An error occurred during verification.");
      }
    };

    processDocuments();
  }, [sessionId, navigate]);

  return (
    <div className="max-w-xl mx-auto mt-20">
      <div className="bg-white rounded-3xl shadow-xl overflow-hidden border border-slate-100 p-12 text-center">
        {error ? (
          <div>
            <div className="w-20 h-20 bg-red-100 text-red-500 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-slate-800 mb-4">Verification Failed</h2>
            <p className="text-slate-500 mb-8">{error}</p>
            <button
              onClick={() => navigate('/')}
              className="px-6 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded-xl transition-colors"
            >
              Try Again
            </button>
          </div>
        ) : (
          <div>
            <div className="relative w-24 h-24 mx-auto mb-8">
              <div className="absolute inset-0 bg-blue-100 rounded-full animate-ping opacity-75"></div>
              <div className="relative bg-white rounded-full w-full h-full shadow-sm border border-blue-100 flex items-center justify-center z-10">
                <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
              </div>
            </div>
            <h2 className="text-2xl font-bold text-slate-800 mb-3">Analyzing Documents</h2>
            <p className="text-slate-500 max-w-sm mx-auto">
              Please wait while our system extracts information and cross-verifies your documents. This may take a moment.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
