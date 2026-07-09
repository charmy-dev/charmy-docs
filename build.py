import shlex
import subprocess

def run(command: str) -> None:
    print(f"> {command}")
    subprocess.run(shlex.split(command), check=True)

run("sphinx-build -b gettext ./source build/gettext")
run("sphinx-intl update -p build/gettext -l en")
run("sphinx-build -b html -D language=zh_CN ./source build/html/zh_CN")
run("sphinx-build -b html -D language=en ./source build/html/en")
