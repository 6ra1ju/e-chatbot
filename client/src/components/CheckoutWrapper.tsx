import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Checkout from './Checkout';
import { Product } from '../types/Product';

interface CartItem {
  product: Product;
  quantity: number;
}

const CheckoutWrapper: React.FC = () => {
  const navigate = useNavigate();
  const [cartItems, setCartItems] = useState<CartItem[]>([]);

  useEffect(() => {
    // Load cart from localStorage
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
      try {
        setCartItems(JSON.parse(savedCart));
      } catch (error) {
        console.error('Error loading cart from localStorage:', error);
      }
    }
  }, []);

  const handleBackToCart = () => {
    // Just navigate back to Home, don't clear localStorage
    navigate('/');
  };

  const handleClearCart = () => {
    setCartItems([]);
    localStorage.removeItem('cart'); // Clear localStorage when cart is cleared
    navigate('/');
  };

  const handlePaymentSuccess = () => {
    // Clear cart after successful payment
    localStorage.removeItem('cart');
    navigate('/done');
  };

  return (
    <Checkout
      cartItems={cartItems}
      onBackToCart={handleBackToCart}
      onClearCart={handleClearCart}
      onPaymentSuccess={handlePaymentSuccess}
    />
  );
};

export default CheckoutWrapper; 