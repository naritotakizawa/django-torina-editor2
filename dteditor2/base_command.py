"""便利なコマンドが登録してあるモジュールです.

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
import os
import shutil
import sys

import cmdpr
from dteditor2 import utils
from dteditor2.utils import editor as edt


@edt.command.register
def save(editor, file_name=None):
    """プログラムの保存を行う.

    save: 開いているファイルの保存 save test.py: test.pyとして、カレントディレクトリに保存

    """
    code = editor.code
    binary_code = code.encode(editor.save_encoding)

    if file_name:
        file_path = os.path.join(editor.current_dir, file_name)
        if os.path.exists(file_path):
            cmdpr.add_line(f'既にファイルが存在します {file_path}')
        else:
            with open(file_path, 'wb') as file:
                file.write(binary_code)
            cmdpr.add_line(f'新しく保存しました {file_path}')

            # 新規作成後、そのファイルを開く
            editor.update_file(file_path)

    elif not file_name and editor.opening_file:
        with open(editor.opening_file, 'wb') as file:
            file.write(binary_code)
        cmdpr.add_line(f'上書き保存しました {editor.opening_file}')
    else:
        cmdpr.add_line(f'ファイル名を指定するか、ファイルを開いてください')


@edt.command.register
def deletelog(editor):
    """出力を一度削除する."""
    cmdpr.delete_cmd_log()
    cmdpr.add_line(f'出力をクリアーしました')


@edt.command.register
def deletecmd(editor):
    """コマンド履歴の削除."""
    del editor.command.command_history[:]


@edt.command.register
def cd(editor, dir_path):
    """cdコマンドを上書き。エディタのディレクトリと同期させる.

    エディタの仕様として、コマンドラインと画面左のディレクトリは同期させたい
    cdコマンドを使った際は、画面左のディレクトリもそれに応じて動くように するためにcdコマンド自体を上書き

    """
    editor.update_dir(dir_path)


@edt.command.register
def history(editor):
    """コマンド履歴の表示."""
    for cmd in editor.command.command_history:
        cmdpr.add_line(cmd)


@edt.command.register
def rm2(editor, file_name):
    """ファイル・ディレクトリの削除.

    rm2 test: testの削除

    """
    path = os.path.join(editor.current_dir, file_name)

    if os.path.isfile(path):
        os.remove(path)
        cmdpr.add_line(f'ファイルを削除しました {path}')
    elif os.path.isdir(path):
        shutil.rmtree(path)
        cmdpr.add_line(f'ディレクトリを削除しました {path}')
    elif not os.path.exists(path):
        cmdpr.add_line(f'ファイル・ディレクトリがないです {path}')


@edt.command.register
def mv2(editor, before, after):
    """ファイル・ディレクトリのリネーム・移動.

    mv2 before after: beforeをafterに変更

    """
    before_path = os.path.join(editor.current_dir, before)
    after_path = os.path.join(editor.current_dir, after)

    if not os.path.exists(before_path):
        cmdpr.add_line(f'名前が見当たらないです {before_path}')
    else:
        shutil.move(before_path, after_path)
        cmdpr.add_line(f'mvしました {before}→{after}')


@edt.command.register
def cp2(editor, before, after):
    """ファイル・ディレクトリのコピー.

    cp2 origin new:  originをnewへコピー

    """
    before_path = os.path.join(editor.current_dir, before)
    after_path = os.path.join(editor.current_dir, after)

    if not os.path.exists(before_path):
        cmdpr.add_line(f'名前が見当たらないです {before_path}')
    else:
        # ファイルのコピー
        if os.path.isfile(before_path):
            shutil.copy(before_path, after_path)
        # でぃれくとりのコピー
        else:
            shutil.copytree(before_path, after_path)

        cmdpr.add_line(f'cpしました {before}→{after}')


@edt.command.register
def check(editor, file_name=None):
    """スタイルガイドのチェックを行う.

    check file_name: そのファイルに対してチェック
    check: 今開いているファイルに対してチェック

    このエディタを実行しているPythonで、flake8とお好きなプラグインを
    pipしておいてください。

    python(sys.executable) -m flake8 file.py
    というコマンドを実行します。

    """
    # 「check file_name」 ファイル名の指定があれば、そのファイルをチェック
    if file_name:
        file_path = os.path.join(editor.current_dir, file_name)
        if not os.path.exists(file_path):
            cmdpr.add_line(f'ファイルが存在しません {file_path}')
        else:
            cmdpr.run_cmd(f'{sys.executable} -m flake8 {file_path}')

    # 「check」file_nameがなければ、今開いているファイルをチェック
    elif not file_name and editor.opening_file:
        cmdpr.run_cmd(f'{sys.executable} -m flake8 {editor.opening_file}')
    else:
        cmdpr.add_line(f'ファイル名を指定するか、ファイルを開いてください')


@edt.command.register
def auto(editor, relative_path='.'):
    """pythonファイルチェックを行う.

    auto path: pathはファイルかディレクトリ。pythonファイルをチェック
    auto: カレントディレクトリのpythonファイルをチェック

    このエディタを実行しているPythonで、pyformatをpipしてください。
    以下のコマンドを実行します

    python(sys.executable) -m pyformat -i file.py

    引数:
        path: カレントディレクトリからの、相対パス

    """
    path = os.path.join(editor.current_dir, relative_path)

    # 指定あるけど存在しないパス
    if not os.path.exists(path):
        cmdpr.add_line('存在しないパスです')

    # パスがファイルで、pythonファイルなら実行
    elif os.path.isfile(path) and path.endswith('.py'):
        cmd = f'{sys.executable} -m pyformat -i {path}'
        cmdpr.run_cmd(cmd)

    # パスがファイルで、pythonファイルじゃない
    elif os.path.isfile(path):
        cmdpr.add_line('pythonファイルかディレクトリを選択して')

    # パスがディレクトリなら、中のpythonファイルに実行
    elif os.path.isdir(path):
        for file_name in os.listdir(path):
            if file_name.endswith('.py'):
                file_path = os.path.join(path, file_name)
                cmd = f'{sys.executable} -m pyformat -i {file_path}'
                cmdpr.run_cmd(cmd)


@edt.command.register
def freeze(editor, path, kind='zip'):
    """圧縮を行う.

    freeze path
    freeze path tar
    tar等を指定しなければ、zip圧縮です。
    圧縮の種類はshutilに準拠

    pathには、圧縮したいディレクトリの相対・絶対パスを入力してください。
    カレントに、対象のディレクトリ名.zip が作成されます。

    """
    target = os.path.join(editor.current_dir, path)

    head, tail = os.path.split(path)
    base_name = os.path.join(editor.current_dir, tail)
    root_dir = os.path.join(editor.current_dir, head)
    base_dir = tail

    if not os.path.exists(target):
        cmdpr.add_line(f'名前が見当たらないです {target}')
    else:
        shutil.make_archive(
            base_name, kind, root_dir=root_dir, base_dir=base_dir)
        cmdpr.add_line(f'圧縮しました {path}')


@edt.command.register
def unfreeze(editor, path):
    """解凍を行う.

    unfreeze my.zip: my.zipを解凍 対応している解凍の種類はshutilに準拠

    """
    target_path = os.path.join(editor.current_dir, path)

    if not os.path.exists(target_path):
        cmdpr.add_line(f'名前が見当たらないです {target_path}')
    else:
        shutil.unpack_archive(target_path, editor.current_dir)
        cmdpr.add_line(f'解凍しました {target_path}')


@edt.command.register
def save_encoding(editor, encoding):
    """ファイル保存のエンコーディングを変更."""
    editor.save_encoding = encoding


@edt.command.register
def open_encoding(editor, encoding):
    """ファイルオープンのエンコーディングを変更."""
    editor.open_encoding = encoding


@edt.command.register
def venv(editor):
    """仮想環境の情報を表示する.(echo $VIRTUAL_ENV)."""
    cmdpr.run_cmd(f'echo $VIRTUAL_ENV')


@edt.command.register
def set_sort(editor, sort_type):
    """ファイル・ディレクトリ表示方法を変更する.

    name: 名前でソート
    size: サイズでソート
    update: 更新日順でソート
    """
    editor.tree.sort_type = sort_type


@edt.command.register
def reverse(editor):
    """ファイル・ディレクトリ表示方法を、逆さにする"""
    if editor.tree.reverse:
        editor.tree.reverse = False
    else:
        editor.tree.reverse = True


@edt.command.register
def size2(editor, name):
    """ファイル・ディレクトリのサイズを返す"""
    path = os.path.join(editor.current_dir, name)
    size = utils.get_dir_size(path)
    human_size = utils.change_bytes(size)
    cmdpr.add_line(f'{name}: {human_size} - {size}')
