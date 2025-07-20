import re
import urllib.parse
from pathlib import Path

VAULT_PATH = Path("/mnt/c/Sandbox/obsidian-landmark").resolve()  # ← change this

# Map note stems to their full paths
note_map = {f.stem: f.relative_to(VAULT_PATH) for f in VAULT_PATH.rglob("*.md")}


def wikilink_to_mdlink(match, current_file):
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

    target_path = VAULT_PATH / target_entry.with_suffix(".md")
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
        link_path = abs_path.as_posix()
    else:
        # Use relative path
        link_path = relative_path.as_posix()

    # Encode URL (spaces, special chars)
    encoded_path = urllib.parse.quote(link_path)
    return f"[{alias}]({encoded_path}{anchor})"


def convert_file(file_path):
    text = file_path.read_text(encoding="utf-8")

    def repl(match):
        return wikilink_to_mdlink(match, file_path.resolve())

    converted = re.sub(r"\[\[([^\]\|#]+)(#[^\]\|]+)?(\|([^\]]+))?\]\]", repl, text)
    file_path.write_text(converted, encoding="utf-8")


if __name__ == "__main__":
    # Process all .md files in vault
    for md_file in VAULT_PATH.rglob("*.md"):
        print(md_file)
        convert_file(md_file)

    print("✅ All wikilinks converted.")
