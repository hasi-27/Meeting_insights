import React from 'react';

export function OverviewCards({ meeting }) {
    const cards = [
        {
            label: 'Meeting Duration',
            value: meeting?.duration_seconds
                ? meeting.duration_seconds < 60
                    ? `${meeting.duration_seconds} sec`
                    : `${Math.floor(meeting.duration_seconds / 60)} min`
                : '-',
            icon: '⏱️',
        },
        {
            label: 'Number of Speakers',
            value: meeting?.speakers?.length || 0,
            icon: '👥',
        },
        {
            label: 'Decisions Made',
            value: meeting?.decisions?.length || 0,
            icon: '✅',
        },
        {
            label: 'Action Items',
            value: meeting?.action_items?.length || 0,
            icon: '📋',
        },
        {
            label: 'Open Questions',
            value: meeting?.open_questions?.length || 0,
            icon: '❓',
        },
    ];

    return (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
            {cards.map((card) => (
                <div
                    key={card.label}
                    className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500"
                >
                    <p className="text-4xl mb-2">{card.icon}</p>
                    <p className="text-gray-600 text-sm">{card.label}</p>
                    <p className="text-2xl font-bold text-gray-900">{card.value}</p>
                </div>
            ))}
        </div>
    );
}
