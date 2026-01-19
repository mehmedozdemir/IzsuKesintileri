import customtkinter
import requests
import threading

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("İZSU Su Kesintileri")
        self.geometry("900x700")

        customtkinter.set_appearance_mode("system") 

        # --- Main Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Top Frame for Filters ---
        self.filter_frame = customtkinter.CTkFrame(self, height=50)
        self.filter_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        self.search_entry = customtkinter.CTkEntry(self.filter_frame, placeholder_text="İlçe veya mahalle ara...")
        self.search_entry.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self.filter_outages)

        # --- Scrollable Frame for Outages ---
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self, label_text="Güncel Kesintiler")
        self.scrollable_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # --- Data ---
        self.outages = []
        self.load_data()

    def fetch_data(self):
        """Fetches water outage data in a separate thread."""
        def thread_target():
            try:
                url = "https://www.izsu.gov.tr/SuKesintileri/suKesintileriGetirJS"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                self.outages = response.json()
                # Schedule the UI update on the main thread - CORRECTED
                self.after(0, self.populate_outages, self.outages)
            except requests.RequestException as e:
                print(f"Veri çekilemedi: {e}")
                self.after(0, self.show_error)

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        loading_label = customtkinter.CTkLabel(self.scrollable_frame, text="Veriler yükleniyor...", font=("Arial", 16))
        loading_label.pack(pady=20)

        fetch_thread = threading.Thread(target=thread_target)
        fetch_thread.start()

    # MOVED to correct indentation
    def populate_outages(self, outages_list):
        """Clears the list and populates it with a given list of outages."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not outages_list:
            no_outage_label = customtkinter.CTkLabel(self.scrollable_frame, text="Bu filtreyle eşleşen kesinti bulunamadı.", font=("Arial", 16))
            no_outage_label.pack(pady=20)
            return

        for outage in outages_list:
            # Create a container frame for each outage entry
            outage_frame = customtkinter.CTkFrame(self.scrollable_frame, corner_radius=5)
            outage_frame.pack(pady=8, padx=10, fill="x")
            outage_frame.grid_columnconfigure(1, weight=1) # Allow data column to expand

            # --- Ilce (District) ---
            ilce = outage.get('IlceAdi', 'N/A')
            ilce_label = customtkinter.CTkLabel(outage_frame, text=f"📍 {ilce}", font=customtkinter.CTkFont(size=16, weight="bold"))
            ilce_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

            # --- Mahalleler (Neighborhoods) ---
            mahalleler = outage.get('Mahalleler', 'N/A')
            mahalleler_label = customtkinter.CTkLabel(outage_frame, text=f"🏘️ Mahalleler: {mahalleler}", justify="left", wraplength=700)
            mahalleler_label.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")
            
            # --- Kesinti Suresi (Outage Duration) ---
            kesinti_suresi = outage.get('KesintiSuresi', 'N/A')
            suresi_label = customtkinter.CTkLabel(outage_frame, text=f"🕒 Süre: {kesinti_suresi}", justify="left", wraplength=700)
            suresi_label.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

            # --- Aciklama (Description) ---
            aciklama = outage.get('Aciklama', 'N/A')
            aciklama_label = customtkinter.CTkLabel(outage_frame, text=f"ℹ️ Açıklama: {aciklama}", justify="left", wraplength=700)
            aciklama_label.grid(row=3, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="w")
    
    def filter_outages(self, event=None):
        """Filter outages based on the search entry text."""
        search_term = self.search_entry.get().lower()

        if not search_term:
            self.populate_outages(self.outages)
            return

        filtered_list = []
        for outage in self.outages:
            ilce = outage.get('IlceAdi', '').lower()
            mahalleler = outage.get('Mahalleler', '').lower()
            if search_term in ilce or search_term in mahalleler:
                filtered_list.append(outage)
        
        self.populate_outages(filtered_list)

    def show_error(self):
        """Displays an error message in the scrollable frame."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        error_label = customtkinter.CTkLabel(self.scrollable_frame, text="Veriler yüklenemedi.\nİnternet bağlantınızı kontrol edin.", font=("Arial", 16), text_color="red")
        error_label.pack(pady=20)

    def load_data(self):
        """Initiates the data loading process."""
        self.fetch_data()


if __name__ == "__main__":
    app = App()
    app.mainloop()
