import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route
          path="/dashboard"
          element={
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
              <div className="text-center">
                <h1 className="text-3xl font-bold text-gray-900">HRM Dashboard</h1>
                <p className="mt-2 text-gray-500">Willkommen im HR-Management-Dashboard.</p>
              </div>
            </div>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
