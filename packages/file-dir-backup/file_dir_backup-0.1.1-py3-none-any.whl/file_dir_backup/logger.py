#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

def get_logger(log_level=logging.INFO):
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

    # 修改日志格式，添加函数名、行号和进程号
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - [%(process)d] - %(funcName)s:%(lineno)d - %(message)s'
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    logger = logging.getLogger(__name__)

    return logger
