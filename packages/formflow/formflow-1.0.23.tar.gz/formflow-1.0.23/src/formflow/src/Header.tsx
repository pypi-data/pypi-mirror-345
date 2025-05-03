import { Link } from 'react-router-dom';
import Navigation from './Navigation';

const Header = () => {
    return (
        <>
            <header>
                <h1><Link to="/">FormFlow</Link></h1>
                <p>HTML Forms Made Easy</p>
            </header>
            <Navigation />
        </>
    );
};

export default Header;
