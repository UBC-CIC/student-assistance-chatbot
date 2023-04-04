import './App.css';
import ChatPage from './page/ChatPage';
import FeedbackPage from './page/FeedbackPage';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import AdminPage from './page/AdminPage';


function App() {
  return (
    <BrowserRouter>
    <Routes>
      <Route path="/" element={<ChatPage />} />
      <Route path="/feedback" element={<FeedbackPage />} />
      <Route path="/admin" element={<AdminPage />} />
    </Routes>
  </BrowserRouter>
  );
}

export default App;
