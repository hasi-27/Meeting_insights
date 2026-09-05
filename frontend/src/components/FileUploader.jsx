import React, { useState } from 'react';

export function FileUploader({ onFileSelect, isProcessing }) {
    const [dragActive, setDragActive] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true);
        } else if (e.type === 'dragleave') {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        const files = e.dataTransfer.files;
        if (files && files[0]) {
            setSelectedFile(files[0]);
            onFileSelect(files[0]);
        }
    };

    const handleChange = (e) => {
        const files = e.target.files;
        if (files && files[0]) {
            setSelectedFile(files[0]);
            onFileSelect(files[0]);
        }
    };

    return (
        <div
            className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${dragActive
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 bg-gray-50'
                }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
        >
            <svg
                className="mx-auto h-12 w-12 text-gray-400"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 48 48"
            >
                <path
                    d="M28 8H12a4 4 0 00-4 4v20a4 4 0 004 4h24a4 4 0 004-4V16z"
                    strokeWidth={2}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                />
            </svg>

            <p className="mt-2 text-sm text-gray-600">
                <label className="relative cursor-pointer rounded-md font-medium text-blue-600 hover:text-blue-500">
                    <span>Click to upload</span>
                    <input
                        type="file"
                        className="sr-only"
                        onChange={handleChange}
                        accept=".mp3,.wav,.m4a,.mp4"
                        disabled={isProcessing}
                    />
                </label>
                {' or drag and drop'}
            </p>

            <p className="text-xs text-gray-500 mt-1">
                MP3, WAV, M4A, or MP4 up to 500MB
            </p>

            {selectedFile && (
                <div className="mt-4 p-3 bg-white rounded border border-gray-200">
                    <p className="text-sm font-medium text-gray-700">
                        Selected: {selectedFile.name}
                    </p>
                    <p className="text-xs text-gray-500">
                        Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                </div>
            )}
        </div>
    );
}
