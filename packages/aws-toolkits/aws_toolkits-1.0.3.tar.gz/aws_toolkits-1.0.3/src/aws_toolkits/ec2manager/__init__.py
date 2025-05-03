# -*- coding: utf-8 -*-
# @Time    : 2025/3/18 13:41
# @Author  : YQ Tsui
# @File    : __init__.py.py
# @Purpose :

from .ec2_manager import EC2Manager
from PySide6.QtWidgets import QApplication


def main():
    print("in ec2manager __init__.py")
    app = QApplication([])
    manager = EC2Manager()
    manager.show()
    app.exec()
