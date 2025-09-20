import cv2
import os

# Funzione per generare l'outline
def create_outline(image_path):
    # Leggi l'immagine
    img = cv2.imread(image_path)
    
    if img is None:
        print(f"Errore: Immagine non trovata o non leggibile nel percorso {image_path}")
        return None
    
    # Converte l'immagine in scala di grigi
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Applica una sfocatura per ridurre il rumore
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Trova i contorni utilizzando Canny
    edges = cv2.Canny(blurred, threshold1=100, threshold2=200)
    
    # Crea un'immagine con il contorno
    outline_img = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)  # Per renderla a 3 canali come l'originale
    
    return outline_img

# Funzione per salvare l'immagine risultante
def save_image(output_path, image):
    cv2.imwrite(output_path, image)

if __name__ == "__main__":
    # Ottieni il percorso della cartella in cui si trova lo script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Percorso completo dell'immagine di input (nella stessa cartella dello script)
    input_image = os.path.join(script_dir, 'immagine.jpg')  # Modifica con il nome dell'immagine
    
    # Verifica se l'immagine esiste nella stessa cartella dello script
    if os.path.exists(input_image):
        # Crea il contorno
        outline = create_outline(input_image)
        
        if outline is not None:
            # Salva l'immagine di output nella stessa cartella
            output_image = os.path.join(script_dir, 'outline_immagine.jpg')
            save_image(output_image, outline)
            
            print(f"Immagine con contorno salvata come: {output_image}")
    else:
        print(f"L'immagine '{input_image}' non è stata trovata nel percorso {script_dir}.")
