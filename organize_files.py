import os
import shutil

DOWNLOADS = r"C:\Users\rcxsm\Downloads"

def unique_path(path: str) -> str:
    """Return a non-clashing path by appending (1), (2), ... if needed."""
    base, ext = os.path.splitext(path)
    i = 1
    candidate = path
    while os.path.exists(candidate):
        candidate = f"{base} ({i}){ext}"
        i += 1
    return candidate

def main(folder: str = DOWNLOADS) -> None:
    try:
        script_path = os.path.abspath(__file__)
    except NameError:
        script_path = None

    # Work only on top-level files
    for entry in os.scandir(folder):
        if not entry.is_file():
            continue
        if script_path and os.path.abspath(entry.path) == script_path:
            continue

        name = entry.name
        ext = name.rsplit(".", 1)[-1].lower() if "." in name else "noext"
        dest_dir = os.path.join(folder, ext)

        os.makedirs(dest_dir, exist_ok=True)

        target = os.path.join(dest_dir, name)
        target = unique_path(target)

        try:
            shutil.move(entry.path, target)
            print(f"Moved: {name} -> {dest_dir}")
        except Exception as e:
            print(f"Skip:  {name}  Reason: {e}")

if __name__ == "__main__":
    main()
