import { ReactElement } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../AuthContext';

interface PrivateRouteProps {
    element: ReactElement;
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ element }) => {
    const { isAuthenticated } = useAuth();

    const notAuthenticatedMessage = (
        <div className="center">
            <p>This page is only available to signed in users.</p>
            <p>
                <Link to="/sign-up">Sign up</Link> or
                {' '}<Link to="/sign-in">sign in</Link>.
            </p>
        </div>
    );

    return isAuthenticated ? element : notAuthenticatedMessage;
};

export default PrivateRoute;
