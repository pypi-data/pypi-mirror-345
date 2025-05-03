# epub-optimizer

This CLI will optimize your epub file size, by performing the following operations:
- converting all PNG images to black and white JPGs
- removing any un-used fonts
- running `jpegoptim` on all jpgs, if it is installed and available

## Installation

```console
$ pip install epub-optimizer
```

## Usage

```console
$ epub-optimizer --help
usage: epub-optimizer [-h] -i INPUT [--verbose] output

Optimize epub file size

positional arguments:
  output                The output filepath

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        The input filepath
  --verbose
```

Example:
```console
$ epub-optimizer -i ~/Downloads/Oathbringer\ \(The\ Stormlight\ Archive\ \#3\)\ -\ Brandon\ Sanderson.epub output.epub
The EPUB size was optimized from 32 MB to 11 MB
```
