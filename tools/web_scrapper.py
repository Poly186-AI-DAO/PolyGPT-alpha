# -*- coding: utf-8 -*-
"""
Created on Sat Oct  7 11:31:30 2023

@author: mysticmarks
"""

import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
from urllib.parse import urlparse, urljoin

# --- Utility Layer ---

class URLManager:
    def __init__(self):
        self.visited_urls = set()
    
    def normalize_url(self, url, base_url=None):
        if base_url:
            url = urljoin(base_url, url)
        parts = urlparse(url)
        return parts.geturl()
    
    def mark_visited(self, url):
        self.visited_urls.add(self.normalize_url(url))
    
    def is_visited(self, url):
        return self.normalize_url(url) in self.visited_urls

class Logger:
    def log(self, message, level='INFO'):
        print(f"{level}: {message}")

# --- Scraping Layer ---

class HttpClient:
    def __init__(self, timeout=10):
        self.timeout = timeout
        
    def send_request(self, url):
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise ConnectionError(f"Error fetching {url}: {str(e)}") from e

class Scraper:
    def __init__(self):
        self.http_client = HttpClient()
        self.url_manager = URLManager()
        self.logger = Logger()
    
    def scrape_url(self, url, folder_path):
        if self.url_manager.is_visited(url):
            self.logger.log(f"Skipping already visited URL: {url}")
            return
        self.url_manager.mark_visited(url)
        
        try:
            html = self.http_client.send_request(url)
            self.parse_and_store_data(html, folder_path, url)
        except ConnectionError as e:
            self.logger.log(str(e), level='ERROR')
    
    def parse_and_store_data(self, data, folder_path, base_url):
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(data, 'html.parser')
        
        # Example: Extract and log all links on the page
        for link in soup.find_all('a'):
            href = link.get('href')
            absolute_url = self.url_manager.normalize_url(href, base_url)
            self.logger.log(f"Found link: {absolute_url}")
        
        # Store the original HTML data
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        with open(os.path.join(folder_path, "data.html"), "w", encoding="utf-8") as file:
            file.write(data)

# --- Application Layer ---

class AppController:
    def __init__(self):
        self.scraper = Scraper()
    
    def start_scraping(self, url, folder_path):
        threading.Thread(target=self.scraper.scrape_url, args=(url, folder_path)).start()

class GUI(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Web Scraper")
        self.setup_ui()
    
    def setup_ui(self):
        self.url_label = ttk.Label(self, text="Enter URL:")
        self.url_label.pack(padx=10, pady=5)

        self.url_entry = ttk.Entry(self, width=50)
        self.url_entry.pack(padx=10, pady=5)

        self.scrape_button = ttk.Button(self, text="Scrape Data", command=self.on_start_scraping)
        self.scrape_button.pack(padx=10, pady=5)

    def on_start_scraping(self):
        url = self.url_entry.get()
        self.controller.start_scraping(url, 'output_folder')
        messagebox.showinfo("Started", "The scraping has started!")

# --- Main Application Logic ---

controller = AppController()
gui = GUI(controller)
gui.mainloop()