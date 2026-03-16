#!/usr/bin/env python3
import argparse
import os
import brotli


def compress_file(file_path, remove_original=False):
    with open(file_path, 'rb') as f_in:
        data = f_in.read()
    
    compressed_data = brotli.compress(data)
    
    output_path = file_path + '.br'
    with open(output_path, 'wb') as f_out:
        f_out.write(compressed_data)
    
    if remove_original:
        os.remove(file_path)
    
    return output_path


def decompress_file(file_path, remove_original=False):
    if not file_path.endswith('.br'):
        return None
    
    with open(file_path, 'rb') as f_in:
        compressed_data = f_in.read()
    
    data = brotli.decompress(compressed_data)
    
    output_path = file_path[:-3]
    with open(output_path, 'wb') as f_out:
        f_out.write(data)
    
    if remove_original:
        os.remove(file_path)
    
    return output_path


def process_directory(directory, compress=True, remove_original=False):
    if not os.path.isdir(directory):
        print(f"Error: '{directory}' is not a valid directory.")
        return
    
    all_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)
            all_files.append((full_path, file))
    
    if not all_files:
        print("No files found in directory.")
        return
    
    for full_path, file in all_files:
        
        if compress:
            if file.endswith('.br'):
                print(f"Skipping {file} (already compressed)")
                continue
            try:
                output = compress_file(full_path, remove_original)
                print(f"Compressed: {file} -> {os.path.basename(output)}")
            except Exception as e:
                print(f"Error compressing {file}: {e}")
        else:
            if not file.endswith('.br'):
                continue
            try:
                output = decompress_file(full_path, remove_original)
                print(f"Decompressed: {file} -> {os.path.basename(output)}")
            except Exception as e:
                print(f"Error decompressing {file}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Compress or decompress files in a directory using Brotli"
    )
    parser.add_argument(
        "directory",
        help="Path to the directory containing files"
    )
    parser.add_argument(
        "-c", "--compress",
        action="store_true",
        default=True,
        help="Compress files (default)"
    )
    parser.add_argument(
        "-d", "--decompress",
        action="store_true",
        help="Decompress .br files"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "-r", "--remove-original",
        action="store_true",
        help="Remove original files after compression/decompression"
    )

    args = parser.parse_args()

    compress = not args.decompress
    action = "Compressing" if compress else "Decompressing"

    if args.verbose:
        print(f"Target directory: {args.directory}")
        print(f"Mode: {action.lower()}")

    print(f"{action} files in: {args.directory}")
    process_directory(args.directory, compress=compress, remove_original=args.remove_original)


if __name__ == "__main__":
    main()
