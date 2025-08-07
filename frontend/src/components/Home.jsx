import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Sparkles, 
  Palette, 
  Image, 
  Brain, 
  Heart, 
  Zap,
  ArrowRight
} from 'lucide-react';

const Home = () => {
  const features = [
    {
      icon: Brain,
      title: "AI Mood Analysis",
      description: "Analyzes your emotions and mood using advanced AI to understand your creative vision"
    },
    {
      icon: Image,
      title: "Smart Visual Suggestions",
      description: "Generates beautiful, theme-matching images using AI"
    },
    {
      icon: Palette,
      title: "Automatic Color Palette",
      description: "Creates perfect color combinations that match your mood and style"
    },
    {
      icon: Heart,
      title: "Inspiration Text",
      description: "Generates personalized inspiring quotes and creative prompts"
    },
    {
      icon: Zap,
      title: "Instant Generation",
      description: "Creates your complete mood board in seconds with AI-powered tools"
    }
  ];

  return (
    <div className="space-y-20">
      {/* Hero Section */}
      <section className="text-center py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl mx-auto"
        >
          <div className="flex items-center justify-center mb-6">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="w-16 h-16 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl flex items-center justify-center mr-4"
            >
              <Sparkles className="w-8 h-8 text-white" />
            </motion.div>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            <span className="gradient-text">AI Mood Board</span>
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Analyze your emotions and mood with AI to create personalized 
            <span className="font-semibold text-purple-400"> visual inspiration boards</span>
          </p>
          
          <div className="flex justify-center">
            <Link to="/mood-board">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="btn-primary text-lg px-8 py-4 flex items-center space-x-2"
              >
                <span>Create Mood Board</span>
                <ArrowRight className="w-5 h-5" />
              </motion.button>
            </Link>
          </div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            <span className="gradient-text">Features</span>
          </h2>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            Discover your creativity with AI-powered features
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-7xl mx-auto justify-items-center">
          <div className="md:col-span-2 lg:col-span-3 grid md:grid-cols-2 lg:grid-cols-3 gap-8 w-full max-w-6xl">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="card p-8 hover:scale-105 bg-gray-800/70 backdrop-blur-sm"
            >
              <div className="w-14 h-14 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl flex items-center justify-center mb-6">
                <feature.icon className="w-7 h-7 text-white" />
              </div>
              <h3 className="text-xl font-semibold mb-4 text-gray-200">
                {feature.title}
              </h3>
              <p className="text-gray-300 leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-purple-600 to-pink-600 rounded-3xl text-white text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl mx-auto"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Discover Your Creativity
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Visualize your inspiration with AI-powered mood boards and 
            bring your creative projects to life
          </p>
          <Link to="/mood-board">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="bg-white text-purple-600 font-semibold py-4 px-8 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 flex items-center space-x-2 mx-auto"
            >
              <span>Get Started Now</span>
              <ArrowRight className="w-5 h-5" />
            </motion.button>
          </Link>
        </motion.div>
      </section>
    </div>
  );
};

export default Home; 