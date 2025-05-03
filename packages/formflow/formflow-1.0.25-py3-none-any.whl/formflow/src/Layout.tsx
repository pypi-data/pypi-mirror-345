import { ReactNode, FC } from 'react';
import { useAuth } from './AuthContext';
import Header from './Header';
import Footer from './Footer';

interface LayoutProps {
    children: ReactNode;
}

const Layout: FC<LayoutProps> = ({ children }) => {
    const { loading } = useAuth();

    if (loading) {
        children = <div id="loading"></div>;
    }

    return (
        <>
            <Header />
            {children}
            <Footer />
        </>
    );
};

export default Layout;
