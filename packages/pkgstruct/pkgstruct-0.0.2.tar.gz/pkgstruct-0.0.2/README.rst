pkgstruct
=========

- Utility module for formalising the directory structure of software
  package. The top directory path can be infered from the script path.

- ``pkgstruct`` supports having a directory structure under the top
  directory, such as ``var``, ``share``,\ ``etc``,… under the top
  directory, and supports the creation of directory structures according
  to the GNU Coding Standard and the Filesystem Hierarchy Standard.

Requirement
-----------

- ``pkgstruct`` uses only standard modules.

Usage
-----

install
~~~~~~~

::

   % pip install pkgstruct

Example
~~~~~~~

Example usage of pkgstruct.py

First, import the module and define an entity of class PkgStruct that
uses it. The top directory name is inferred from the script name given
in the constructor argument.

::

   import pkgstruct
   ...
       Pkg_info = pkgstruct.PkgStruct(script_path=sys.argv[0])
       # pkg_info.dump(relpath=False, with_seperator=True)
   ...
       pkg_info.make_subdirs(‘pkg_sysconfdir’, 0o755, True, ‘kivy’)
       os.environ[‘KIVY_HOME’] = pkg_info.concat_path(‘pkg_sysconfdir’, ‘kivy’)
   ....

What subdirectories are defined by it can be displayed with the member
function dump().

If the script path (``base_script``) given as argument is
``~/tmp/py_working_tool/lib/python/show_status3.py``, Further parent
directories of the upper than ``lib/python/``, which is its directory
name ``py_working_tool``, is interpreted as the package
name:``pkg_name``, and the location of that directory
``~/tmp/py_working_tool`` is recognized as the top of the directory
structure (``prefix``). Then the following directory structure is
deteremied according the rules similar to the GNU Coding Standard or
FHS.

- ``bindir``: ~/tmp/py_working_tool/bin
- ``datadir``: ~/tmp/py_working_tool/share
- ``sysconfdir``: ~/tmp/py_working_tool/etc
- ``localstatedir``: ~/tmp/py_working_tool/var
- ``runstatedir``: ~/tmp/py_working_tool/var/run
- ``tmpdir``: ~/tmp/py_working_tool/tmp

and other subdirectories of the package name (``pkg_name``) directly
under these directory names

- ``pkg_datadir``: ~/tmp/py_working_tool/share/py_working_tool
- ``pkg_sysconfdir``: ~/tmp/py_working_tool/etc/py_working_tool
- ``pkg_cachedir``: ~/tmp/py_working_tool/var/cache/py_working_tool
- ``pkg_statedatadir``: ~/tmp/py_working_tool/var/lib/py_working_tool
- ``pkg_logdir``: ~/tmp/py_working_tool/var/log/py_working_tool
- ``pkg_spooldir``: ~/tmp/py_working_tool/var/spool/py_working_tool

The equivalent string is defined and can be accessed as a property of
the ``PkgStruct`` class. What properties (subdirectory names) are
defined can also be checked by directly executing ``pkgstruct.py`` on
its own. (``********`` will be the name of the executing user).

Then following is the Example of running ``pkgstruct.py``

