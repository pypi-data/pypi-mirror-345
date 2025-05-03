import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { formToJson } from '../utils';

const SignIn = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);

    const handleSignIn = async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setLoading(true);
        const response = await fetch("https://formflow.org/auth", {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: formToJson(e.currentTarget),
        });
        setLoading(false);
        if (response.ok) {
            navigate('/check-email/sign-in');
        } else {
            console.log(response.text());
            alert("There was an error signing in.");
        }
    };

    if (loading) {
        return <div id="loading"></div>;
    }

    return (
        <>
            <h2>Sign In</h2>
            <form className="little" onSubmit={handleSignIn}>
                <label htmlFor="email">Email address:</label>
                <input id="email" type="email" name="email" placeholder="Email address" required/>
                <button className="center" type="submit">Sign In</button>
            </form>
        </>
    );
};

export default SignIn;
