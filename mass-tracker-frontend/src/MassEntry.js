import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/';

function MassEntry({ token }) {
    const [massIntentions, setMassIntentions] = useState([]);
    const [selectedIntention, setSelectedIntention] = useState('');
    const [celebrationDate, setCelebrationDate] = useState(new Date().toISOString().split('T')[0]);
    const [notes, setNotes] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        fetchMassIntentions();
    }, []);

    const fetchMassIntentions = async () => {
        try {
            const response = await axios.get(`${API_URL}mass-intentions/`, {
                headers: { Authorization: `Token ${token}` }
            });
            setMassIntentions(response.data);
        } catch (err) {
            setError('Failed to fetch mass intentions');
            console.error(err);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setMessage('');
        
        try {
            const response = await axios.post(`${API_URL}celebrate-mass/`, {
                mass_intention_id: selectedIntention,
                celebration_date: celebrationDate,
                notes: notes
            }, {
                headers: { Authorization: `Token ${token}` }
            });
            
            setMessage('Mass celebrated successfully!');
            setNotes('');
            // Reset form or redirect as needed
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to record mass celebration');
            console.error(err);
        }
    };

    return (
        <div>
            <h2>Record Mass Celebration</h2>
            <form onSubmit={handleSubmit}>
                <div>
                    <label>Mass Intention:</label>
                    <select 
                        value={selectedIntention} 
                        onChange={(e) => setSelectedIntention(e.target.value)}
                        required
                    >
                        <option value="">Select an intention</option>
                        {massIntentions.map((intention) => (
                            <option key={intention.id} value={intention.id}>
                                {intention.title}
                            </option>
                        ))}
                    </select>
                </div>
                
                <div>
                    <label>Celebration Date:</label>
                    <input
                        type="date"
                        value={celebrationDate}
                        onChange={(e) => setCelebrationDate(e.target.value)}
                        required
                    />
                </div>
                
                <div>
                    <label>Notes (optional):</label>
                    <textarea
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        rows="3"
                    />
                </div>
                
                <button type="submit">Record Mass Celebration</button>
            </form>
            
            {message && <p style={{ color: 'green' }}>{message}</p>}
            {error && <p style={{ color: 'red' }}>{error}</p>}
        </div>
    );
}

export default MassEntry;

