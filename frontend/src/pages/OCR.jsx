import { useState } from 'react';
import { Upload, FileText, Image as ImageIcon, Loader } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';
import api from '../services/api';
import toast from 'react-hot-toast';

function OCR() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [ocrType, setOcrType] = useState('text'); // 'text', 'invoice', 'receipt'

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setResult(null);
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleOCR = async () => {
    if (!selectedFile) {
      toast.error('Please select an image file');
      return;
    }

    try {
      setLoading(true);
      const formData = new FormData();
      formData.append('image', selectedFile);

      let endpoint = '/ocr/ocr/extract-text/';
      if (ocrType === 'invoice') {
        endpoint = '/ocr/ocr/extract-invoice/';
      } else if (ocrType === 'receipt') {
        endpoint = '/ocr/ocr/extract-receipt/';
      }

      const response = await api.post(endpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data);
      toast.success('OCR completed successfully');
    } catch (error) {
      toast.error('OCR failed. Make sure Tesseract OCR is installed.');
      console.error('OCR error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout title="OCR - Text Extraction">
      <div className="p-6 space-y-6">
        <div className="card p-6">
          <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Upload Image for OCR</h2>
          
          {/* OCR Type Selection */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
              OCR Type
            </label>
            <select
              value={ocrType}
              onChange={(e) => setOcrType(e.target.value)}
              className="input-field w-full"
            >
              <option value="text">Extract Text</option>
              <option value="invoice">Extract Invoice Data</option>
              <option value="receipt">Extract Receipt Data</option>
            </select>
          </div>

          {/* File Upload */}
          <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center">
            <input
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="cursor-pointer flex flex-col items-center"
            >
              {preview ? (
                <img src={preview} alt="Preview" className="max-w-full max-h-64 mb-4 rounded" />
              ) : (
                <>
                  <Upload className="w-12 h-12 text-gray-400 mb-4" />
                  <p className="text-gray-600 dark:text-gray-400">
                    Click to upload or drag and drop
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
                    PNG, JPG, GIF up to 10MB
                  </p>
                </>
              )}
            </label>
          </div>

          {selectedFile && (
            <div className="mt-4">
              <button
                onClick={handleOCR}
                disabled={loading}
                className="btn-primary w-full"
              >
                {loading ? (
                  <>
                    <Loader className="w-4 h-4 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <FileText className="w-4 h-4 mr-2" />
                    Extract Text
                  </>
                )}
              </button>
            </div>
          )}

          {/* Results */}
          {result && (
            <div className="mt-6 space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Extracted Data:</h3>
              
              {result.success ? (
                <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                  {ocrType === 'text' && (
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Confidence: {result.confidence?.toFixed(2)}%</p>
                      <pre className="whitespace-pre-wrap text-sm text-gray-900 dark:text-white">
                        {result.text}
                      </pre>
                    </div>
                  )}
                  
                  {(ocrType === 'invoice' || ocrType === 'receipt') && result.extracted_data && (
                    <div className="space-y-2">
                      {result.extracted_data.invoice_number && (
                        <p><strong>Invoice Number:</strong> {result.extracted_data.invoice_number}</p>
                      )}
                      {result.extracted_data.date && (
                        <p><strong>Date:</strong> {result.extracted_data.date}</p>
                      )}
                      {result.extracted_data.total_amount && (
                        <p><strong>Total Amount:</strong> ₹{result.extracted_data.total_amount}</p>
                      )}
                      {result.extracted_data.vendor_name && (
                        <p><strong>Vendor:</strong> {result.extracted_data.vendor_name}</p>
                      )}
                      <div className="mt-4">
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Full Text:</p>
                        <pre className="whitespace-pre-wrap text-xs text-gray-900 dark:text-white bg-white dark:bg-gray-900 p-2 rounded">
                          {result.text}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                  <p className="text-red-800 dark:text-red-200">Error: {result.error}</p>
                  <p className="text-sm text-red-600 dark:text-red-400 mt-2">
                    Make sure Tesseract OCR is installed on your system.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}

export default OCR;






