import { Link, useParams } from 'react-router-dom';

const CheckEmail = () => {
    const { type } = useParams<{ type: string }>();

    const text = (
        type === "sign-up" ? (
            `You have been sent a link to confirm your email address. Please check
            your inbox and click the link to complete your registration and sign
            in.`
        ) : (
            `You have been sent a link to sign in. Please check your inbox and
            click the link to access your account.`
        )
    );

    return (
        <>
            <p>{text}</p>
            <p>After you have done that, you can <Link to="/account">click here</Link> to proceed to your account.</p>
        </>
    );
};

export default CheckEmail;
