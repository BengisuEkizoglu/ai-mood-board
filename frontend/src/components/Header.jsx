import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Menu, X, Sparkles, Palette } from 'lucide-react';

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();

  const navItems = [
    { name: 'Home', path: '/' },
    { name: 'Mood Board', path: '/mood-board' },
  ];

  return (
    <header className="bg-gray-900/80 backdrop-blur-md border-b border-gray-700 sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <motion.div
              whileHover={{ rotate: 360 }}
              transition={{ duration: 0.6 }}
              className="w-10 h-10 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl flex items-center justify-center"
            >
              <Sparkles className="w-6 h-6 text-white" />
            </motion.div>
            <div>
              <h1 className="text-xl font-bold gradient-text">AI Mood Board</h1>
              <p className="text-xs text-gray-400 -mt-1">AI-Powered Inspiration Board</p>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`relative px-3 py-2 rounded-lg font-medium transition-all duration-300 ${
                  location.pathname === item.path
                    ? 'text-purple-400 bg-purple-900/30'
                    : 'text-gray-300 hover:text-purple-400 hover:bg-gray-800'
                }`}
              >
                {item.name}
                {location.pathname === item.path && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute inset-0 bg-purple-900/30 rounded-lg -z-10"
                    initial={false}
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  />
                )}
              </Link>
            ))}
          </nav>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-gray-800 transition-colors"
          >
            {isMenuOpen ? (
              <X className="w-6 h-6 text-gray-600" />
            ) : (
              <Menu className="w-6 h-6 text-gray-600" />
            )}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden border-t border-gray-700 py-4"
          >
            <nav className="flex flex-col space-y-2">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setIsMenuOpen(false)}
                  className={`px-3 py-2 rounded-lg font-medium transition-all duration-300 ${
                    location.pathname === item.path
                      ? 'text-purple-400 bg-purple-900/30'
                      : 'text-gray-300 hover:text-purple-400 hover:bg-gray-800'
                  }`}
                >
                  {item.name}
                </Link>
              ))}
            </nav>
          </motion.div>
        )}
      </div>
    </header>
  );
};

export default Header; 