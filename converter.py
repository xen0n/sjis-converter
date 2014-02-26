#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

import os
import sys
import six
import glob
import unidecode


def detect_chars(s):
    '''检测需要转换的字符位置.

        >>> detect_chars(u'AKB0048 ED \u5922\u306f\u4f55\u5ea6\u3082\u751f\u307e\u308c\u5909\u308f\u308b.mp3')
        []
        >>> detect_chars(u'\u5411\u94f6\u6cb3\u5f00\u7403\uff01\uff01 IN \u5730\u7403\u5100\u30ea\u30d5\u30c6\u30a3\u30f3\u30b0.mp3')
        [1, 3]

    '''

    sjis_bytes = s.encode('sjis', 'replace')
    roundtrip_str = sjis_bytes.decode('sjis')

    # ? 字符出现的位置就是原 Unicode 串中需要转换的字符位置
    result, found_idx = [], -1
    while True:
        try:
            found_idx = roundtrip_str.index('?', found_idx + 1)
            result.append(found_idx)
        except ValueError:
            break

    return result


def convert_char(s):
    '''转换单个字为小写拼音.

    >>> convert_char(u'向')
    u'xiang'

    '''

    return six.u(unidecode.unidecode(s).strip().lower())


def convert_str(s):
    '''转换完整的文件名.

    >>> print(convert_str(u'AKB0048 ED \u5922\u306f\u4f55\u5ea6\u3082\u751f\u307e\u308c\u5909\u308f\u308b.mp3'))
    AKB0048 ED 夢は何度も生まれ変わる.mp3
    >>> print(convert_str(u'向银河开球！！ IN 地球儀リフティング.mp3'))
    向yin河kai球！！ IN 地球儀リフティング.mp3

    '''

    chars_to_convert = detect_chars(s)
    if not chars_to_convert:
        return s

    frags, last_idx = [], 0
    for idx in chars_to_convert:
        # 至今为止不需要转换的片段
        frags.append(s[last_idx:idx])
        # 需要转换的字
        frags.append(convert_char(s[idx]))
        last_idx = idx + 1

    frags.append(s[last_idx:])

    return ''.join(frags)


def convert_file(name):
    new_name = convert_str(name)
    if new_name != name:
        os.rename(name, new_name)
        return True, new_name

    return False, new_name


def main(argv):
    if len(argv) < 2:
        print('usage: %s <directories to convert>' % (argv[0], ))
        return 2

    # 编码不仔细搞了
    dirs = [i.decode('utf-8') for i in argv[1:]]
    for directory in dirs:
        print("Listing directory '%s'..." % (directory, ))
        for filename in glob.iglob('%s/*' % (directory, )):
            converted, new_name = convert_file(filename)
            if converted:
                print('%s -> %s' % (filename, new_name, ))

    return 0



if __name__ == '__main__':
    sys.exit(main(sys.argv))


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
