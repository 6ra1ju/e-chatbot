import React from 'react';
import { Link } from 'react-router-dom';
import { Product } from '../types/Product';

interface CartItem {
  product: Product;
  quantity: number;
}

interface CheckoutProps {
  cartItems: CartItem[];
  onBackToCart: () => void;
  onClearCart: () => void;
  onPaymentSuccess?: () => void;
}

const Checkout: React.FC<CheckoutProps> = ({ 
  cartItems, 
  onBackToCart, 
  onClearCart, 
  onPaymentSuccess 
}) => {
  const subtotal = cartItems.reduce((sum, item) => sum + (item.product.price * item.quantity), 0);
  const shipping = 0; // FREE
  const taxes = cartItems.length > 0 ? 10 : 0;
  const total = subtotal + shipping + taxes;

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('vi-VN').format(price);
  };

  const handlePayNow = () => {
    // Simulate payment process
    setTimeout(() => {
      onClearCart();
      if (onPaymentSuccess) {
        onPaymentSuccess();
      }
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-blue-50 p-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white p-8 rounded-xl shadow-md">
          <h1 className="text-2xl font-bold mb-8 text-gray-800 text-center">Order Summary</h1>
          
          {/* Items */}
          <div className="mb-8 space-y-4">
            {cartItems.map((item) => (
              <div key={item.product.id} className="flex justify-between items-center p-4 border border-gray-200 rounded-lg bg-gray-50">
                <div className="flex-1">
                  <div className="font-bold text-base mb-2 text-gray-600">Product #{item.product.id}</div>
                  <div className="text-gray-600 text-sm">Quantity: {item.quantity}</div>
                </div>
                <div className="font-bold text-base">₫{formatPrice(item.product.price * item.quantity)}</div>
              </div>
            ))}
          </div>

          {/* Cost Breakdown */}
          <div className="border-t-2 border-gray-200 pt-6 mb-8 space-y-3">
            <div className="flex justify-between text-base">
              <span>Subtotal:</span>
              <span>₫{formatPrice(subtotal)}</span>
            </div>
            <div className="flex justify-between text-base">
              <span>Shipping:</span>
              <span className="text-green-500 font-bold">FREE</span>
            </div>
            <div className="flex justify-between text-base">
              <span>Taxes:</span>
              <span>₫{formatPrice(taxes)}</span>
            </div>
            <div className="flex justify-between border-t-2 border-gray-800 pt-4 text-xl font-bold">
              <span>Total:</span>
              <span>₫{formatPrice(total)}</span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4">
            <Link 
              to="/" 
              className="flex-1 bg-gray-100 text-gray-800 border border-gray-300 rounded-lg py-4 text-base cursor-pointer font-bold hover:bg-gray-200 transition-colors text-center"
            >
              Back to Home
            </Link>
            <button
              onClick={handlePayNow}
              className="flex-1 bg-green-500 text-white border-none rounded-lg py-4 text-base font-bold cursor-pointer hover:bg-green-600 transition-colors"
            >
              Pay Now
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Checkout;
