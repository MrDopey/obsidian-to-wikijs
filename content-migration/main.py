import datetime
import os

import yaml

date_now = (
    datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
)


def copy_folder_recursively(
    base_source_folder: str, base_destination_folder: str, suffix: str
) -> None:
    """
    Recursively copies the contents of the source_folder to the destination_folder,
    preserving the directory structure (depth). This implementation avoids using shutil.

    Args:
        source_folder (str): The path to the source folder.
        destination_folder (str): The path to the destination folder.
    """
    source_folder = os.path.join(base_source_folder, suffix)
    destination_folder = os.path.join(base_destination_folder, fix_file_name(suffix))

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
            destination_item_path = os.path.join(
                destination_folder, fix_file_name(item_name)
            )

            if os.path.isfile(source_item_path):

                file_type = item_name.rsplit(".", 1)[1]
                print(
                    f"Copying file {file_type}: '{source_item_path}' to '{destination_item_path}'"
                )

                match file_type:
                    case "md":
                        # If it's a file, copy it
                        with open(source_item_path, "r", encoding="utf-8") as src_file:
                            with open(
                                destination_item_path, "w", encoding="utf-8"
                            ) as dest_file:
                                data = add_front_matter(src_file.read(), item_name)
                                print(data)
                                dest_file.write(data)
                    case _:
                        with open(source_item_path, "rb") as src_file:
                            with open(destination_item_path, "wb") as dest_file:
                                dest_file.write(src_file.read())
            elif os.path.isdir(source_item_path):
                # If it's a directory, recursively call the function
                print(f"Entering directory: '{source_item_path}'")
                copy_folder_recursively(
                    base_source_folder,
                    base_destination_folder,
                    os.path.join(suffix, item_name),
                )
            else:
                print(f"Skipping unsupported item type: '{source_item_path}'")

        print(
            f"Successfully copied contents of '{source_folder}' to '{destination_folder}'."
        )
    except OSError as e:
        print(f"Operating system error during copy: {e}")


def fix_file_name(path: str) -> str:
    return path.lower().replace(" ", "-")


def add_front_matter(original_text: str, original_path: str) -> str:
    title = original_path.rsplit(".", 1)[0]

    matter, markdown = parse_markdown_with_front_matter(original_text)

    matter["title"] = title
    matter["description"] = title
    matter["published"] = True
    matter["date"] = date_now
    # https://github.com/requarks/wiki/blob/d96bbaf42c792f26559540e609b859fa038766ce/server/modules/storage/disk/common.js#L83
    # https://www.geeksforgeeks.org/javascript/lodash-_-isnil-method/
    tags = matter.get("tags", [])
    if len(tags) > 0:
        matter["tags"] = ", ".join(tags)
    matter["editor"] = "markdown"
    matter["dateCreated"] = date_now

    return f"---\n{yaml.dump(matter)}---\n\n{markdown}"


# ---
# title: Hello-world
# description:
# published: true
# date: 2025-07-19T14:40:21.207Z
# tags:
# editor: markdown
# dateCreated: 2025-07-17T13:14:54.918Z
# ---


def parse_markdown_with_front_matter(
    markdown_string: str,
) -> tuple[dict[str, any], str]:
    """
    Parses a Markdown string to extract front matter (YAML) and the remaining content.

    Front matter is expected to be at the very beginning of the string,
    enclosed by '---' on lines by themselves.

    Args:
        markdown_string (str): The input Markdown string, potentially with front matter.

    Returns:
        Tuple[Dict[str, Any], str]: A tuple containing:
            - A dictionary of the parsed front matter.
            - The Markdown string with the front matter removed.
            If no front matter is found, an empty dictionary and the original string are returned.
    """
    front_matter: dict[str, any] = {}
    content_start_index: int = 0
    lines = markdown_string.splitlines()

    # Check for the opening '---'
    if len(lines) > 0 and lines[0].strip() == "---":
        # Find the closing '---'
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                # Found the closing '---', extract the YAML content
                yaml_content = "\n".join(lines[1:i])
                try:
                    front_matter = yaml.safe_load(yaml_content)
                    if front_matter is None:  # Handle empty front matter block
                        front_matter = {}
                    content_start_index = (
                        i + 1
                    )  # Content starts after the closing '---'
                except yaml.YAMLError as e:
                    print(f"Warning: Could not parse front matter as YAML. Error: {e}")
                    # If parsing fails, treat the whole thing as regular markdown
                    front_matter = {}
                    content_start_index = 0
                break
        else:
            # No closing '---' found, treat the whole thing as regular markdown
            front_matter = {}
            content_start_index = 0
    else:
        # No opening '---', so no front matter
        front_matter = {}
        content_start_index = 0

    # Reconstruct the markdown content without the front matter
    truncated_markdown = "\n".join(lines[content_start_index:])

    return front_matter, truncated_markdown


if __name__ == "__main__":
    # --- Example Usage ---
    # Define your source and destination paths here.
    # For demonstration, we'll create some dummy folders and files.

    # Create a dummy source folder structure
    # dummy_source = "/workspaces/media-wiki/pages/supervising/policy"
    dummy_source = "/workspaces/media-wiki/pages"
    dummy_destination = "/workspaces/media-wiki/pages-parsed"

    if os.path.exists(dummy_destination) and os.path.isdir(dummy_destination):
        import shutil  # Temporarily import shutil for cleanup

        shutil.rmtree(dummy_destination)

    # Call the copy function
    copy_folder_recursively(dummy_source, dummy_destination, "")

    print("\n--- Verification ---")
    if os.path.exists(dummy_destination):
        print(f"Destination folder '{dummy_destination}' exists.")
        # print("Contents:")
        # for root, dirs, files in os.walk(dummy_destination):
        #     level = root.replace(dummy_destination, "").count(os.sep)
        #     indent = " " * 4 * (level)
        #     print(f"{indent}{os.path.basename(root)}/")
        #     subindent = " " * 4 * (level + 1)
        #     for f in files:
        #         print(f"{subindent}{f}")
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
