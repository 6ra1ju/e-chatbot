import React from 'react';
import { Link } from 'react-router-dom';

const Header: React.FC = () => {
  return (
    <div className="flex justify-center p-4 bg-white border-b border-gray-200">
      <Link to="/" className="no-underline">
        <button className="rounded-full px-5 py-2.5 mx-2.5 cursor-pointer text-sm transition-all duration-300 ease-in-out bg-blue-600 text-white hover:bg-blue-700">
          Home
        </button>
      </Link>
      <Link to="/about" className="no-underline">
        <button className="rounded-full px-5 py-2.5 mx-2.5 cursor-pointer text-sm transition-all duration-300 ease-in-out bg-white text-blue-600 border-2 border-blue-600 hover:bg-blue-600 hover:text-white">
          About
        </button>
      </Link>
    </div>
  );
};

export default Header;
