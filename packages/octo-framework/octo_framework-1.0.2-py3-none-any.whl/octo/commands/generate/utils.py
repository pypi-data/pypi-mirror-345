import os


def read_file(file_path):
    """Reads the content of the file."""
    with open(file_path, "r") as file:
        content = file.readlines()
    return content


def write_file(file_path, content):
    """Writes the content to the file."""
    with open(file_path, "w") as file:
        file.writelines(content)


def replace_in_files(file_list, old_word="$NAME$", new_word="", project_path=None):
    """Replaces a specific word in multiple files within the current working directory."""

    results = {}
    current_dir = os.path.join(os.getcwd(), project_path)

    for filename in file_list:
        file_path = os.path.join(current_dir, filename)

        if not os.path.exists(file_path):
            results[filename] = "Error: File not found"
            continue

        if not os.path.isfile(file_path):
            results[filename] = "Error: Not a regular file"
            continue

        try:
            # Read file content
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            # Perform replacement
            new_content = content.replace(old_word, new_word)

            if new_content == content:
                results[filename] = "No changes made (target word not found)"
                continue

            # Write modified content back to file
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(new_content)

            results[filename] = "Successfully replaced"

        except PermissionError:
            results[filename] = "Error: Permission denied"
        except UnicodeDecodeError:
            results[filename] = "Error: Could not decode file (try different encoding)"
        except Exception as e:
            results[filename] = f"Error: {str(e)}"

    return results
