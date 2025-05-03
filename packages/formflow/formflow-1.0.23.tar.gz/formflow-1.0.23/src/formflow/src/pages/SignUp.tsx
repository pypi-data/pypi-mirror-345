import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { formToJson } from '../utils';

const SignUp = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);

    const handleSignUp = async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setLoading(true);
        const response = await fetch("https://formflow.org/auth", {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: formToJson(e.currentTarget),
        });
        setLoading(false);
        if (response.ok) {
            navigate('/check-email/sign-up');
        } else {
            console.log(response.text());
            alert("There was an error signing up.");
        }
    };

    if (loading) {
        return <div id="loading"></div>;
    }

    return (
        <>
            <h2>Sign up</h2>
            <p className="center">
                Sign up with the email address that you want to use for receiving form submissions.
            </p>
            <form className="little" onSubmit={handleSignUp}>
                <input type="email" name="email" placeholder="Email address" required/>
                <button className="center" type="submit">Sign Up</button>
            </form>
        </>
    );
};

export default SignUp;
