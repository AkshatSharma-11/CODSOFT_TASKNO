import os
import json
import shutil
import hashlib
import secrets
from datetime import datetime

APP_NAME = "CLOUD FILE STORAGE SYSTEM"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(BASE_DIR, "cloud_storage")
USERS_FILE = os.path.join(BASE_DIR, "users.json")

os.makedirs(STORAGE_DIR, exist_ok=True)


# ---------- USER MANAGEMENT ----------

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}

    try:
        with open(USERS_FILE, "r") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return {}


def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=4)


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        bytes.fromhex(salt),
        200000
    ).hex()


def register_user():
    users = load_users()

    print("\n========== REGISTRATION ==========")
    username = input("Create username: ").strip()

    if not username or any(c in username for c in r'\/:*?"<>|'):
        print("Invalid username.")
        return

    if username in users:
        print("Username already exists.")
        return

    password = input("Create password: ")

    if len(password) < 6:
        print("Password must be at least 6 characters.")
        return

    salt = secrets.token_hex(16)

    users[username] = {
        "salt": salt,
        "password": hash_password(password, salt),
        "created_at": datetime.now().isoformat()
    }

    save_users(users)
    os.makedirs(os.path.join(STORAGE_DIR, username), exist_ok=True)

    print("Registration successful!")


def login_user():
    users = load_users()

    print("\n========== LOGIN ==========")
    username = input("Username: ").strip()
    password = input("Password: ")

    if username not in users:
        print("Account not found.")
        return None

    salt = users[username]["salt"]
    password_hash = hash_password(password, salt)

    if password_hash != users[username]["password"]:
        print("Incorrect password.")
        return None

    print("Login successful. Welcome,", username)
    return username


# ---------- FILE MANAGEMENT ----------

def user_folder(username):
    folder = os.path.join(STORAGE_DIR, username)
    os.makedirs(folder, exist_ok=True)
    return folder


def safe_file_path(username, filename):
    if not filename or os.path.basename(filename) != filename:
        raise ValueError("Invalid file name.")

    return os.path.join(user_folder(username), filename)


def upload_file(username):
    print("\n========== UPLOAD FILE ==========")

    source = input("Enter complete file path: ").strip().strip('"')

    if not os.path.isfile(source):
        print("Source file not found.")
        return

    filename = os.path.basename(source)

    try:
        destination = safe_file_path(username, filename)

        if os.path.exists(destination):
            print("File already exists.")
            return

        shutil.copy2(source, destination)

        print("File uploaded successfully!")
        print("Name:", filename)
        print("Size:", os.path.getsize(destination), "bytes")

    except (OSError, ValueError) as error:
        print("Upload error:", error)


def list_files(username):
    print("\n========== YOUR FILES ==========")

    folder = user_folder(username)
    files = os.listdir(folder)

    if not files:
        print("Your storage is empty.")
        return

    for number, filename in enumerate(files, 1):
        path = os.path.join(folder, filename)

        if os.path.isfile(path):
            size = os.path.getsize(path)
            modified = datetime.fromtimestamp(
                os.path.getmtime(path)
            ).strftime("%d-%m-%Y %H:%M")

            print(
                f"{number}. {filename} | "
                f"{size} bytes | {modified}"
            )


def download_file(username):
    print("\n========== DOWNLOAD FILE ==========")

    filename = input("Enter file name: ").strip()

    try:
        source = safe_file_path(username, filename)

        if not os.path.isfile(source):
            print("File not found.")
            return

        destination = input(
            "Enter destination folder path: "
        ).strip().strip('"')

        if not os.path.isdir(destination):
            print("Destination folder does not exist.")
            return

        target = os.path.join(destination, filename)

        if os.path.abspath(source) == os.path.abspath(target):
            print("File is already at this location.")
            return

        if os.path.exists(target):
            print("A file with this name already exists there.")
            return

        shutil.copy2(source, target)
        print("Download successful!")

    except (OSError, ValueError) as error:
        print("Download error:", error)


