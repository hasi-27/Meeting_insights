import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

export function SpeakerAnalytics({ speakers }) {
    if (!speakers || speakers.length === 0) {
        return (
            <div className="bg-white rounded-lg shadow p-6 mb-8 border-l-4 border-indigo-500">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">🎙️ Speaker Analytics</h2>
                <p className="text-gray-600">No speaker data available.</p>
            </div>
        );
    }

    // Data for talk time chart
    const talkTimeData = speakers.map((s) => ({
        name: s.speaker,
        minutes: Math.round(s.talk_time_seconds / 60),
    }));

    // Sentiment colors
    const sentimentColors = {
        positive: 'text-green-600',
        neutral: 'text-gray-600',
        negative: 'text-red-600',
    };

    return (
        <div className="bg-white rounded-lg shadow p-6 mb-8 border-l-4 border-indigo-500">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">🎙️ Speaker Analytics</h2>

            {/* Talk Time Chart */}
            <div className="mb-8">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Talk Time by Speaker</h3>
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={talkTimeData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis label={{ value: 'Minutes', angle: -90, position: 'insideLeft' }} />
                        <Tooltip />
                        <Bar dataKey="minutes" fill="#3B82F6" />
                    </BarChart>
                </ResponsiveContainer>
            </div>

            {/* Speaker Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {speakers.map((speaker, index) => (
                    <div key={index} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                        <h4 className="font-semibold text-gray-900 mb-3">{speaker.speaker}</h4>
                        <div className="space-y-2 text-sm">
                            <p className="text-gray-700">
                                <span className="font-medium">Talk Time:</span>{' '}
                                {Math.floor(speaker.talk_time_seconds / 60)}m{' '}
                                {speaker.talk_time_seconds % 60}s
                            </p>
                            <p className="text-gray-700">
                                <span className="font-medium">Meeting Share:</span> {speaker.talk_percentage.toFixed(1)}%
                            </p>
                            <p className="text-gray-700">
                                <span className="font-medium">Sentiment:</span>{' '}
                                <span className={`font-semibold capitalize ${sentimentColors[speaker.sentiment]}`}>
                                    {speaker.sentiment}
                                </span>
                            </p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
