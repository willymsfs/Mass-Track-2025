
import React, { useState } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/auth/'; // Assuming backend runs on port 8000

function Auth({ setToken }) {
    const [isLogin, setIsLogin] = useState(true);
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            let response;
            if (isLogin) {
                response = await axios.post(`${API_URL}login/`, { email, password });
            } else {
                response = await axios.post(`${API_URL}register/`, { username, email, password, first_name: firstName, last_name: lastName });
            }
            setToken(response.data.token);
            localStorage.setItem('token', response.data.token);
        } catch (err) {
            setError(err.response?.data?.error || 'An error occurred');
            console.error(err);
        }
    };

    return (
        <div>
            <h2>{isLogin ? 'Login' : 'Register'}</h2>
            <form onSubmit={handleSubmit}>
                {!isLogin && (
                    <input
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                )}
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                {!isLogin && (
                    <>
                        <input
                            type="text"
                            placeholder="First Name"
                            value={firstName}
                            onChange={(e) => setFirstName(e.target.value)}
                            required
                        />
                        <input
                            type="text"
                            placeholder="Last Name"
                            value={lastName}
                            onChange={(e) => setLastName(e.target.value)}
                            required
                        />
                    </>
                )}
                <button type="submit">{isLogin ? 'Login' : 'Register'}</button>
            </form>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <button onClick={() => setIsLogin(!isLogin)}>
                {isLogin ? 'Need an account? Register' : 'Already have an account? Login'}
            </button>
        </div>
    );
}

export default Auth;


