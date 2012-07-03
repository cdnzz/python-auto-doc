#!/usr/bin/python2
# -*- coding: utf-8 -*-
"""
sphinx文档自动生成脚本

This script parses a directory tree looking for python modules and packages and
creates ReST files appropriately to create code documentation with Sphinx.
"""

# Copyright 2012 CDNZZ.COM
# All rights reserved.

import os
import sys
try:
    import src
except ImportError:
    print '\033[91m Fatal Error: Can not found __init__.py file. \033[0m'
    sys.exit(1)

# 项目源代码目录
SOURCE_DIR = 'src'
# 生成文档路径
DOCS_DIR = 'doc'
# package初始化文件
INIT = '__init__.py'
# automodule options
OPTIONS = ['members',
           'undoc-members',
           'show-inheritance']
# Makefile模版
TPL_MAKE_FILE = '''# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =
BUILDDIR      = _build
# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .
# the i18n builder cannot share the environment and doctrees with the others
I18NSPHINXOPTS  = $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

.PHONY: help clean html

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html       to make standalone HTML files"

clean:
	-rm -rf $(BUILDDIR)/*

html:
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

'''
# conf.py模版
TPL_CONF = '''# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.abspath('_themes'))
sys.path.insert(0, os.path.abspath("../.."))
import %s

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode']
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = u'%s'
copyright = u'2012, GridSafe'
version = release = '%s'
pygments_style = 'sphinx'
html_theme = '%s'
html_theme_path = ['_themes']

'''
# index.rst模版
TPL_INDEX = '''
Welcome
=======
%s

Contents
--------
.. include:: modules.rst.inc

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
'''
# modules.rst.inc模版
TPL_MODULES_INC = '''
.. toctree::
   :maxdepth: 4

'''
# sphinx主题风格(目前支持flask,celery)
HTML_THEME = 'celery'

# 终端显示颜色定义列表
BCOLORS = {
    'header' : '\033[95m',
    'okblue' : '\033[94m',
    'okgreen' : '\033[92m',
    'warning' : '\033[93m',
    'fail' : '\033[91m',
    'endc' : '\033[0m',
}

def color_print(str, color=None):
    """
    命令行终端彩色打印输出

    :param str: 要打印的字符串
    :param color: 命令行终端显示的颜色
    """
    if color not in BCOLORS:
        color = 'header'
    print '%s%s%s' % (BCOLORS[color], str, BCOLORS['endc'])


