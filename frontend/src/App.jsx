import { BrowserRouter, Routes, Route } from 'react-router-dom';
import UploadView from './views/UploadView';
import ProcessingView from './views/ProcessingView';
import ResultsView from './views/ResultsView';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50 font-sans">
        <header className="bg-white shadow-sm border-b border-slate-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
              DocuVerify
            </h1>
            <span className="text-sm font-medium text-slate-500">Passport Verification System</span>
          </div>
        </header>
        
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<UploadView />} />
            <Route path="/processing/:sessionId" element={<ProcessingView />} />
            <Route path="/results/:sessionId" element={<ResultsView />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
