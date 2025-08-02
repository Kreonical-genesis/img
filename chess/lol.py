import os
from PIL import Image, ImageSequence

def get_combined_bbox(frames):
    bbox = None
    for frame in frames:
        alpha = frame.getchannel("A")  # Альфа-канал
        frame_bbox = alpha.getbbox()
        if frame_bbox:
            if bbox is None:
                bbox = frame_bbox
            else:
                bbox = (
                    min(bbox[0], frame_bbox[0]),
                    min(bbox[1], frame_bbox[1]),
                    max(bbox[2], frame_bbox[2]),
                    max(bbox[3], frame_bbox[3]),
                )
    return bbox

def crop_gif(path):
    original = Image.open(path)
    frames = []

    # Преобразуем в RGBA каждый кадр
    for frame in ImageSequence.Iterator(original):
        frame_rgba = frame.convert("RGBA")
        frames.append(frame_rgba)

    bbox = get_combined_bbox(frames)
    if bbox is None:
        print(f"[!] {path} содержит только прозрачные пиксели.")
        return

    # Обрезаем все кадры
    cropped_frames = [f.crop(bbox) for f in frames]

    # Сохраняем
    os.makedirs("cropped", exist_ok=True)
    save_path = os.path.join("cropped", os.path.basename(path))
    cropped_frames[0].save(
        save_path,
        save_all=True,
        append_images=cropped_frames[1:],
        loop=original.info.get("loop", 0),
        duration=original.info.get("duration", 100),
        disposal=2,
        transparency=0
    )
    print(f"[✓] Сохранено: {save_path}")

def crop_all_gifs_in_folder():
    for filename in os.listdir("."):
        if filename.lower().endswith(".gif"):
            crop_gif(filename)

if __name__ == "__main__":
    crop_all_gifs_in_folder()
