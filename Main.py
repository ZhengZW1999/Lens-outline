"""
camera_app_mod.py
Applicazione: live camera + scatto + anteprima originale + outline (UI moderna con customtkinter)
Dipendenze: opencv-python, pillow, customtkinter
Installa: pip install opencv-python pillow customtkinter
"""

import cv2
import os
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
from datetime import datetime

# -----------------------
# Config customtkinter
# -----------------------
ctk.set_appearance_mode("System")  # "Light", "Dark", "System"
ctk.set_default_color_theme("blue")

# -----------------------
# Funzioni di elaborazione
# -----------------------
def create_outline_from_bgr(frame_bgr):
    """
    Crea l'immagine di contorno (outline) a partire da un frame BGR (OpenCV).
    Ritorna un'immagine BGR (3 canali) con i contorni in bianco su sfondo nero.
    """
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 100, 200)
    outline_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    return outline_bgr

def bgr_to_tkimage(frame, max_size=(800, 600)):
    # BGR → RGB
    img = Image.fromarray(frame[:, :, ::1])

    # Ridimensionamento
    img.thumbnail(max_size, Image.Resampling.LANCZOS)

    # Converti in CTkImage
    ctk_img = ctk.CTkImage(light_image=img, size=img.size)

    return ctk_img
# -----------------------
# Finestra di anteprima (Original + Outlined)
# -----------------------
class PreviewWindow(ctk.CTkToplevel):
    def __init__(self, parent, original_bgr, outlined_bgr):
        super().__init__(parent)
        self.title("Anteprima - Originale e Outline")
        self.geometry("1000x600")
        self.resizable(True, True)

        self.original_bgr = original_bgr
        self.outlined_bgr = outlined_bgr

        # Frame per le immagini affiancate
        imgs_frame = ctk.CTkFrame(self)
        imgs_frame.pack(fill="both", expand=True, padx=12, pady=12)

        # Colonne per Originale e Outline
        left_col = ctk.CTkFrame(imgs_frame)
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0,6))
        right_col = ctk.CTkFrame(imgs_frame)
        right_col.grid(row=0, column=1, sticky="nsew", padx=(6,0))

        imgs_frame.grid_columnconfigure(0, weight=1)
        imgs_frame.grid_columnconfigure(1, weight=1)
        imgs_frame.grid_rowconfigure(0, weight=1)

        # Converti immagini adatte al display (ridotte se necessario)
        # Prendiamo la dimensione corrente della finestra per scegliere una size ragionevole:
        max_thumb = (480, 480)

        self.tk_original = bgr_to_tkimage(self.original_bgr, max_size=max_thumb)
        self.tk_outlined = bgr_to_tkimage(self.outlined_bgr, max_size=max_thumb)

        # Labels per le immagini
        self.lbl_orig = ctk.CTkLabel(left_col, text="Originale", image=self.tk_original, compound="top")
        self.lbl_orig.pack(fill="both", expand=True, padx=6, pady=6)

        self.lbl_out = ctk.CTkLabel(right_col, text="Outlined", image=self.tk_outlined, compound="top")
        self.lbl_out.pack(fill="both", expand=True, padx=6, pady=6)

        # Frame bottoni
        btns_frame = ctk.CTkFrame(self)
        btns_frame.pack(fill="x", padx=12, pady=(0,12))

        save_orig_btn = ctk.CTkButton(btns_frame, text="💾 Salva Originale", command=self.save_original)
        save_orig_btn.pack(side="left", padx=8)

        save_out_btn = ctk.CTkButton(btns_frame, text="💾 Salva Outline", command=self.save_outlined)
        save_out_btn.pack(side="left", padx=8)

        close_btn = ctk.CTkButton(btns_frame, text="Chiudi", command=self.destroy)
        close_btn.pack(side="right", padx=8)

    def save_original(self):
        # Dialog per scegliere percorso di salvataggio per immagine originale
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"Original_{now}.jpg"
        path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")],
                                            initialfile=default_name,
                                            title="Salva immagine originale")
        if path:
            cv2.imwrite(path, self.original_bgr)

    def save_outlined(self):
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"Outlined_{now}.jpg"
        path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")],
                                            initialfile=default_name,
                                            title="Salva immagine outline")
        if path:
            cv2.imwrite(path, self.outlined_bgr)

# -----------------------
# Applicazione principale
# -----------------------
class CameraApp(ctk.CTk):
    def __init__(self, device_index=0):
        super().__init__()
        self.title("Outile - Live Camera")
        self.geometry("900x700")
        self.resizable(True, True)

        # Variabili
        self.device_index = device_index
        self.cap = cv2.VideoCapture(self.device_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Impossibile aprire la camera con indice {self.device_index}")

        self.current_frame = None  # frame BGR corrente
        self.preview_open = False

        # Layout: area video + barra inferiore con bottone centrato
        self.video_frame = ctk.CTkFrame(self)
        self.video_frame.pack(fill="both", expand=True, padx=12, pady=(12,6))

        # Label che conterrà l'immagine (live o immagine congelata)
        self.video_label = ctk.CTkLabel(self.video_frame, text="")
        self.video_label.place(relx=0.5, rely=0.5, anchor="center")  # posizionamento centrale

        # Barra inferiore con bottone Scatta centrato
        bottom_bar = ctk.CTkFrame(self, height=80)
        bottom_bar.pack(fill="x", side="bottom", padx=12, pady=12)

        # riempi lo spazio con due spaziatori e bottone al centro
        left_spacer = ctk.CTkFrame(bottom_bar, width=1)
        left_spacer.pack(side="left", expand=True)
        self.capture_btn = ctk.CTkButton(bottom_bar, text="📸 Scatta Foto", width=220, height=44,
                                         command=self.capture_photo)
        self.capture_btn.pack(side="left", pady=8)
        right_spacer = ctk.CTkFrame(bottom_bar, width=1)
        right_spacer.pack(side="left", expand=True)

        # Hook per chiusura pulita
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Avvia loop video
        self.after(10, self.update_video_loop)

    def update_video_loop(self):
        """
        Legge un frame dalla camera e lo mostra nella GUI.
        Chiamata ricorsiva tramite after().
        """
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame.copy()
            # dimensione adattiva: riduci immagine per adattarsi alla finestra
            win_w = max(200, self.winfo_width() - 40)
            win_h = max(200, self.winfo_height() - 140)
            # calcola una size massima per thumbnail
            max_size = (win_w, win_h)
            tkimg = bgr_to_tkimage(frame, max_size=max_size)
            # assegna immagine alla label
            self.video_label.configure(image=tkimg)
            self.video_label.image = tkimg  # keep reference

        # loop
        self.after(20, self.update_video_loop)

    def capture_photo(self):
        """
        Quando l'utente preme Scatta Foto:
          - congela l'ultimo frame
          - genera outline
          - apre PreviewWindow che mostra Originale e Outline
        """
        if self.current_frame is None:
            return

        original = self.current_frame.copy()
        outlined = create_outline_from_bgr(original)

        # apri finestra di anteprima
        PreviewWindow(self, original, outlined)

    def on_close(self):
        # rilascio camera e chiusura
        try:
            if self.cap is not None:
                self.cap.release()
        except Exception:
            pass
        self.destroy()


# -----------------------
# MAIN
# -----------------------
def main():
    # Se vuoi cambiare device_index metti 1,2,...
    app = CameraApp(device_index=0)
    app.mainloop()

if __name__ == "__main__":
    main()
