import { useState, useEffect } from 'react';
import { copyToClipboard } from '../utils';
import { useNavigate, Link } from 'react-router-dom';

const Account = () => {
    const navigate = useNavigate();
    const [userId, setUserId] = useState();
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        (async () => {
            try {
                const response = await fetch(`https://formflow.org/me`, {
                    method: 'GET',
                    credentials: 'include',
                });
                if (response.ok) {
                    const object = await response.json();
                    setUserId(object.id);
                } else {
                    navigate('/');
                }
            } catch (error) {
                console.error(error);
            } finally {
                setLoading(false);
            }
        })();
    }, []);

    if (loading) {
        return <div id="loading"></div>;
    }

    const example_form = `<link rel="stylesheet" href="https://formflow.org/styles.css" />
<form
    class="formflow"
    id="formflow"
    action="https://formflow.org/email"
    method="POST"
    enctype="multipart/form-data"
>
    <!-- REQUIRED FIELDS: user_id -->
    <input type="hidden" name="user_id" value="${userId}" />

    <!-- CUSTOM FIELDS: Name, Email, Message, Attachments -->

    <label for="field-name">Name:</label>
    <input id="field-name" type="text" name="Name" placeholder="Name" required />

    <label for="field-email">Email address:</label>
    <input id="field-email" type="email" name="Email" placeholder="Email address" required />

    <label for="field-message">Message:</label>
    <textarea id="field-message" name="Message" placeholder="Message"></textarea>

    <label for="field-attachments">File attachments:</label>
    <input type="file" name="Attachments" multiple />

    <button type="submit">Send</button>
</form>
<script src="https://hikaru.org/js/FRM.js"></script>
<script>FRM.listen(document.getElementById("formflow"));</script>`;

    return (
        <div>
            <h2>HTML for your website</h2>
            <p>Here is your form accepting Name, Email, Message, and Attachments.</p>
            <div className="code-container">
                <pre><code>{example_form}</code></pre>
                <button className="copy-button" onClick={(e) => copyToClipboard(e.target as HTMLElement)}>Copy</button>
                <div className="tooltip"></div>
            </div>
            <h2>Custom Forms</h2>
            <p>
                If you haven't already, check out
                the <Link to="/how-it-works">How It Works</Link> page for
                information on customizing your form.
            </p>
            <p>
                We recommend using the form above as a starting point. In
                particular, you'll need to retain the <strong>user_id</strong> field,
                as this is what lets our backend server know who to send the
                submission to.
            </p>
        </div>
    );
};

export default Account;
