// src/AuthContext.js
import { createContext, useState, useEffect, useContext } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const AuthContext = createContext({
    isAuthenticated: false,
    loading: true,
    signOut: () => {},
});

export const AuthProvider = ({ children }: Record<any, any>) => {
    const navigate = useNavigate();
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);
    const location = useLocation();

    const checkAuth = async () => {
        setLoading(true);
        try {
            const response = await fetch(`https://formflow.org/me`);
            if (response.ok) {
                setIsAuthenticated(true);
            } else {
                setIsAuthenticated(false);
            }
        } catch (error) {
            console.error('Error checking authentication', error);
            setIsAuthenticated(false);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        checkAuth();
    }, []);

    useEffect(() => {
        if (location.pathname === "/account" && !isAuthenticated) {
            checkAuth();
        }
    }, [location]);

    const signOut = async () => {
        setLoading(true);
        await fetch('https://formflow.org/sign_out', {method: 'POST'});
        setLoading(false);
        setIsAuthenticated(false);
        navigate('/');
    };

    return (
        <AuthContext.Provider value={{ isAuthenticated, loading, signOut }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
