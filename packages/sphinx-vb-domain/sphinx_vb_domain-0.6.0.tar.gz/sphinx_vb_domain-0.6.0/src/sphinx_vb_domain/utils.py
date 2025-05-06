import hashlib
import re
from docutils.nodes import make_id


def to_safe_label(name: str, encode_: bool) -> str:
    '''Generate a valid label by encoding invalid characters with md5.'''
    invalid_symbols = re.compile(r'[!-/:-@\[-`{-~]')
    target_ptn = re.compile(r'[a-zA-Z0-9_\-]+')

    # Split name into parts.
    # e.g. 'Module1.Function1' -> ['Module1', 'Function1']
    name_parts = name.split('.')

    target_parts = []
    for name_part in name_parts:
        # ラベルに使えない記号をハイフンに置き換える。
        name_part = invalid_symbols.sub('-', name_part)

        if encode_:
            match = target_ptn.fullmatch(name_part)
            if match:
                target_part = name_part
            else:
                target_part = \
                    hashlib.md5(name_part.encode('utf-8')).hexdigest()[:8]
        else:
            target_part = name_part

        target_parts.append(make_id(target_part))

    return '.'.join(target_parts)