def delete_file(username):
    print("\n========== DELETE FILE ==========")

    filename = input("Enter file name: ").strip()

    try:
        path = safe_file_path(username, filename)

        if not os.path.isfile(path):
            print("File not found.")
            return

        confirm = input(
            "Confirm deletion? (yes/no): "
        ).lower().strip()

        if confirm == "yes":
            os.remove(path)
            print("File deleted successfully.")
        else:
            print("Deletion cancelled.")

    except (OSError, ValueError) as error:
        print("Delete error:", error)


def rename_file(username):
    print("\n========== RENAME FILE ==========")

    old_name = input("Current file name: ").strip()
    new_name = input("New file name: ").strip()

    try:
        old_path = safe_file_path(username, old_name)
        new_path = safe_file_path(username, new_name)

        if not os.path.isfile(old_path):
            print("Original file not found.")
            return

        if os.path.exists(new_path):
            print("New file name already exists.")
            return

        os.rename(old_path, new_path)
        print("File renamed successfully.")

    except (OSError, ValueError) as error:
        print("Rename error:", error)


def search_file(username):
    print("\n========== SEARCH FILE ==========")

    keyword = input("Enter file name or keyword: ").lower().strip()

    if not keyword:
        print("Please enter a keyword.")
        return

    folder = user_folder(username)

    results = [
        name for name in os.listdir(folder)
        if keyword in name.lower()
        and os.path.isfile(os.path.join(folder, name))
    ]

    if results:
        print("Matching files:")
        for name in results:
            print("-", name)
    else:
        print("No matching files found.")


# ---------- STORAGE ANALYTICS ----------

def storage_report(username):
    print("\n========== STORAGE REPORT ==========")

    folder = user_folder(username)

    total_size = 0
    file_count = 0
    file_types = {}

    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)

        if os.path.isfile(path):
            size = os.path.getsize(path)
            total_size += size
            file_count += 1

            extension = os.path.splitext(filename)[1].lower()
            extension = extension if extension else "No extension"

            file_types[extension] = (
                file_types.get(extension, 0) + 1
            )

    print("Total files:", file_count)
    print("Total storage:", round(total_size / 1024, 2), "KB")
    print("Total storage:", round(total_size / (1024 * 1024), 2), "MB")

    print("\nFile type summary:")

    if file_types:
        for extension, count in file_types.items():
            print(extension, ":", count, "file(s)")
    else:
        print("No files available.")


# ---------- USER DASHBOARD ----------

def dashboard(username):
    while True:
        print("\n")
        print("=" * 45)
        print("          CLOUD STORAGE DASHBOARD")
        print("=" * 45)
        print("Logged in as:", username)
        print("-" * 45)

        print("1. Upload File")
        print("2. View All Files")
        print("3. Download File")
        print("4. Delete File")
        print("5. Rename File")
        print("6. Search File")
        print("7. Storage Report")
        print("8. Logout")

        print("=" * 45)

        choice = input("Select an option (1-8): ").strip()

        if choice == "1":
            upload_file(username)

        elif choice == "2":
            list_files(username)

        elif choice == "3":
            download_file(username)

        elif choice == "4":
            delete_file(username)

        elif choice == "5":
            rename_file(username)

        elif choice == "6":
            search_file(username)

        elif choice == "7":
            storage_report(username)

        elif choice == "8":
            print("Logged out successfully.")
            break

        else:
            print("Invalid choice. Please try again.")


# ---------- MAIN APPLICATION ----------

def main():
    while True:
        print("\n")
        print("=" * 45)
        print("       " + APP_NAME)
        print("=" * 45)

        print("1. Register")
        print("2. Login")
        print("3. Exit")

        print("=" * 45)

        choice = input("Enter your choice (1-3): ").strip()

        if choice == "1":
            register_user()

        elif choice == "2":
            username = login_user()

            if username:
                dashboard(username)

        elif choice == "3":
            print("Thank you for using Cloud File Storage!")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()