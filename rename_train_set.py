import os


def rename_files(folder_path):
    if not os.path.isdir(folder_path):
        print("Invalid folder path")
        return

    files = sorted(os.listdir(folder_path))  # Sort to maintain order
    count = 1

    for file in files:
        file_path = os.path.join(folder_path, file)

        if os.path.isfile(file_path):  # Ensure it's a file
            ext = os.path.splitext(file)[1]  # Get file extension
            new_name = f"your_label_name_{count}{ext}"
            new_path = os.path.join(folder_path, new_name)

            os.rename(file_path, new_path)
            print(f'Renamed: {file} -> {new_name}')
            count += 1


# Example usage
folder_path = r""  # Replace with your actual folder path
rename_files(folder_path)