import subprocess


def generate(shell: str) -> str:
    mp = subprocess.Popen(
        f"_MP_COMPLETE={shell}_source mp",
        shell=True,
        stdout=subprocess.PIPE,
        ).stdout.read().decode("utf-8").strip()
    metaprocessor = subprocess.Popen(
        f"_METAPROCESSOR_COMPLETE={shell}_source metaprocessor",
        shell=True,
        stdout=subprocess.PIPE,
    ).stdout.read().decode("utf-8").strip()
    return f"{mp}\n\n{metaprocessor}"
