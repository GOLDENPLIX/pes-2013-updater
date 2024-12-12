import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from Manage_Kits_and_Logos import update_kits_and_logos
from data_manager import DataManager
import threading
import os

class PESUpdater:
    def __init__(self, root):
        self.root = root
        self.root.title("PES 2013 Updater")
        self.root.geometry("600x500")
        
        # Initialize data manager
        self.data_manager = DataManager()
        
        # Folder paths
        self.kit_folder = tk.StringVar()
        self.logo_folder = tk.StringVar()
        self.dest_folder = tk.StringVar()
        
        # Create GUI elements
        self.create_widgets()
    
    def create_widgets(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Update tab
        update_frame = ttk.Frame(notebook)
        notebook.add(update_frame, text='Update Game')
        
        # Downloads tab
        downloads_frame = ttk.Frame(notebook)
        notebook.add(downloads_frame, text='Download Content')
        
        # Setup Update tab
        self.setup_update_tab(update_frame)
        
        # Setup Downloads tab
        self.setup_downloads_tab(downloads_frame)
    
    def setup_update_tab(self, parent):
        # Kit folder selection
        tk.Label(parent, text="Kit Folder:").pack(pady=5)
        kit_frame = tk.Frame(parent)
        kit_frame.pack(fill='x', padx=20)
        tk.Entry(kit_frame, textvariable=self.kit_folder, width=50).pack(side='left')
        tk.Button(kit_frame, text="Browse", command=lambda: self.browse_folder(self.kit_folder)).pack(side='left', padx=5)
        
        # Logo folder selection
        tk.Label(parent, text="Logo Folder:").pack(pady=5)
        logo_frame = tk.Frame(parent)
        logo_frame.pack(fill='x', padx=20)
        tk.Entry(logo_frame, textvariable=self.logo_folder, width=50).pack(side='left')
        tk.Button(logo_frame, text="Browse", command=lambda: self.browse_folder(self.logo_folder)).pack(side='left', padx=5)
        
        # Destination folder selection
        tk.Label(parent, text="PES 2013 Folder:").pack(pady=5)
        dest_frame = tk.Frame(parent)
        dest_frame.pack(fill='x', padx=20)
        tk.Entry(dest_frame, textvariable=self.dest_folder, width=50).pack(side='left')
        tk.Button(dest_frame, text="Browse", command=lambda: self.browse_folder(self.dest_folder)).pack(side='left', padx=5)
        
        # Status message
        self.status_label = tk.Label(parent, text="", wraplength=400)
        self.status_label.pack(pady=20)
        
        # Update button
        tk.Button(parent, text="Update PES", command=self.update_pes, 
                 bg='#4CAF50', fg='white', padx=20, pady=10).pack(pady=20)
    
    def setup_downloads_tab(self, parent):
        # Progress information
        self.download_status = tk.Label(parent, text="", wraplength=400)
        self.download_status.pack(pady=10)
        
        self.progress = ttk.Progressbar(parent, length=400, mode='indeterminate')
        self.progress.pack(pady=10)
        
        # Download buttons frame
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=20)
        
        # Download buttons
        tk.Button(btn_frame, text="Download Transfers", 
                 command=self.download_transfers,
                 bg='#2196F3', fg='white', padx=10, pady=5).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="Download Kits & Logos", 
                 command=self.download_assets,
                 bg='#2196F3', fg='white', padx=10, pady=5).pack(side='left', padx=5)
        
        # Output location
        output_frame = tk.Frame(parent)
        output_frame.pack(fill='x', padx=20, pady=20)
        tk.Label(output_frame, text="Output Location:").pack(side='left')
        tk.Label(output_frame, text=self.data_manager.output_dir, fg='blue').pack(side='left', padx=5)
    
    def browse_folder(self, var):
        folder = filedialog.askdirectory()
        if folder:
            var.set(folder)
    
    def update_pes(self):
        # Validate folders
        if not all([self.kit_folder.get(), self.logo_folder.get(), self.dest_folder.get()]):
            messagebox.showerror("Error", "Please select all folders first!")
            return
        
        # Update status
        self.status_label.config(text="Updating PES 2013...", fg='blue')
        self.root.update()
        
        # Perform update
        success = update_kits_and_logos(
            self.kit_folder.get(),
            self.logo_folder.get(),
            self.dest_folder.get()
        )
        
        # Show result
        if success:
            self.status_label.config(text="Update completed successfully!", fg='green')
            messagebox.showinfo("Success", "PES 2013 has been updated successfully!")
        else:
            self.status_label.config(text="Update failed. Check the logs for details.", fg='red')
            messagebox.showerror("Error", "Failed to update PES 2013. Check the logs for details.")
    
    def download_transfers(self):
        self.progress.start()
        self.download_status.config(text="Downloading transfer data...", fg='blue')
        
        def download():
            try:
                self.data_manager.fetch_transfers()
                self.root.after(0, lambda: self.download_status.config(
                    text="Transfer data downloaded successfully!", fg='green'))
            except Exception as e:
                self.root.after(0, lambda: self.download_status.config(
                    text=f"Error downloading transfers: {str(e)}", fg='red'))
            finally:
                self.root.after(0, self.progress.stop)
        
        threading.Thread(target=download, daemon=True).start()
    
    def download_assets(self):
        self.progress.start()
        self.download_status.config(text="Downloading kits and logos...", fg='blue')
        
        def download():
            try:
                zip_file = self.data_manager.update_all()
                if zip_file:
                    self.root.after(0, lambda: self.download_status.config(
                        text=f"Assets downloaded and packaged successfully!\nSaved to: {zip_file}", 
                        fg='green'))
                else:
                    raise Exception("Failed to create update package")
            except Exception as e:
                self.root.after(0, lambda: self.download_status.config(
                    text=f"Error downloading assets: {str(e)}", fg='red'))
            finally:
                self.root.after(0, self.progress.stop)
        
        threading.Thread(target=download, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = PESUpdater(root)
    root.mainloop()
