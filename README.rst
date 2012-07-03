Python Auto Doc
===============


Python Sphinx document auto generator

**Code Tree:**
::

 --autodoc.py
 --doc
 --src
   |
   --__init__.py


**__init__.py at root of src must contains some property, For example**::

 __version__ = '0.1'
 __author__ = ['Rebill']
 __description__ = 'Style Guide for Python Code'
 __dependent_3rd__ = {
     'gevent': 'http://www.gevent.org/'
 }


**Requirement**

sphinx: http://sphinx.pocoo.org/


**Sphinx Themes**

celery: https://github.com/cdnzz/celery-sphinx-themes

flask: https://github.com/cdnzz/flask-sphinx-themes


**Code Style**

Python Style Guide: https://github.com/cdnzz/python-style-guide

