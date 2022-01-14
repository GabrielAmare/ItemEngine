"""This module can be run to download all the requirements that are present in 'https://test.pypi.org/'"""
import os
import sys


def main():
    os.system(f"{sys.executable} -m pip install -i https://test.pypi.org/simple/ python-generator")


if __name__ == '__main__':
    main()
