import argparse
import os
import shutil

from src.utils.io import ensure_dir


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Copy raw dataset into data/raw for DVC tracking")
	parser.add_argument("--input", type=str, required=True, help="Path to source CSV (in repo root)")
	parser.add_argument("--output", type=str, required=True, help="Destination path under data/raw")
	return parser.parse_args()


def main() -> None:
	args = parse_args()
	dst_dir = os.path.dirname(args.output)
	ensure_dir(dst_dir)
	shutil.copyfile(args.input, args.output)
	print(f"Copied {args.input} -> {args.output}")


if __name__ == "__main__":
	main()


