// /Users/1byinf8/Documents/QRYPTOVAULT/frontend/src/Hero.js
import React, { useState, useEffect } from "react";
import axios from "axios";
import io from "socket.io-client";
import "./Hero.css";
import inboxMessages from "../Assets/inbox"; // Mock data

const API_URL = "http://localhost:8000";
const socket = io(API_URL);

export default function Hero() {
    const [files, setFiles] = useState(inboxMessages); // Initial mock data
    const [uploadedFile, setUploadedFile] = useState(null);
    const [recipient, setRecipient] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [serverMessage, setServerMessage] = useState({ type: "", text: "" });
    const [blockchain, setBlockchain] = useState([]);

    useEffect(() => {
        axios
            .get(`${API_URL}/blockchain`)
            .then((response) => {
                setBlockchain(response.data);
                setFiles(
                    response.data.map((block) => ({
                        sender: block.owner,
                        timestamp: new Date(block.timestamp * 1000).toLocaleString(),
                    }))
                );
            })
            .catch((error) => console.error("Error fetching blockchain:", error));

        socket.on("connect", () => console.log("Connected to WebSocket"));
        socket.on("new_block", (block) => {
            setBlockchain((prev) => [...prev, block]);
            setFiles((prev) => [
                ...prev,
                {
                    sender: block.owner,
                    timestamp: new Date(block.timestamp * 1000).toLocaleString(),
                },
            ]);
        });
        socket.on("blockchain_update", (blocks) => {
            setBlockchain(blocks);
            setFiles(
                blocks.map((block) => ({
                    sender: block.owner,
                    timestamp: new Date(block.timestamp * 1000).toLocaleString(),
                }))
            );
        });

        return () => socket.disconnect();
    }, []);

    const handleFileUpload = (event) => {
        setUploadedFile(event.target.files[0]);
    };

    const submitFileUpload = async (e) => {
        e.preventDefault();

        if (!uploadedFile ||!recipient) {
            setServerMessage({ type: "error", text: "Please select a file, log in, and specify a recipient" });
            return;
        }

        setIsLoading(true);
        const formData = new FormData();
        formData.append("file", uploadedFile);
        formData.append("shared_with", recipient);

        try {
            const response = await axios.post(`${API_URL}/upload`, formData);
            setServerMessage({ type: "success", text: `File uploaded successfully! File ID: ${response.data.file_id}` });
            setUploadedFile(null);
            setRecipient("");
        } catch (error) {
            console.error("Upload error:", error);
            setServerMessage({ type: "error", text: error.response?.data?.detail || "Upload failed!" });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="hero">
            <div className="inbox-section">
                <h1>Inbox</h1>
                {files.length > 0 ? (
                    files.slice(0, 5).map((inbox, index) => (
                        <div className="spane" key={index}>
                            <p style={{ color: "white" }}>{inbox.sender}</p>
                            <p style={{ color: "white" }}>{inbox.timestamp}</p>
                        </div>
                    ))
                ) : (
                    <p style={{ color: "white" }}>No files yet</p>
                )}
            </div>
            <div className="upload-section">
                <h2>Upload File</h2>
                <form onSubmit={submitFileUpload}>
                    <input type="file" onChange={handleFileUpload} disabled={isLoading} />
                    <h2>Recipient Name</h2>
                    <input
                        type="text"
                        placeholder="Enter recipient name"
                        value={recipient}
                        onChange={(e) => setRecipient(e.target.value)}
                        disabled={isLoading}
                    />
                    <button className="submit" type="submit" disabled={isLoading}>
                        {isLoading ? "Sending..." : "Send"}
                    </button>
                </form>
                {serverMessage.text && (
                    <p style={{ color: serverMessage.type === "success" ? "green" : "red" }}>
                        {serverMessage.text}
                    </p>
                )}
            </div>
        </div>
    );
}
