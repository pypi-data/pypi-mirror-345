#!/usr/bin/env python
# -*- coding: utf-8 -*-
import shutil
import subprocess
import os
import zlib
from .constants import logger, RSYNC_METHOD, SHUTIL_METHOD, FULL_BACKUP, INCREMENTAL_BACKUP

__version__ = '0.1.0'
__author__ = 'hjl'
__description__ = 'A simple backup tool'
__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2023 hjl'
__email__ = '1878324764@qq.com'


def full_backup(source, destination, method, compress=False, bandwidth_limit=None):
    try:
        if method == RSYNC_METHOD:
            command = ['rsync', '-avz'] if compress else ['rsync', '-av']
            if bandwidth_limit:
                command.extend(['--bwlimit', str(bandwidth_limit)])
            command.extend([f'{source}/', f'{destination}/'])
            subprocess.run(command, check=True)
            logger.info(f'Full backup completed using rsync from {source} to {destination}')
        elif method == SHUTIL_METHOD:
            if os.path.exists(destination):
                shutil.rmtree(destination)
            if compress:
                for root, dirs, files in os.walk(source):
                    relative_path = os.path.relpath(root, source)
                    dest_dir = os.path.join(destination, relative_path)
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)
                    for file in files:
                        src_file = os.path.join(root, file)
                        dest_file = os.path.join(dest_dir, file)
                        with open(src_file, 'rb') as f_in:
                            data = f_in.read()
                            compressed_data = zlib.compress(data)
                        with open(dest_file, 'wb') as f_out:
                            f_out.write(compressed_data)
            else:
                shutil.copytree(source, destination)
            logger.info(f'Full backup completed using shutil from {source} to {destination}')
    except Exception as e:
        logger.error(f'Full backup failed: {e}')


def incremental_backup(source, destination, method, compress=False, bandwidth_limit=None):
    try:
        if method == RSYNC_METHOD:
            command = ['rsync', '-avzu'] if compress else ['rsync', '-avu']
            if bandwidth_limit:
                command.extend(['--bwlimit', str(bandwidth_limit)])
            command.extend([f'{source}/', f'{destination}/'])
            subprocess.run(command, check=True)
            logger.info(f'Incremental backup completed using rsync from {source} to {destination}')
        elif method == SHUTIL_METHOD:
            for root, dirs, files in os.walk(source):
                relative_path = os.path.relpath(root, source)
                dest_dir = os.path.join(destination, relative_path)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                for file in files:
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(dest_dir, file)
                    if not os.path.exists(dest_file) or os.path.getmtime(src_file) > os.path.getmtime(dest_file):
                        if compress:
                            with open(src_file, 'rb') as f_in:
                                data = f_in.read()
                                compressed_data = zlib.compress(data)
                            with open(dest_file, 'wb') as f_out:
                                f_out.write(compressed_data)
                        else:
                            shutil.copy2(src_file, dest_file)
            logger.info(f'Incremental backup completed using shutil from {source} to {destination}')
    except Exception as e:
        logger.error(f'Incremental backup failed: {e}')


def backup(source, destination, backup_type=FULL_BACKUP, method=RSYNC_METHOD, compress=False, bandwidth_limit=None):
    if backup_type == FULL_BACKUP:
        full_backup(source, destination, method, compress, bandwidth_limit)
    elif backup_type == INCREMENTAL_BACKUP:
        incremental_backup(source, destination, method, compress, bandwidth_limit)
