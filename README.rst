=====================
django-torina-editor2
=====================
.. image:: https://travis-ci.org/naritotakizawa/django-torina-editor2.svg?branch=master
    :target: https://travis-ci.org/naritotakizawa/django-torina-editor2

.. image:: https://coveralls.io/repos/github/naritotakizawa/django-torina-editor2/badge.svg?branch=master
    :target: https://coveralls.io/github/naritotakizawa/django-torina-editor2?branch=master


Djangoで作成した、シンプルなエディター。


Requirement
--------------

:Python: 3.6以上
:Django: 1.11以上


Quick start
-----------
1. 必要なライブラリのインストール::

    pip install -U https://github.com/naritotakizawa/cmdpr/archive/master.tar.gz
    pip install django


2. あると尚良いライブラリのインストール::

    # 「check」コマンドで呼ばれる。flake8プラグインもお好きに入れて
    pip install flake8

    # 「auto」コマンドで呼ばれる
    pip install pyformat

3. プロジェクトのクローン::

    git clone https://github.com/naritotakizawa/django-torina-editor2

4. うごかす::

    python manage.py runserver

