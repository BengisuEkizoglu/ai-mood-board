import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ExternalLink, Download, Heart, Sparkles } from 'lucide-react';
import toast from 'react-hot-toast';

const ImageGrid = ({ images }) => {
  const [selectedImage, setSelectedImage] = useState(null);

  const handleImageClick = (image) => {
    setSelectedImage(image);
  };

  const handleDownload = async (imageUrl, imageName) => {
    try {
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${imageName || 'mood-board-image'}.jpg`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('Görsel indirildi!');
    } catch (error) {
      toast.error('Görsel indirilemedi');
    }
  };

  const handleExternalLink = (imageUrl) => {
    window.open(imageUrl, '_blank');
  };

  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {images.map((image, index) => (
          <motion.div
            key={image.id || index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            className="group relative overflow-hidden rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
          >
            <div className="relative">
              <img
                src={image.urls?.regular || image.url}
                alt={image.alt_description || 'Mood board image'}
                className="w-full h-64 object-cover cursor-pointer transition-transform duration-300 group-hover:scale-105"
                onClick={() => handleImageClick(image)}
                loading="lazy"
              />
              
              {/* AI Generated Badge */}
              {image.isAIGenerated && (
                <div className="absolute top-3 left-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-3 py-1 rounded-full text-xs font-medium flex items-center space-x-1">
                  <Sparkles className="w-3 h-3" />
                  <span>AI Üretimi</span>
                </div>
              )}
              
              {/* Overlay with actions */}
              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all duration-300 flex items-center justify-center">
                <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex space-x-2">
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => handleDownload(image.urls?.regular || image.url, image.alt_description)}
                    className="bg-white text-gray-800 p-2 rounded-full shadow-lg hover:bg-gray-100 transition-colors"
                    title="İndir"
                  >
                    <Download className="w-4 h-4" />
                  </motion.button>
                  
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => handleExternalLink(image.urls?.regular || image.url)}
                    className="bg-white text-gray-800 p-2 rounded-full shadow-lg hover:bg-gray-100 transition-colors"
                    title="Yeni sekmede aç"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </motion.button>
                  
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="bg-white text-gray-800 p-2 rounded-full shadow-lg hover:bg-gray-100 transition-colors"
                    title="Beğen"
                  >
                    <Heart className="w-4 h-4" />
                  </motion.button>
                </div>
              </div>
            </div>
            
            {/* Image info */}
            <div className="p-4 bg-white">
              <p className="text-sm text-gray-600 line-clamp-2">
                {image.alt_description || 'Mood board görseli'}
              </p>
              {image.user?.name && (
                <p className="text-xs text-gray-500 mt-1">
                  Fotoğrafçı: {image.user.name}
                </p>
              )}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Image Modal */}
      <AnimatePresence>
        {selectedImage && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
            onClick={() => setSelectedImage(null)}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="relative max-w-4xl max-h-[90vh] bg-white rounded-2xl overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              <img
                src={selectedImage.urls?.regular || selectedImage.url}
                alt={selectedImage.alt_description || 'Mood board image'}
                className="w-full h-auto max-h-[70vh] object-contain"
              />
              
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">
                  {selectedImage.alt_description || 'Mood board görseli'}
                </h3>
                {selectedImage.user?.name && (
                  <p className="text-gray-600 mb-4">
                    Fotoğrafçı: {selectedImage.user.name}
                  </p>
                )}
                
                <div className="flex space-x-3">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleDownload(selectedImage.urls?.regular || selectedImage.url, selectedImage.alt_description)}
                    className="btn-primary flex items-center space-x-2"
                  >
                    <Download className="w-4 h-4" />
                    <span>İndir</span>
                  </motion.button>
                  
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleExternalLink(selectedImage.urls?.regular || selectedImage.url)}
                    className="btn-secondary flex items-center space-x-2"
                  >
                    <ExternalLink className="w-4 h-4" />
                    <span>Yeni Sekmede Aç</span>
                  </motion.button>
                </div>
              </div>
              
              <button
                onClick={() => setSelectedImage(null)}
                className="absolute top-4 right-4 bg-white bg-opacity-80 hover:bg-opacity-100 p-2 rounded-full transition-all duration-300"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default ImageGrid; 