import os


def copy_folder_recursively(source_folder: str, destination_folder: str) -> None:
    """
    Recursively copies the contents of the source_folder to the destination_folder,
    preserving the directory structure (depth). This implementation avoids using shutil.

    Args:
        source_folder (str): The path to the source folder.
        destination_folder (str): The path to the destination folder.
    """
    # Check if the source folder exists
    if not os.path.exists(source_folder):
        print(f"Error: Source folder '{source_folder}' does not exist.")
        return

    # Check if the source path is actually a directory
    if not os.path.isdir(source_folder):
        print(f"Error: Source path '{source_folder}' is not a directory.")
        return

    # Create the destination root folder if it doesn't exist
    # If it exists, we will proceed to copy into it, overwriting files if they have the same name.
    os.makedirs(destination_folder, exist_ok=True)
    print(f"Ensured destination folder '{destination_folder}' exists.")

    try:
        # Walk through the source directory
        for item_name in os.listdir(source_folder):
            source_item_path = os.path.join(source_folder, item_name)
            destination_item_path = os.path.join(destination_folder, item_name)

            if os.path.isfile(source_item_path):
                # If it's a file, copy it
                print(
                    f"Copying file: '{source_item_path}' to '{destination_item_path}'"
                )
                with open(source_item_path, "rb") as src_file:
                    with open(destination_item_path, "wb") as dest_file:
                        dest_file.write(src_file.read())
            elif os.path.isdir(source_item_path):
                # If it's a directory, recursively call the function
                print(f"Entering directory: '{source_item_path}'")
                copy_folder_recursively(source_item_path, destination_item_path)
            else:
                print(f"Skipping unsupported item type: '{source_item_path}'")

        print(
            f"Successfully copied contents of '{source_folder}' to '{destination_folder}'."
        )
    except OSError as e:
        print(f"Operating system error during copy: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    # --- Example Usage ---
    # Define your source and destination paths here.
    # For demonstration, we'll create some dummy folders and files.

    # Create a dummy source folder structure
    dummy_source = "source_folder_example_manual"
    dummy_destination = "destination_folder_example_manual"

    # Clean up previous runs if they exist
    # Using os.path.exists and os.path.isdir to avoid issues if it's a file
    if os.path.exists(dummy_source) and os.path.isdir(dummy_source):
        import shutil  # Temporarily import shutil for cleanup

        shutil.rmtree(dummy_source)
    if os.path.exists(dummy_destination) and os.path.isdir(dummy_destination):
        import shutil  # Temporarily import shutil for cleanup

        shutil.rmtree(dummy_destination)

    os.makedirs(os.path.join(dummy_source, "sub_dir1"), exist_ok=True)
    os.makedirs(os.path.join(dummy_source, "sub_dir2", "nested_dir"), exist_ok=True)

    with open(os.path.join(dummy_source, "file1.txt"), "w") as f:
        f.write("This is file 1.")
    with open(os.path.join(dummy_source, "sub_dir1", "file2.txt"), "w") as f:
        f.write("This is file 2 in sub_dir1.")
    with open(
        os.path.join(dummy_source, "sub_dir2", "nested_dir", "file3.txt"), "w"
    ) as f:
        f.write("This is file 3 in nested_dir.")

    print(f"Created dummy source folder: {dummy_source}")
    print("Contents:")
    for root, dirs, files in os.walk(dummy_source):
        level = root.replace(dummy_source, "").count(os.sep)
        indent = " " * 4 * (level)
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 4 * (level + 1)
        for f in files:
            print(f"{subindent}{f}")
    print("-" * 30)

    # Call the copy function
    copy_folder_recursively(dummy_source, dummy_destination)

    print("\n--- Verification ---")
    if os.path.exists(dummy_destination):
        print(f"Destination folder '{dummy_destination}' exists.")
        print("Contents:")
        for root, dirs, files in os.walk(dummy_destination):
            level = root.replace(dummy_destination, "").count(os.sep)
            indent = " " * 4 * (level)
            print(f"{indent}{os.path.basename(root)}/")
            subindent = " " * 4 * (level + 1)
            for f in files:
                print(f"{subindent}{f}")
    else:
        print(
            f"Destination folder '{dummy_destination}' does not exist after copy attempt."
        )

    # You can uncomment the following lines to clean up the dummy folders after running
    # Note: Using shutil for cleanup as it's more robust for removing directories.
    # if os.path.exists(dummy_source) and os.path.isdir(dummy_source):
    #     import shutil
    #     shutil.rmtree(dummy_source)
    # if os.path.exists(dummy_destination) and os.path.isdir(dummy_destination):
    #     import shutil
    #     shutil.rmtree(dummy_destination)
    # print("\nCleaned up dummy folders.")
