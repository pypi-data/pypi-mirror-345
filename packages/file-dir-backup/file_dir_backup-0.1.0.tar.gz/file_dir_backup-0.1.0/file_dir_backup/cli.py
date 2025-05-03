import argparse
from .core import backup
from .constants import FULL_BACKUP, INCREMENTAL_BACKUP, RSYNC_METHOD, SHUTIL_METHOD


def main():
    parser = argparse.ArgumentParser(description='File and directory backup tool')
    parser.add_argument('source', help='Source directory to backup')
    parser.add_argument('destination', help='Destination directory for backup')
    parser.add_argument('--backup-type', choices=[FULL_BACKUP, INCREMENTAL_BACKUP], default=FULL_BACKUP,
                        help='Backup type: full or incremental')
    parser.add_argument('--method', choices=[RSYNC_METHOD, SHUTIL_METHOD], default=RSYNC_METHOD,
                        help='Backup method: rsync or shutil')
    parser.add_argument('--compress', action='store_true', help='Compress data during transfer')
    parser.add_argument('--bandwidth-limit', type=int, help='Limit the bandwidth in KB/s')
    args = parser.parse_args()

    backup(args.source, args.destination, args.backup_type, args.method, args.compress, args.bandwidth_limit)


if __name__ == '__main__':
    main()
