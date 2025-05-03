import { Link } from 'react-router-dom';
import './LandingPage.css';

const LandingPage = () => {
    return (
        <>
            <div id="hero">
                <div id="text-box">
                    <p>Easily Add a Contact Form to Your Site in Minutes</p>
                    <p><Link className="button" id="get-started" to="/sign-up">Get Started</Link></p>
                </div>
                <div id="image-box">
                    <img src="contact-us.webp"/>
                </div>
            </div>
        </>
    );
};

export default LandingPage;
