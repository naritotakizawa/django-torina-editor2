"""エディタを管理するモジュール."""
from datetime import datetime
import inspect
import os
import sys

import cmdpr
from django.conf import settings


SUFFIXES = {
    1000: ['KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'],
    1024: ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']
}


def get_dir_size(path):
    """再帰的にディレクトリの名前とサイズを返す.

    基準となるディレクトリを受け取り、中のディレクトリ・ファイルを全て足したサイズを返す

    引数:
        path: 基準となるディレクトリのパス

    """
    if os.path.isfile(path):
        return os.path.getsize(path)
    else:
        for root, dirs, files in os.walk(path):
            files_path = (os.path.join(root, file) for file in files)
            dirs_path = (os.path.join(root, dr) for dr in dirs)
            files_size = sum(os.path.getsize(path) for path in files_path)
            dirs_size = sum(get_dir_size(path) for path in dirs_path)
            return files_size + dirs_size


def change_bytes(size, a_kilobyte_is_1024_bytes=False):
    """ファイルサイズを見やすい形に変換する.

    元コード:
    http://diveintopython3-ja.rdy.jp/your-first-python-program.html

    Keyword arguments:
    size -- file size in bytes
    a_kilobyte_is_1024_bytes -- if True (default), use multiples of 1024
                                if False, use multiples of 1000

    Returns: string

    """
    if size < 0:
        raise ValueError('number must be non-negative')

    multiple = 1024 if a_kilobyte_is_1024_bytes else 1000
    for suffix in SUFFIXES[multiple]:
        size /= multiple
        if size < multiple:
            return '{0:.1f} {1}'.format(size, suffix)

    raise ValueError('number too large')


class File:
    """ファイルを表すクラス."""

    def __init__(self, path, name=None):
        self.path = path
        self.size = os.path.getsize(path)
        self.last_update = datetime.fromtimestamp(os.path.getmtime(path))
        if name is None:
            self.name = os.path.basename(path)
        else:
            self.name = name


class Directory:
    """ディレクトリを表すクラス."""

    def __init__(self, path, name=None):
        self.path = path
        if name is None:
            self.name = os.path.basename(path)
        else:
            self.name = name


class Tree:
    """エディタのディレクトリツリー作成クラス."""

    def __init__(self, editor):
        """初期化."""
        self.editor = editor
        self.sort_type = 'name'
        self.reverse = False
        self.dirs = []
        self.files = []

    def update(self):
        """ディレクトリ、ファイルの一覧を返す."""
        # ディレクトリや全てのファイルの名前が入る
        files_and_dirs = os.listdir(self.editor.current_dir)

        # dirnameで前のフォルダを表せます
        before_dir = Directory(
            os.path.dirname(self.editor.current_dir), name='..')

        # ファイル一覧とディレクトリ一覧の作成処理
        files = []
        dirs = [before_dir]

        for name in files_and_dirs:
            full_path = os.path.join(self.editor.current_dir, name)

            if os.path.isdir(full_path):
                direcory = Directory(full_path, name=name)
                dirs.append(direcory)
            else:
                file = File(full_path, name=name)
                files.append(file)

        if self.sort_type == 'size':
            files.sort(key=lambda file: file.size, reverse=self.reverse)

        elif self.sort_type == 'name':
            files.sort(key=lambda file: file.name, reverse=self.reverse)
            dirs.sort(key=lambda direcory: direcory.name, reverse=self.reverse)

        elif self.sort_type == 'update':
            files.sort(key=lambda file: file.last_update, reverse=self.reverse)

        self.files = files
        self.dirs = dirs


