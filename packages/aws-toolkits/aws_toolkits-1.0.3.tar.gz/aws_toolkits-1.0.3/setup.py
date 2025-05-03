# -*- coding: utf-8 -*-
# @Time    : 2025/3/19 7:56
# @Author  : YQ Tsui
# @File    : setup.py.py
# @Purpose :
from setuptools import setup
from setuptools_scm.version import guess_next_version


def custom_version_scheme(version):
    if version.exact:
        return version.format_with("{tag}")
    else:
        return guess_next_version(version)


def custom_local_scheme(version):
    if version.exact:
        return ""
    else:
        return "+git_" + version.node[1:] if version.node else ""


setup(
    use_scm_version={
        "version_scheme": custom_version_scheme,
        "local_scheme": custom_local_scheme,
    },
)
