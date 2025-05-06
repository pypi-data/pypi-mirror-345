# **************************************************************************** #
# @file
# Platform specific definitions, specifics, and headers. This file is
# included by `tidy.h` already, and need not be included separately.
#
# @note It should be largely unnecessary to modify this file unless adding
# support for a completely new architecture. Most options defined in this
# file specify defaults that can be overridden by the build system; for
# example, passing -D flags to CMake.
#
# @author  Charles Reitzel [creitzel@rcn.com]
# @author  HTACG, et al (consult git log)
#
# @copyright
#     Copyright (c) 1998-2017 World Wide Web Consortium (Massachusetts
#     Institute of Technology, European Research Consortium for Informatics
#     and Mathematics, Keio University).
# @copyright
#     See tidy.h for license.
#
# @date      Created 2001-05-20 by Charles Reitzel
# @date      Updated 2002-07-01 by Charles Reitzel
# @date      Further modifications: consult git log.
# **************************************************************************** #

import ctypes as ct

from ._platform import defined
from . import _platform as platform

xxx = """  *** form CMakeLists.txt ***
 #------------------------------------------------------------------------
 # Runtime Configuration File Support
 #   By default on Unix-like systems when building for the console program,
 #   support runtime configuration files in /etc/ and in ~/. To prevent this,
 #   set ENABLE_CONFIG_FILES to NO. Specify -DTIDY_CONFIG_FILE and/or
 #   -DTIDY_USER_CONFIG_FILE to override the default paths in tidyplatform.h.
 # @note: this section refactored to support #584.
 #------------------------------------------------------------------------
 if ( UNIX AND SUPPORT_CONSOLE_APP )

   option ( ENABLE_CONFIG_FILES
            "Set to OFF to disable Tidy runtime configuration file support" ON )

     # All Unixes support getpwnam(); undef'd in tidyplatform.h if necessary.
     add_definitions( -DSUPPORT_GETPWNAM=1 )

 else ()

   option ( ENABLE_CONFIG_FILES
            "Set to ON to enable Tidy runtime configuration file support" OFF )

   if ( SUPPORT_GETPWNAM )
     add_definitions( -DSUPPORT_GETPWNAM=1 )
   endif ()

 endif ()

 if ( ENABLE_CONFIG_FILES )

     message(STATUS "*** Building support for runtime configuration files.")

     add_definitions( -DTIDY_ENABLE_CONFIG_FILES )

     # define a default here so we can pass to XSL.
     if ( NOT TIDY_CONFIG_FILE )
         set( TIDY_CONFIG_FILE "/etc/tidy.conf" )
     endif ()

     # define a default here so we can pass to XSL.
     if ( NOT TIDY_USER_CONFIG_FILE )
         set( TIDY_USER_CONFIG_FILE "~/.tidyrc" )
     endif ()

     # do *not* add these unless ENABLE_CONFIG_FILES!
     add_definitions( -DTIDY_CONFIG_FILE="${TIDY_CONFIG_FILE}" )
     add_definitions( -DTIDY_USER_CONFIG_FILE="${TIDY_USER_CONFIG_FILE}" )

 endif ()
"""

# =============================================================================
# Unix console application features
#   By default on Unix-like systems when building for the console program,
#   support runtime configuration files in /etc/ and in ~/. To prevent this,
#   set ENABLE_CONFIG_FILES to NO. Specify -DTIDY_CONFIG_FILE and/or
#   -DTIDY_USER_CONFIG_FILE to override the default paths in tidyplatform.h.
# @note: this section refactored to support #584.
# =============================================================================

# #define ENABLE_CONFIG_FILES

# if defined(TIDY_ENABLE_CONFIG_FILES)
#  if !defined(TIDY_CONFIG_FILE)
#    define TIDY_CONFIG_FILE "/etc/tidy.conf"
#  endif
#  if !defined(TIDY_USER_CONFIG_FILE)
#    define TIDY_USER_CONFIG_FILE "~/.tidyrc"
#  endif
# else
#  if defined(TIDY_CONFIG_FILE)
#    undef TIDY_CONFIG_FILE
#  endif
#  if defined(TIDY_USER_CONFIG_FILE)
#    undef TIDY_USER_CONFIG_FILE
#  endif
# endif

