# QuantumVault

QuantumVault is a **quantum-secure encryption system** that integrates **Quantum Key Distribution (QKD)**, **AES encryption**, and a **custom cryptographic chain** to provide enhanced security in the post-quantum era. This project serves as an example use case showcasing secure key transfer, decentralized encryption, and quantum resistance.

## 🚀 Features
- **Quantum Key Distribution (QKD)** for secure key transfer.
- **AES Encryption** for data security.
- **Custom Cryptographic Chain** for decentralization and added security.
- **Quantum-Secure Encryption** designed to withstand quantum attacks.
- **Core Module for Simulation** of QKD and cryptographic mechanisms.

## 📦 Setup & Installation

### **1️⃣ Clone the Repository**
```sh
 git clone https://github.com/1byinf8/QuantumVault.git
 cd QuantumVault
```

### **2️⃣ Backend Setup**
#### **Create a Virtual Environment**
```sh
 python3 -m venv venv
 source venv/bin/activate   # macOS/Linux
 venv\Scripts\activate     # Windows
```

#### **Install Backend Dependencies**
```sh
 pip install -r requirements.txt
```

#### **Install Additional Libraries (if needed)**
```sh
 pip install cryptography qiskit qiskit-aer fastapi uvicorn
```

### **3️⃣ Frontend Setup (React App)**
```sh
 cd frontend
 npm install
 npm run dev   # Start the frontend development server
```

### **4️⃣ Running the Project**
#### **Backend**
```sh
 uvicorn app:main --reload
```

#### **Frontend**
```sh
 cd frontend
 npm start
```

## 📜 License
This project is licensed under an **Open Source License** – see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing
1. Fork the repo
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit changes (`git commit -m "Add new feature"`)
4. Push to the branch (`git push origin feature-branch`)
5. Create a Pull Request

## 📞 Contact
For any queries, reach out via [GitHub Issues](https://github.com/1byinf8/QuantumVault/issues).

