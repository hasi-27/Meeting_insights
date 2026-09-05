import React, { useState } from 'react';
import { UploadPage } from './pages/UploadPage';
import { DashboardPage } from './pages/DashboardPage';
import './App.css';

export function App() {
    const [currentMeetingId, setCurrentMeetingId] = useState(null);

    return (
        <div className="App">
            {currentMeetingId ? (
                <DashboardPage
                    meetingId={currentMeetingId}
                    onBack={() => setCurrentMeetingId(null)}
                />
            ) : (
                <UploadPage onMeetingCreated={setCurrentMeetingId} />
            )}
        </div>
    );
}
