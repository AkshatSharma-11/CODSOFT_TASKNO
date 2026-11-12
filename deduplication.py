import os
import hashlib

def calculate_hash(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def scan_folder(folder_path):
    hash_map = {}
    duplicates = []

    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)

            try:
                file_hash = calculate_hash(file_path)

                if file_hash in hash_map:
                    duplicates.append(
                        (file_path, hash_map[file_hash])
                    )
                else:
                    hash_map[file_hash] = file_path

            except Exception as error:
                print("Error:", file_path, error)

    return hash_map, duplicates


def main():
    print("\n=== CLOUD DATA DEDUPLICATION SYSTEM ===")

    folder_path = input("Enter folder path to scan: ").strip()
    folder_path = folder_path.strip('"')

    if not os.path.isdir(folder_path):
        print("Invalid folder path!")
        return

    unique_files, duplicates = scan_folder(folder_path)

    print("\n--- SCAN REPORT ---")
    print("Unique files:", len(unique_files))
    print("Duplicate files:", len(duplicates))

    for duplicate, original in duplicates:
        print("\nDuplicate:", duplicate)
        print("Original :", original)

    print("\nScan completed successfully!")


if __name__ == "__main__":
    main()
