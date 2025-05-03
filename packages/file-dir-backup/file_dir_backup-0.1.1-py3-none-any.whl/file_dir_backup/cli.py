import argparse
from .core import backup
from .constants import FULL_BACKUP, INCREMENTAL_BACKUP, RSYNC_METHOD, SHUTIL_METHOD, DEFAULT_CONFIG


def main():
    parser = argparse.ArgumentParser(description='File and directory backup tool')
    parser.add_argument('source', nargs='?', help='Source directory to backup')
    parser.add_argument('destination', nargs='?', help='Destination directory for backup')
    parser.add_argument('--backup-type', choices=[FULL_BACKUP, INCREMENTAL_BACKUP],
                        help='Backup type: full or incremental')
    parser.add_argument('--method', choices=[RSYNC_METHOD, SHUTIL_METHOD],
                        help='Backup method: rsync or shutil')
    parser.add_argument('--compress', action='store_true', help='Compress data during transfer')
    parser.add_argument('--bandwidth-limit', type=int, help='Limit the bandwidth in KB/s')
    args = parser.parse_args()

    # 合并命令行参数和默认配置
    source = args.source if args.source else DEFAULT_CONFIG['source']
    destination = args.destination if args.destination else DEFAULT_CONFIG['destination']
    backup_type = args.backup_type if args.backup_type else DEFAULT_CONFIG['backup_type']
    method = args.method if args.method else DEFAULT_CONFIG['method']
    compress = args.compress if args.compress is not None else DEFAULT_CONFIG['compress']
    bandwidth_limit = args.bandwidth_limit if args.bandwidth_limit is not None else DEFAULT_CONFIG['bandwidth_limit']

    if not source or not destination:
        parser.error(
            "Source and destination directories are required. Please provide them via command line or config file.")

    backup(source, destination, backup_type, method, compress, bandwidth_limit)


if __name__ == '__main__':
    main()
