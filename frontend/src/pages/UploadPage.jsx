import React, { useState } from 'react';
import { FileUploader } from '../components/FileUploader';
import { meetingsAPI } from '../services/api';

export function UploadPage({ onMeetingCreated }) {
    const [selectedFile, setSelectedFile] = useState(null);
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState(null);

    const handleFileSelect = (file) => {
        setSelectedFile(file);
        setError(null);
    };

    const handleUpload = async () => {
        if (!selectedFile) {
            setError('Please select a file');
            return;
        }

        setIsUploading(true);
        setError(null);

        try {
            const response = await meetingsAPI.uploadMeeting(selectedFile);
            const { meeting_id } = response.data;
            onMeetingCreated(meeting_id);
        } catch (err) {
            setError(err.response?.data?.detail || 'Upload failed. Please try again.');
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
            <div className="max-w-2xl mx-auto px-4 py-16">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">
                        🎙️ AI Meeting Insights
                    </h1>
                    <p className="text-xl text-gray-600">
                        Upload a meeting recording and get instant insights
                    </p>
                </div>

                <FileUploader
                    onFileSelect={handleFileSelect}
                    isProcessing={isUploading}
                />

                {error && (
                    <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                        <p className="text-red-700">{error}</p>
                    </div>
                )}

                <button
                    onClick={handleUpload}
                    disabled={!selectedFile || isUploading}
                    className="w-full mt-6 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 rounded-lg transition-colors"
                >
                    {isUploading ? 'Uploading...' : 'Upload & Analyze'}
                </button>

                <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="p-4 text-center">
                        <p className="text-3xl mb-2">⚡</p>
                        <p className="font-semibold text-gray-900">Fast Processing</p>
                        <p className="text-sm text-gray-600">Get results in minutes</p>
                    </div>
                    <div className="p-4 text-center">
                        <p className="text-3xl mb-2">🎯</p>
                        <p className="font-semibold text-gray-900">Smart Insights</p>
                        <p className="text-sm text-gray-600">AI-powered analysis</p>
                    </div>
                    <div className="p-4 text-center">
                        <p className="text-3xl mb-2">👥</p>
                        <p className="font-semibold text-gray-900">Speaker Tracking</p>
                        <p className="text-sm text-gray-600">Know who said what</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
