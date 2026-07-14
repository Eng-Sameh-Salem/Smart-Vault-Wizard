# 🛡️ Smart Backup Vault | Personal Encrypted Vault

A professional Python application built with a modern GUI using **CustomTkinter** to provide maximum security for your files. The program compresses and encrypts your local folders using strong **AES-256-CFB** encryption, then automatically uploads them to your secure **Google Drive** storage.

---

## ✨ Key Features

* **Strong Local Encryption**: Leverages the `cryptography` library to generate unique encryption keys per session using `PBKDF2HMAC` with a highly secure random Salt.
* **Instant Cloud Integration**: Automatically uploads your encrypted files to a dedicated folder on your Google Drive (the folder is created automatically if it doesn't exist).
* **Modern UI/UX**: An elegant, interactive dark-themed interface featuring refined gold accents.
* **Asynchronous Execution (Multi-threading)**: Compression, encryption, and uploading run seamlessly in the background to ensure the GUI remains responsive.
* **Direct Decryption & Recovery**: A dedicated tab allowing you to pick any `.enc` file, enter the original password, and restore your files and folder structure instantly.

---

## 🛠️ Prerequisites & Installation

### 1. Install Required Libraries
Make sure you have Python installed on your system, then run the following command in your terminal/command prompt:

```bash
pip install customtkinter cryptography google-auth google-auth-oauthlib google-api-python-client

2. Set Up Google Drive API
To enable the automatic cloud backup feature, follow these steps:

Go to the Google Cloud Console.

Create a new project and enable the Google Drive API.

Configure your OAuth Consent Screen as External, and add your email address under Test Users.

Navigate to Credentials and create an OAuth client ID credential (select Desktop App as the application type).

Download the JSON file containing your client secrets, rename it to credentials.json, and place it in the root directory of this project (next to the main script).

⚠️ Security Warning: The credentials.json file and the generated token.json file contain sensitive credentials. They have been added to the .gitignore template to prevent you from accidentally exposing them on GitHub.

🚀 How to Use
Part 1: Encryption & Backup
Step 1: Click "Add Folder to List" to select the local folders you want to backup.

Step 2: Enter the target folder name for your Google Drive (e.g., My_Cloud_Vault).

Step 3: Enter a strong master password and click "Execute Secure Encryption & Cloud Upload".

Part 2: Decryption & Restoration
Switch to the "Decryption & Instant Recovery" tab.

Choose your encrypted vault file (with a .enc extension) from your device.

Enter the exact password used during the encryption process.

Click "Start Decryption & Data Restoration" and select the local directory where you want to extract your restored files.

👨‍💻 Developer
Developer: Sameh Salem (Engineer)

📄 License
This project is open-source and available under the MIT License.