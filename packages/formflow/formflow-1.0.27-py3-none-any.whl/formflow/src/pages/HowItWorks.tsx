import { Link } from 'react-router-dom';

const HowItWorks = () => {
    return (
        <>
            <p>This site makes it easy to create a "Contact Us" form or any
            other type of form.</p>
            <h2>Don't like coding?</h2>
            <p>If you don't like coding, you can sign up with the email address
            you want to receive the submissions from the contact form, and
            we'll provide some HTML for you to copy into your website. This
            standard template collects name, email address, a message, and any
            file attachments from your visitors.</p>
            <p className="center"><Link to="/sign-up">Click here to sign up</Link>.</p>
            <h2>Customizing form fields</h2>
            <p>If you have a solid understanding of HTML, you can create a form
            with any arbitrary fields. For example, you might have a form with:</p>
            <ul>
                <li><code>{'<input name="Name" />'}</code></li>
                <li><code>{'<input name="Age" />'}</code></li>
                <li><code>{'<input name="Profession" />'}</code></li>
                <li><code>{'<input name="Gender" />'}</code></li>
            </ul>
            <p>There are three reserved field names, they are:</p>
            <ul>
                <li><code>user_id</code>: This field must be set to your user id.</li>
                <li><code>redirect</code>: This optional field is the URL your
                visitor is redirected to after filling out a form.</li>
                <li><code>subject</code>: This optional field is the subject of
                the email you will receive.</li>
            </ul>
            <p>To submit the form, make a POST request to https://formflow.org/email</p>
        </>
    );
};

export default HowItWorks;