::

   ‘pkg_name': py_working_tool
   ‘pkg_path': ~/tmp/py_working_tool
   ----------------------------------------------------------------------
   ‘base_script': ~/tmp/py_working_tool/lib/python/pkgstruct.py
   ----------------------------------------------------------------------
   ‘script_mnemonic': pkgstruct
   ‘script_path': ~/tmp/py_working_tool/lib/python/pkgstruct.py
   ‘script_location': ~/tmp/py_working_tool/lib/python
   ‘script_basename': pkgstruct.py
   ----------------------------------------------------------------------
   ‘prefix': ~/tmp/py_working_tool
   ----------------------------------------------------------------------
   ‘exec_user’: ********
   ----------------------------------------------------------------------
   'exec_prefix':       '${prefix}'
   'bindir':            '${prefix}'/bin
   'datarootdir':       '${prefix}'/share
   'datadir':           '${prefix}'/share
   'sysconfdir':        '${prefix}'/etc
   'sharedstatedir':    '${prefix}'/com
   'localstatedir':     '${prefix}'/var
   'include':           '${prefix}'/include
   'libdir':            '${prefix}'/lib
   'srcdir':            '${prefix}'/src
   'infodir':           '${prefix}'/share/info
   'runstatedir':       '${prefix}'/var/run
   'localedir':         '${prefix}'/share/locale
   'lispdir':           '${prefix}'/emacs/lisp
   'docdir':            '${prefix}'/doc/py_working_tool
   'htmldir':           '${prefix}'/doc/py_working_tool
   'dvidir':            '${prefix}'/doc/py_working_tool
   'pdfdir':            '${prefix}'/doc/py_working_tool
   'psdir':             '${prefix}'/doc/py_working_tool
   'mandir':            '${prefix}'/share/man
   'man0dir':           '${prefix}'/share/man/man0
   'man1dir':           '${prefix}'/share/man/man1
   'man2dir':           '${prefix}'/share/man/man2
   'man3dir':           '${prefix}'/share/man/man3
   'man4dir':           '${prefix}'/share/man/man4
   'man5dir':           '${prefix}'/share/man/man5
   'man6dir':           '${prefix}'/share/man/man6
   'man7dir':           '${prefix}'/share/man/man7
   'man8dir':           '${prefix}'/share/man/man8
   'man9dir':           '${prefix}'/share/man/man9
   'manndir':           '${prefix}'/share/man/mann
   'sbindir':           '${prefix}'/sbin
   'bootdir':           '${prefix}'/boot
   'devdir':            '${prefix}'/dev
   'mediadir':          '${prefix}'/media
   'mntdir':            '${prefix}'/mnt
   'optdir':            '${prefix}'/opt
   'tmpdir':            '${prefix}'/tmp
   'xmldir':            '${prefix}'/etc/xml
   'etcoptdir':         '${prefix}'/etc/opt
   'cachedir':          '${prefix}'/var/cache
   'statedatadir':      '${prefix}'/var/lib
   'lockdir':           '${prefix}'/var/lock
   'logdir':            '${prefix}'/var/log
   'spooldir':          '${prefix}'/var/spool
   'statetmpdir':       '${prefix}'/var/tmp
   'user_home':         '${prefix}'/Users/********
   'home':              '${prefix}'/Users/********
   'homedir':           '${prefix}'/Users
   ----------------------------------------------------------------------
   'pkg_datadir':       '${prefix}'/share/py_working_tool
   'pkg_sysconfdir':    '${prefix}'/etc/py_working_tool
   'pkg_runstatedir':   '${prefix}'/var/run/py_working_tool
   'pkg_include':       '${prefix}'/include/py_working_tool
   'pkg_libdir':        '${prefix}'/lib/py_working_tool
   'pkg_srcdir':        '${prefix}'/src/py_working_tool
   'pkg_tmpdir':        '${prefix}'/tmp/py_working_tool
   'pkg_xmldir':        '${prefix}'/etc/xml/py_working_tool
   'pkg_cachedir':      '${prefix}'/var/cache/py_working_tool
   'pkg_statedatadir':  '${prefix}'/var/lib/py_working_tool
   'pkg_lockdir':       '${prefix}'/var/lock/py_working_tool
   'pkg_logdir':        '${prefix}'/var/log/py_working_tool
   'pkg_spooldir':      '${prefix}'/var/spool/py_working_tool
   'pkg_statetmpdir':   '${prefix}'/var/tmp/py_working_tool
   ----------------------------------------------------------------------

In addition, the member function ``concat_path()`` was implemented to
create another directory/file name string under these. The member
function ``make_subdirs()`` was also implemented to actually create the
directory. Example:

::

   pkg_info.make_subdirs(‘pkg_sysconfdir’, 0o755, True, ‘kivy’)
   os.environ[‘KIVY_HOME’] = pkg_info.concat_path(‘pkg_sysconfdir’, ‘kivy’)

The above is the code that creates the directory
``~/tmp/py_working_tool/etc/py_working_tool/kivy`` and sets this
directory in the environment variable ``'KIVY_HOME'``.

Another member function ``complement(..., filename=, ...)`` was
implemented to complement the path name only for the given file name is
not absolute path. ( i.e. if given starts from ‘/’ or ‘./’ or ‘../’, the
return value is the given filename. Otherwise the return value is the
output of ``concat_path(...)``)

Author
------

Nanigashi Uji (53845049+nanigashi-uji@users.noreply.github.com)
