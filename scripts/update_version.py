import re
import sys
import glob

if __name__ == "__main__":
    version = sys.argv[1]

    for file in glob.glob("./.env*"):
        with open(file, "r") as f:
            content = f.read()

        content_new = re.sub(
            "APP_VERSION=[a-zA-Z0-9.\-:]+",
            f"APP_VERSION={version}",
            content,
            flags=re.M,
        )

        with open(file, "w") as f:
            f.write(content_new)
