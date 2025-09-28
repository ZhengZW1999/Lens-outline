import cv2
import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk
import os
from datetime import datetime

device_index = 0
camera = None
frame = None
captured_img = None
elaborated_img = None
status =  None

# ==== PATH CARTELLA BASE ====
BASE_DIR = os.path.join(os.path.expanduser("~"), "Documents", "Outline")

# Funzione per aggiornare l'immagine nella finestra
def update_frame():
    ret, frame = camera.read()
    if ret:
        # Converti l'immagine da BGR (OpenCV) a RGB (Pillow)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)

        # Aggiorna la label con la nuova immagine
        label.imgtk = imgtk
        label.configure(image=imgtk)

    # Richiama questa funzione dopo 10ms (loop)
    root.after(10, update_frame)

def capture_image():
    global captured_img, save_dir
    if frame is None:
        return
    captured_img = frame.copy()
    #show_image(captured_img, original=True)
    

if __name__ == "__main__":

    """
    Mostra la camera in una finestra Tkinter.
    """
    # Apri la camera
    camera = cv2.VideoCapture(device_index)
    if not camera.isOpened():
        raise RuntimeError(f"Impossibile aprire la camera con indice {device_index}")

    # Crea finestra Tkinter
    root = tk.Tk()
    root.title("Live Camera")

    # Label per mostrare le immagini
    label = tk.Label(root)
    label.pack()

    btn_capture = Button(root, text="Cattura Immagine", command=capture_image)
    btn_capture.pack()

    # Avvia aggiornamento del frame
    update_frame()

    # Quando chiudi la finestra, libera la camera
    def on_closing():
        camera.release()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Avvia il loop della finestra
    root.mainloop()