import React, { useState } from 'react';

export function TranscriptViewer({ transcript }) {
    const [searchTerm, setSearchTerm] = useState('');

    const filteredTranscript = transcript?.filter(
        (item) =>
            item.text.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.speaker.toLowerCase().includes(searchTerm.toLowerCase())
    ) || [];

    if (!transcript || transcript.length === 0) {
        return (
            <div className="bg-white rounded-lg shadow p-6 border-l-4 border-cyan-500">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">📄 Full Transcript</h2>
                <p className="text-gray-600">No transcript available.</p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-cyan-500">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">📄 Full Transcript</h2>

            {/* Search */}
            <div className="mb-6">
                <input
                    type="text"
                    placeholder="Search transcript..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                />
            </div>

            {/* Transcript */}
            <div className="space-y-4 max-h-[600px] overflow-y-auto">
                {filteredTranscript.length === 0 ? (
                    <p className="text-gray-600">No results found.</p>
                ) : (
                    filteredTranscript.map((item, index) => (
                        <div key={index} className="flex gap-4 p-4 bg-gray-50 rounded-lg">
                            <div className="flex-shrink-0">
                                <p className="text-sm font-mono text-gray-500 min-w-[70px]">
                                    {item.timestamp}
                                </p>
                            </div>
                            <div className="flex-grow">
                                <p className="font-semibold text-gray-900">{item.speaker}</p>
                                <p className="text-gray-700 mt-1">{item.text}</p>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
