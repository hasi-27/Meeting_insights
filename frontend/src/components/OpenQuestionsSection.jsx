import React from 'react';

export function OpenQuestionsSection({ questions }) {
    if (!questions || questions.length === 0) {
        return (
            <div className="bg-white rounded-lg shadow p-6 mb-8 border-l-4 border-red-500">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">❓ Open Questions</h2>
                <p className="text-gray-600">No clear open questions identified.</p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow p-6 mb-8 border-l-4 border-red-500">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">❓ Open Questions</h2>
            <ul className="space-y-2">
                {questions.map((question, index) => (
                    <li key={index} className="flex gap-3 p-3 bg-red-50 rounded">
                        <span className="text-red-600 font-bold">?</span>
                        <p className="text-gray-700">{question}</p>
                    </li>
                ))}
            </ul>
        </div>
    );
}
