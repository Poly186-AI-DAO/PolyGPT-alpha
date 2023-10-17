# -*- coding: utf-8 -*-
"""
Created on Sat Oct  7 11:44:07 2023

@author: mysticmarks
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import hashlib
from bs4 import BeautifulSoup

# --- Utility Layer: WebConstructor ---

class WebConstructor:
    def __init__(self, base_output_path):
        self.base_output_path = base_output_path

    def construct_page(self, html_content, output_path):
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Example: Extract and update image references
        for img_tag in soup.find_all('img'):
            img_url = img_tag.get('src')
            img_filename = os.path.basename(img_url)
            img_tag['src'] = os.path.join('images', img_filename)
        
        # Save the modified HTML content
        html_filepath = os.path.join(output_path, "index.html")
        with open(html_filepath, 'w', encoding='utf-8') as html_file:
            html_file.write(str(soup))

    def construct_website(self, scraped_data_folder):
        for filename in os.listdir(scraped_data_folder):
            filepath = os.path.join(scraped_data_folder, filename)
            with open(filepath, 'r', encoding='utf-8') as html_file:
                html_content = html_file.read()
            
            # Define a folder path based on the filename
            folder_name = hashlib.md5(filename.encode()).hexdigest()
            output_path = os.path.join(self.base_output_path, folder_name)
            os.makedirs(output_path, exist_ok=True)
            
            # Construct the individual page
            self.construct_page(html_content, output_path)

# --- Application Layer: Tkinter GUI ---

class WebConstructorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Web Constructor")
        self.setup_ui()
        self.web_constructor = WebConstructor('constructed_website')
    
    def setup_ui(self):
        self.folder_label = ttk.Label(self, text="Path to Scraped Data Folder:")
        self.folder_label.pack(padx=10, pady=5)

        self.folder_entry = ttk.Entry(self, width=50)
        self.folder_entry.pack(padx=10, pady=5)
        self.folder_entry.insert(0, "output_folder")

        self.construct_button = ttk.Button(self, text="Construct Website", command=self.on_start_constructing)
        self.construct_button.pack(padx=10, pady=5)

    def on_start_constructing(self):
        folder_path = self.folder_entry.get()
        threading.Thread(target=self.construct_website, args=(folder_path,)).start()
        messagebox.showinfo("Started", "Website construction has started!")

    def construct_website(self, folder_path):
        try:
            self.web_constructor.construct_website(folder_path)
            messagebox.showinfo("Completed", "Website construction has completed!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

# --- Main Application Logic ---

app = WebConstructorApp()
app.mainloop()