from django import forms


class EditorForm(forms.Form):

    # コード入力欄
    code = forms.CharField(
        widget=forms.HiddenInput,
        required=False,
    )

    # コマンド入力欄
    cmd = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
        })
    )
