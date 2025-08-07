import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Github, Linkedin } from 'lucide-react';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  const socialLinks = [
    {
      name: 'GitHub',
      icon: Github,
      url: 'https://github.com/BengisuEkizoglu',
      color: 'hover:text-gray-800'
    },
    {
      name: 'LinkedIn',
      icon: Linkedin,
      url: 'https://www.linkedin.com/in/bengisuekizoglu/',
      color: 'hover:text-blue-600'
    }
  ];

  const quickLinks = [
    { name: 'Home', url: '/' },
    { name: 'Mood Board', url: '/mood-board' }
  ];

  return (
    <footer className="bg-gray-900/50 border-t border-gray-700 mt-20">
      <div className="container mx-auto px-4 py-12">
        <div className="grid md:grid-cols-3 gap-8">
          {/* Brand Section */}
          <div className="md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <motion.div
                whileHover={{ rotate: 360 }}
                transition={{ duration: 0.6 }}
                className="w-10 h-10 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl flex items-center justify-center"
              >
                <Sparkles className="w-6 h-6 text-white" />
              </motion.div>
              <div>
                <h3 className="text-xl font-bold gradient-text">AI Mood Board</h3>
                <p className="text-sm text-gray-400">AI-Powered Inspiration Board</p>
              </div>
            </div>
            
            <p className="text-gray-400 mb-6 max-w-md">
              Analyze your emotions and mood with AI to create personalized 
              visual inspiration boards. Discover your creativity.
            </p>
            
            <div className="flex space-x-4">
              {socialLinks.map((social) => (
                <motion.a
                  key={social.name}
                  href={social.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  whileHover={{ scale: 1.1, y: -2 }}
                  whileTap={{ scale: 0.9 }}
                  className={`w-10 h-10 bg-gray-800 hover:bg-gray-700 rounded-lg flex items-center justify-center transition-all duration-300 ${social.color}`}
                >
                  <social.icon className="w-5 h-5" />
                </motion.a>
              ))}
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-lg font-semibold text-gray-200 mb-4">Quick Links</h4>
            <ul className="space-y-2">
              {quickLinks.map((link) => (
                <li key={link.name}>
                  <a
                    href={link.url}
                    className="text-gray-400 hover:text-purple-400 transition-colors duration-300"
                  >
                    {link.name}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="border-t border-gray-700 mt-8 pt-8">
          <p className="text-gray-400 text-sm text-center">
            © {currentYear} AI Mood Board. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 