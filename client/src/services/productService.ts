import { Product } from '../types/Product';
import { API_ENDPOINTS, apiClient } from '../config/api';

// Transform backend data to frontend format
const transformProduct = (product: any): Product => ({
  id: product.id,
  name: product.name,
  price: product.price,
  originalPrice: product.original_price,
  discount: product.discount,
  rating: product.rating,
  soldCount: product.sold_count,
  image: product.image,
  labels: product.labels || []
});

// Transform frontend data to backend format
const transformToBackendFormat = (product: Partial<Product>) => ({
  name: product.name,
  price: product.price,
  original_price: product.originalPrice,
  discount: product.discount,
  rating: product.rating,
  sold_count: product.soldCount,
  image: product.image,
  labels: product.labels
});

export const productService = {
  // Get all products
  async getAllProducts(): Promise<Product[]> {
    try {
      const data = await apiClient.get(API_ENDPOINTS.PRODUCTS);
      return data.map(transformProduct);
    } catch (error) {
      console.error('Error fetching products:', error);
      throw error;
    }
  },

  // Get product by ID
  async getProductById(id: number): Promise<Product> {
    try {
      const data = await apiClient.get(API_ENDPOINTS.PRODUCT_DETAIL(id));
      return transformProduct(data);
    } catch (error) {
      console.error(`Error fetching product ${id}:`, error);
      throw error;
    }
  },

  // Create new product
  async createProduct(product: Partial<Product>): Promise<Product> {
    try {
      const backendData = transformToBackendFormat(product);
      const data = await apiClient.post(API_ENDPOINTS.CREATE_PRODUCT, backendData);
      return transformProduct(data);
    } catch (error) {
      console.error('Error creating product:', error);
      throw error;
    }
  }
}; 