# =============================================================================
# Unix tilde expansion support
#   By default on Unix-like systems when building for the console program,
#   this flag is set so that Tidy knows getpwname() is available. It allows
#   tidy to find files named ~your/foo for use in the HTML_TIDY environment
#   variable or TIDY_CONFIG_FILE or TIDY_USER_CONFIG_FILE or on the command
#   command line: -config ~joebob/tidy.cfg
# Contributed by Todd Lewis.
# =============================================================================

# #define SUPPORT_GETPWNAM

# =============================================================================
# Optional Tidy features support
# =============================================================================

# Enable/disable support for additional languages
# ifndef SUPPORT_LOCALIZATIONS
#  define SUPPORT_LOCALIZATIONS 1
# endif

# Enable/disable support for console
# ifndef SUPPORT_CONSOLE_APP
#  define SUPPORT_CONSOLE_APP 1
# endif
# if defined, then only tidyOptGetDocLinksList exists in .dll/.so

# =============================================================================
# Platform specific convenience definitions
# =============================================================================

# === Convenience defines for Mac platforms ===

# if defined(macintosh)
# Mac OS 6.x/7.x/8.x/9.x, with or without CarbonLib - MPW or Metrowerks 68K/PPC compilers
#  define MAC_OS_CLASSIC

#  ifdef SUPPORT_GETPWNAM
#    undef SUPPORT_GETPWNAM
#  endif

# elif defined(__APPLE__) && defined(__MACH__)
#  # Mac OS X (client) 10.x (or server 1.x/10.x) - gcc or Metrowerks MachO compilers
#  define MAC_OS_X
# endif

if platform.is_macos:  # pragma: no cover
    FILENAMES_CASE_SENSITIVE = False
# endif

# === Convenience defines for Windows platforms ===

if platform.is_windows:  # pragma: no cover
    FILENAMES_CASE_SENSITIVE = False
#  if defined(__MWERKS__) || defined(__MSL__)
#    # not available with Metrowerks Standard Library
#    ifdef SUPPORT_GETPWNAM
#      undef SUPPORT_GETPWNAM
#    endif
#  endif
# endif

# === Convenience defines for Cygwin platforms ===

if platform.is_cygwin:  # pragma: no cover
    FILENAMES_CASE_SENSITIVE = False
# endif

# === Convenience defines for OpenVMS ===

# if defined(__VMS)
#   FILENAMES_CASE_SENSITIVE = False
# endif

# =============================================================================
# Case sensitive file systems
# =============================================================================

# By default, use case-sensitive filename comparison.
if not defined("FILENAMES_CASE_SENSITIVE"):  # pragma: no cover
    FILENAMES_CASE_SENSITIVE = True
# endif

# =============================================================================
# Windows file functions
# Windows needs _ prefix for Unix file functions.
# Not required by Metrowerks Standard Library (MSL).
#
# WINDOWS automatically set by Win16 compilers.
# _WIN32 automatically set by Win32 compilers.
# =============================================================================

# if is_windows: && !defined(__MSL__) && !defined(__BORLANDC__)

#  if defined(_MSC_VER)
#    if !defined(NDEBUG) && !defined(ENABLE_DEBUG_LOG) && !defined(DISABLE_DEBUG_LOG)
#      define ENABLE_DEBUG_LOG
#    endif
#  endif

# endif # is_windows #

# =============================================================================
# Other definitions
# =============================================================================

byte    = ct.c_ubyte
tchar   = ct.c_uint    # uint      # single, full character
tmbchar = ct.c_char    # ct.c_char # single, possibly partial character
tmbstr  = ct.c_char_p  # tmbchar * # pointer to buffer of possibly partial chars
ctmbstr = ct.c_char_p  # tmbchar const * # Ditto, but const
NULLSTR = ct.c_char_p(b"")

# `bool` is a reserved word in some but not all C++ compilers depending on age.
# age. Work around is to avoid bool by introducing a new enum called `Bool`.

# typedef enum
# {
no  = False
yes = True
# } Bool;

# for NULL pointers
# #define null ((const void*)0)
# extern void* null;
null = ct.c_void_p(None)

# Opaque data structure.
# Cast to implementation type struct within lib.
# This will reduce inter-dependencies/conflicts w/ application code.
#

# Opaque data structure used to pass back
# and forth to keep current position in a
# list or other collection.
#
class _TidyIterator(ct.Structure): pass  # { int _opaque; }
TidyIterator = ct.POINTER(_TidyIterator)  # noqa: E305

del ct, defined, platform

# eof
