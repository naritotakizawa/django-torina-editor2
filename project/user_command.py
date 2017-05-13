"""ユーザーがコマンドを追加するためのモジュール.

優先順は以下のようになります。
project.user_command.py(ユーザー定義)
dteditor2.base_command.py（このモジュール）
DOSなどの元々のコマンド

※注意点
「python」や「python manage.py runserver」等の特定の入力があるまで無限ループ
をする処理は現在上手く動きません
この場合は、「start python」、「start python manage.py runserver」、
「gnome-terminal」等としてください

不具合が起きたら、このアプリを一旦終了して再起動してください

"""

import cmdpr
from django.utils import timezone

from dteditor2.utils import editor


@editor.command.register
def now(editor):
    """現在時刻を出力エリアに表示する."""
    now = timezone.now()

    # 画面下に表示する場合は、この関数を呼んでね
    cmdpr.add_line(now)


