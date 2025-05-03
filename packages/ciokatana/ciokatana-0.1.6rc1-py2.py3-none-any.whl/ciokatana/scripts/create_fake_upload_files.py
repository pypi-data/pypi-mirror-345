import os
import random
import sys
WORDS = [
    "file1",
    "document",
    "report",
    "project",
    "image",
    "video",
    "audio",
    "code",
    "program",
    "backup",
    "note",
    "presentation",
    "spreadsheet",
    "template",
    "log",
    "archive",
    "database",
    "configuration",
    "text",
    "worksheet",
    "invoice",
    "receipt",
    "letter",
    "memo",
    "form",
    "schedule",
    "agenda",
    "resume",
    "manual",
    "catalog",
    "index",
    "directory",
    "newsletter",
    "contract",
    "proposal",
    "agenda",
    "budget",
    "chart",
    "graph",
    "diagram",
    "plan",
    "summary",
    "survey",
    "policy",
    "procedure",
    "guide",
    "manifest",
    "manifesto",
    "manifestation",
    "request",
    "response",
    "history",
    "journal",
    "message",
    "announcement",
    "notification",
    "reminder",
    "alert",
    "task",
    "todo",
    "bookmark",
    "favorite",
    "link",
    "resource",
    "download",
    "upload",
    "attachment",
    "thumbnail",
    "avatar",
    "icon",
    "logo",
    "banner",
    "header",
    "footer",
    "slide",
    "frame",
    "badge",
    "button",
    "widget",
    "plugin",
    "theme",
    "template",
    "stylesheet",
    "script",
    "library",
    "package"
]

EXTS = [
    "txt",
    "pdf",
    "docx",
    "xlsx",
    "pptx",
    "jpg",
    "png",
    "gif",
    "mp3",
    "mp4",
    "wav",
    "avi",
    "csv",
    "json",
    "xml",
    "html",
    "css",
    "js",
    "py",
    "cpp",
    "h",
    "java",
    "php",
    "rb",
    "sh",
    "md",
    "zip",
    "rar",
    "tar",
    "gz"
]

ROOT_FOLDER = "C:/Users/julia/local_projects/test_files/"

MB_TO_BYTES = 1024 * 1024


def get_folder_size(folder_path):
    total_size = 0
    
    for path, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(path, file_name)
            total_size += os.path.getsize(file_path)
    
    return total_size

def report_folder_size(folder_path):
    size = get_folder_size(folder_path)
    
    if size < 1024:
        print(f"Folder size: {size} bytes")
    elif size < 1024**2:
        print(f"Folder size: {size/1024:.2f} KB")
    elif size < 1024**3:
        print(f"Folder size: {size/1024**2:.2f} MB")
    else:
        print(f"Folder size: {size/1024**3:.2f} GB")

def generate_files(
    min_directories=3,
    max_directories=7,
    min_seqs=1,
    max_seqs=3,
    min_files=10,
    max_files=20,
    min_size_mb=0.1,
    max_size_mb=1,
):
    # Create the root folder if it doesn't exist


    # Generate a random number of directories within the specified range
    num_directories = random.randint(min_directories, max_directories)

    directory_names = random.sample(WORDS, num_directories)
    files_to_generate = []
    folders_to_generate = []
    for i, directory_name in enumerate(directory_names):
        directory = os.path.join(ROOT_FOLDER, directory_name)
        folders_to_generate.append(directory)

        # Generate a random number of sequences within the specified range
        num_sequences = random.randint(min_seqs, max_seqs)
        sequence_names = random.sample(WORDS, num_sequences)
        extensions = random.sample(EXTS, num_sequences)

        for j, basename in enumerate(sequence_names):
            num_files = random.randint(min_files, max_files)
            size_mb = random.uniform(min_size_mb, max_size_mb)
            size_bytes = int(size_mb * MB_TO_BYTES)
            ext = extensions[j]
            # Generate a continuous sequence for each directory

            for k in range(num_files):
                
                # Convert the sequence to a padded string with leading zeros
                sequence_str = str(k).zfill(4)

                # Create the file with the desired format
                filename = f"{basename}.{sequence_str}.{ext}"
                filepath = os.path.join(directory, filename)

                files_to_generate.append((filepath, size_bytes))
                # Increment the sequence for the next file

    # Print the list of affected files
    print("The following files will be generated:")
    for file_path, size_bytes in files_to_generate:
        print(file_path, size_bytes)

    # Ask for confirmation before running the operation
    confirm = input("Do you want to continue? (yes/no): ")
    if confirm.lower() != "yes":
        print("Operation cancelled.")
        return

    for folder in folders_to_generate:
        os.makedirs(folder, exist_ok=True)
    for filepath, size_bytes in files_to_generate:
        with open(filepath, "wb") as file:
            file.write(os.urandom(size_bytes))
    print("Operation completed successfully.")
    report_folder_size(ROOT_FOLDER)

def replace_files(percentage, min_size_mb=None, max_size_mb=None):
    # Get a list of all files in the root folder and its subdirectories
    file_list = []
    for subdir, dirs, files in os.walk(ROOT_FOLDER):
        for file in files:
            file_path = os.path.join(subdir, file)
            file_list.append(file_path)

    # Calculate the number of files to be replaced based on the given percentage
    num_files_to_replace = int(len(file_list) * (percentage / 100))

    # Randomly select files from the list to replace
    files_to_replace = random.sample(file_list, num_files_to_replace)

    # Print the list of affected files
    print("The following files will be replaced with random content:")
    for file_path in files_to_replace:
        print(file_path)

    # Ask for confirmation before running the operation
    confirm = input("Do you want to continue? (yes/no): ")
    if confirm.lower() != "yes":
        print("Operation cancelled.")
        return

    # Replace the selected files with random content
    for file_path in files_to_replace:
        file_size = os.path.getsize(file_path)
        if min_size_mb is not None and max_size_mb is not None:
            min_size = int(min_size_mb * MB_TO_BYTES)
            max_size = int(max_size_mb * MB_TO_BYTES)
            file_size = random.randint(min_size, max_size)
        with open(file_path, "wb") as file:
            file.write(os.urandom(file_size))

    print("Operation completed successfully.")
    report_folder_size(ROOT_FOLDER)

# # Usage example:
# percentage = 5
# replace_files_with_random_content(root_folder, percentage)



# generate_files(
#     min_directories=3,
#     max_directories=7,
#     min_seqs=1,
#     max_seqs=3,
#     min_files=10,
#     max_files=20,
#     min_size_mb=0.1,
#     max_size_mb=1,
# )

replace_files(80, min_size_mb=1, max_size_mb=3)
