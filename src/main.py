#!/usr/bin/env python3
import argparse
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List, Tuple

import brotli


def get_optimal_workers() -> int:
    cpu_count = os.cpu_count() or 1
    return max(1, cpu_count - 1)


def get_directory_size(directory: str, exclude: Optional[List[str]] = None) -> int:
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


def format_size(size_bytes: float) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def compress_file(file_path: str, remove_original: bool = False) -> str:
    with open(file_path, 'rb') as f_in:
        data = f_in.read()
    
    compressed_data = brotli.compress(data)
    
    output_path = file_path + '.br'
    with open(output_path, 'wb') as f_out:
        f_out.write(compressed_data)
    
    if remove_original:
        os.remove(file_path)
    
    return output_path


def decompress_file(file_path: str, remove_original: bool = False) -> Optional[str]:
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


def process_directory(
    directory: str,
    compress: bool = True,
    remove_original: bool = False,
    exclude: Optional[List[str]] = None,
    logger: Optional[logging.Logger] = None
) -> None:
    if logger is None:
        logger = logging.getLogger(__name__)
    
    if exclude is None:
        exclude = []
    
    exclude_normalized = [os.path.normpath(os.path.join(directory, e)) for e in exclude]
    
    if not os.path.isdir(directory):
        logger.error(f"'{directory}' is not a valid directory.")
        return
    
    all_files: List[Tuple[str, str]] = []
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
        logger.info("No files found in directory.")
        return
    
    files_to_process: List[Tuple[str, str]] = []
    for full_path, file in all_files:
        if compress:
            if file.endswith('.br'):
                logger.info(f"Skipping {file} (already compressed)")
                continue
            files_to_process.append((full_path, file))
        else:
            if file.endswith('.br'):
                files_to_process.append((full_path, file))
    
    if not files_to_process:
        logger.info("No files to process.")
        return
    
    workers = get_optimal_workers()
    
    def process_single(full_path: str, file: str) -> Tuple[str, Optional[str]]:
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
                logger.error(f"Error {'compressing' if compress else 'decompressing'} {file}: {error}")
            else:
                logger.info(f"{'Compressing' if compress else 'Decompressing'}: {file}")


def main() -> None:
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
    parser.add_argument(
        "-n", "--dry-run",
        action="store_true",
        help="Show what would be processed without executing"
    )

    args = parser.parse_args()

    import sys
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(message)s',
        stream=sys.stdout
    )
    logger = logging.getLogger(__name__)

    compress = not args.decompress
    action = "Compressing" if compress else "Decompressing"

    if args.verbose:
        logger.info(f"Target directory: {args.directory}")
        logger.info(f"Mode: {action.lower()}")

    if args.dry_run:
        logger.info(f"[DRY RUN] {action} files in: {args.directory}")
        logger.info("")
        
        exclude_normalized = [os.path.normpath(os.path.join(args.directory, e)) for e in args.exclude]
        
        all_files: List[Tuple[str, str]] = []
        for root, dirs, files in os.walk(args.directory):
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
            logger.info("No files found in directory.")
            return
        
        files_to_process = []
        for full_path, file in all_files:
            if compress:
                if file.endswith('.br'):
                    rel_path = os.path.relpath(full_path, args.directory)
                    logger.info(f"Would skip {rel_path} (already compressed)")
                    continue
                files_to_process.append((full_path, file))
            else:
                if file.endswith('.br'):
                    files_to_process.append((full_path, file))
        
        if not files_to_process:
            logger.info("No files to process.")
            return
        
        logger.info(f"Would process {len(files_to_process)} file(s):")
        for full_path, file in files_to_process:
            rel_path = os.path.relpath(full_path, args.directory)
            if compress:
                logger.info(f"  Would compress: {rel_path} -> {rel_path}.br")
            else:
                original = os.path.relpath(full_path[:-3], args.directory)
                logger.info(f"  Would decompress: {rel_path} -> {original}")
        
        logger.info("")
        logger.info(f"[DRY RUN] Total: {len(files_to_process)} file(s)")
        
        size_before = get_directory_size(args.directory, exclude=args.exclude)
        estimated_size = size_before * 0.3
        logger.info(f"[DRY RUN] Estimated size after: {format_size(estimated_size)} (based on ~70% compression ratio)")
        
        return

    logger.info(f"{action} files in: {args.directory} (using {get_optimal_workers()} workers)")
    
    start_time = time.time()
    size_before = get_directory_size(args.directory, exclude=args.exclude)
    
    process_directory(args.directory, compress=compress, remove_original=args.remove_original, exclude=args.exclude, logger=logger)
    
    size_after = get_directory_size(args.directory, exclude=args.exclude)
    elapsed_time = time.time() - start_time
    
    logger.info("")
    logger.info("=== Summary ===")
    logger.info(f"Size before: {format_size(size_before)}")
    logger.info(f"Size after:  {format_size(size_after)}")
    if size_before > 0:
        reduction = (1 - size_after / size_before) * 100
        logger.info(f"Reduced:     {reduction:.1f}%")
    logger.info(f"Time:        {elapsed_time:.2f}s")


if __name__ == "__main__":
    main()