class Command:
    """エディタのコマンド関連のクラス."""

    def __init__(self, editor):
        """初期化."""
        self.editor = editor
        self.command_history = []
        self.base_command_dict = {}
        self.base_command_list = []
        self.user_command_dict = {}
        self.user_command_list = []
        self.output = ''
        self.first = False

    def register(self, func):
        """関数を登録するデコレータとして利用してね."""
        name = func.__name__
        doc = inspect.getdoc(func) or ''
        source_file = inspect.getsourcefile(func)
        lineno = inspect.getsourcelines(func)[1]

        # ユーザー定義用モジュールならuser_command_dict,listへ
        if os.path.basename(source_file) == 'user_command.py':
            self.user_command_dict[name] = func
            self.user_command_list.append((name, doc, lineno))

        # そうでなければbase_command_dict,listへ
        elif os.path.basename(source_file) == 'base_command.py':
            self.base_command_dict[name] = func
            self.base_command_list.append((name, doc, lineno))

        return func

    def eval_command(self, cmd):
        """入力されたコマンドを評価する.

        project.user_command.py(ユーザー定義) dteditor2.base_command.py（もともとの）
        DOSなどの元々のコマンド の順で、コマンド名を探す

        """
        # 最後に入力したコマンドと、今のコマンドが同じならヒストリーに追加しない
        last_comand = self.command_history[-1] if self.command_history else ''
        if not cmd == last_comand:
            self.command_history.append(cmd)
        commands = cmd.split()
        command_name = commands[0]
        command_args = commands[1:]

        # ユーザー定義 or このモジュール
        function = self.user_command_dict.get(
            command_name) or self.base_command_dict.get(command_name)

        if function:
            try:
                function(self.editor, *command_args)
            except TypeError as e:
                cmdpr.add_line(f'引数が一致しません {e}')

        # このモジュールにコマンドがとうろく登録されていない
        else:
            # cd でディレクトリをエディタと同期
            cmdpr.run_cmd(f'cd {self.editor.current_dir}')
            cmdpr.run_cmd(cmd)

    def update(self):
        """コマンドが入力されていれば実行し、最新の出力を取得する."""
        # 初回だけ、コマンド登録用モジュールを読み込む
        # 一度読み込めばそれでOK。registerで登録してくれる
        if not self.first:
            import dteditor2.base_command
            import project.user_command
            self.first = True

        # コマンドの入力があれば実行
        cmd = self.editor.request.POST.get('cmd', '')
        if cmd:
            self.eval_command(cmd)

        # 現在の出力の取得
        self.output = cmdpr.get_output(0)


class Editor:
    """エディタ情報の管理を行うクラス."""

    def __init__(self):
        """初期化."""
        self.request = None
        self.editor_python_path = sys.executable
        self.editor_project_path = settings.BASE_DIR
        self.open_encoding = 'utf-8'
        self.save_encoding = 'utf-8'
        self.current_dir = settings.BASE_DIR
        self.opening_file = ''
        self.file_name = 'no file'
        self.file_extension = 'no file'
        self.file_type = settings.DEFAULT_ACE_TYPE
        self.code = ''
        self.tree = Tree(self)
        self.command = Command(self)

    def update(self, request):
        """エディタの更新."""
        self.request = request
        self.update_dir()
        self.update_file()
        self.update_code()
        self.command.update()
        self.tree.update()

    def update_code(self):
        """エディタのコードを更新."""
        # ファイル、ディレクトリクリック等のGETアクセス時は
        # 開いているファイルのコードを読み込む
        post_code = self.request.POST.get('code')
        if not post_code:
            try:
                code = open(self.opening_file, 'rb').read()
                code = code.decode(self.open_encoding)
            except FileNotFoundError:
                code = 'ファイルが見つかりませんでした'
            except UnicodeDecodeError:
                code = f'{self.open_encoding}でデコードできませんでした'
            finally:
                self.code = code

        # Send Command が押されたらここ。特にSave 時に変更コードを取得するため
        else:
            self.code = post_code

    def update_file(self, file_path=None):
        """開いているファイルの更新."""
        opening_file = file_path or self.request.GET.get('opening_file')
        if opening_file:
            self.opening_file = opening_file
            self.file_name = os.path.basename(opening_file)
            _, self.file_extension = os.path.splitext(opening_file)
            self.file_type = settings.FILE_TYPE.get(
                self.file_extension, settings.DEFAULT_ACE_TYPE)

    def update_dir(self, dir_path=None):
        """カレントディレクトリの更新."""
        if dir_path:
            current_dir = os.path.abspath(
                os.path.join(self.current_dir, dir_path))
        else:
            current_dir = self.request.GET.get('current_dir')

        if current_dir and os.path.isdir(current_dir):
            self.current_dir = current_dir


editor = Editor()
