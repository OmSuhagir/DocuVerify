import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { CheckCircle, AlertTriangle, XCircle, ChevronLeft, FileText } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const FIELD_LABELS = { 
  name: 'Name', 
  dob: 'Date of Birth', 
  address: 'Address', 
  city: 'City',
  candidate_name: 'Candidate Name',
  degree_title: 'Degree Title',
  date_year: 'Date/Year'
};

export default function ResultsView() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/results/${sessionId}`);
        setResults(response.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchResults();
  }, [sessionId]);

  if (loading) {
    return <div className="text-center mt-20 text-slate-500 font-medium">Loading results...</div>;
  }

  if (!results) {
    return <div className="text-center mt-20 text-red-500 font-medium">Failed to load results.</div>;
  }

  const { overall_score, eligible, message, documents, comparisons, category_results } = results;
  const percentage = Math.round((overall_score || 0) * 100);

  const docMap = Object.fromEntries((documents || []).map(d => [d.id, d.filename]));

  let StatusIcon = AlertTriangle;
  let statusColor = 'text-yellow-500';
  let bgStatus = 'bg-yellow-50 border-yellow-200';

  if (eligible === true) {
    StatusIcon = CheckCircle;
    statusColor = 'text-emerald-500';
    bgStatus = 'bg-emerald-50 border-emerald-200';
  } else if (overall_score < 0.70) {
    StatusIcon = XCircle;
    statusColor = 'text-red-500';
    bgStatus = 'bg-red-50 border-red-200';
  }

  const getCategoryDocs = (cat) => documents.filter(d => d.category === cat);
  const getCategoryComparisons = (cat) => {
    const seen = new Set();
    return (comparisons || []).filter(c => c.category === cat).filter(comp => {
      const key = [comp.doc1_id, comp.doc2_id].sort().join('|');
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  };

  const renderCategoryPanel = (title, catKey, docFields) => {
    const catResult = (category_results || []).find(c => c.category === catKey);
    const catDocs = getCategoryDocs(catKey);
    const catComps = getCategoryComparisons(catKey);
    const scorePct = catResult ? Math.round(catResult.similarity_score * 100) : 0;
    
    return (
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden mt-8">
        <div className="px-6 py-5 border-b border-slate-200 bg-slate-50 flex justify-between items-center">
          <h3 className="text-xl font-bold text-slate-800">{title}</h3>
          {catResult && (
            <span className={`px-4 py-1.5 rounded-full text-sm font-bold ${catResult.is_valid ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>
              Category Score: {scorePct}%
            </span>
          )}
        </div>
        
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            {catDocs.map((doc, idx) => (
              <div key={doc.id} className="bg-slate-50 rounded-xl border border-slate-100 p-5">
                <div className="flex items-center mb-3 border-b border-slate-200 pb-2">
                  <FileText className="w-4 h-4 text-indigo-400 mr-2" />
                  <span className="font-semibold text-slate-700 truncate">{doc.filename}</span>
                  <span className="ml-auto text-xs font-bold text-slate-400 uppercase">{doc.document_type?.replace(/_/g, ' ')}</span>
                </div>
                <div className="space-y-2">
                  {docFields.map(field => (
                    <div key={field} className="flex flex-col">
                      <span className="text-[10px] text-slate-400 font-bold uppercase">{FIELD_LABELS[field]}</span>
                      <span className="text-sm text-slate-800 font-medium">
                        {doc.extracted_data?.[field] || <span className="text-slate-300 italic">Not found</span>}
                      </span>
                    </div>
                  ))}
                  {doc.extracted_data && Object.keys(doc.extracted_data)
                    .filter(f => !docFields.includes(f) && doc.extracted_data[f])
                    .map(field => (
                      <div key={field} className="flex flex-col mt-2 pt-2 border-t border-slate-100">
                        <span className="text-[10px] text-slate-400 font-bold uppercase">{FIELD_LABELS[field] || field}</span>
                        <span className="text-sm text-slate-800 font-medium">
                          {doc.extracted_data[field]}
                        </span>
                      </div>
                    ))}
                </div>
              </div>
            ))}
          </div>

          {catComps.length > 0 && (
            <div>
              <h4 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4">Pairwise Comparisons</h4>
              <div className="space-y-4">
                {catComps.map((comp, idx) => {
                  const doc1Name = docMap[comp.doc1_id] || comp.doc1_id;
                  const doc2Name = docMap[comp.doc2_id] || comp.doc2_id;
                  const pairScore = Math.round(comp.average_score * 100);
                  return (
                    <div key={idx} className="bg-white border border-slate-200 rounded-xl p-4">
                      <div className="flex items-center justify-between mb-3 border-b border-slate-100 pb-2">
                        <div className="text-xs font-semibold text-slate-500 truncate max-w-sm">
                          <span className="text-slate-700">{doc1Name}</span> <span className="mx-1 text-slate-400">vs</span> <span className="text-slate-700">{doc2Name}</span>
                        </div>
                        <span className={`text-xs font-bold px-2 py-1 rounded-md ${pairScore >= 90 ? 'bg-emerald-50 text-emerald-600' : 'bg-red-50 text-red-600'}`}>
                          {pairScore}% Match
                        </span>
                      </div>
                      <div className="space-y-2">
                        {Object.entries(comp.field_scores).map(([field, score]) => {
                          const pct = Math.round(score * 100);
                          const color = pct >= 85 ? 'bg-emerald-500' : pct >= 60 ? 'bg-yellow-500' : 'bg-red-500';
                          return (
                            <div key={field} className="flex items-center justify-between text-xs">
                              <span className="w-24 font-medium text-slate-600 capitalize">{FIELD_LABELS[field] || field}</span>
                              <div className="flex-1 bg-slate-100 rounded-full h-1.5 mx-3">
                                <div className={`h-1.5 rounded-full ${color}`} style={{ width: `${pct}%` }} />
                              </div>
                              <span className="w-8 text-right font-bold text-slate-700">{pct}%</span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-12">
      <button
        onClick={() => navigate('/')}
        className="flex items-center text-slate-500 hover:text-slate-800 transition-colors font-medium bg-white px-4 py-2 rounded-lg shadow-sm border border-slate-200 w-max"
      >
        <ChevronLeft className="w-5 h-5 mr-1" />
        Start New Verification
      </button>

      {/* Overall result banner */}
      <div className={`rounded-3xl border p-8 shadow-sm ${bgStatus}`}>
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center">
            <StatusIcon className={`w-16 h-16 mr-6 flex-shrink-0 ${statusColor}`} />
            <div>
              <h2 className="text-3xl font-bold text-slate-800 mb-2">{message}</h2>
              <p className="text-slate-600 font-medium text-lg">
                Overall Consistency Score:{' '}
                <span className={`font-bold ${statusColor}`}>{percentage}%</span>
              </p>
            </div>
          </div>

          <div className="w-32 h-32 relative flex-shrink-0">
            <svg viewBox="0 0 36 36" className="w-full h-full -rotate-90">
              <path className="stroke-black/5" strokeWidth="3" fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
              <path
                className={`${statusColor} stroke-current`}
                strokeDasharray={`${percentage}, 100`}
                strokeWidth="3" strokeLinecap="round" fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className={`text-2xl font-bold ${statusColor}`}>{percentage}%</span>
            </div>
          </div>
        </div>
      </div>

      {renderCategoryPanel("Identification Proof", "IDENTIFICATION", ["name", "dob"])}
      {renderCategoryPanel("Address Proof", "ADDRESS", ["address", "city"])}
      {renderCategoryPanel("Non-ECR Proof", "NON_ECR", ["candidate_name", "degree_title", "date_year"])}

      {/* Cross-Category matches */}
      {getCategoryComparisons("CROSS_CATEGORY").length > 0 && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden mt-8">
          <div className="px-6 py-5 border-b border-slate-200 bg-indigo-50 flex justify-between items-center">
            <h3 className="text-xl font-bold text-indigo-900">Global Cross-Category Matches</h3>
          </div>
          <div className="p-6">
            <p className="text-slate-500 mb-6 text-sm">
              The following common fields were automatically compared across different document categories to ensure consistency.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {getCategoryComparisons("CROSS_CATEGORY").map((comp, idx) => {
                const doc1Name = docMap[comp.doc1_id] || comp.doc1_id;
                const doc2Name = docMap[comp.doc2_id] || comp.doc2_id;
                const pairScore = Math.round(comp.average_score * 100);
                return (
                  <div key={idx} className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                    <div className="flex flex-col mb-4 border-b border-slate-100 pb-3">
                      <div className="flex justify-between items-start mb-2">
                        <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Document Pair</span>
                        <span className={`text-xs font-bold px-2 py-1 rounded-md ${pairScore >= 90 ? 'bg-emerald-50 text-emerald-600' : pairScore >= 70 ? 'bg-yellow-50 text-yellow-600' : 'bg-red-50 text-red-600'}`}>
                          {pairScore}% Match
                        </span>
                      </div>
                      <div className="text-sm font-semibold text-slate-700 truncate">{doc1Name}</div>
                      <div className="text-xs text-slate-400 italic my-0.5">compared with</div>
                      <div className="text-sm font-semibold text-slate-700 truncate">{doc2Name}</div>
                    </div>
                    <div className="space-y-3">
                      {Object.entries(comp.field_scores).map(([field, score]) => {
                        const pct = Math.round(score * 100);
                        const color = pct >= 85 ? 'bg-emerald-500' : pct >= 60 ? 'bg-yellow-500' : 'bg-red-500';
                        return (
                          <div key={field} className="flex items-center justify-between text-xs">
                            <span className="w-24 font-medium text-slate-600 capitalize">{FIELD_LABELS[field] || field}</span>
                            <div className="flex-1 bg-slate-100 rounded-full h-1.5 mx-3">
                              <div className={`h-1.5 rounded-full ${color}`} style={{ width: `${pct}%` }} />
                            </div>
                            <span className="w-8 text-right font-bold text-slate-700">{pct}%</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
