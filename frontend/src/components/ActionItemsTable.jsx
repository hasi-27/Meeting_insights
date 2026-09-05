import React from 'react';

export function ActionItemsTable({ items }) {
    if (!items || items.length === 0) {
        return (
            <div className="bg-white rounded-lg shadow p-6 mb-8 border-l-4 border-orange-500">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">📋 Action Items</h2>
                <p className="text-gray-600">No action items identified.</p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow p-6 mb-8 border-l-4 border-orange-500">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">📋 Action Items</h2>
            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-gray-200">
                            <th className="text-left py-3 px-4 font-semibold text-gray-700">Task</th>
                            <th className="text-left py-3 px-4 font-semibold text-gray-700">
                                Assigned To
                            </th>
                            <th className="text-left py-3 px-4 font-semibold text-gray-700">
                                Deadline
                            </th>
                            <th className="text-left py-3 px-4 font-semibold text-gray-700">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items.map((item, index) => (
                            <tr key={index} className="border-b border-gray-200 hover:bg-gray-50">
                                <td className="py-3 px-4 text-gray-700">{item.task}</td>
                                <td className="py-3 px-4 text-gray-700">{item.assignee}</td>
                                <td className="py-3 px-4 text-gray-700">{item.deadline}</td>
                                <td className="py-3 px-4">
                                    <span className="inline-block px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
                                        {item.status}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