class AutoDoc(object):
    """
    自动生成Sphinx文档
    """

    def __init__(self):
        self.version = src.__version__
        self.author = src.__author__
        self.description = src.__description__
        self.dependent_3rd = src.__dependent_3rd__
        self.version_path = None
        color_print('Auto Doc Start......')

    def build(self):
        """
        自动构建文档
        """
        if os.path.exists(DOCS_DIR):
            self.version_path = '%s/v%s' % (DOCS_DIR, self.version)
            if not os.path.exists(self.version_path):
                try:
                    os.mkdir(self.version_path)
                except IOError:
                    print 'Can not create dir: %s' % self.version_path
                    print IOError
            # 每次运行将重新生成覆盖
            self.gen_makefile()
            self.gen_conf()
            self.gen_index()
            self.gen_modules()
            self.clone_themes()
            command = 'cd %s; make html' % self.version_path
            os.system(command)
            color_print('Auto Doc Done......', 'okgreen')
        else:
            color_print('Fatal Error: "doc" dir do not exists.', 'fail')
            sys.exit(1)

    def gen_makefile(self):
        """
        生成Makefile文件
        """
        make_file = '%s/Makefile' % self.version_path
        if not os.path.exists(make_file):
            with open(make_file, 'w') as f:
                f.write(TPL_MAKE_FILE)

    def gen_conf(self):
        """
        生成conf.py配置文件
        """
        conf_file = '%s/conf.py' % self.version_path
        contents = TPL_CONF % (SOURCE_DIR, self.description, self.version, HTML_THEME)
        with open(conf_file, 'w') as f:
            f.write(contents)

    def gen_index(self):
        """
        生成index.rst入口引导文件
        """
        index_file = '%s/index.rst' % self.version_path
        docs = self.description
        if self.dependent_3rd:
            docs += '\n\nThis project depends on some external libraries. ' \
                    'These libraries are not documented here. ' \
                    'If you want to dive into their documentation, ' \
                    'check out the following links:\n\n'
            for pkg in self.dependent_3rd:
                docs += '-   `%s <%s>`_\n' % (pkg, self.dependent_3rd[pkg])
        contents = TPL_INDEX % docs
        with open(index_file, 'w') as f:
            f.write(contents)

    def gen_modules(self):
        """
        生成项目模块inc文件和子模块toc文件
        """
        # 要include的子模块，最后结果写入到modules.rst.inc文件中
        modules = set()
        # 存储子模块数据，key为包名，value为模块名（数组），如果value为None，则为模块
        rst = {}
        tree = os.walk(SOURCE_DIR)
        for root, subs, files in tree:
            sub_modules = self.find_module(files)
            if root == SOURCE_DIR:
                # 根模块处理
                for sub_module in sub_modules:
                    modules.add(sub_module)
                    rst[sub_module] = None
            else:
                # 包模块处理
                package_name = root.replace('%s/' % SOURCE_DIR, '')\
                                   .replace('/', '.')
                modules.add(package_name)
                for sub_module in sub_modules:
                    rst[package_name] = sub_module
        # 重新排序，令显示更优雅
        modules = list(modules)
        modules.sort()
        # 生成.inc文件
        module_file = '%s/modules.rst.inc' % self.version_path
        with open(module_file, 'w') as f:
            f.write(TPL_MODULES_INC)
            for module in modules:
                contents = '   %s\n' % module
                f.write(contents)
        # 生成子模块rst文件
        for k in rst:
            if rst[k]:
                # is package
                heading = '`%s` Package' % k
                mod = ':mod:`%s` Module' % rst[k]
            else:
                # is module
                heading = '`%s` Module' % k
                mod = ':mod:`%s` Module' % k

            contents = list()
            contents.append(self.format_heading(1, heading))
            contents.append(self.format_heading(2, mod))
            contents.append(self.format_directive(rst[k], '%s.%s' % (SOURCE_DIR, k)))

            rst_file = '%s/%s.rst' % (self.version_path, k)
            with open(rst_file, 'w') as f:
                for content in contents:
                    f.write(content)

    def clone_themes(self):
        """
        克隆flask-sphinx主题
        """
        themes_path = '%s/_themes' % self.version_path
        if not os.path.exists(themes_path):
            command = 'cd %s; git clone https://github.com/cdnzz/%s-sphinx-themes.git _themes' % (self.version_path, HTML_THEME)
            os.system(command)

    def find_module(self, files):
        """
        识别模块，排除__init__.py等其他文件

        :param files: files in dir tree
        :returns: modules
        """
        modules = []
        if INIT in files:
            files.remove(INIT)
        for file in files:
            ext = os.path.splitext(file)
            if ext[1] == '.py':
                modules.append(ext[0])
        return modules

    def format_heading(self, level, text):
        """
        Create a heading of <level> [1, 2 or 3 supported].

        :param level: heading of <level>
        :param text: heading of text
        :returns: heading string
        """
        underlining = ['=', '-', '~', ][level-1] * len(text)
        return '%s\n%s\n\n' % (text, underlining)

    def format_directive(self, module, package):
        """
        Create the automodule directive.

        :param module: module name
        :param package: package name
        :returns: automodule directive
        """
        if module:
            automodule = '%s.%s' % (package, module)
        else:
            automodule = package

        directive = '.. automodule:: %s\n' % automodule
        for option in OPTIONS:
            directive += '    :%s:\n' % option
        return directive


if __name__ == '__main__':
    auto_doc = AutoDoc()
    auto_doc.build()
