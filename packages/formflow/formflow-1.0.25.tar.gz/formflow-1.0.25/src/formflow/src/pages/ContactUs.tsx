import { useRef, useEffect } from 'react';

const ContactUs = () => {
    const ref = useRef(null);

    useEffect(() => {
        if (ref.current) {
            FRM.listen(ref.current);
        }
    }, []);

    return (
        <>
            <form
                ref={ref}
                id="formflow"
                className="formflow"
                action="https://formflow.org/email"
                method="POST"
                encType="multipart/form-data"
            >
                <input type="hidden" name="user_id" value="23d601f8-7f43-462e-91b1-ac7daa688ea3" />
                <label htmlFor="field-name">Name:</label>
                <input id="field-name" type="text" name="Name" placeholder="Name" required />
                <label htmlFor="field-email">Email address:</label>
                <input id="field-email" type="email" name="Email" placeholder="Email address" required />
                <label htmlFor="field-message">Message:</label>
                <textarea id="field-message" name="Message" placeholder="Message"></textarea>
                <label htmlFor="field-attachments">File attachments:</label>
                <input type="file" name="Attachments" multiple />
                <button type="submit">Send</button>
            </form>
        </>
    );
};

export default ContactUs;
