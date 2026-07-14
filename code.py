import os
import shutil
import threading
from datetime import datetime
import customtkinter as ctk
from tkinter import filedialog, messagebox

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    GOOGLE_DRIVE_SUPPORT = True
except ImportError:
    GOOGLE_DRIVE_SUPPORT = False

SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Theme & Palette Settings
BG_MAIN = "#121212"       
BG_CARD = "#1A1A1A"       
GOLD_BASE = "#D4AF37"     
GOLD_HOVER = "#B8902E"    
TEXT_WHITE = "#FFFFFF"
TEXT_MUTED = "#888888"

class ProfessionalVaultWizard(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Smart Backup Vault | Personal Encrypted Vault")
        self.geometry("650x640")
        self.resizable(False, False)
        self.configure(fg_color=BG_MAIN)
        
        self.selected_folders = []
        self.decrypt_file_path = ""
        self.current_step = 1
        
        self.step_frames = {}
        self.init_ui_components()
        
    def init_ui_components(self):
        self.title_label = ctk.CTkLabel(
            self, 
            text="Smart Encrypted Backup Vault", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=GOLD_BASE
        )
        self.title_label.pack(pady=(20, 5))
        
        self.subtitle_label = ctk.CTkLabel(
            self, 
            text="Strong Local Encryption & Seamless Cloud Management", 
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=TEXT_MUTED
        )
        self.subtitle_label.pack(pady=(0, 15))

        self.signature_label = ctk.CTkLabel(
            self, text="Designed by Eng. Sameh Salem",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=GOLD_BASE
        )
        self.signature_label.pack(side="bottom", pady=(5, 2))

        self.status_bar = ctk.CTkLabel(
            self, text="Status: Awaiting operation selection...",
            font=ctk.CTkFont(family="Segoe UI", size=12), text_color=TEXT_MUTED
        )
        self.status_bar.pack(side="bottom", pady=2)

        self.main_tab_view = ctk.CTkTabview(
            self, width=580, height=440,
            fg_color=BG_MAIN, segmented_button_selected_color=GOLD_BASE,
            segmented_button_selected_hover_color=GOLD_HOVER,
            segmented_button_unselected_hover_color="#333333",
            text_color=TEXT_WHITE
        )
        self.main_tab_view.pack(padx=20, pady=5, fill="both", expand=True)
        
        self.main_tab_view.add("Encryption & Cloud Upload")
        self.main_tab_view.add("Decryption & Instant Recovery")
        
        self.setup_encrypt_wizard_tab()
        self.setup_decrypt_direct_tab()

    def setup_encrypt_wizard_tab(self):
        tab = self.main_tab_view.tab("Encryption & Cloud Upload")
        
        self.wizard_container = ctk.CTkFrame(tab, fg_color=BG_MAIN)
        self.wizard_container.pack(fill="both", expand=True)
        
        self.create_step_1_frame()
        self.create_step_2_frame()
        self.create_step_3_frame()
        
        self.nav_frame = ctk.CTkFrame(tab, fg_color=BG_MAIN)
        self.nav_frame.pack(side="bottom", fill="x", pady=(10, 0))

        self.btn_next = ctk.CTkButton(
            self.nav_frame, text="Next", command=self.next_step,
            fg_color=GOLD_BASE, hover_color=GOLD_HOVER, text_color=BG_MAIN,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), width=100
        )
        self.btn_next.pack(side="right")

        self.btn_prev = ctk.CTkButton(
            self.nav_frame, text="Previous", command=self.prev_step,
            fg_color="#333333", hover_color="#444444", text_color=TEXT_WHITE,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), width=100
        )
        self.btn_prev.pack(side="left")
        
        self.show_step(1)

    def create_step_1_frame(self):
        frame = ctk.CTkFrame(self.wizard_container, fg_color=BG_CARD, border_color="#262626", border_width=1)
        self.step_frames[1] = frame
        
        lbl = ctk.CTkLabel(
            frame, text="Step 1: Select folders from your device to secure and backup",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=TEXT_WHITE
        )
        lbl.pack(pady=(15, 5), padx=15, anchor="w")
        
        btn_browse = ctk.CTkButton(
            frame, text="Add Folder to List", command=self.browse_folder,
            fg_color=GOLD_BASE, hover_color=GOLD_HOVER, text_color=BG_MAIN,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        )
        btn_browse.pack(pady=5, padx=15, anchor="w")
        
        self.txt_folders = ctk.CTkTextbox(
            frame, height=130, width=520, state="disabled",
            fg_color="#222222", text_color=TEXT_WHITE, border_color="#333333", border_width=1
        )
        self.txt_folders.pack(pady=(5, 15), padx=15)

    def create_step_2_frame(self):
        frame = ctk.CTkFrame(self.wizard_container, fg_color=BG_CARD, border_color="#262626", border_width=1)
        self.step_frames[2] = frame
        
        lbl = ctk.CTkLabel(
            frame, text="Step 2: Define target Cloud folder destination",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=TEXT_WHITE
        )
        lbl.pack(pady=(15, 5), padx=15, anchor="w")

        lbl_desc = ctk.CTkLabel(
            frame, text="The folder will be auto-created on your cloud drive if it doesn't exist.",
            font=ctk.CTkFont(family="Segoe UI", size=11), text_color=TEXT_MUTED
        )
        lbl_desc.pack(pady=(0, 5), padx=15, anchor="w")
        
        self.entry_drive_folder = ctk.CTkEntry(
            frame, width=520, placeholder_text="Enter cloud folder name (e.g., My_Cloud_Vault)",
            fg_color="#222222", text_color=TEXT_WHITE, border_color=GOLD_BASE, justify="left",
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.entry_drive_folder.pack(pady=(5, 20), padx=15)

    def create_step_3_frame(self):
        frame = ctk.CTkFrame(self.wizard_container, fg_color=BG_CARD, border_color="#262626", border_width=1)
        self.step_frames[3] = frame
        
        lbl = ctk.CTkLabel(
            frame, text="Step 3: Provide a strong master password for local data encryption",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=TEXT_WHITE
        )
        lbl.pack(pady=(15, 5), padx=15, anchor="w")
        
        self.entry_password = ctk.CTkEntry(
            frame, show="*", width=520, placeholder_text="Master encryption password",
            fg_color="#222222", text_color=TEXT_WHITE, border_color=GOLD_BASE, justify="center"
        )
        self.entry_password.pack(pady=(5, 15), padx=15)

        self.btn_execute = ctk.CTkButton(
            frame, text="Execute Secure Encryption & Cloud Upload", command=self.trigger_async_backup,
            fg_color=GOLD_BASE, hover_color=GOLD_HOVER, text_color=BG_MAIN,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), height=42, width=380
        )
        self.btn_execute.pack(pady=(10, 15))

    def setup_decrypt_direct_tab(self):
        tab = self.main_tab_view.tab("Decryption & Instant Recovery")
        
        frame = ctk.CTkFrame(tab, fg_color=BG_CARD, border_color="#262626", border_width=1)
        frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        lbl_select = ctk.CTkLabel(
            frame, text="1. Select encrypted vault file (.enc):",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=TEXT_WHITE
        )
        lbl_select.pack(pady=(20, 2), padx=20, anchor="w")
        
        self.btn_select_enc = ctk.CTkButton(
            frame, text="Browse Encrypted Vault File", command=self.browse_enc_file,
            fg_color="#333333", hover_color="#444444", text_color=TEXT_WHITE,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        )
        self.btn_select_enc.pack(pady=5, padx=20, anchor="w")
        
        self.lbl_enc_path = ctk.CTkLabel(
            frame, text="Selected File: None",
            font=ctk.CTkFont(family="Segoe UI", size=11), text_color=TEXT_MUTED
        )
        self.lbl_enc_path.pack(pady=2, padx=20, anchor="w")
        
        lbl_pass = ctk.CTkLabel(
            frame, text="2. Enter original password to decrypt and extract files:",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=TEXT_WHITE
        )
        lbl_pass.pack(pady=(15, 2), padx=20, anchor="w")
        
        self.entry_decrypt_password = ctk.CTkEntry(
            frame, show="*", width=500, placeholder_text="Enter vault password",
            fg_color="#222222", text_color=TEXT_WHITE, border_color=GOLD_BASE, justify="center"
        )
        self.entry_decrypt_password.pack(pady=5)
        
        self.btn_decrypt = ctk.CTkButton(
            frame, text="Start Decryption & Data Restoration", command=self.trigger_async_decrypt,
            fg_color="#27ae60", hover_color="#219653", text_color=TEXT_WHITE,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), height=42, width=380
        )
        self.btn_decrypt.pack(pady=25)

    def show_step(self, step):
        for f in self.step_frames.values():
            f.pack_forget()
        
        self.step_frames[step].pack(fill="both", expand=True)
        self.current_step = step
        
        if step == 1:
            self.btn_prev.configure(state="disabled")
            self.btn_next.configure(state="normal", text="Next")
            self.status_bar.configure(text="Status: Waiting for folders to be added...")
        elif step == 2:
            self.btn_prev.configure(state="normal")
            self.btn_next.configure(state="normal", text="Next")
            self.status_bar.configure(text="Status: Waiting for target cloud destination folder...")
        elif step == 3:
            self.btn_prev.configure(state="normal")
            self.btn_next.configure(state="disabled", text="Finish")
            self.status_bar.configure(text="Status: Ready to execute after entering password.")

    def next_step(self):
        if self.current_step == 1 and not self.selected_folders:
            messagebox.showerror("Notice", "Please select at least one folder to proceed.")
            return
        if self.current_step == 2 and not self.entry_drive_folder.get().strip():
            messagebox.showerror("Notice", "Please provide a target cloud folder name to proceed.")
            return
        if self.current_step < 3:
            self.show_step(self.current_step + 1)

    def prev_step(self):
        if self.current_step > 1:
            self.show_step(self.current_step - 1)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder and folder not in self.selected_folders:
            self.selected_folders.append(folder)
            self.txt_folders.configure(state="normal")
            self.txt_folders.delete("1.0", ctk.END)
            for path in self.selected_folders:
                self.txt_folders.insert(ctk.END, f"{path}\n")
            self.txt_folders.configure(state="disabled")
            self.status_bar.configure(text=f"Status: {len(self.selected_folders)} folder(s) added successfully.")

    def browse_enc_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Encrypted Files", "*.enc")])
        if file_path:
            self.decrypt_file_path = file_path
            filename = os.path.basename(file_path)
            self.lbl_enc_path.configure(text=f"Selected File: {filename}", text_color=GOLD_BASE)

    def get_google_service(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    raise FileNotFoundError("Missing 'credentials.json' file.")
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return build('drive', 'v3', credentials=creds)

    def get_or_create_drive_folder(self, service, folder_name):
        query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])
        
        if items:
            return items[0]['id']
        else:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = service.files().create(body=folder_metadata, fields='id').execute()
            return folder.get('id')

    def trigger_async_backup(self):
        threading.Thread(target=self.execute_backup_pipeline, daemon=True).start()

    def trigger_async_decrypt(self):
        threading.Thread(target=self.execute_decryption_pipeline, daemon=True).start()

    def execute_backup_pipeline(self):
        password = self.entry_password.get()
        target_drive_folder = self.entry_drive_folder.get().strip()
        
        if not password:
            messagebox.showerror("Notice", "Securing your vault requires a master encryption password.")
            return

        self.btn_execute.configure(state="disabled", text="Processing pipeline...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"vault_raw_{timestamp}"
        encrypted_output = f"Protected_Vault_{timestamp}.enc"
        
        try:
            self.status_bar.configure(text="Status: Compressing selected local directories...", text_color=GOLD_BASE)
            temp_container = f"vault_payload_{timestamp}"
            os.makedirs(temp_container, exist_ok=True)
            
            for f in self.selected_folders:
                base_name = os.path.basename(f)
                shutil.copytree(f, os.path.join(temp_container, base_name))
                
            shutil.make_archive(archive_name, 'zip', temp_container)
            shutil.rmtree(temp_container)
            
            self.status_bar.configure(text="Status: Performing AES-256 local encryption...", text_color=GOLD_BASE)
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(), length=32, salt=salt,
                iterations=100_000, backend=default_backend()
            )
            key = kdf.derive(password.encode())
            iv = os.urandom(16)
            
            cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            
            raw_zip_path = f"{archive_name}.zip"
            with open(raw_zip_path, 'rb') as r_file:
                raw_bytes = r_file.read()
                
            encrypted_bytes = encryptor.update(raw_bytes) + encryptor.finalize()
            
            with open(encrypted_output, 'wb') as e_file:
                e_file.write(salt + iv + encrypted_bytes)
                
            os.remove(raw_zip_path)
            
            self.status_bar.configure(text="Status: Connecting to cloud storage servers...", text_color=GOLD_BASE)
            if not GOOGLE_DRIVE_SUPPORT:
                raise ImportError("Google Drive client libraries are missing.")
                
            service = self.get_google_service()
            folder_id = self.get_or_create_drive_folder(service, target_drive_folder)
            
            self.status_bar.configure(text="Status: Uploading encrypted vault to Google Drive...", text_color=GOLD_BASE)
            
            file_metadata = {
                'name': encrypted_output,
                'parents': [folder_id]
            }
            media = MediaFileUpload(encrypted_output, mimetype='application/octet-stream', resumable=True)
            request = service.files().create(body=file_metadata, media_body=media, fields='id')
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                
            del media
            del request
            
            self.status_bar.configure(text="Status: Cleaning up temporary environment...", text_color=GOLD_BASE)
            
            if os.path.exists(encrypted_output):
                try:
                    os.remove(encrypted_output)
                except OSError:
                    pass
                
            self.status_bar.configure(text="Status: Operation completed successfully!", text_color="#00FF00")
            messagebox.showinfo("Success", f"Great job Eng. Sameh!\nYour files were securely encrypted and uploaded to your cloud destination.")
            
            self.selected_folders = []
            self.txt_folders.configure(state="normal")
            self.txt_folders.delete("1.0", ctk.END)
            self.txt_folders.configure(state="disabled")
            self.entry_password.delete(0, ctk.END)
            self.entry_drive_folder.delete(0, ctk.END)
            self.show_step(1)
            
        except Exception as err:
            self.status_bar.configure(text="Status: Pipeline terminated due to an error.", text_color="#FF3333")
            messagebox.showerror("Error", f"Execution failed:\n{str(err)}")
        finally:
            self.btn_execute.configure(state="normal", text="Execute Secure Encryption & Cloud Upload")

    def execute_decryption_pipeline(self):
        password = self.entry_decrypt_password.get()
        
        if not self.decrypt_file_path:
            messagebox.showerror("Notice", "Please choose an encrypted vault file (.enc) first.")
            return
        if not password:
            messagebox.showerror("Notice", "Please enter the vault password to proceed.")
            return
            
        output_dir = filedialog.askdirectory(title="Select Target Folder For Restored Files")
        if not output_dir:
            return
            
        self.btn_decrypt.configure(state="disabled", text="Decrypting...")
        self.status_bar.configure(text="Status: Verifying key signatures and reading vault...", text_color=GOLD_BASE)
        
        try:
            with open(self.decrypt_file_path, 'rb') as f_in:
                salt = f_in.read(16)
                iv = f_in.read(16)
                encrypted_data = f_in.read()
                
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(), length=32, salt=salt,
                iterations=100_000, backend=default_backend()
            )
            key = kdf.derive(password.encode())
            
            cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            
            decrypted_bytes = decryptor.update(encrypted_data) + decryptor.finalize()
            
            temp_zip_path = os.path.join(output_dir, "restored_vault_temp.zip")
            with open(temp_zip_path, 'wb') as f_out:
                f_out.write(decrypted_bytes)
                
            self.status_bar.configure(text="Status: Unpacking and reconstructing folder structure...", text_color=GOLD_BASE)
            
            shutil.unpack_archive(temp_zip_path, output_dir, "zip")
            os.remove(temp_zip_path)
            
            self.status_bar.configure(text="Status: Vault successfully restored!", text_color="#00FF00")
            messagebox.showinfo("Success", "Excellent Eng. Sameh!\nVault decrypted successfully. All directories have been restored.")
            
            self.entry_decrypt_password.delete(0, ctk.END)
            self.decrypt_file_path = ""
            self.lbl_enc_path.configure(text="Selected File: None", text_color=TEXT_MUTED)
            
        except Exception as err:
            self.status_bar.configure(text="Status: Decryption failed. Invalid credentials.", text_color="#FF3333")
            messagebox.showerror("Error", "Restoration failed. The password might be incorrect or the file is corrupted.")
        finally:
            self.btn_decrypt.configure(state="normal", text="Start Decryption & Data Restoration")

if __name__ == "__main__":
    app = ProfessionalVaultWizard()
    app.mainloop()