# rm -rf ./pages/classrooms/ ./pages/one-off/ ./pages/supervising/Courses/ ./pages/Templates/ ./pages/index.md
import datetime
import os
from pathlib import Path

import re
import urllib.parse
import yaml

date_now = (
    datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
)


def copy_folder_recursively(
    base_source_folder: str,
    base_destination_folder: str,
    suffix: str,
    note_map: dict[str, Path],
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
                                data = add_front_matter(
                                    src_file.read(),
                                    item_name,
                                    Path(source_item_path),
                                    note_map,
                                )
                                # print(data)
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
                    note_map,
                )
            else:
                print(f"Skipping unsupported item type: '{source_item_path}'")

        print(
            f"Successfully copied contents of '{source_folder}' to '{destination_folder}'."
        )

        markddown_files = [ f for f in os.listdir(source_folder)] 
        if suffix != "" and len(markddown_files) > 0:
            markdown_index = create_index_markdown(os.path.basename(source_folder), markddown_files)
            index_file_name = os.path.join(destination_folder, "..", f"{os.path.basename(destination_folder)}.md")
            with open(index_file_name, "w") as dest_file:
                dest_file.write(markdown_index)

            print(f"Wrote index file {index_file_name}")
    except OSError as e:
        print(f"Operating system error during copy: {e}")

def create_index_markdown(title: str, markddown_files: list[str]) -> str:
    markddown_files.sort(key=lambda x: x.lower())
    converted_link_markdown = "\n".join(f"  - [{"" if f.endswith(".md") else "/"}{get_file_name(f)}](./{fix_file_name(title)}/{fix_file_name(get_file_name(f))})" for f in markddown_files)
    matter = {}
    matter["title"] = title
    matter["description"] = title
    matter["published"] = True
    matter["date"] = date_now
    matter["editor"] = "markdown"
    matter["dateCreated"] = date_now

    return f"---\n{yaml.dump(matter)}---\n\n{converted_link_markdown}"

def fix_file_name(path: str) -> str:
    """
    Sanitizes a file path by replacing dots with hyphens in the filename
    portion, while preserving the extension.

    Args:
        filepath (str): The original file path.

    Returns:
        str: The sanitized file path.
    """
    directory, filename = os.path.split(path)
    name, ext = os.path.splitext(filename)

    # return path
    sanitized_name = name.replace('.', '')
    sanitized_filename = sanitized_name + ext

    return os.path.join(directory, sanitized_filename).lower().replace(" - ", "-").replace(" ", "-")

def get_file_name(path: str) -> str:
    return path[:-3] if path.endswith(".md") else path

def add_front_matter(
    original_text: str, original_path: str, path: Path, note_map: dict[str, Path]
) -> str:
    title = original_path.rsplit(".", 1)[0]

    matter, markdown = parse_markdown_with_front_matter(original_text)
    converted_link_markdown = convert_wikilinks_to_markdown_links(
        markdown, path, note_map
    )

    parsed_tags = get_extra_tags(converted_link_markdown)

    matter["title"] = title
    matter["description"] = title
    matter["published"] = True
    matter["date"] = date_now
    # https://github.com/requarks/wiki/blob/d96bbaf42c792f26559540e609b859fa038766ce/server/modules/storage/disk/common.js#L83
    # https://www.geeksforgeeks.org/javascript/lodash-_-isnil-method/
    tags = matter.get("tags", [])
    tags.extend(parsed_tags)
    filtered_tags = filter_tags(tags)
    if len(filtered_tags) > 0:
        matter["tags"] = ", ".join(filtered_tags)
    matter["editor"] = "markdown"
    matter["dateCreated"] = date_now

    return f"---\n{yaml.dump(matter)}---\n\n{converted_link_markdown}"


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


def wikilink_to_mdlink(match, current_file: Path, note_map: dict[str, Path]):
    raw = match.group(0)
    target = match.group(1).strip()
    anchor = match.group(2) or ""
    alias = match.group(4) or target.split("/")[-1]

    # Remove anchor from target
    if "#" in target:
        target, inline_anchor = target.split("#", 1)
        anchor = f"#{inline_anchor}"

    # Get note path
    target_entry = note_map.get(target.split("/")[-1])
    if not target_entry:
        return raw  # leave wikilink as-is if target not found

    target_path = target_entry.with_suffix(".md")
    # use_absolute = True
    # if target_path.is_relative_to(current_file.parent.resolve()):
    #     relative_path = target_path.relative_to(current_file.parent.resolve())
    #     use_absolute = sum(1 for part in relative_path.parts if part == "..") > 1
    try:
        relative_path = target_path.relative_to(current_file.parent.resolve())
    except ValueError:
        # Not a subpath → use absolute-from-vault
        # relative_path = target_path.relative_to(VAULT_PATH)
        use_absolute = True
    else:
        use_absolute = sum(1 for part in relative_path.parts if part == "..") > 1
    # Count how many parent traversals are needed (e.g. ../../)

    if use_absolute:
        # Use absolute-from-vault path
        abs_path = target_entry.with_suffix(".md")
        link_path = f"/{abs_path.as_posix()}"
    else:
        # Use relative path
        link_path = relative_path.as_posix()

    # Encode URL (spaces, special chars)
    encoded_path = urllib.parse.quote(fix_file_name(link_path).rsplit(".", 1)[0])
    return f"[{alias}]({encoded_path}{anchor})"


def convert_wikilinks_to_markdown_links(
    markdown: str, file_path: Path, note_map: dict[str, Path]
) -> str:
    def repl(match):
        return wikilink_to_mdlink(match, file_path.resolve(), note_map)

    converted = re.sub(r"\[\[([^\]\|#]+)(#[^\]\|]+)?(\|([^\]]+))?\]\]", repl, markdown)
    return converted


def get_extra_tags(markdown: str) -> list[str]:
    regex = r"[^#\w](#[a-zA-Z/]+)"
    return re.findall(regex, markdown)

def filter_tags(tags: list[str]) -> list[str]:
    res = set[str]()
    for t in tags:
        # Need to break it up, as slashes are individually requested
        # https://github.com/requarks/wiki/blob/d96bbaf42c792f26559540e609b859fa038766ce/client/components/tags.vue#L245
        splits = (t[1:] if t.startswith("#") else t).split("/")
        if splits[0] == "course" and len(splits) > 2:
            continue
        else:
            for s in splits:
                res.add(s)

    return [*res]


if __name__ == "__main__":
    # --- Example Usage ---
    # Define your source and destination paths here.
    # For demonstration, we'll create some dummy folders and files.

    # Create a dummy source folder structure
    # dummy_source = "/workspaces/media-wiki/pages/supervising/policy"
    dummy_source = "./pages"
    dummy_destination = "./pages-parsed"

    if os.path.exists(dummy_destination) and os.path.isdir(dummy_destination):
        import shutil  # Temporarily import shutil for cleanup

        shutil.rmtree(dummy_destination)

    vault_path = Path(dummy_source)
    note_map = {f.stem: f.relative_to(vault_path) for f in vault_path.rglob("*.md")}

    # Call the copy function
    copy_folder_recursively(dummy_source, dummy_destination, "", note_map)

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
