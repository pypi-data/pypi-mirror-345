import { useAuth } from './AuthContext';
import { Link } from 'react-router-dom';

const Navigation = () => {
    const { isAuthenticated, signOut } = useAuth();

    const elements = [
        <Link key={'how-it-works'} to="/how-it-works">How It Works</Link>,
        <Link key={'contact-us'} to="/contact-us">Contact Us</Link>,
    ];
   
    if (isAuthenticated) {
        elements.push(<Link key={'account'} to="/account">Account</Link>);
        elements.push(<button className="link" key={'sign-out'} onClick={signOut}>Sign Out</button>);
    } else {
        elements.push(<Link key={'sign-up'} to="/sign-up">Sign Up</Link>);
        elements.push(<Link key={'sign-in'} to="/sign-in">Sign In</Link>);
    }

    const joinedElements = elements.reduce((acc: any, element: any, index: number) => {
       if (index === 0) return [element];
       return [...acc, ' ', element];
    }, []);

    return <nav>{joinedElements}</nav>;
};

export default Navigation;
