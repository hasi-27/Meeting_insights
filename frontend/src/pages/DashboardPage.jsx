import React, { useState, useEffect } from 'react';
import { ProcessingLoader } from '../components/ProcessingLoader';
import { OverviewCards } from '../components/OverviewCards';
import { SummaryCard } from '../components/SummaryCard';
import { DecisionsSection } from '../components/DecisionsSection';
import { ActionItemsTable } from '../components/ActionItemsTable';
import { OpenQuestionsSection } from '../components/OpenQuestionsSection';
import { SpeakerAnalytics } from '../components/SpeakerAnalytics';
import { TranscriptViewer } from '../components/TranscriptViewer';
import { meetingsAPI } from '../services/api';

const POLLING_INTERVAL = 2000; // 2 seconds
const MAX_RETRIES = 180; // 6 minutes max

export function DashboardPage({ meetingId, onBack }) {
    const [meeting, setMeeting] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [retryCount, setRetryCount] = useState(0);

    useEffect(() => {
        let pollInterval;

        const pollMeeting = async () => {
            try {
                const response = await meetingsAPI.getMeeting(meetingId);
                setMeeting(response.data);

                if (response.data.status === 'completed') {
                    setIsLoading(false);
                    if (pollInterval) clearInterval(pollInterval);
                } else if (response.data.status === 'failed') {
                    setError(response.data.error_message || 'Processing failed');
                    setIsLoading(false);
                    if (pollInterval) clearInterval(pollInterval);
                }
            } catch (err) {
                if (retryCount < MAX_RETRIES) {
                    setRetryCount(retryCount + 1);
                } else {
                    setError('Processing timeout. Please try again.');
                    setIsLoading(false);
                    if (pollInterval) clearInterval(pollInterval);
                }
            }
        };

        // Initial poll
        pollMeeting();

        // Set up polling
        pollInterval = setInterval(pollMeeting, POLLING_INTERVAL);

        return () => {
            if (pollInterval) clearInterval(pollInterval);
        };
    }, [meetingId]);

    if (error) {
        return (
            <div className="min-h-screen bg-red-50 p-6">
                <div className="max-w-4xl mx-auto">
                    <div className="bg-white rounded-lg shadow p-6 border-l-4 border-red-500">
                        <h2 className="text-2xl font-bold text-red-600 mb-4">Error</h2>
                        <p className="text-gray-700 mb-6">{error}</p>
                        <button
                            onClick={onBack}
                            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg"
                        >
                            ← Back to Upload
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    if (isLoading) {
        return (
            <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center">
                <div className="w-full max-w-2xl px-4">
                    <ProcessingLoader
                        status="Processing Your Meeting..."
                        message="Transcribing audio, analyzing content, and extracting insights"
                    />
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <div className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 py-6">
                    <div className="flex justify-between items-center">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">
                                📊 Meeting Insights
                            </h1>
                            <p className="text-gray-600 text-sm mt-1">{meeting?.filename}</p>
                        </div>
                        <button
                            onClick={onBack}
                            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg"
                        >
                            ← New Meeting
                        </button>
                    </div>
                </div>
            </div>

            {/* Dashboard Content */}
            <div className="max-w-7xl mx-auto px-4 py-8">
                {meeting && (
                    <>
                        <OverviewCards meeting={meeting} />
                        <SummaryCard summary={meeting.summary} />
                        <DecisionsSection decisions={meeting.decisions} />
                        <ActionItemsTable items={meeting.action_items} />
                        <OpenQuestionsSection questions={meeting.open_questions} />
                        <SpeakerAnalytics speakers={meeting.speakers} />
                        <TranscriptViewer transcript={meeting.transcript} />
                    </>
                )}
            </div>
        </div>
    );
}
