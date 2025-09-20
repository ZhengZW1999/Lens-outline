import cv2
import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk
import os
from datetime import datetime

# ==== PATH CARTELLA BASE ====
BASE_DIR = os.path.join(os.path.expanduser("~"), "Documents", "Outile")

# ==== VARIABILI GLOBALI ====
cap = cv2.VideoCapture(0)  # webcam (cambia indice se non è 0)
frame = None
captured_img = None
processed_img = None
save_dir = None

# ==== FUNZIONI ====
def show_frame():
    global frame
    ret, frame = cap.read()
    if ret:
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)
    lmain.after(10, show_frame)

def capture_image():
    global captured_img, save_dir
    if frame is None:
        return
    captured_img = frame.copy()
    show_image(captured_img, original=True)

def show_image(img, original=False, processed=False):
    cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img_pil)
    if original:
        lcaptured.imgtk = imgtk
        lcaptured.configure(image=imgtk, text="Originale")
    if processed:
        lprocessed.imgtk = imgtk
        lprocessed.configure(image=imgtk, text="Elaborata")

def process_image():
    global captured_img, processed_img
    if captured_img is None:
        return
    gray = cv2.cvtColor(captured_img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    processed_img = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    show_image(processed_img, processed=True)

def export_data():
    global captured_img, processed_img, save_dir
    if captured_img is None or processed_img is None:
        return
    # crea cartella timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_dir = os.path.join(BASE_DIR, timestamp)
    os.makedirs(save_dir, exist_ok=True)

    # salva immagini
    cv2.imwrite(os.path.join(save_dir, "Original.jpg"), captured_img)
    cv2.imwrite(os.path.join(save_dir, "Outlined.jpg"), processed_img)

    # crea file DXF placeholder
    dxf_path = os.path.join(save_dir, "Data.dxf")
    with open(dxf_path, "w") as f:
        f.write("0\nSECTION\n2\nHEADER\n0\nENDSEC\n0\nEOF\n")
    print("Salvato tutto in:", save_dir)

# ==== UI ====
root = tk.Tk()
root.title("Camera Capture Tool")

# live preview
lmain = Label(root)
lmain.pack()

btn_capture = Button(root, text="Cattura Immagine", command=capture_image)
btn_capture.pack()

lcaptured = Label(root, text="Immagine Originale")
lcaptured.pack()

btn_process = Button(root, text="Elabora Immagine", command=process_image)
btn_process.pack()

lprocessed = Label(root, text="Immagine Elaborata")
lprocessed.pack()

btn_export = Button(root, text="Esporta", command=export_data)
btn_export.pack()

# avvia loop live
show_frame()
root.mainloop()

# cleanup
cap.release()
cv2.destroyAllWindows()
