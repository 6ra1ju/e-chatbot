import React from 'react';
import { useNavigate } from 'react-router-dom';

const Done: React.FC = () => {
  const navigate = useNavigate();

  const handleContinueShopping = () => {
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-blue-50 flex items-center justify-start flex-col pt-36">
      <div className="bg-white p-12 rounded-xl shadow-lg text-center max-w-lg w-11/12">
        <div className="text-6xl text-green-500 mb-4">
          ✓
        </div>
        <h1 className="text-green-500 text-2xl mb-4">
          Successful payment!
        </h1>
        <p className="text-gray-600 text-base mb-8">
          Thank you for your purchase. Your order has been confirmed and will be shipped soon.
        </p>
        <button
          onClick={handleContinueShopping}
          className="bg-blue-600 text-white border-none rounded-lg px-6 py-3 text-base cursor-pointer font-bold hover:bg-blue-700 transition-colors"
        >
          Continue Shopping
        </button>
      </div>
    </div>
  );
};

export default Done; 