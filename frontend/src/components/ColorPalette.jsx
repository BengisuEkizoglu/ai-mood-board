import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Palette, Copy, Check } from 'lucide-react';
import toast from 'react-hot-toast';

const ColorPalette = ({ colors }) => {
  const [copiedColor, setCopiedColor] = useState(null);

  const handleCopyColor = async (color, index) => {
    try {
      await navigator.clipboard.writeText(color);
      setCopiedColor(index);
      toast.success(`${color} copied!`);
      setTimeout(() => setCopiedColor(null), 2000);
    } catch (error) {
      toast.error('Color could not be copied');
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="card p-8"
    >
      <div className="flex items-center space-x-2 mb-6">
        <Palette className="w-6 h-6 text-primary-600" />
        <h3 className="text-2xl font-bold text-gray-200">Color Palette</h3>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {colors.map((color, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4, delay: index * 0.1 }}
            className="group relative"
          >
            <div
              className="w-full h-24 rounded-xl shadow-lg cursor-pointer transition-all duration-300 hover:scale-105 hover:shadow-xl"
              style={{ backgroundColor: color }}
              onClick={() => handleCopyColor(color, index)}
            >
              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-300 rounded-xl flex items-center justify-center">
                {copiedColor === index ? (
                  <Check className="w-6 h-6 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                ) : (
                  <Copy className="w-6 h-6 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                )}
              </div>
            </div>
            <div className="mt-2 text-center">
              <p className="text-sm font-mono text-gray-300">{color}</p>
            </div>
          </motion.div>
        ))}
      </div>
      
      <div className="mt-6 p-4 bg-gray-800 rounded-xl">
        <p className="text-sm text-gray-300 text-center">
          💡 Click on colors to copy them. These colors were selected by AI based on your mood.
        </p>
      </div>
    </motion.div>
  );
};

export default ColorPalette; 