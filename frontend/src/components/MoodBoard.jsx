import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, 
  Palette, 
  Image, 
  Download, 
  Share2, 
  Heart,
  Loader2,
  Wand2,
  RefreshCw,
  Copy,
  Check
} from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';
import ColorPalette from './ColorPalette';
import ImageGrid from './ImageGrid';
import InspirationCard from './InspirationCard';

const MoodBoard = () => {
  const [description, setDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [moodBoard, setMoodBoard] = useState(null);
  const [copied, setCopied] = useState(false);
  const [examplePrompts, setExamplePrompts] = useState([
    "I want to feel like walking in the streets of Paris in autumn",
    "Looking for inspiration for a minimalist and modern office design", 
    "I want to create a romantic dinner atmosphere",
    "A peaceful living space concept in harmony with nature",
    "An energetic and dynamic gym design"
  ]);
  const [promptCategory, setPromptCategory] = useState('mixed');
  const [isLoadingPrompts, setIsLoadingPrompts] = useState(false);

  // Load example prompts on component mount with timeout
  useEffect(() => {
    const loadExamplePrompts = async () => {
      setIsLoadingPrompts(true);
      try {
        // Add timeout to prevent hanging
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 second timeout
        
        const response = await axios.get('/api/example-prompts', {
          signal: controller.signal,
          timeout: 3000
        });
        
        clearTimeout(timeoutId);
        setExamplePrompts(response.data.prompts);
        setPromptCategory(response.data.category);
      } catch (error) {
        console.error('Error loading example prompts:', error);
        // Keep existing static prompts if API fails
      } finally {
        setIsLoadingPrompts(false);
      }
    };

    // Small delay to ensure component is fully mounted
    const timer = setTimeout(loadExamplePrompts, 100);
    return () => clearTimeout(timer);
  }, []);

  const handleAnalyzeMood = async () => {
    if (!description.trim()) {
        toast.error('Please enter a description');
      return;
    }

    setIsLoading(true);
    try {
      const response = await axios.post('/api/analyze-mood', {
        description: description.trim(),
        style: 'modern'
      });

      setMoodBoard(response.data);
      toast.success('Mood board created successfully!');
    } catch (error) {
      console.error('Error analyzing mood:', error);
      toast.error('An error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateImage = async () => {
    if (!moodBoard) return;

    try {
      const response = await axios.post('/api/generate-image', {
        prompt: description,
        style: 'realistic'
      });

      // Add the generated image to the mood board
      setMoodBoard(prev => ({
        ...prev,
        images: [...prev.images, {
          id: 'ai_generated',
          urls: { regular: response.data.url },
          alt_description: 'AI Generated Image',
          user: { name: 'AI Generated' },
          isAIGenerated: true
        }]
      }));

      toast.success('AI image generated successfully!');
    } catch (error) {
      console.error('Error generating image:', error);
      toast.error('Error occurred while generating image.');
    }
  };

  const handleSaveBoard = async () => {
    if (!moodBoard) return;

    try {
      await axios.post('/api/save-board', {
        description,
        moodBoard,
        timestamp: new Date().toISOString()
      });
      toast.success('Mood board saved!');
    } catch (error) {
      console.error('Error saving board:', error);
      toast.error('Error occurred while saving.');
    }
  };

  const handleCopyInspiration = () => {
    if (moodBoard?.inspiration_text) {
      navigator.clipboard.writeText(moodBoard.inspiration_text);
      setCopied(true);
      toast.success('Inspiration text copied!');
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleReset = () => {
    setDescription('');
    setMoodBoard(null);
    setCopied(false);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="gradient-text">Create Mood Board</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Define your emotions and mood, let AI create a personalized inspiration board for you
          </p>
        </motion.div>
      </div>

      {/* Input Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="card p-8"
      >
        <div className="space-y-6">
          <div>
            <label className="block text-lg font-semibold text-gray-200 mb-3">
              Your Mood Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
                              placeholder="Example: I want to feel like walking in the streets of Paris in autumn..."
              className="input-field h-32 resize-none"
              disabled={isLoading}
            />
          </div>

          {/* Example Prompts */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <p className="text-sm text-gray-400">Example descriptions:</p>
              <div className="flex items-center gap-2">
                {isLoadingPrompts && (
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-3 border border-purple-400 border-t-transparent rounded-full animate-spin"></div>
                    <span className="text-xs text-purple-400">Loading...</span>
                  </div>
                )}
                {promptCategory && promptCategory !== 'mixed' && !isLoadingPrompts && (
                  <span className="text-xs bg-purple-900/50 text-purple-300 px-2 py-1 rounded-full border border-purple-700/50">
                    {promptCategory} theme
                  </span>
                )}
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              {examplePrompts.map((prompt, index) => (
                <button
                  key={index}
                  onClick={() => setDescription(prompt)}
                  className="text-sm bg-gray-700 hover:bg-gray-600 text-gray-200 px-3 py-1 rounded-full transition-colors"
                  disabled={isLoadingPrompts}
                >
                  {prompt.length > 40 ? prompt.substring(0, 40) + '...' : prompt}
                </button>
              ))}
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-4">
            <motion.button
              onClick={handleAnalyzeMood}
              disabled={isLoading || !description.trim()}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="btn-primary flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  <span>Create Mood Board</span>
                </>
              )}
            </motion.button>

            {moodBoard && (
              <motion.button
                onClick={handleReset}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="btn-secondary flex items-center justify-center space-x-2"
              >
                <RefreshCw className="w-5 h-5" />
                                  <span>Start Over</span>
              </motion.button>
            )}
          </div>
        </div>
      </motion.div>

      {/* Mood Board Results */}
      <AnimatePresence>
        {moodBoard && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.6 }}
            className="space-y-8"
          >
            {/* Inspiration Text */}
            <InspirationCard
              text={moodBoard.inspiration_text}
              onCopy={handleCopyInspiration}
              copied={copied}
            />

            {/* Color Palette */}
            <ColorPalette colors={moodBoard.color_palette} />

            {/* Images */}
            <div className="card p-8">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-gray-200 flex items-center space-x-2">
                  <Image className="w-6 h-6" />
                  <span>Image Suggestions</span>
                </h3>
                <div className="flex space-x-3">
                  <motion.button
                    onClick={handleGenerateImage}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="btn-secondary flex items-center space-x-2"
                  >
                    <Wand2 className="w-4 h-4" />
                    <span>Generate AI Image</span>
                  </motion.button>
                  <motion.button
                    onClick={handleSaveBoard}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="btn-primary flex items-center space-x-2"
                  >
                    <Heart className="w-4 h-4" />
                    <span>Save</span>
                  </motion.button>
                </div>
              </div>
              <ImageGrid images={moodBoard.images} />
            </div>

            {/* Mood Analysis */}
            <div className="card p-8 bg-gray-800/70 backdrop-blur-sm">
              <h3 className="text-2xl font-bold text-gray-200 mb-4 flex items-center space-x-2">
                <Sparkles className="w-6 h-6" />
                                  <span>Mood Analysis</span>
              </h3>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                                      <h4 className="font-semibold text-gray-300 mb-2">Detected Mood:</h4>
                  <p className="text-lg text-purple-400 font-medium capitalize">
                    {moodBoard.mood_analysis.mood}
                  </p>
                </div>
                <div>
                                      <h4 className="font-semibold text-gray-300 mb-2">Keywords:</h4>
                  <div className="flex flex-wrap gap-2">
                    {moodBoard.mood_analysis.keywords.map((keyword, index) => {
                      const colors = [
                        "bg-purple-900/50 text-purple-300 border-purple-700/50",
                        "bg-pink-900/50 text-pink-300 border-pink-700/50",
                        "bg-blue-900/50 text-blue-300 border-blue-700/50",
                        "bg-green-900/50 text-green-300 border-green-700/50",
                        "bg-yellow-900/50 text-yellow-300 border-yellow-700/50",
                        "bg-red-900/50 text-red-300 border-red-700/50",
                        "bg-indigo-900/50 text-indigo-300 border-indigo-700/50",
                        "bg-teal-900/50 text-teal-300 border-teal-700/50"
                      ];
                      const colorClass = colors[index % colors.length];
                      
                      return (
                        <span
                          key={index}
                          className={`${colorClass} px-3 py-1 rounded-full text-sm border`}
                        >
                          {keyword}
                        </span>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default MoodBoard; 