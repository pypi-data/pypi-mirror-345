import os
import re
import sys

EXTENSIONS = [
    ".py", ".js", ".ts", ".rs", ".c", ".cpp", ".h", ".hpp", ".cs", ".json", ".yaml", ".yml"
]

SINGLE_COMMENT = {
    ".py": r"#",
    ".js": r"//",
    ".ts": r"//",
    ".rs": r"//",
    ".c": r"//",
    ".cpp": r"//",
    ".h": r"//",
    ".hpp": r"//",
    ".cs": r"//",
    ".json": r"//",
    ".yaml": r"#",
    ".yml": r"#",
}

MULTI_COMMENT = {
    ".js": (r"/\*", r"\*/"),
    ".ts": (r"/\*", r"\*/"),
    ".rs": (r"/\*", r"\*/"),
    ".c": (r"/\*", r"\*/"),
    ".cpp": (r"/\*", r"\*/"),
    ".h": (r"/\*", r"\*/"),
    ".hpp": (r"/\*", r"\*/"),
    ".cs": (r"/\*", r"\*/"),
}

def get_files(path):
    files = []
    if os.path.isfile(path):
        if any(path.endswith(ext) for ext in EXTENSIONS):
            files.append(path)
    else:
        for root, _, filenames in os.walk(path):
            for fname in filenames:
                if any(fname.endswith(ext) for ext in EXTENSIONS):
                    files.append(os.path.join(root, fname))
    return files

def remove_comments_from_line(line, ext):
    def remove_outside_strings(line, comment_symbol):
        in_single = False
        in_double = False
        in_backtick = False
        escape = False
        for i, c in enumerate(line):
            if escape:
                escape = False
                continue
            if c == '\\':
                escape = True
                continue
            if not in_double and not in_backtick and c == "'":
                in_single = not in_single
            elif not in_single and not in_backtick and c == '"':
                in_double = not in_double
            elif not in_single and not in_double and c == '`':
                in_backtick = not in_backtick
            elif not in_single and not in_double and not in_backtick:
                if line[i:i+len(comment_symbol)] == comment_symbol:
                    return line[:i]
        return line

    if ext in [".json", ".yaml", ".yml"]:
        if ext == ".json":
            return remove_outside_strings(line, "//")
        else:
            return remove_outside_strings(line, "#")
    else:
        single = SINGLE_COMMENT.get(ext)
        if single:
            return remove_outside_strings(line, single)
    return line

def remove_multiline_comments(text, ext):
    if ext in MULTI_COMMENT:
        start, end = MULTI_COMMENT[ext]
        pattern = rf"{re.escape(start)}[\s\S]*?{re.escape(end)}"
        return re.sub(pattern, "", text)
    return text

def process_file(path):
    ext = os.path.splitext(path)[1]
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    content = remove_multiline_comments(content, ext)
    lines = content.splitlines()
    new_lines = []
    for line in lines:
        if line.strip() == "":
            new_lines.append("")
            continue
        cleaned = remove_comments_from_line(line, ext).rstrip()
        if cleaned.strip():
            new_lines.append(cleaned)
    new_content = "\n".join(new_lines)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

def main():
    if len(sys.argv) > 1:
        user_path = sys.argv[1]
    else:
        user_path = input("Enter the path to the file or folder: ").strip()
    if not os.path.exists(user_path):
        print("Path does not exist.")
        return
    files = get_files(user_path)
    print(f"Found {len(files)} files")
    if not files:
        print("No files with supported extensions found for processing.")
        return
    for file in files:
        print(f"Processing file: {file}")
        process_file(file)
    print(f"Processed {len(files)} files")

if __name__ == "__main__":
    main()