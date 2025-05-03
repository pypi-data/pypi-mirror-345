#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import configparser


def get_config(p, section, key, env_var, default):
    if env_var is not None:
        value = os.environ.get(env_var, None)
        if value is not None:
            return value
    if p is not None:
        try:
            return p.get(section, key)
        except:
            return default
    return default


def load_config_file():
    """
    按顺序尝试读取多个配置文件路径，找到第一个存在的配置文件并读取。
    """
    p = configparser.ConfigParser()
    path1 = os.path.expanduser(os.environ.get('FILE_DIR_BACKUP_CONFIG', "~/.file_dir_backup.cfg"))
    path2 = os.path.join(os.getcwd(), "etc", "file_dir_backup.cfg")
    path3 = "/etc/file_dir_backup.cfg"
    paths = [path1, path2, path3]
    for path in paths:
        if os.path.exists(path):
            p.read(path)
            return p
    return None


def shell_expand_path(path):
    if path:
        path = os.path.expanduser(path)
    return path


p = load_config_file()

# 备份类型
FULL_BACKUP = 'full'
INCREMENTAL_BACKUP = 'incremental'

# 备份方法
RSYNC_METHOD = 'rsync'
SHUTIL_METHOD = 'shutil'

# 默认配置
DEFAULT_CONFIG = {
    'source': None,
    'destination': None,
    'backup_type': FULL_BACKUP,
    'method': RSYNC_METHOD,
    'compress': False,
    'bandwidth_limit': None
}

if p:
    DEFAULT_CONFIG['source'] = shell_expand_path(get_config(p, 'backup', 'source', 'FILE_DIR_BACKUP_SOURCE', None))
    DEFAULT_CONFIG['destination'] = shell_expand_path(
        get_config(p, 'backup', 'destination', 'FILE_DIR_BACKUP_DESTINATION', None))
    DEFAULT_CONFIG['backup_type'] = get_config(p, 'backup', 'backup_type', 'FILE_DIR_BACKUP_TYPE', FULL_BACKUP)
    DEFAULT_CONFIG['method'] = get_config(p, 'backup', 'method', 'FILE_DIR_BACKUP_METHOD', RSYNC_METHOD)
    DEFAULT_CONFIG['compress'] = get_config(p, 'backup', 'compress', 'FILE_DIR_BACKUP_COMPRESS', False)
    DEFAULT_CONFIG['bandwidth_limit'] = get_config(p, 'backup', 'bandwidth_limit', 'FILE_DIR_BACKUP_BANDWIDTH_LIMIT',
                                                   None)