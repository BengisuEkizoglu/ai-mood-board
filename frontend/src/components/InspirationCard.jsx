import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Copy, Check, Heart } from 'lucide-react';

const InspirationCard = ({ text, onCopy, copied }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="card p-8 bg-gradient-to-r from-purple-900/30 to-pink-900/30 border-purple-700/50"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-2">
          <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-200">Inspiration Text</h3>
            <p className="text-sm text-gray-400">Specially created by AI</p>
          </div>
        </div>
        
        <motion.button
          onClick={onCopy}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="flex items-center space-x-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg shadow-sm border border-gray-600 transition-all duration-300"
        >
          {copied ? (
            <>
              <Check className="w-4 h-4 text-green-600" />
              <span className="text-sm text-green-400 font-medium">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-4 h-4 text-gray-300" />
              <span className="text-sm text-gray-300">Copy</span>
            </>
          )}
        </motion.button>
      </div>
      
      <div className="relative">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="text-lg md:text-xl text-gray-200 leading-relaxed italic font-medium"
        >
          "{text}"
        </motion.div>
        
        {/* Decorative elements */}
        <div className="absolute -top-2 -left-2 text-4xl text-purple-400 opacity-30">
          "
        </div>
        <div className="absolute -bottom-2 -right-2 text-4xl text-purple-400 opacity-30">
          "
        </div>
      </div>
      
      <div className="mt-6 flex items-center justify-between">
        <div className="flex items-center space-x-2 text-sm text-gray-400">
          <Heart className="w-4 h-4 text-red-400" />
          <span>This text was generated specifically for your mood</span>
        </div>
        
        <div className="flex items-center space-x-1">
          <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></div>
          <div className="w-2 h-2 bg-pink-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
          <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
        </div>
      </div>
    </motion.div>
  );
};

export default InspirationCard; 