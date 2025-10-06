import React, { useState } from 'react';
import { Product } from '../types/Product';

interface CartItem {
  product: Product;
  quantity: number;
}

interface Props {
  cart: Product[];
  cartItems: CartItem[];
  onUpdateQuantity: (productId: number, newQuantity: number) => void;
  onCheckout: () => void;
}

const Summary: React.FC<Props> = ({ cart, cartItems, onUpdateQuantity, onCheckout }) => {
  const [selectedItems, setSelectedItems] = useState<Set<number>>(new Set());

  const handleItemToggle = (productId: number) => {
    const newSelected = new Set(selectedItems);
    if (newSelected.has(productId)) {
      newSelected.delete(productId);
    } else {
      newSelected.add(productId);
    }
    setSelectedItems(newSelected);
  };

  const handleRemoveItem = (productId: number) => {
    onUpdateQuantity(productId, 0); // Set quantity to 0 to remove item
  };

  const handleClearAll = () => {
    cartItems.forEach(item => {
      onUpdateQuantity(item.product.id, 0);
    });
  };

  const selectedProducts = cartItems.filter(item => selectedItems.has(item.product.id));
  const subtotal = selectedProducts.reduce((sum, item) => sum + (item.product.price * item.quantity), 0);
  //const subtotal = cartItems.reduce((sum, item) => sum + (item.product.price * item.quantity), 0);
  const shipping = 0; // FREE
  const taxes = selectedProducts.length > 0 ? 10 : 0;
  //const taxes = cartItems.length > 0 ? 10 : 0;
  const total = subtotal + shipping + taxes;

  return (
    <div className="w-full bg-white border-l border-gray-200 rounded-l-3xl mt-3">
      <div className="bg-white p-6 border-b border-gray-200 rounded-tl-3xl">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">
            Shopping Cart
          </h2>
          {cartItems.length > 0 && (
            <button
              onClick={handleClearAll}
              className="bg-red-500 text-white border-none rounded-lg px-3 py-2 text-xs cursor-pointer font-bold hover:bg-red-600 transition-colors"
              title="Clear all items"
            >
              Clear All
            </button>
          )}
        </div>
      </div>

      {/* Items List */}
      <div className="p-6">
        {cartItems.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🛒</div>
            <p className="text-gray-500 text-lg mb-2">Your cart is empty</p>
            <p className="text-gray-400 text-sm">Add some delicious food to get started!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {cartItems.map((item) => (
              <div key={item.product.id} className="bg-gray-50 rounded-xl p-4 border border-gray-200 relative">
                <input
                  type="checkbox"
                  checked={selectedItems.has(item.product.id)}
                  onChange={() => handleItemToggle(item.product.id)}
                  className="mr-3 w-5 h-5"
                />
                <div className="flex-1">
                  <div className="font-bold mb-2 text-base">
                    {item.product.name}
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="font-semibold text-gray-700 text-base">₫{item.product.price.toLocaleString()}</span>
                    <div className="flex items-center gap-3">
                      {/* Quantity Controls */}
                      <div className="flex items-center border border-gray-300 rounded-lg overflow-hidden bg-white">
                        <button
                          onClick={() => onUpdateQuantity(item.product.id, item.quantity - 1)}
                          className="border-none bg-gray-100 px-3 py-2 cursor-pointer text-sm hover:bg-gray-200 transition-colors font-bold"
                        >
                          -
                        </button>
                        <span className="px-4 py-2 bg-white text-sm font-bold min-w-8 text-center">
                          {item.quantity}
                        </span>
                        <button
                          onClick={() => onUpdateQuantity(item.product.id, item.quantity + 1)}
                          className="border-none bg-gray-100 px-3 py-2 cursor-pointer text-sm hover:bg-gray-200 transition-colors font-bold"
                        >
                          +
                        </button>
                      </div>
                      <span className="font-bold text-gray-800 text-base">
                        ₫{(item.product.price * item.quantity).toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>
                
                {/* Delete Button */}
                <button
                  onClick={() => handleRemoveItem(item.product.id)}
                  className="absolute top-3 right-3 bg-red-500 text-white border-none rounded-full w-7 h-7 cursor-pointer flex items-center justify-center text-sm font-bold hover:bg-red-600 transition-colors"
                  title="Remove item"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Cost Breakdown */}
      <div className="p-6 border-t border-gray-200 bg-gray-50">
        <div className="space-y-3 mb-6">
          <div className="flex justify-between text-base">
            <span className="font-medium">Subtotal:</span>
            <span className="font-bold">₫{subtotal.toLocaleString()}</span>
          </div>
          <div className="flex justify-between text-base">
            <span className="font-medium">Shipping:</span>
            <span className="text-green-600 font-bold">FREE</span>
          </div>
          <div className="flex justify-between text-base">
            <span className="font-medium">Taxes:</span>
            <span className="font-bold">₫{taxes.toLocaleString()}</span>
          </div>
        </div>
        <div className="flex justify-between border-t-2 border-gray-300 pt-4 text-xl font-bold">
          <span>Total:</span>
          <span>₫{total.toLocaleString()}</span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="p-6 bg-white border-t border-gray-200 rounded-bl-3xl">
        <div className="space-y-3">
          <button 
            onClick={onCheckout}
            disabled={cartItems.length === 0}
            className={`w-full text-white border-none rounded-xl py-4 text-lg font-bold transition-all duration-300 ${
              cartItems.length === 0 
                ? 'bg-gray-400 cursor-not-allowed' 
                : 'bg-green-600 cursor-pointer hover:bg-green-700 shadow-lg hover:shadow-xl'
            }`}
          >
            Checkout
          </button>
        </div>
      </div>
    </div>
  );
};

export default Summary;
