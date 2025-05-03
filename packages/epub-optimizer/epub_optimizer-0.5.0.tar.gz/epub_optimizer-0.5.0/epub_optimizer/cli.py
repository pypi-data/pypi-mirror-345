import argparse
import math
import os
import shutil
import subprocess
import tempfile
import zipfile
from contextlib import contextmanager
from pathlib import Path

from PIL import Image


def parse_args():
    parser = argparse.ArgumentParser(description="Optimize epub file size")
    parser.add_argument("-i", "--input", help="The input filepath", type=Path, required=True)
    parser.add_argument("--verbose", action="store_true", default=False)
    parser.add_argument("output", help="The output filepath", type=Path)
    return parser.parse_args()


@contextmanager
def cwd_temp_dir():
    initial_wd = os.getcwd()
    destination = Path(tempfile.mkdtemp())
    os.chdir(destination)
    yield destination
    os.chdir(initial_wd)


def get_folder_size(folder_path: Path):
    total_size = 0
    for path in Path(folder_path).rglob("*"):
        if path.is_file():
            total_size += path.stat().st_size
    return total_size


def format_size(size: float):
    power = 2**10
    n = 0
    units = {0: "", 1: "KB", 2: "MB", 3: "GB", 4: "TB"}
    while size > power:
        size /= power
        n += 1
    return f"{math.floor(size)} {units[n]}"


def convert_format(input: Path, output: Path):
    img = Image.open(input)
    bw_img = img.convert("L")
    bw_img.save(output)


class EpubOptimizer:

    def __init__(
        self, epub_filepath: Path, output_filepath: Path, working_dir: Path, verbose: bool
    ):
        self.epub_filepath = epub_filepath
        self.output_filepath = output_filepath
        self.working_dir = working_dir
        self.verbose = verbose
        self.oebps_dir = working_dir / "OEBPS"
        self.xhtml_dir = self.oebps_dir / "xhtml"
        self.images_dir = self.oebps_dir / "images"
        self.fonts_dir = self.oebps_dir / "fonts"
        self.style_file = self.oebps_dir / "style.css"
        self.steps = [
            self.convert_png_images_to_black_and_white_jpg,
            self.remove_unused_fonts,
            self.run_jpegoptim,
        ]

    def unpack_epub(self):
        epub_copy = self.working_dir / self.epub_filepath.name
        shutil.copyfile(self.epub_filepath.absolute(), epub_copy)
        with zipfile.ZipFile(epub_copy, "r") as zip_ref:
            zip_ref.extractall(self.working_dir)
        epub_copy.unlink()

    def repack_epub(self):
        with zipfile.ZipFile(
            self.output_filepath.absolute(), "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as zf:
            for dirname, subdirs, files in os.walk("."):
                zf.write(dirname)
                for filename in files:
                    zf.write(os.path.join(dirname, filename))

    def report_working_dir_folder_size(self):
        print(f"total: {format_size(get_folder_size(self.working_dir))}")
        self.report_subfolders_size()

    def report_subfolders_size(self):
        for folder in (self.images_dir, self.xhtml_dir, self.fonts_dir):
            folder_size = get_folder_size(folder)
            print(f"- {folder.name}: {format_size(folder_size)}")

    def replace_in_xhtml_files(self, string_to_replacement: dict[str, str]) -> dict[str, bool]:
        found = {string: False for string in string_to_replacement}
        for xhtml_filepath in self.xhtml_dir.glob("*.xhtml"):
            with open(xhtml_filepath) as f:
                text = f.read()
            for string, replacement in string_to_replacement.items():
                new_text = text.replace(string, replacement)
                if text != new_text:
                    found[string] = True
                text = new_text
            with open(xhtml_filepath, "w") as f:
                f.write(text)
        return found

    def convert_png_images_to_black_and_white_jpg(self):
        replacements = {}
        for png_image_path in self.images_dir.glob("*.png"):
            relative_png_image_path = os.path.join("../images", png_image_path.name)
            relative_jpg_image_path = relative_png_image_path.replace(".png", ".jpg")
            replacements[relative_png_image_path] = relative_jpg_image_path
            convert_format(
                input=png_image_path,
                output=png_image_path.parent / png_image_path.name.replace(".png", ".jpg"),
            )
            png_image_path.unlink()
        images_found_in_xhtml_files = self.replace_in_xhtml_files(replacements)
        for image, found in images_found_in_xhtml_files.items():
            if not found:
                img_file = self.images_dir / Path(image).name
                print(f"Deleting {img_file} as it was not found anywhere in the book")
                img_file.unlink()

    def remove_unused_fonts(self):
        for font_image_path in self.fonts_dir.glob("*"):
            relative_font_path = os.path.join("fonts", font_image_path.name)
            if relative_font_path in self.style_file.read_text():
                break
            else:
                print(f"Deleting {font_image_path} as it was not found anywhere in the book")
                font_image_path.unlink()

    def run_jpegoptim(self):
        if not shutil.which("jpegoptim"):
            print("jpegoptim is not installed. Skipping this step.")
            return
        cmd = ["jpegoptim", "--strip-all", "--max=80"] + list(self.images_dir.glob("*.jpg"))
        subprocess.run(cmd, capture_output=True)

    def run(self):
        self.initial_size = self.epub_filepath.stat().st_size
        self.unpack_epub()
        self.initial_directory_size = get_folder_size(self.working_dir)
        if self.verbose:
            print("[+] Initial size")
            self.report_working_dir_folder_size()
        for step in self.steps:
            if self.verbose:
                print()
                print(f"[+] {step.__name__}")
            step()
            if self.verbose:
                self.report_working_dir_folder_size()
        self.repack_epub()
        self.output_size = self.output_filepath.stat().st_size
        print(
            f"The EPUB size was optimized from {format_size(self.initial_size)} to {format_size(self.output_size)}"
        )


def main():
    args = parse_args()
    input = args.input.absolute()
    output = args.output.absolute()
    with cwd_temp_dir() as working_dir:
        EpubOptimizer(
            epub_filepath=input,
            output_filepath=output,
            working_dir=working_dir,
            verbose=args.verbose,
        ).run()
        shutil.rmtree(working_dir)


if __name__ == "__main__":
    main()
