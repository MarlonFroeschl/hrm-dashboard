import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ApplicantListPage, ApplicantDetailPage } from "./pages/recruiting";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/recruiting" replace />} />
        <Route path="/recruiting" element={<ApplicantListPage />} />
        <Route path="/recruiting/:id" element={<ApplicantDetailPage />} />
      </Routes>
    </BrowserRouter>
  );
}
