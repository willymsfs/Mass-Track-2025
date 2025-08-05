import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/';

function Dashboard({ token, setToken }) {
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            const response = await axios.get(`${API_URL}dashboard/`, {
                headers: { Authorization: `Token ${token}` }
            });
            setDashboardData(response.data);
        } catch (err) {
            setError('Failed to fetch dashboard data');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleToggleBulkMassPause = async (bulkMassIntentionId) => {
        try {
            await axios.post(`${API_URL}toggle-bulk-mass-pause/`, 
                { bulk_mass_intention_id: bulkMassIntentionId },
                { headers: { Authorization: `Token ${token}` } }
            );
            fetchDashboardData(); // Refresh dashboard data after toggling
        } catch (err) {
            setError('Failed to toggle bulk mass pause status');
            console.error(err);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        setToken(null);
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h1>Mass Tracker Dashboard</h1>
                <button onClick={handleLogout}>Logout</button>
            </div>
            
            {dashboardData?.alerts?.length > 0 && (
                <div style={{ marginBottom: '20px', padding: '10px', backgroundColor: '#ffe0b2', border: '1px solid #ffc107', borderRadius: '5px' }}>
                    <h3>Alerts:</h3>
                    <ul>
                        {dashboardData.alerts.map((alert, index) => (
                            <li key={index}>{alert}</li>
                        ))}
                    </ul>
                </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                <div>
                    <h2>Today's Status</h2>
                    {dashboardData?.today_status ? (
                        <p>Mass Celebrated: {dashboardData.today_status.celebrated_mass ? 'Yes' : 'No'}</p>
                    ) : (
                        <p>No status recorded for today</p>
                    )}
                </div>

                <div>
                    <h2>Personal Masses This Month</h2>
                    <p>Completed: {dashboardData?.personal_masses_celebrated_count || 0}/3</p>
                    {dashboardData?.personal_masses_details?.map((mass, index) => (
                        <div key={index}>
                            <p>Month {mass.month}/{mass.year}: {mass.celebrated_date ? `Celebrated on ${mass.celebrated_date}` : 'Not celebrated'}</p>
                        </div>
                    ))}
                </div>

                <div>
                    <h2>Active Bulk Masses</h2>
                    {dashboardData?.bulk_masses?.length > 0 ? (
                        dashboardData.bulk_masses.map((bulk, index) => (
                            <div key={index}>
                                <p>Title: {bulk.mass_intention.title}</p>
                                <p>Remaining: {bulk.remaining_masses}/{bulk.total_masses}</p>
                                <p>Status: {bulk.is_paused ? 'Paused' : 'Active'}</p>
                                {bulk.estimated_end_date && <p>Estimated End: {bulk.estimated_end_date}</p>}
                                <button onClick={() => handleToggleBulkMassPause(bulk.mass_intention.id)}>
                                    {bulk.is_paused ? 'Resume' : 'Pause'}
                                </button>
                            </div>
                        ))
                    ) : (
                        <p>No active bulk masses</p>
                    )}
                </div>

                <div>
                    <h2>Upcoming Fixed Date Masses</h2>
                    {dashboardData?.upcoming_fixed_masses?.length > 0 ? (
                        dashboardData.upcoming_fixed_masses.map((mass, index) => (
                            <div key={index}>
                                <p>Title: {mass.mass_intention.title}</p>
                                <p>Date: {mass.original_date}</p>
                                <p>Status: {mass.is_celebrated ? 'Celebrated' : 'Pending'}</p>
                            </div>
                        ))
                    ) : (
                        <p>No upcoming fixed date masses</p>
                    )}
                </div>
            </div>
        </div>
    );
}

export default Dashboard;

