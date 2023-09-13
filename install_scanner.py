import requests
import sys
import subprocess
import zipfile
from pathlib import Path
from tqdm import tqdm


def download_file(
    url, file_name, display_name, replace_exsisting=False, cl="content-length"
):
    file = requests.get(
        url,
        allow_redirects=True,
        stream=True,
        headers={"Accept-Encoding": "None", "Content-Encoding": "gzip"},
    )

    with tqdm.wrapattr(
        open(file_name, "wb"),
        "write",
        miniters=1,
        desc=display_name,
        total=int(file.headers.get(cl, 0)),
    ) as fout:
        for chunk in file.iter_content(chunk_size=4096):
            fout.write(chunk)


def main():
    try:
        root_dir = Path(__file__).parent

        # create needed folders
        Path(root_dir / "deps").mkdir(parents=True, exist_ok=True)
        Path(root_dir / "platform-tools").mkdir(parents=True, exist_ok=True)
        Path(root_dir / "installer_downloads").mkdir(parents=True, exist_ok=True)

        # download build tools
        download_file(
            "https://aka.ms/vs/17/release/vs_BuildTools.exe",
            root_dir / "installer_downloads" / "BuildTools.exe",
            "Microsoft Build Tools",
            cl="Content-Length",
        )
        process = subprocess.Popen(
            root_dir / "installer_downloads" / "BuildTools.exe", stdout=subprocess.PIPE
        )
        process.wait()

        # download tesseract python library
        download_file(
            "https://github.com/simonflueckiger/tesserocr-windows_build/releases/download/tesserocr-v2.6.0-tesseract-5.3.1/tesserocr-2.6.0-cp311-cp311-win_amd64.whl",
            root_dir / "deps" / "tesserocr-2.6.0-cp311-cp311-win_amd64.whl",
            "Tesseract Python Lib",
            cl="Content-Length",
        )

        # download adb utils library
        download_file(
            "https://dl.google.com/android/repository/platform-tools_r31.0.3-windows.zip",
            root_dir / "installer_downloads" / "platform-tools_r31.0.3-windows.zip",
            "ADB Tools",
        )

        with zipfile.ZipFile(
            root_dir / "installer_downloads" / "platform-tools_r31.0.3-windows.zip", "r"
        ) as zip_ref:
            zip_ref.extractall(root_dir)

        # download tesseract files
        download_file(
            "https://github.com/tesseract-ocr/tessdata/archive/refs/tags/4.1.0.zip",
            root_dir / "installer_downloads" / "tessdata.zip",
            "Tesseract Data",
            cl="Content-Length",
        )

        with zipfile.ZipFile(
            root_dir / "installer_downloads" / "tessdata.zip", "r"
        ) as zip_ref:
            zip_ref.extractall(root_dir / "deps")

        Path(root_dir / "deps" / "tessdata-4.1.0").rename(
            root_dir / "deps" / "tessdata-main"
        )
    except:
        print("Installation FAILED! Try to follow the error message or open an issue.")
        sys.exit(1)


if __name__ == "__main__":
    main()
    print("Installation successful!")
    sys.exit(0)
