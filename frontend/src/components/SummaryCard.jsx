import React from 'react';

export function SummaryCard({ summary }) {
    return (
        <div className="bg-white rounded-lg shadow p-6 mb-8 border-l-4 border-green-500">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">📝 Meeting Summary</h2>
            <p className="text-gray-700 leading-relaxed">
                {summary || 'No summary available'}
            </p>
        </div>
    );
}
