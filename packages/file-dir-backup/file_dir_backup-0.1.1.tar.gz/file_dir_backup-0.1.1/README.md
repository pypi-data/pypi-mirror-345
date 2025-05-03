# file_dir_backup

`file_dir_backup` 是一个用于文件和目录备份的 Python 第三方库，支持全量备份和增量备份，同时支持 `rsync` 和 `shutil` 两种备份方法。

## 安装

```bash
pip install file_dir_backup
```

## 使用方法
### 命令行使用
```bash
#  查看帮助
$ file_dir_backup -h
usage: file_dir_backup [-h] [--backup-type {full,incremental}] [--method {rsync,shutil}] [--compress] [--bandwidth-limit BANDWIDTH_LIMIT] source destination

File and directory backup tool

positional arguments:
  source                Source directory to backup
  destination           Destination directory for backup

optional arguments:
  -h, --help            show this help message and exit
  --backup-type {full,incremental}
                        Backup type: full or incremental
  --method {rsync,shutil}
                        Backup method: rsync or shutil
  --compress            Compress data during transfer
  --bandwidth-limit BANDWIDTH_LIMIT
                        Limit the bandwidth in KB/s



$ file_dir_backup /path/to/source /path/to/destination --backup-type full --method rsync --compress --bandwidth-limit 1000
# 全量同步示例：
#$ file_dir_backup /home/hujianli/test/ /home/hujianli/backup/ --backup-type full --method rsync --compress --bandwidth-limit 1000

# 或者
$ python -m file_dir_backup /path/to/source /path/to/destination --backup-type full --method rsync --compress --bandwidth-limit 1000

# 增量同步示例：
#$ python -m file_dir_backup /home/hujianli/test/ /home/hujianli/backup/ --backup-type incremental --method rsync --compress --bandwidth-limit 1000
```

### 使用配置文件

支持的配置文件查找规则：

1. 环境变量 `FILE_DIR_BACKUP_CONFIG`
2. `~/.file_dir_backup.cfg`
3. `./etc/file_dir_backup.cfg`
4. `/etc/file_dir_backup.cfg`


配置文件格式,以`/etc/file_dir_backup.cfg`为示例：
```bash
[backup]
source = /home/hujianli/test
destination =/home/hujianli/backup
# 备份类型
backup_type = full
# 备份方法
method = rsync
# 是否传输过程中压缩数据
compress = true
# 传输限速
bandwidth_limit = 1000
```
### Python 代码使用

```bash
from file_dir_backup import backup
backup('/path/to/source', '/path/to/destination', backup_type='full', method='rsync', compress=True, bandwidth_limit=1000)
```


## 测试

测试代码在 `tests` 目录下，使用  `unittest` 模块进行测试。

```bash
python -m unittest test.test_file_dir_backup
```
    