import logging

# 日志配置
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# 备份类型
FULL_BACKUP = 'full'
INCREMENTAL_BACKUP = 'incremental'

# 备份方法
RSYNC_METHOD = 'rsync'
SHUTIL_METHOD = 'shutil'