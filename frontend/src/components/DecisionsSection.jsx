import React from 'react';

export function DecisionsSection({ decisions }) {
    if (!decisions || decisions.length === 0) {
        return (
            <div className="bg-white rounded-lg shadow p-6 mb-8 border-l-4 border-purple-500">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">✅ Decisions</h2>
                <p className="text-gray-600">No clear decisions identified.</p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow p-6 mb-8 border-l-4 border-purple-500">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">✅ Decisions</h2>
            <div className="space-y-3">
                {decisions.map((item, index) => (
                    <div key={index} className="flex gap-3 p-3 bg-purple-50 rounded">
                        <span className="text-purple-600 font-bold">•</span>
                        <p className="text-gray-700">{item.decision}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
