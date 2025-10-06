import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ProductListComponent from './ProductListComponent';
import Summary from './Summary';
import { Product } from '../types/Product';

interface CartItem {
  product: Product;
  quantity: number;
}

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [cart, setCart] = useState<CartItem[]>([]);

  // Load cart from localStorage when component mounts
  useEffect(() => {
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
      try {
        const parsedCart = JSON.parse(savedCart);
        setCart(parsedCart);
      } catch (error) {
        console.error('Error loading cart from localStorage:', error);
      }
    }
  }, []);

  const handleAdd = (product: Product) => {
    setCart(prevCart => {
      const existingItem = prevCart.find(item => item.product.id === product.id);
      if (existingItem) {
        return prevCart.map(item =>
          item.product.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      } else {
        return [...prevCart, { product, quantity: 1 }];
      }
    });
  };

  const handleUpdateQuantity = (productId: number, newQuantity: number) => {
    if (newQuantity <= 0) {
      setCart(prevCart => prevCart.filter(item => item.product.id !== productId));
    } else {
      setCart(prevCart => prevCart.map(item =>
        item.product.id === productId
          ? { ...item, quantity: newQuantity }
          : item
      ));
    }
  };

  const handleCheckout = () => {
    // Save cart to localStorage before navigating
    localStorage.setItem('cart', JSON.stringify(cart));
    navigate('/checkout');
  };

  // Update localStorage whenever cart changes
  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(cart));
  }, [cart]);

  const cartProducts = cart.flatMap(item => 
    Array(item.quantity).fill(item.product)
  );

  return (
    <div className="flex min-h-[calc(100vh-80px)]">
      <div className="flex-1 max-w-4xl">
        <ProductListComponent onAdd={handleAdd} />
      </div>
      <div className="w-96 flex-shrink-0 sticky top-0 h-screen overflow-y-auto space-y-4 p-4">
        <Summary 
          cart={cartProducts} 
          cartItems={cart}
          onUpdateQuantity={handleUpdateQuantity}
          onCheckout={handleCheckout}
        />
      </div>
    </div>
  );
};

export default Home;