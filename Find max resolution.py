COMMON_RESOLUTIONS = [
    (640, 480),
    (800, 600),
    (1024, 768),
    (1280, 720),
    (1280, 960),
    (1600, 1200),
    (1920, 1080),
    (2560, 1440),
    (3840, 2160),
]

def find_max_supported_resolution(device_index=0):
    """
    Testa un insieme di risoluzioni standard e restituisce la massima supportata.
    """
    cap = cv2.VideoCapture(device_index)
    if not cap.isOpened():
        raise RuntimeError(f"Impossibile aprire la camera index={device_index}")

    supported = []
    for w, h in COMMON_RESOLUTIONS:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

        actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if actual_w == w and actual_h == h:
            supported.append((w, h))

    cap.release()

    if not supported:
        raise RuntimeError("Nessuna risoluzione standard supportata trovata.")

    # Ordina per area (w*h) e restituisci la più grande
    supported.sort(key=lambda x: x[0]*x[1], reverse=True)
    return supported[0]