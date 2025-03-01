import React, { useState } from "react";
import "./Hero.css";
import inboxMessages from "../Assets/inbox";

export default function Hero() {
    console.log(inboxMessages)
    const [files, setFiles] = useState(inboxMessages);
    const [uploadedFile, setUploadedFile] = useState(null);
    const [recipient, setRecipient] = useState("");

    const handleFileUpload = (event) => {
        setUploadedFile(event.target.files[0]);
    };

    const file_history = inboxMessages.slice(0, 5).map((inbox, index) => {
        console.log(inbox)
        return(
        <div className="spane" key={index}>
            <p style={{color:"white"}}>{inbox.sender}</p>
            <p style={{color:"white"}}>{inbox.timestamp}</p>
        </div>
    )});

    return (
        <div className="hero">
            <div className="inbox-section">
                <h1>Inbox</h1>
                {file_history}
            </div>
            <div className="upload-section">
                <h2>Upload File</h2>
                <input type="file" onChange={handleFileUpload} />

                <h2>Recipient Name</h2>
                <input
                    type="text"
                    placeholder="Enter recipient name"
                    value={recipient}
                    onChange={(e) => setRecipient(e.target.value)}
                />
                <button className="submit" type="submit">Send</button>
            </div>
        </div>
    );
}
