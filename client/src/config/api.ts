// API Configuration
export const API_BASE_URL = 'http://127.0.0.1:8000';

export const API_ENDPOINTS = {
  PRODUCTS: `${API_BASE_URL}/api/products/`,
  PRODUCT_DETAIL: (id: number) => `${API_BASE_URL}/api/products/${id}/`,
  CREATE_PRODUCT: `${API_BASE_URL}/api/products/create/`,
};

// API utility functions
export const apiClient = {
  async get(endpoint: string) {
    const response = await fetch(endpoint);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  },

  async post(endpoint: string, data: any) {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  },
}; 