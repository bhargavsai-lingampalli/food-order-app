import React, { useState, useEffect } from 'react';
import { ShoppingCart, Plus, Minus, X, Bell, Check, Clock, ChefHat, Users } from 'lucide-react';
import './App.css';

// Backend API base URL
const API_BASE = 'http://localhost:8000';

// API utility functions
async function fetchMenu() {
  const res = await fetch(`${API_BASE}/menu`);
  if (!res.ok) throw new Error('Failed to fetch menu');
  return res.json();
}

async function placeOrder(order: any) {
  const res = await fetch(`${API_BASE}/order`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(order),
  });
  if (!res.ok) throw new Error('Failed to place order');
  return res.json();
}

async function fetchOrders() {
  const res = await fetch(`${API_BASE}/order`);
  if (!res.ok) throw new Error('Failed to fetch orders');
  return res.json();
}

async function updateOrderStatus(orderId: number, status: string) {
  const res = await fetch(`${API_BASE}/order/${orderId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error('Failed to update order');
  return res.json();
}

interface MenuItem {
  id: number;
  name: string;
  price: number;
}

interface MenuData {
  [category: string]: MenuItem[];
}

interface Order {
  id: number;
  customerInfo: {
    name: string;
    phone: string;
    table: string;
  };
  items: CartItem[];
  total: number;
  timestamp: string;
  status: string;
}

type CartItem = {
  id: number;
  name: string;
  price: number;
  quantity: number;
};

const App = () => {
  const [currentView, setCurrentView] = useState('customer'); // 'customer' or 'chef'
  const [showCart, setShowCart] = useState(false);
  const [customerInfo, setCustomerInfo] = useState({ name: '', phone: '', table: '' });
  const [orderPlaced, setOrderPlaced] = useState(false);
  const [menuData, setMenuData] = useState<MenuData>({
    "ICE CREAM": [
      { id: 1, name: "Vanilla", price: 39 },
      { id: 2, name: "Butterscotch", price: 49 },
      { id: 3, name: "Chocolate", price: 59 },
      { id: 4, name: "Black Current", price: 69 },
      { id: 5, name: "American Dryfruit", price: 79 },
    ],
    "BUTTERMILK": [
      { id: 6, name: "Classic Buttermilk", price: 29 },
      { id: 7, name: "Masala Buttermilk", price: 39 },
    ],
    "LASSI": [
      { id: 8, name: "Sweet Lassi", price: 39 },
      { id: 9, name: "Banana Lassi", price: 39 },
      { id: 10, name: "Mango Lassi", price: 39 },
      { id: 11, name: "Strawberry Lassi", price: 39 },
      { id: 12, name: "Chocolate Lassi", price: 49 },
      { id: 13, name: "Dry Fruit Lassi", price: 69 },
    ],
    "SNACKS": [
      { id: 14, name: "French Fries Small", price: 59 },
      { id: 15, name: "Veg Steamed Momos", price: 79 },
      { id: 16, name: "Veg Fried Momos", price: 89 },
      { id: 17, name: "Paneer Steamed Momos", price: 89 },
      { id: 18, name: "Paneer Fried Momos", price: 99 },
      { id: 19, name: "Chicken Steamed Momos", price: 99 },
      { id: 20, name: "French Fries Large", price: 99 },
      { id: 21, name: "Chicken Nuggets", price: 99 },
      { id: 22, name: "Chicken Fried Momos", price: 119 },
    ],
    "MAGGIE": [
      { id: 23, name: "Veg Maggie", price: 49 },
      { id: 24, name: "Egg Maggie", price: 59 },
    ],
    "SIZZLING BROWNIE": [
      { id: 25, name: "Sizzling Brownie", price: 139 },
    ],
    "COMBO OFFER": [
      { id: 26, name: "French Fries + Matka Soda (Any Single Flavoured)", price: 79 },
      { id: 27, name: "Maggie + Mocktail (Any Single Flavoured)", price: 89 },
      { id: 28, name: "French Fries + Mocktail (Any Single Flavoured)", price: 99 },
      { id: 29, name: "Veg Steamed momos + Mocktail (Any Single Flavoured)", price: 109 },
      { id: 30, name: "French Fries + Butterscotch Shake", price: 99 },
      { id: 31, name: "Chicken Steamed momos + Mocktail (Any Single Flavoured)", price: 129 },
      { id: 32, name: "Chicken Fried Momos + Oreo Shake", price: 169 },
    ]
  });
  const [orders, setOrders] = useState<Order[]>([
    {
      id: 1,
      customerInfo: {
        name: "John Doe",
        phone: "123-456-7890",
        table: "1"
      },
      items: [
        { id: 1, name: "Vanilla", price: 39, quantity: 2 },
        { id: 2, name: "Butterscotch", price: 49, quantity: 1 }
      ],
      total: 127,
      timestamp: "2025-06-01 17:00:00",
      status: "pending"
    }
  ]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch menu for customer view
  useEffect(() => {
    if (currentView === 'customer') {
      setLoading(true);
      fetchMenu()
        .then(data => setMenuData(data))
        .catch(() => setError('Failed to load menu'))
        .finally(() => setLoading(false));
    }
  }, [currentView]);

  // Fetch orders for chef view
  useEffect(() => {
    if (currentView === 'chef') {
      setLoading(true);
      fetchOrders()
        .then(data => setOrders(data))
        .catch(() => setError('Failed to load orders'))
        .finally(() => setLoading(false));
    }
  }, [currentView]);

  // Add to cart handler
  const addToCart = (item: MenuItem) => {
    setCart(prev => {
      const found = prev.find(ci => ci.id === item.id);
      if (found) {
        return prev.map(ci => ci.id === item.id ? { ...ci, quantity: ci.quantity + 1 } : ci);
      }
      return [...prev, { ...item, quantity: 1 }];
    });
  };

  // Remove from cart handler
  const removeFromCart = (id: number) => {
    setCart(prev => prev.filter(ci => ci.id !== id));
  };

  // Update quantity handler
  const updateQuantity = (id: number, delta: number) => {
    setCart(prev => prev.map(ci => ci.id === id ? { ...ci, quantity: Math.max(1, ci.quantity + delta) } : ci));
  };

  // Place order handler
  const handlePlaceOrder = async () => {
    if (!customerInfo.name || !customerInfo.phone || !customerInfo.table || cart.length === 0) {
      setError('Please fill all details and add items to cart.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await placeOrder({ customerInfo, items: cart });
      setOrderPlaced(true);
      setCart([]);
    } catch {
      setError('Failed to place order');
    } finally {
      setLoading(false);
    }
  };

  const CustomerView = () => (
    <div className="min-h-screen" style={{ background: 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)' }}>
      {/* Decorative Header */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23B8860B' fill-opacity='0.1'%3E%3Cpath d='M30 30c0-11.046-8.954-20-20-20s-20 8.954-20 20 8.954 20 20 20 20-8.954 20-20zm0 0c0 11.046 8.954 20 20 20s20-8.954 20-20-8.954-20-20-20-20 8.954-20 20z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }} />
        <div className="relative px-4 py-8">
          <div className="text-center mb-6">
            <div className="flex justify-center items-center mb-4">
              <div className="text-6xl text-red-800 font-extrabold tracking-wider" style={{ fontFamily: 'serif' }}>
                MOCKTAIL LOUNGE
              </div>
            </div>
            <div className="text-2xl text-red-800 italic font-semibold">
              More than Mocktail.....
            </div>
          </div>
          {/* Menu Section */}
          <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-6">
            {Object.entries(menuData).map(([category, items]) => (
              <div key={category} className="bg-white rounded-lg shadow p-4">
                <h2 className="text-xl font-bold text-yellow-700 mb-2">{category}</h2>
                <ul>
                  {items.map(item => (
                    <li key={item.id} className="flex justify-between items-center py-2 border-b last:border-b-0">
                      <span>{item.name} <span className="text-gray-500">₹{item.price}</span></span>
                      <button className="bg-yellow-400 px-3 py-1 rounded text-red-800 font-bold hover:bg-yellow-500" onClick={() => addToCart(item)}>
                        <Plus size={16} />
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          {/* Cart Button */}
          <button className="fixed bottom-8 right-8 bg-red-800 text-white p-4 rounded-full shadow-lg flex items-center gap-2" onClick={() => setShowCart(true)}>
            <ShoppingCart />
            Cart ({cart.reduce((sum, ci) => sum + ci.quantity, 0)})
          </button>
          {/* Cart Sidebar */}
          {showCart && (
            <div className="fixed inset-0 bg-black bg-opacity-40 flex justify-end z-50">
              <div className="bg-white w-96 h-full p-6 shadow-lg relative">
                <button className="absolute top-4 right-4" onClick={() => setShowCart(false)}><X /></button>
                <h2 className="text-xl font-bold mb-4">Your Cart</h2>
                {cart.length === 0 ? <div className="text-gray-500">Cart is empty</div> : (
                  <ul>
                    {cart.map(item => (
                      <li key={item.id} className="flex justify-between items-center py-2 border-b last:border-b-0">
                        <span>{item.name} (x{item.quantity})</span>
                        <div className="flex items-center gap-2">
                          <button onClick={() => updateQuantity(item.id, -1)} className="bg-gray-200 px-2 rounded"><Minus size={14} /></button>
                          <button onClick={() => updateQuantity(item.id, 1)} className="bg-gray-200 px-2 rounded"><Plus size={14} /></button>
                          <button onClick={() => removeFromCart(item.id)} className="text-red-500"><X size={14} /></button>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
                <div className="mt-4 font-bold">Total: ₹{cart.reduce((sum, ci) => sum + ci.price * ci.quantity, 0)}</div>
                {/* Order Form */}
                <div className="mt-6">
                  <h3 className="font-semibold mb-2">Customer Details</h3>
                  <input className="w-full mb-2 p-2 border rounded" placeholder="Name" value={customerInfo.name} onChange={e => setCustomerInfo({ ...customerInfo, name: e.target.value })} />
                  <input className="w-full mb-2 p-2 border rounded" placeholder="Phone" value={customerInfo.phone} onChange={e => setCustomerInfo({ ...customerInfo, phone: e.target.value })} />
                  <input className="w-full mb-2 p-2 border rounded" placeholder="Table No." value={customerInfo.table} onChange={e => setCustomerInfo({ ...customerInfo, table: e.target.value })} />
                  <button className="w-full bg-yellow-400 text-red-800 font-bold py-2 rounded mt-2" onClick={handlePlaceOrder} disabled={loading}>
                    {loading ? 'Placing Order...' : 'Place Order'}
                  </button>
                  {error && <div className="text-red-600 mt-2">{error}</div>}
                  {orderPlaced && <div className="text-green-600 mt-2">Order placed successfully!</div>}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const ChefView = () => (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-yellow-400 shadow-sm border-b-4 border-red-800">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-red-800 flex items-center gap-2">
            <ChefHat size={28} />
            Mocktail Lounge - Chef Dashboard
          </h1>
        </div>
      </header>
    </div>
  );

  return currentView === 'customer' ? <CustomerView /> : <ChefView />;
};

export default App;
