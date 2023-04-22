import glob
import re
import sys

if __name__ == "__main__":
    VERSION = sys.argv[1]

    for file in glob.glob("./.env*"):
        with open(file, encoding="UTF-8") as f:
            content = f.read()

        content_new = re.sub(
            r"APP_VERSION=[a-zA-Z0-9.\-:]+",
            f"APP_VERSION={VERSION}",
            content,
            flags=re.M,
        )

        with open(file, "w", encoding="UTF-8") as f:
            f.write(content_new)
