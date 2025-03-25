import os
import argparse


def main(args):
    os.system(f'unzip "{args.input}" -d "{args.output}"')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unzip files in a directory.")

    parser.add_argument('--input', type=str, help='Zip file path', required=True, default=None)
    parser.add_argument('--output', type=str, help='Output unzipped directory', default='1_DeepFluoro_unzipped')

    args = parser.parse_args()

    main(args)
