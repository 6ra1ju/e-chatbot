import React, { useEffect, useState, useMemo } from 'react';
import { Product } from '../types/Product';
import { productService } from '../services/productService';
import SearchFilter from './SearchFilter';


interface Props {
  onAdd: (product: Product) => void;
}

const ProductListComponent: React.FC<Props> = ({ onAdd }) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterBrand, setFilterBrand] = useState('');
  const [filterCategory, setFilterCategory] = useState('');

  useEffect(() => {
    // Fetch data from Django API
    const fetchProducts = async () => {
      try {
        setLoading(true);
        setError(null);
        const products = await productService.getAllProducts();
        setProducts(products);
      } catch (error) {
        console.error('Error fetching products:', error);
        setError('Không thể kết nối với server. Vui lòng kiểm tra lại.');
        setProducts([]);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('vi-VN').format(price);
  };

  const formatSoldCount = (count: number) => {
    if (count >= 1000000) {
      return `${(count / 1000000).toFixed(1)}M`;
    } else if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}k`;
    }
    return count.toString();
  };

  const getProductImage = (product: Product) => {
    // Prefer server-provided image URL when available
    if (product.image && typeof product.image === 'string') {
      const trimmed = product.image.trim();
      if (trimmed.startsWith('http://') || trimmed.startsWith('https://')) {
        return trimmed;
      }
    }
    return '';
  };

  const getProductBrand = (product: Product) => {
    if (product.labels && product.labels.length > 0) {
      // Amazon products typically have brand as first label
      const brand = product.labels.find(label => 
        !['amazon', 'imported', 'shopee'].includes(label.toLowerCase())
      );
      return brand || 'Amazon';
    }
    return 'Amazon';
  };

  const getProductCategory = (product: Product) => {
    if (product.labels && product.labels.length > 1) {
      return product.labels[1] || 'General';
    }
    return 'General';
  };

  // Extract unique brands and categories for filters
  const { brands, categories } = useMemo(() => {
    const uniqueBrands = new Set<string>();
    const uniqueCategories = new Set<string>();
    
    products.forEach(product => {
      const brand = getProductBrand(product);
      const category = getProductCategory(product);
      uniqueBrands.add(brand);
      uniqueCategories.add(category);
    });
    
    return {
      brands: Array.from(uniqueBrands).sort(),
      categories: Array.from(uniqueCategories).sort()
    };
  }, [products]);

  // Filter products based on search and filter criteria
  const filteredProducts = useMemo(() => {
    return products.filter(product => {
      const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase());
      const brand = getProductBrand(product);
      const category = getProductCategory(product);
      const matchesBrand = !filterBrand || brand.toLowerCase().includes(filterBrand.toLowerCase());
      const matchesCategory = !filterCategory || category.toLowerCase().includes(filterCategory.toLowerCase());
      
      return matchesSearch && matchesBrand && matchesCategory;
    });
  }, [products, searchTerm, filterBrand, filterCategory]);

  const handleSearch = (term: string) => {
    setSearchTerm(term);
  };

  const handleFilter = (brand: string, category: string) => {
    setFilterBrand(brand);
    setFilterCategory(category);
  };



  return (
    <div className="w-full p-4 bg-blue-50 min-h-screen">
      {loading && (
        <div className="flex justify-center items-center h-50 text-lg text-gray-600">
          Đang tải dữ liệu...
        </div>
      )}

      {error && (
        <div className="flex justify-center items-center h-50 text-lg text-red-500 text-center p-5">
          {error}
        </div>
      )}

      {!loading && !error && (
        <>
          {/* Search and Filter */}
          <SearchFilter
            onSearch={handleSearch}
            onFilter={handleFilter}
            brands={brands}
            categories={categories}
          />

          {/* Results count */}
          <div className="mb-4 text-sm text-gray-600">
            Hiển thị {filteredProducts.length} trong tổng số {products.length} sản phẩm
          </div>

          {/* Products Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredProducts.map((product) => (
          <div key={product.id} className="bg-white rounded-lg p-4 shadow-md relative hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
            {/* Product Image */}
            <div className="w-full h-40 rounded-lg mb-3 overflow-hidden">
              <img 
                src={getProductImage(product)} 
                alt={product.name}
                className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"

              />
            </div>

            {/* Discount Badge */}
            <div className="absolute top-3 left-3 bg-red-500 text-white px-2 py-1 rounded-full text-xs font-bold shadow-md">
              -{product.discount || 17}%
            </div>



            {/* Labels */}
            <div className="mb-2 flex flex-wrap gap-1">
              {product.labels?.map((label, index) => (
                <span key={index} className={`px-2 py-1 rounded-full text-xs font-medium text-white ${
                  label.includes('VOUCHER') ? 'bg-red-400' : 'bg-green-500'
                }`}>
                  {label}
                </span>
              ))}
            </div>

            {/* Brand and Category */}
            <div className="mb-1 flex flex-wrap gap-1">
              <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full font-medium">
                {getProductBrand(product)}
              </span>
              <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                {getProductCategory(product)}
              </span>
            </div>

            {/* Product Name */}
            <h3 className="mb-2 text-sm font-bold text-gray-800 leading-tight line-clamp-2">
              {product.name}
            </h3>

            {/* Price */}
            <div className="mb-2">
              <span className="text-lg font-bold text-red-500">
                ₫{formatPrice(product.price)}
              </span>
              <span className="text-xs text-gray-500 line-through ml-2">
                ₫{formatPrice(Math.round(product.price / (1 - (product.discount || 17) / 100)))}
              </span>
            </div>

            {/* Sold Count */}
            <div className="text-xs text-gray-600 mb-3">
              Đã bán {formatSoldCount(product.soldCount || 0)}
            </div>

            {/* Add to Cart Button */}
            <button
              onClick={() => onAdd(product)}
              className="w-full bg-blue-600 text-white border-none rounded-lg py-2 cursor-pointer text-sm hover:bg-blue-700 transition-all duration-300 font-semibold shadow-md hover:shadow-lg"
            >
              Add to Cart
            </button>
          </div>
        ))}
          </div>
        </>
      )}
    </div>
  );
};

export default ProductListComponent;
