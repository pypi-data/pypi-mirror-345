#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pkgstruct
import sys
import argparse
import json

def main():
    """
    Example code to use module: pkgstruct
    """
    argpsr = argparse.ArgumentParser(description='Assigning the package directory structure/names',
                                     epilog='Directory structure/names are inspired by GNU Coding Standards and FHS')

    argpsr.add_argument('-H', '-C', '--class-help',  action='store_true', help='show class help')
    argpsr.add_argument('-r', '--relative-path',     action='store_true', help='show with relative path (default)')
    argpsr.add_argument('-a', '--absolute-path',     action='store_true', help='show with absolute path')
    argpsr.add_argument('-S', '--without-separator', action='store_true', help='show without seperators')
    argpsr.add_argument('-s', '--with-separator',    action='store_true', help='show with seperators (default)')
    argpsr.add_argument('-j', '--json',              action='store_true', help='Show with JSON format')
    argpsr.add_argument('-N', '--non-mimic-home',    action='store_true', help='Not mimic home')

    argpsr.add_argument('filenames', nargs='*')

    args=argpsr.parse_args()

    if args.class_help:
        help(pkgstruct.PkgStruct)
    else:
        for __f in args.filenames if len(args.filenames)>1 else sys.argv[:1]:
            __pkg_info=pkgstruct.PkgStruct(script_path=__f, prefix=None, pkg_name=None,
                                           flg_realpath=False, remove_tail_digits=True,
                                           mimic_home=(not args.non_mimic_home),
                                           remove_head_dots=True, unnecessary_exts=['.sh', '.py', '.tar.gz'])
            if args.json:
                print(json.dumps(__pkg_info.pkg_info, ensure_ascii=False, indent=4, sort_keys=True))
            else:
                __pkg_info.dump(relpath=(not args.absolute_path), with_seperator=(not args.without_separator))

if __name__ == '__main__':
    main()
