import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Home from './components/Home';
import About from './components/About';
import CheckoutWrapper from './components/CheckoutWrapper';
import Done from './components/Done';
import FloatingChatbot from './components/FloatingChatbot';

const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen bg-blue-50">
        <Header />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/checkout" element={<CheckoutWrapper />} />
          <Route path="/done" element={<Done />} />
        </Routes>
        
        {/* Global Floating Chatbot */}
        <FloatingChatbot />
      </div>
    </Router>
  );
};

export default App;
