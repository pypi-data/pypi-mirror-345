#!/usr/bin/env python
# -*- coding:utf8 -*-
import logging


def setup_logger(name, level=logging.INFO):
    """设置日志记录器"""
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(stream_handler)

    return logger


logger = setup_logger('asb_pl_template')
