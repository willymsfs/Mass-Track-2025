import React, { useState } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/';

function ExcelImport({ token }) {
    const [selectedFile, setSelectedFile] = useState(null);
    const [startYear, setStartYear] = useState(2000);
    const [endYear, setEndYear] = useState(new Date().getFullYear());
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleFileChange = (event) => {
        setSelectedFile(event.target.files[0]);
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        setMessage('');
        setError('');

        if (!selectedFile) {
            setError('Please select an Excel file.');
            return;
        }

        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('start_year', startYear);
        formData.append('end_year', endYear);

        try {
            const response = await axios.post(`${API_URL}import-excel/`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'Authorization': `Token ${token}`
                },
            });
            setMessage(response.data.message);
            setSelectedFile(null);
        } catch (err) {
            setError(err.response?.data?.error || 'Error importing data.');
            console.error(err);
        }
    };

    return (
        <div>
            <h2>Import Mass Data from Excel</h2>
            <form onSubmit={handleSubmit}>
                <div>
                    <label>Excel File:</label>
                    <input type="file" accept=".xlsx, .xls" onChange={handleFileChange} required />
                </div>
                <div>
                    <label>Start Year (for historical data):</label>
                    <input 
                        type="number" 
                        value={startYear} 
                        onChange={(e) => setStartYear(parseInt(e.target.value))}
                        min="1900" 
                        max={new Date().getFullYear()}
                        required 
                    />
                </div>
                <div>
                    <label>End Year (for historical data):</label>
                    <input 
                        type="number" 
                        value={endYear} 
                        onChange={(e) => setEndYear(parseInt(e.target.value))}
                        min="1900" 
                        max={new Date().getFullYear() + 100} // Allow future for 


deceased priests
                        required 
                    />
                </div>
                <button type="submit">Import Data</button>
            </form>
            {message && <p style={{ color: 'green' }}>{message}</p>}
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <p>Expected Excel columns (case-sensitive, first row header):</p>
            <ul>
                <li><b>Date</b> (YYYY-MM-DD)</li>
                <li><b>Intention</b></li>
                <li><b>Source</b> (e.g., Personal, Province, Generalate, Individual)</li>
                <li><b>Type</b> (e.g., Personal, Fixed-Date, Bulk, Special)</li>
                <li><b>Notes</b> (optional)</li>
                <li><b>Bulk_Remaining</b> (for Bulk type, optional)</li>
                <li><b>Bulk_Total</b> (for Bulk type, optional)</li>
            </ul>
        </div>
    );
}

export default ExcelImport;


