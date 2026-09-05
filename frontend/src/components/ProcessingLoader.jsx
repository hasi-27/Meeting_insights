import React from 'react';

export function ProcessingLoader({ status, message }) {
    return (
        <div className="flex flex-col items-center justify-center py-12">
            <div className="relative w-16 h-16 mb-4">
                <div className="absolute inset-0 border-4 border-gray-200 rounded-full"></div>
                <div className="absolute inset-0 border-4 border-transparent border-t-blue-500 rounded-full animate-spin"></div>
            </div>
            <p className="text-lg font-semibold text-gray-900">{status}</p>
            {message && <p className="text-sm text-gray-600 mt-2">{message}</p>}
        </div>
    );
}
