import os


def list_files_as_array(directory_path):
    # Get all files in the directory
    files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

    # Format the output string
    output = "let data = [\n"

    # Add each file with proper formatting
    for i, file in enumerate(files):
        if i > 0:
            output += ",\n"
        output += f'    "{file}"'

    output += "\n];"

    # Print and return the result
    print(output)
    return output


# Example usage
if __name__ == "__main__":
    directory_path = (
        "C:\\Users\\schwittlick\\dev\\schwittlick.net\\img\\composition92\\digital_png\\"
    )  # Change this to your directory path
    list_files_as_array(directory_path)
