import os
import shutil


def copy_folder_recursively(source_folder, destination_folder):
    """
    Recursively copies the contents of the source_folder to the destination_folder,
    preserving the directory structure (depth).

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

    # Check if the destination folder already exists.
    # shutil.copytree requires the destination to NOT exist.
    if os.path.exists(destination_folder):
        print(f"Warning: Destination folder '{destination_folder}' already exists.")
        print("Attempting to remove existing destination to ensure a clean copy.")
        try:
            shutil.rmtree(destination_folder)
            print(
                f"Successfully removed existing destination folder: '{destination_folder}'"
            )
        except OSError as e:
            print(
                f"Error: Could not remove existing destination folder '{destination_folder}'."
            )
            print(
                f"Please delete it manually or choose a different destination. Error: {e}"
            )
            return

    try:
        # shutil.copytree copies the entire directory tree from src to dst.
        # The dst directory must not already exist. It is created during the copy.
        shutil.copytree(source_folder, destination_folder)
        print(f"Successfully copied '{source_folder}' to '{destination_folder}'.")
    except shutil.Error as e:
        print(f"Error during copy operation: {e}")
    except OSError as e:
        print(f"Operating system error during copy: {e}")


if __name__ == "__main__":
    # --- Example Usage ---
    # Define your source and destination paths here.
    # For demonstration, we'll create some dummy folders and files.

    # Create a dummy source folder structure
    dummy_source = "source_folder_example"
    dummy_destination = "destination_folder_example"

    # Clean up previous runs if they exist
    if os.path.exists(dummy_source):
        shutil.rmtree(dummy_source)
    if os.path.exists(dummy_destination):
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
    # if os.path.exists(dummy_source):
    #     shutil.rmtree(dummy_source)
    # if os.path.exists(dummy_destination):
    #     shutil.rmtree(dummy_destination)
    # print("\nCleaned up dummy folders.")
