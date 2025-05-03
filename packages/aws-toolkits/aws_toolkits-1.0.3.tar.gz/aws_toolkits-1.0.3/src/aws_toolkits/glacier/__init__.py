# -*- coding: utf-8 -*-
# @Time    : 2025/3/18 16:06
# @Author  : YQ Tsui
# @File    : __init__.py.py
# @Purpose :

import argparse
import platform
import subprocess
import sys

from .glacier import (
    check_and_handle_jobs,
    delete_archive,
    list_inventory,
    list_jobs,
    mark_jobs_as_aborted,
    submit_downloads,
    submit_inventory_update,
    upload_archive,
)


def main():
    parser = argparse.ArgumentParser(description="AWS Glacier Operator")
    parser.add_argument("--no-watchdog", action="store_true")
    parser.add_argument("-v", "--vault", type=str, required=True)

    subparsers = parser.add_subparsers(help="sub-command help", dest="command")

    parser_list_inventory = subparsers.add_parser(
        "list", help="List archives according to local record (note might be outdated)"
    )
    parser_list_inventory.add_argument(
        "-c",
        "--columns",
        default="FileName,Size",
        type=str,
        help="Columns of archive list, one or more from "
        "{FileName,Size,CreationDate,LastModify,ArchiveId,SHA256TreeHash},"
        "sepearted by comma (,).",
    )
    parser_list_inventory.add_argument("-f", "--filter", default="", type=str, help="Regex to filter FileName")
    parser_list_inventory.set_defaults(func=list_inventory)

    parser_update_inventory_list = subparsers.add_parser("inventory_update", help="Submit inventory update request")
    parser_update_inventory_list.set_defaults(func=submit_inventory_update)

    parser_download = subparsers.add_parser("download", help="Download archive by name and/or archive id")
    parser_download.add_argument("-id", "--archive-id", default=[], nargs="+", help="Archive ids")
    parser_download.add_argument("-n", "--archive-name", default=[], nargs="+", help="Archive names")
    parser_download.set_defaults(func=submit_downloads)

    parser_delete = subparsers.add_parser("delete", help="Delete archive by name and/or id.")
    parser_delete.add_argument("-id", "--archive-id", default=[], nargs="+", help="Archive ids")
    parser_delete.add_argument("-n", "--archive-name", default=[], nargs="+", help="Archive names")
    parser_delete.set_defaults(func=delete_archive)

    parser_upload = subparsers.add_parser("upload", help="Upload files to vault")
    parser_upload.add_argument("-f", "--file-paths", default=[], nargs="+", help="Files to upload")
    parser_upload.add_argument("--num-threads", type=int, default=2, help="No. of threads for parallel upload.")
    parser_upload.add_argument(
        "--upload-chunk-size",
        type=int,
        default=4,
        help="Upload chunksize (MB, between 4-4096 and power of 2)",
    )
    parser_upload.add_argument(
        "--check-duplicates",
        type=bool,
        default=True,
        help="Check if filename duplicates before upload",
    )
    parser_upload.set_defaults(func=upload_archive)

    parser_job = subparsers.add_parser("job", help="Job related operations")
    subparsers_job = parser_job.add_subparsers(dest="job_commands", help="job command help")
    parser_job_list = subparsers_job.add_parser("list", help="List jobs")
    parser_job_list.set_defaults(func=list_jobs)
    parser_job_abort = subparsers_job.add_parser("abort", help="Abort a job")
    parser_job_abort.add_argument("job_ids", default=[], nargs="+", help="Job IDs to abort")
    parser_job_abort.set_defaults(func=mark_jobs_as_aborted)
    parser_job_process = subparsers_job.add_parser("process", help="Process jobs")
    parser_job_process.add_argument(
        "--download-chunk-size",
        type=int,
        default=16,
        help="download chunksize (MB, must be power of 2)",
    )
    parser_job_process.add_argument("--log-file", type=str, default="", help="log file name")
    parser_job_process.set_defaults(func=check_and_handle_jobs)

    parser_debug = subparsers.add_parser("debug", help="Just for debugging")

    args = parser.parse_args()

    if "func" in args:
        args.func(args)

    if not args.no_watchdog and args.command in (
        "inventory_update",
        "download",
        "debug",
    ):
        if "windows" in platform.system().lower():
            with subprocess.Popen(
                f"python aws_glacier.py -v {args.vault} job process --log-file glacier.log &",
                shell=True,
            ):
                pass
        if "linux" in platform.system().lower():
            with subprocess.Popen(
                f"aws_glacier -v {args.vault} job process --log-file glacier.log > /dev/null 2>&1 &",
                shell=True,
            ):
                pass
        sys.exit(0)
