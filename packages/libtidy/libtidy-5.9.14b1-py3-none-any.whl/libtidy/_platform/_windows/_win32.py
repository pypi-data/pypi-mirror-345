# Copyright (c) 2024 Adam Karpierz
# SPDX-License-Identifier: HTMLTIDY

import ctypes
from ctypes import windll
from ctypes.wintypes import BOOL, UINT, DWORD

# DWORD WINAPI GetLastError(void);
GetLastError = windll.kernel32.GetLastError
GetLastError.restype  = DWORD
GetLastError.argtypes = []

CP_ACP        = 0      # default to ANSI code page
CP_OEMCP      = 1      # default to OEM  code page
CP_MACCP      = 2      # default to MAC  code page
CP_THREAD_ACP = 3      # current thread's ANSI code page
CP_SYMBOL     = 42     # SYMBOL translations

CP_UTF7       = 65000  # UTF-7 translation
CP_UTF8       = 65001  # UTF-8 translation

# UINT WINAPI GetConsoleCP(void);
GetConsoleCP = windll.kernel32.GetConsoleCP
GetConsoleCP.restype  = UINT
GetConsoleCP.argytpes = []

# UINT WINAPI GetConsoleOutputCP(void);
GetConsoleOutputCP = windll.kernel32.GetConsoleOutputCP
GetConsoleOutputCP.restype  = UINT
GetConsoleOutputCP.argytpes = []

# BOOL WINAPI SetConsoleCP(
#  _In_  UINT wCodePageID
# );
SetConsoleCP = windll.kernel32.SetConsoleCP
SetConsoleCP.restype  = BOOL
SetConsoleCP.argytpes = [UINT]

# BOOL WINAPI SetConsoleOutputCP(
#  _In_  UINT wCodePageID
# );
SetConsoleOutputCP = windll.kernel32.SetConsoleOutputCP
SetConsoleOutputCP.restype  = BOOL
SetConsoleOutputCP.argytpes = [UINT]

del ctypes  # noqa: E305
