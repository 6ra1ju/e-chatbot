import React, { useState, useEffect } from 'react';

interface SearchFilterProps {
  onSearch: (searchTerm: string) => void;
  onFilter: (brand: string, category: string) => void;
  brands: string[];
  categories: string[];
}

const SearchFilter: React.FC<SearchFilterProps> = ({ 
  onSearch, 
  onFilter, 
  brands, 
  categories 
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedBrand, setSelectedBrand] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');

  useEffect(() => {
    onSearch(searchTerm);
  }, [searchTerm, onSearch]);

  useEffect(() => {
    onFilter(selectedBrand, selectedCategory);
  }, [selectedBrand, selectedCategory, onFilter]);

  return (
    <div className="bg-white p-4 rounded-lg shadow-md mb-4">
      <div className="flex flex-col md:flex-row gap-4">
        {/* Search Input */}
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Tìm kiếm sản phẩm
          </label>
          <input
            type="text"
            placeholder="Nhập tên sản phẩm..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Brand Filter */}
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Thương hiệu
          </label>
          <input
            type="text"
            placeholder="Nhập tên thương hiệu..."
            value={selectedBrand}
            onChange={(e) => setSelectedBrand(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Clear Filters */}
        <div className="flex items-end">
          <button
            onClick={() => {
              setSearchTerm('');
              setSelectedBrand('');
              setSelectedCategory('');
            }}
            className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition-colors"
          >
            Xóa bộ lọc
          </button>
        </div>
      </div>
    </div>
  );
};

export default SearchFilter;