#!/usr/bin/env python3
import argparse
import os
import time
import brotli
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_optimal_workers():
    cpu_count = os.cpu_count() or 1
    return max(1, cpu_count - 1)


def get_directory_size(directory, exclude=None):
    if exclude is None:
        exclude = []
    
    exclude_normalized = [os.path.normpath(os.path.join(directory, e)) for e in exclude]
    total_size = 0
    
    for root, dirs, files in os.walk(directory):
        root_normalized = os.path.normpath(root)
        
        should_exclude = False
        for exc in exclude_normalized:
            if root_normalized == exc or root_normalized.startswith(exc + os.sep):
                should_exclude = True
                break
        
        if should_exclude:
            continue
        
        for file in files:
            full_path = os.path.join(root, file)
            if os.path.isfile(full_path):
                total_size += os.path.getsize(full_path)
    
    return total_size


def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


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


def process_directory(directory, compress=True, remove_original=False, exclude=None):
    if exclude is None:
        exclude = []
    
    exclude_normalized = [os.path.normpath(os.path.join(directory, e)) for e in exclude]
    directory_normalized = os.path.normpath(directory)
    
    if not os.path.isdir(directory):
        print(f"Error: '{directory}' is not a valid directory.")
        return
    
    all_files = []
    for root, dirs, files in os.walk(directory):
        root_normalized = os.path.normpath(root)
        
        should_exclude = False
        for exc in exclude_normalized:
            if root_normalized == exc or root_normalized.startswith(exc + os.sep):
                should_exclude = True
                break
        
        if should_exclude:
            continue
        
        for file in files:
            full_path = os.path.join(root, file)
            all_files.append((full_path, file))
    
    if not all_files:
        print("No files found in directory.")
        return
    
    files_to_process = []
    for full_path, file in all_files:
        if compress:
            if file.endswith('.br'):
                print(f"Skipping {file} (already compressed)")
                continue
            files_to_process.append((full_path, file))
        else:
            if file.endswith('.br'):
                files_to_process.append((full_path, file))
    
    if not files_to_process:
        print("No files to process.")
        return
    
    if not files_to_process:
        print("No files to process.")
        return
    
    workers = get_optimal_workers()
    
    def process_single(full_path, file):
        try:
            if compress:
                output = compress_file(full_path, remove_original)
            else:
                output = decompress_file(full_path, remove_original)
            return (file, None)
        except Exception as e:
            return (file, str(e))
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(process_single, fp, f): f for fp, f in files_to_process}
        
        for future in as_completed(futures):
            file, error = future.result()
            if error:
                print(f"Error {'compressing' if compress else 'decompressing'} {file}: {error}")
            else:
                print(f"{'Compressing' if compress else 'Decompressing'}: {file}")


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
    parser.add_argument(
        "-e", "--exclude",
        nargs="*",
        default=[],
        help="List of directories to exclude from compression/decompression"
    )

    args = parser.parse_args()

    compress = not args.decompress
    action = "Compressing" if compress else "Decompressing"

    if args.verbose:
        print(f"Target directory: {args.directory}")
        print(f"Mode: {action.lower()}")

    print(f"{action} files in: {args.directory} (using {get_optimal_workers()} workers)")
    
    start_time = time.time()
    size_before = get_directory_size(args.directory, exclude=args.exclude)
    
    process_directory(args.directory, compress=compress, remove_original=args.remove_original, exclude=args.exclude)
    
    size_after = get_directory_size(args.directory, exclude=args.exclude)
    elapsed_time = time.time() - start_time
    
    print("")
    print("=== Summary ===")
    print(f"Size before: {format_size(size_before)}")
    print(f"Size after:  {format_size(size_after)}")
    if size_before > 0:
        reduction = (1 - size_after / size_before) * 100
        print(f"Reduced:     {reduction:.1f}%")
    print(f"Time:        {elapsed_time:.2f}s")


if __name__ == "__main__":
    main()
