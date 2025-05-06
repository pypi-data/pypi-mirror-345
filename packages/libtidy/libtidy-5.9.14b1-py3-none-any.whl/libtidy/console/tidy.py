# **************************************************************************** #
# @file
# HTML TidyLib command line driver.
#
# This console application utilizing LibTidy in order to offer a complete
# console application offering all of the features of LibTidy.
#
# @author  HTACG, et al (consult git log)
#
# @copyright
#     Copyright (c) 1998-2017 World Wide Web Consortium (Massachusetts
#     Institute of Technology, European Research Consortium for Informatics
#     and Mathematics, Keio University) and HTACG.
# @par
#     All Rights Reserved.
# @par
#     See `tidy.h` for the complete license.
#
# @date Additional updates: consult git log
# **************************************************************************** #

from __future__ import annotations

from typing import Any, Tuple, List, Callable
import sys
import os
import atexit
import copy
import ctypes as ct
from enum import IntEnum, auto
from dataclasses import dataclass

import libtidy as tidy
from libtidy import TidyDoc, TidyNode, TidyIterator, TidyBuffer, TidyOption
from libtidy._platform import defined, is_windows, is_linux, is_macos
if is_windows: from libtidy._platform._windows import _win32 as win32

# include "sprtf.h"

def sprtf(format: str, *args) -> int:  # noqa: A002
    msg = format % args
    if is_windows:
        prt(msg)  # ensure CR/LF  # noqa: F821
    else:
        oi(msg)  # noqa: F821
    # endif
    return len(msg)


# if defined(ENABLE_DEBUG_LOG) and is_windows and defined(_CRTDBG_MAP_ALLOC):
#  include <crtdbg.h>
# endif

if is_windows:
    win_cp: int = 0  # uint # original Windows code page
# endif

# @defgroup console_application Tidy Console Application
# @copydoc tidy.c
# @{

class Tidy:

    # @name Format strings and decorations used in output.
    # @{
    FMT:        str = "%-27.27s %-9.9s  %-40.40s\n"
    ULINE:      str = 65 * "="
    HELP_FMT:   str = " %-*.*s %-*.*s\n"
    HELP_ULINE: str = 65 * "-"
    HELP_WIDTH: int = 78
    # @}

    # State Machine Setup

    class States(IntEnum):
        """States"""

        DONE     = 0
        DATA     = auto()
        WRITING  = auto()
        TAG_OPEN = auto()
        TAG_NAME = auto()
        ERROR    = auto()

    class CharStates(IntEnum):
        """CharStates"""

        NIL           = 0
        EOF           = auto()
        BRACKET_CLOSE = auto()
        BRACKET_OPEN  = auto()
        OTHER         = auto()

    class Actions(IntEnum):
        """Actions"""

        NIL        = 0
        BUILD_NAME = auto()
        CONSUME    = auto()
        EMIT       = auto()
        EMIT_SUBS  = auto()
        WRITE      = auto()
        ERROR      = auto()

    @dataclass
    class TransitionType:
        """TransitionType"""

        state:      "Tidy.States"
        charstate:  "Tidy.CharStates"
        action:     "Tidy.Actions"
        next_state: "Tidy.States"

    transitions: List[TransitionType] = [
        TransitionType(States.DATA,
                       CharStates.EOF,
                       Actions.NIL,
                       States.DONE),
        TransitionType(States.DATA,
                       CharStates.BRACKET_OPEN,
                       Actions.CONSUME,
                       States.TAG_OPEN),
        # special case allows ;
        TransitionType(States.DATA,
                       CharStates.BRACKET_CLOSE,
                       Actions.EMIT,
                       States.WRITING),
        TransitionType(States.DATA,
                       CharStates.OTHER,
                       Actions.EMIT,
                       States.WRITING),
        TransitionType(States.WRITING,
                       CharStates.OTHER,
                       Actions.WRITE,
                       States.DATA),
        TransitionType(States.WRITING,
                       CharStates.BRACKET_CLOSE,
                       Actions.WRITE,
                       States.DATA),
        TransitionType(States.TAG_OPEN,
                       CharStates.EOF,
                       Actions.ERROR,
                       States.DONE),
        TransitionType(States.TAG_OPEN,
                       CharStates.OTHER,
                       Actions.NIL,
                       States.TAG_NAME),
        TransitionType(States.TAG_NAME,
                       CharStates.BRACKET_OPEN,
                       Actions.ERROR,
                       States.DONE),
        TransitionType(States.TAG_NAME,
                       CharStates.EOF,
                       Actions.ERROR,
                       States.DONE),
        TransitionType(States.TAG_NAME,
                       CharStates.BRACKET_CLOSE,
                       Actions.EMIT_SUBS,
                       States.WRITING),
        TransitionType(States.TAG_NAME,
                       CharStates.OTHER,
                       Actions.BUILD_NAME,
                       States.TAG_NAME),
        TransitionType(States.ERROR,
                       CharStates.NIL,
                       Actions.ERROR,
                       States.DONE),
        TransitionType(States.DONE,
                       CharStates.NIL,
                       Actions.NIL,
                       States.DONE),
    ]

    # MARK: - CLI Options Utilities
    # **************************************************************************** #
    # @defgroup options_cli CLI Options Utilities
    # These structures, arrays, declarations, and definitions are used throughout
    # this console application.
    # **************************************************************************** #
    # @{

    # This enum is used to categorize the options for help output.
    #
    class CmdOptCategory(IntEnum):
        """CmdOptCategory"""

        CmdOptFileManip = 0
        CmdOptProcDir   = auto()
        CmdOptCharEnc   = auto()
        CmdOptMisc      = auto()
        CmdOptXML       = auto()

    # This array contains headings that will be used in help output.
    #
    # mnemonic: str,  # Used in XML as a class.
    # key:      int,  # Key to fetch the localized string.
    #
    cmdopt_catname: List[dict] = [
        dict(mnemonic="file-manip",         key=tidy.TC_STRING_FILE_MANIP),
        dict(mnemonic="process-directives", key=tidy.TC_STRING_PROCESS_DIRECTIVES),
        dict(mnemonic="char-encoding",      key=tidy.TC_STRING_CHAR_ENCODING),
        dict(mnemonic="misc",               key=tidy.TC_STRING_MISC),
        dict(mnemonic="xml",                key=tidy.TC_STRING_XML),
    ]

    # The struct and subsequent array keep the help output structured
    # because we _also_ output all of this stuff as as XML.
    #
    @dataclass
    class CmdOptDesc:
        """CmdOptDesc"""

        categ: "Tidy.CmdOptCategory"  # Category
        name1:    str                 # Name
        key:      int                 # Key to fetch the localized description.
        subkey:   int = 0             # Secondary substitution key.
        eqconfig: str | None = None   # Equivalent configuration option
        name2:    str | None = None   # Name
        name3:    str | None = None   # Name

    # All instances of %s will be substituted with localized string
    # specified by the subkey field.
    #
    cmdopt_defs: List[CmdOptDesc] =  [
        CmdOptDesc(CmdOptCategory.CmdOptFileManip,
                   "-output <%s>",
                   tidy.TC_OPT_OUTPUT,
                   tidy.TC_LABEL_FILE,
                   "output-file: <%s>", "-o <%s>"),
        CmdOptDesc(CmdOptCategory.CmdOptFileManip,
                   "-config <%s>",
                   tidy.TC_OPT_CONFIG,
                   tidy.TC_LABEL_FILE),
        CmdOptDesc(CmdOptCategory.CmdOptFileManip,
                   "-file <%s>",
                   tidy.TC_OPT_FILE,
                   tidy.TC_LABEL_FILE,
                   "error-file: <%s>", "-f <%s>"),
        CmdOptDesc(CmdOptCategory.CmdOptFileManip,
                   "-modify",
                   tidy.TC_OPT_MODIFY,   0,
                   "write-back: yes", "-m"),
        CmdOptDesc(CmdOptCategory.CmdOptProcDir,
                   "-indent",
                   tidy.TC_OPT_INDENT,   0,
                   "indent: auto", "-i"),
        CmdOptDesc(CmdOptCategory.CmdOptProcDir,
                   "-wrap <%s>",
                   tidy.TC_OPT_WRAP,
                   tidy.TC_LABEL_COL,
                   "wrap: <%s>", "-w <%s>"),
        CmdOptDesc(CmdOptCategory.CmdOptProcDir,
                   "-upper",
                   tidy.TC_OPT_UPPER,    0,
                   "uppercase-tags: yes", "-u"),
        CmdOptDesc(CmdOptCategory.CmdOptProcDir,
                   "-clean",
                   tidy.TC_OPT_CLEAN,    0,
                   "clean: yes", "-c"),
        CmdOptDesc(CmdOptCategory.CmdOptProcDir,
                   "-bare",
                   tidy.TC_OPT_BARE,     0,
                   "bare: yes", "-b"),
        CmdOptDesc(CmdOptCategory.CmdOptProcDir,
                   "-gdoc",
                   tidy.TC_OPT_GDOC,     0,
                   "gdoc: yes", "-g"),
        CmdOptDesc(CmdOptCategory.CmdOptProcDir,
                   "-numeric",
                   tidy.TC_OPT_NUMERIC,  0,
                   "numeric-entities: yes", "-n"),
        CmdOptDesc(CmdOptCategory.CmdOptProcDir,
                   "-errors",
                   tidy.TC_OPT_ERRORS,   0,
                   "markup: no", "-e"),
        CmdOptDesc(CmdOptCategory.CmdOptProcDir,
                   "-quiet",
                   tidy.TC_OPT_QUIET,    0,
                   "quiet: yes", "-q"),
        CmdOptDesc(CmdOptCategory.CmdOptProcDir,
                   "-omit",
                   tidy.TC_OPT_OMIT,     0,
                   "omit-optional-tags: yes"),
        CmdOptDesc(CmdOptCategory.CmdOptProcDir,
                   "-xml",
                   tidy.TC_OPT_XML,      0,
                   "input-xml: yes"),
        CmdOptDesc(CmdOptCategory.CmdOptProcDir,
                   "-asxml",
                   tidy.TC_OPT_ASXML,    0,
                   "output-xhtml: yes", "-asxhtml"),
        CmdOptDesc(CmdOptCategory.CmdOptProcDir,
                   "-ashtml",
                   tidy.TC_OPT_ASHTML,   0,
                   "output-html: yes"),
        CmdOptDesc(CmdOptCategory.CmdOptProcDir,
                   "-access <%s>",
                   tidy.TC_OPT_ACCESS,
                   tidy.TC_LABEL_LEVL,
                   "accessibility-check: <%s>"),
        CmdOptDesc(CmdOptCategory.CmdOptCharEnc,
                   "-raw",
                   tidy.TC_OPT_RAW),
        CmdOptDesc(CmdOptCategory.CmdOptCharEnc,
                   "-ascii",
                   tidy.TC_OPT_ASCII),
        CmdOptDesc(CmdOptCategory.CmdOptCharEnc,
                   "-latin0",
                   tidy.TC_OPT_LATIN0),
        CmdOptDesc(CmdOptCategory.CmdOptCharEnc,
                   "-latin1",
                   tidy.TC_OPT_LATIN1),
        # ifndef NO_NATIVE_ISO2022_SUPPORT
        CmdOptDesc(CmdOptCategory.CmdOptCharEnc,
                   "-iso2022",
                   tidy.TC_OPT_ISO2022),
        # endif
        CmdOptDesc(CmdOptCategory.CmdOptCharEnc,
                   "-utf8",
                   tidy.TC_OPT_UTF8),
        CmdOptDesc(CmdOptCategory.CmdOptCharEnc,
                   "-mac",
                   tidy.TC_OPT_MAC),
        CmdOptDesc(CmdOptCategory.CmdOptCharEnc,
                   "-win1252",
                   tidy.TC_OPT_WIN1252),
        CmdOptDesc(CmdOptCategory.CmdOptCharEnc,
                   "-ibm858",
                   tidy.TC_OPT_IBM858),
        CmdOptDesc(CmdOptCategory.CmdOptCharEnc,
                   "-utf16le",
                   tidy.TC_OPT_UTF16LE),
        CmdOptDesc(CmdOptCategory.CmdOptCharEnc,
                   "-utf16be",
                   tidy.TC_OPT_UTF16BE),
        CmdOptDesc(CmdOptCategory.CmdOptCharEnc,
                   "-utf16",
                   tidy.TC_OPT_UTF16),
        CmdOptDesc(CmdOptCategory.CmdOptCharEnc,
                   "-big5",
                   tidy.TC_OPT_BIG5),
        CmdOptDesc(CmdOptCategory.CmdOptCharEnc,
                   "-shiftjis",
                   tidy.TC_OPT_SHIFTJIS),
        CmdOptDesc(CmdOptCategory.CmdOptMisc,
                   "-version",
                   tidy.TC_OPT_VERSION,
                   0, None, "-v"),
        CmdOptDesc(CmdOptCategory.CmdOptMisc,
                   "-help",
                   tidy.TC_OPT_HELP,
                   0, None, "-h", "-?"),
        CmdOptDesc(CmdOptCategory.CmdOptMisc,
                   "-help-config",
                   tidy.TC_OPT_HELPCFG),
        CmdOptDesc(CmdOptCategory.CmdOptMisc,
                   "-help-env",
                   tidy.TC_OPT_HELPENV),
        CmdOptDesc(CmdOptCategory.CmdOptMisc,
                   "-show-config",
                   tidy.TC_OPT_SHOWCFG),
        CmdOptDesc(CmdOptCategory.CmdOptMisc,
                   "-export-config",
                   tidy.TC_OPT_EXP_CFG),
        CmdOptDesc(CmdOptCategory.CmdOptMisc,
                   "-export-default-config",
                   tidy.TC_OPT_EXP_DEF),
        CmdOptDesc(CmdOptCategory.CmdOptMisc,
                   "-help-option <%s>",
                   tidy.TC_OPT_HELPOPT,
                   tidy.TC_LABEL_OPT),
        CmdOptDesc(CmdOptCategory.CmdOptMisc,
                   "-language <%s>",
                   tidy.TC_OPT_LANGUAGE,
                   tidy.TC_LABEL_LANG,
                   "language: <%s>"),
        CmdOptDesc(CmdOptCategory.CmdOptXML,
                   "-xml-help",
                   tidy.TC_OPT_XMLHELP),
        CmdOptDesc(CmdOptCategory.CmdOptXML,
                   "-xml-config",
                   tidy.TC_OPT_XMLCFG),
        CmdOptDesc(CmdOptCategory.CmdOptXML,
                   "-xml-strings",
                   tidy.TC_OPT_XMLSTRG),
        CmdOptDesc(CmdOptCategory.CmdOptXML,
                   "-xml-error-strings",
                   tidy.TC_OPT_XMLERRS),
        CmdOptDesc(CmdOptCategory.CmdOptXML,
                   "-xml-options-strings",
                   tidy.TC_OPT_XMLOPTS),
    ]

    # @} end CLI Options Definitions Utilities group

    def __init__(self):
        """Initialize"""
        self.library_version: str = tidy.LibraryVersion().decode("utf-8")
        self.tidy_platform: str | None = self.bytes2str(tidy.Platform())
        # Localized strings
        self.set_localized_strings()
        #
        self.tdoc: TidyDoc = tidy.Create()
        # Tidy will send errors to this file.
        self.errout: object | None = sys.stderr  # initialize to stderr

    def __del__(self):
        """Finalize"""
        if self.tdoc: tidy.Release(self.tdoc)

    # MARK: - Miscellaneous Utilities
    # **************************************************************************** #
    # @defgroup utilities_misc Miscellaneous Utilities
    # This group contains general utilities used in the console application.
    # **************************************************************************** #
    # @{

    def set_localized_strings(self):
        """Set/Update of localized Tidy strings."""
        self.TC_MAIN_ERROR_LOAD_CONFIG    = tidy.LocalizedString(
                                                 tidy.TC_MAIN_ERROR_LOAD_CONFIG).decode("utf-8")
        self.TC_STRING_VERS_A             = tidy.LocalizedString(
                                                 tidy.TC_STRING_VERS_A).decode("utf-8")
        self.TC_STRING_VERS_B             = tidy.LocalizedString(
                                                 tidy.TC_STRING_VERS_B).decode("utf-8")
        self.TC_STRING_MUST_SPECIFY       = tidy.LocalizedString(
                                                 tidy.TC_STRING_MUST_SPECIFY).decode("utf-8")
        self.TC_STRING_LANG_MUST_SPECIFY  = tidy.LocalizedString(
                                                 tidy.TC_STRING_LANG_MUST_SPECIFY).decode("utf-8")
        self.TC_STRING_LANG_NOT_FOUND     = tidy.LocalizedString(
                                                 tidy.TC_STRING_LANG_NOT_FOUND).decode("utf-8")
        self.TC_STRING_UNKNOWN_OPTION     = tidy.LocalizedString(
                                                 tidy.TC_STRING_UNKNOWN_OPTION).decode("utf-8")
        self.TC_STRING_UNKNOWN_OPTION_B   = tidy.LocalizedString(
                                                 tidy.TC_STRING_UNKNOWN_OPTION_B).decode("utf-8")
        self.TC_STRING_CONF_HEADER        = tidy.LocalizedString(
                                                 tidy.TC_STRING_CONF_HEADER).decode("utf-8")
        self.TC_STRING_CONF_NAME          = tidy.LocalizedString(
                                                 tidy.TC_STRING_CONF_NAME).decode("utf-8")
        self.TC_STRING_CONF_TYPE          = tidy.LocalizedString(
                                                 tidy.TC_STRING_CONF_TYPE).decode("utf-8")
        self.TC_STRING_CONF_VALUE         = tidy.LocalizedString(
                                                 tidy.TC_STRING_CONF_VALUE).decode("utf-8")
        self.TC_STRING_OPT_NOT_DOCUMENTED = tidy.LocalizedString(
                                                 tidy.TC_STRING_OPT_NOT_DOCUMENTED).decode("utf-8")
        self.TC_STRING_FATAL_ERROR        = tidy.LocalizedString(
                                                 tidy.TC_STRING_FATAL_ERROR).decode("utf-8")
        self.TC_TXT_HELP_1                = tidy.LocalizedString(
                                                 tidy.TC_TXT_HELP_1).decode("utf-8")
        self.TC_TXT_HELP_2A               = tidy.LocalizedString(
                                                 tidy.TC_TXT_HELP_2A).decode("utf-8")
        self.TC_TXT_HELP_2B               = tidy.LocalizedString(
                                                 tidy.TC_TXT_HELP_2B).decode("utf-8")
        self.TC_TXT_HELP_3                = tidy.LocalizedString(
                                                 tidy.TC_TXT_HELP_3).decode("utf-8")
        self.TC_TXT_HELP_3A               = tidy.LocalizedString(
                                                 tidy.TC_TXT_HELP_3A).decode("utf-8")
        self.TC_TXT_HELP_CONFIG           = tidy.LocalizedString(
                                                 tidy.TC_TXT_HELP_CONFIG).decode("utf-8")
        self.TC_TXT_HELP_CONFIG_NAME      = tidy.LocalizedString(
                                                 tidy.TC_TXT_HELP_CONFIG_NAME).decode("utf-8")
        self.TC_TXT_HELP_CONFIG_TYPE      = tidy.LocalizedString(
                                                 tidy.TC_TXT_HELP_CONFIG_TYPE).decode("utf-8")
        self.TC_TXT_HELP_CONFIG_ALLW      = tidy.LocalizedString(
                                                 tidy.TC_TXT_HELP_CONFIG_ALLW).decode("utf-8")
        self.TC_TXT_HELP_ENV_1            = tidy.LocalizedString(
                                                 tidy.TC_TXT_HELP_ENV_1).decode("utf-8")
        self.TC_TXT_HELP_ENV_1A           = tidy.LocalizedString(
                                                 tidy.TC_TXT_HELP_ENV_1A).decode("utf-8")
        self.TC_TXT_HELP_ENV_1B           = tidy.LocalizedString(
                                                 tidy.TC_TXT_HELP_ENV_1B).decode("utf-8")
        self.TC_TXT_HELP_ENV_1C           = tidy.LocalizedString(
                                                 tidy.TC_TXT_HELP_ENV_1C).decode("utf-8")
        self.TC_TXT_HELP_LANG_1           = tidy.LocalizedString(
                                                 tidy.TC_TXT_HELP_LANG_1).decode("utf-8")
        self.TC_TXT_HELP_LANG_2           = tidy.LocalizedString(
                                                 tidy.TC_TXT_HELP_LANG_2).decode("utf-8")
        self.TC_TXT_HELP_LANG_3           = tidy.LocalizedString(
                                                 tidy.TC_TXT_HELP_LANG_3).decode("utf-8")

    def out_of_memory():
        """Exits with an error in the event of an out of memory condition."""
        print("%s" %
              tidy.LocalizedString(tidy.TC_STRING_OUT_OF_MEMORY).decode("utf-8"),
              end="", file=sys.stderr)
        sys.exit(1)

    # @} end utilities_misc group

    # MARK: - Configuration Options Utilities
    # **************************************************************************** #
    # @defgroup utilities_cli_options Configuration Options Utilities
    # Provide utilities to manipulate configuration options for output.
    # **************************************************************************** #
    # @{

    # Structure maintains a description of a configuration option.
    #
    @dataclass
    class OptionDesc:
        """OptionDesc"""

        name:  str                 # Name
        categ: str                 # Category
        catid: int                 # Category ID
        type:  str | None = None   # "String, ...  # noqa: A003
        vals:  str | None = None   # Potential values. If None, use an external function
        deflt: str | None = None   # default
        have_vals: bool   = False  # if yes, vals is valid

    # A type for a function pointer for a function used to print out options
    # descriptions.
    # @param TidyDoc The document.
    # @param TidyOption The Tidy option.
    # @param OptionDesc A pointer to the option description structure.
    #
    OptionFunc = Callable[[TidyDoc, TidyOption, OptionDesc], None]

    def for_each_option(self,                    # The Tidy document.
                        topt_func: OptionFunc):  # The printing function to be used.
        """An iterator for the unsorted options."""
        it: TidyIterator = tidy.GetOptionList(self.tdoc)
        while it:
            topt: TidyOption = tidy.GetNextOption(self.tdoc, ct.byref(it))
            desc: Tidy.OptionDesc = self.get_option_desc(topt)
            topt_func(topt, desc)

    def for_each_sorted_option(self,                    # The Tidy document.
                               topt_func: OptionFunc):  # The printing function to be used.
        """An iterator for the sorted options."""
        for topt in self.get_sorted_options():
            desc: Tidy.OptionDesc = self.get_option_desc(topt)
            topt_func(topt, desc)

    def get_sorted_options(self) -> List[TidyOption]:  # The list of options.
        """Returns options sorted.

        A simple option comparator, used for sorting the options.
        """
        toptions = []
        it: TidyIterator = tidy.GetOptionList(self.tdoc)
        while it:
            topt: TidyOption = tidy.GetNextOption(self.tdoc, ct.byref(it))
            toptions.append(topt)
        toptions.sort(key=lambda topt: tidy.OptGetName(topt))
        return toptions

    def get_option_desc(self,
                        topt: TidyOption) -> OptionDesc:  # The option to create a description for.
        """Create OptionDesc "desc" related to "topt"."""
        topt_id:   tidy.TidyOptionId       = tidy.OptGetId(topt)
        topt_type: tidy.TidyOptionType     = tidy.OptGetType(topt)
        tcateg:    tidy.TidyConfigCategory = tidy.OptGetCategory(topt)

        desc = Tidy.OptionDesc(
            name  = tidy.OptGetName(topt).decode("utf-8"),
            categ = self.config_category(tcateg),
            catid = tcateg)
        desc.have_vals = True

        # Handle special cases first.
        if topt_id in [tidy.TidyInlineTags,
                       tidy.TidyBlockTags,
                       tidy.TidyEmptyTags,
                       tidy.TidyPreTags]:

            desc.type  = "Tag Names"
            desc.vals  = "tagX, tagY, ..."
            desc.deflt = None
            desc.have_vals = True

        elif topt_id in [tidy.TidyPriorityAttributes]:

            desc.type  = "Attributes Names"
            desc.vals  = "attributeX, attributeY, ..."
            desc.deflt = None
            desc.have_vals = True

        elif topt_id in [tidy.TidyCharEncoding,
                         tidy.TidyInCharEncoding,
                         tidy.TidyOutCharEncoding]:

            desc.type  = "Encoding"
            desc.vals  = None
            deflt = self.bytes2str(tidy.OptGetEncName(self.tdoc, topt_id))
            desc.deflt = deflt if deflt is not None else "?"
            desc.have_vals = True

            # General case will handle remaining
        else:
            if topt_type == tidy.TidyBoolean:

                desc.type  = "Boolean"
                desc.deflt = self.bytes2str(tidy.OptGetCurrPick(self.tdoc, topt_id))
                desc.have_vals = True

            elif topt_type == tidy.TidyInteger:

                if self.has_picklist(topt):
                    desc.type  = "Enum"
                    desc.deflt = self.bytes2str(tidy.OptGetCurrPick(self.tdoc, topt_id))
                    desc.have_vals = True
                else:
                    desc.type = "Integer"
                    desc.vals = ("0 (no wrapping), 1, 2, ..."
                                 if topt_id == tidy.TidyWrapLen else
                                 "0, 1, 2, ...")
                    desc.deflt = "%u" % tidy.OptGetInt(self.tdoc, topt_id)
                    desc.have_vals = True

            elif topt_type == tidy.TidyString:

                desc.type  = "String"
                desc.vals  = None
                desc.deflt = self.bytes2str(tidy.OptGetValue(self.tdoc, topt_id))
                desc.have_vals = False

        return desc

    def config_category(self, id: tidy.TidyConfigCategory) -> str:  # noqa: A002
        """Returns the configuration category id for the specified configuration

        category id. This will be used as an XML class attribute value.
        @param id The TidyConfigCategory for which to lookup the category name.
        @result Returns the configuration category, such as "diagnostics".
        """
        if id >= tidy.TidyDiagnostics and id <= tidy.TidyInternalCategory:
            return self.bytes2str(tidy.ErrorCodeAsKey(id))
        else:
            print(self.TC_STRING_FATAL_ERROR % int(id), file=sys.stderr)
            assert False
            os.abort()
            return "never_here"  # only for the compiler warning

    @staticmethod
    def has_picklist(topt: TidyOption) -> bool:
        """Utility to determine if an option has a picklist.

        @param topt The option to check.
        @result Returns a bool indicating whether the option has a picklist or not.
        """
        if tidy.OptGetType(topt) != tidy.TidyInteger:
            return False

        it: TidyIterator = tidy.OptGetPickList(topt)
        return tidy.OptGetNextPick(topt, ct.byref(it)) is not None

    # @} end utilities_cli_options group

    # MARK: - Provide the -help Service
    # **************************************************************************** #
    # @defgroup service_help Provide the -help Service
    # **************************************************************************** #
    # @{

    def help(self,  # noqa: A003
             prog: str):  # The path of the current executable.
        """Handles the -help service."""

        print(self.TC_TXT_HELP_1 % (self.get_final_name(prog),
                                    self.library_version))

        if self.tidy_platform is not None:
            help_str = Tidy.string_with_format(self.TC_TXT_HELP_2A,
                                               self.tidy_platform)
        else:
            help_str = Tidy.string_with_format(self.TC_TXT_HELP_2B)
        width = min(self.HELP_WIDTH, len(help_str))
        print("%s" % help_str)
        print("%*.*s\n" % (width, width, self.ULINE))

        self.print_help_options()

        print()
        if hasattr(tidy, "TIDY_CONFIG_FILE") and hasattr(tidy, "TIDY_USER_CONFIG_FILE"):
            help_str = Tidy.string_with_format(self.TC_TXT_HELP_3A,
                                               tidy.TIDY_CONFIG_FILE,
                                               tidy.TIDY_USER_CONFIG_FILE)
            print(self.TC_TXT_HELP_3 % help_str)
        else:
            print(self.TC_TXT_HELP_3 % "\n")

    @staticmethod
    def get_final_name(prog: str) -> str:
        """Returns the final name of the tidy executable by eliminating \
        the path name components from the executable name.

        @param prog The path of the current executable.
        """
        return os.path.basename(prog)

    def print_help_options(self):
        """Outputs all of the complete help options (text)."""
        for categ in Tidy.CmdOptCategory:

            name  = tidy.LocalizedString(self.cmdopt_catname[categ]["key"]).decode("utf-8")
            width = min(self.HELP_WIDTH, len(name))
            print("%s" % name)
            print("%*.*s" % (width, width, self.HELP_ULINE))

            # Tidy's "standard" 78-column output was always 25:52 ratio, so let's
            # try to preserve this approximately 1:2 ratio regardless of whatever
            # silly thing the user might have set for a console width, with a
            # maximum of 50 characters for the first column.
            #
            width1 = self.HELP_WIDTH // 3          # one third of the available
            width1 = min(35, max(1,  width1))      # at least 1 and no greater than 35
            width2 = self.HELP_WIDTH - width1 - 2  # allow two spaces
            width2 = max(1, width2)                # at least 1

            for cdesc in self.cmdopt_defs:
                if cdesc.categ != categ:
                    continue
                Tidy.print2columns(self.HELP_FMT,
                                   width1, width2,
                                   Tidy.get_option_names(cdesc),
                                   tidy.LocalizedString(cdesc.key).decode("utf-8"))
            print()

    @staticmethod
    def get_option_names(cdesc: CmdOptDesc) -> str:
        """Retrieve the option's name(s) from the structure as a single string, \
        localizing the field values if application. For example, this might \
        return `-output <file>, -o <file>`.

        @param cdesc A CmdOptDesc array item for which to get the names.
        @result Returns the name(s) for the option as a single string.
        """
        local_cdesc: Tidy.CmdOptDesc = copy.deepcopy(cdesc)
        Tidy.localize_option_names(local_cdesc)

        name = ""
        name += local_cdesc.name1
        if local_cdesc.name2 is not None:
            name += ", "
            name += local_cdesc.name2
        if local_cdesc.name3 is not None:
            name += ", "
            name += local_cdesc.name3

        return name

    # @} end service_help group

    # MARK: - Provide the -help-config Service
    # **************************************************************************** #
    # @defgroup service_help_config Provide the -help-config Service
    # **************************************************************************** #
    # @{

    def option_help(self):
        """Handles the -help-config service.

        @remark We will not support console word wrapping for the configuration
                options table. If users really have a small console, then they
                should make it wider or output to a file.
        """
        print()
        print("%s" % self.TC_TXT_HELP_CONFIG, end="")
        print(self.FMT % (self.TC_TXT_HELP_CONFIG_NAME,
                          self.TC_TXT_HELP_CONFIG_TYPE,
                          self.TC_TXT_HELP_CONFIG_ALLW), end="")
        print(self.FMT % (self.ULINE, self.ULINE, self.ULINE), end="")

        self.for_each_sorted_option(self.print_option)

    def print_option(self,
                     topt: TidyOption,   # The option to print.
                     desc: OptionDesc):  # A pointer to the OptionDesc array.
        """Prints a single option."""
        if tidy.OptGetCategory(topt) == tidy.TidyInternalCategory:
            return

        if desc.name or desc.type:
            pval = desc.vals
            if not desc.have_vals:
                pval = "-"
            elif pval is None:
                pval = self.get_allowed_values(topt, desc)
            Tidy.print3columns(self.FMT, 27, 9, 40, desc.name, desc.type, pval)

    @staticmethod
    def get_allowed_values(topt: TidyOption,  # A TidyOption for which to get the allowed values.
                           desc: OptionDesc) -> str:  # A pointer to the OptionDesc array.
        """Retrieves allowed values for an option.

        @result A string containing the allowed values.
        """
        if desc.vals is not None:
            return desc.vals[:]
        else:
            return Tidy.get_allowed_values_from_pick(topt)

    @staticmethod
    def get_allowed_values_from_pick(topt: TidyOption) -> str:
        """Retrieves allowed values from an option's pick list.

        @param topt A TidyOption for which to get the allowed values.
        @result A string containing the allowed values.
        """
        value = ""
        first = True
        it: TidyIterator = tidy.OptGetPickList(topt)
        while it:
            if first:
                first = False
            else:
                value += ", "
            pdef = tidy.OptGetNextPick(topt, ct.byref(it))
            if pdef: value += pdef.decode("utf-8")

        return value

    # @} end service_help_config group

    # MARK: - Provide the -help-env Service
    # **************************************************************************** #
    # @defgroup service_help_env Provide the -help-env Service
    # **************************************************************************** #
    # @{

    def help_env(self):
        """Handles the -help-env service."""
        uses_env = ("HTML_TIDY" in os.environ)

        help_str = ""
        if hasattr(tidy, "TIDY_CONFIG_FILE") and hasattr(tidy, "TIDY_USER_CONFIG_FILE"):
            help_str = Tidy.string_with_format(self.TC_TXT_HELP_ENV_1A,
                                               tidy.TIDY_CONFIG_FILE,
                                               tidy.TIDY_USER_CONFIG_FILE)

        env_var = os.environ["HTML_TIDY"] if uses_env else self.TC_TXT_HELP_ENV_1B
        print()
        print(self.TC_TXT_HELP_ENV_1 % (help_str, env_var), end="")

        if hasattr(tidy, "TIDY_CONFIG_FILE") and hasattr(tidy, "TIDY_USER_CONFIG_FILE"):
            if uses_env:
                print(Tidy.string_with_format(self.TC_TXT_HELP_ENV_1C,
                                              tidy.TIDY_USER_CONFIG_FILE), end="")
        print()

    # @} end service_help_env group

    # MARK: - Provide the -help-option Service
    # **************************************************************************** #
    # @defgroup service_help_option Provide the -help-option Service
    # **************************************************************************** #
    # @{

    def option_describe(self,
                        option: str):  # The name of the option.
        """Handles the -help-option service."""
        assert option is not None, "Tidy option name should not be None"

        topt_id: tidy.TidyOptionId       = tidy.OptGetIdForName(self.str2bytes(option))
        topt:    TidyOption              = tidy.GetOption(self.tdoc, topt_id)
        tcateg:  tidy.TidyConfigCategory = tidy.OptGetCategory(topt)

        if topt_id < tidy.N_TIDY_OPTIONS and tcateg != tidy.TidyInternalCategory:
            doc = self.bytes2str(tidy.OptGetDoc(self.tdoc, topt))
            description = self.cleanup_description(doc)
        else:
            description = self.TC_STRING_UNKNOWN_OPTION_B

        print()
        print("`--%s`\n" % option)
        Tidy.print1column("%-{width}.{width}s\n".format(width=self.HELP_WIDTH),
                          self.HELP_WIDTH, description or "")
        print()

    @classmethod
    def cleanup_description(cls, description: str | None) -> str | None:
        """Cleans up the HTML-laden option descriptions for console output. \
        It's just a simple HTML filtering/replacement function.

        @param description The option description.
        @result Returns an allocated string with some HTML stripped away.
        """
        # Substitutions - this might be a good spot to introduce platform
        # dependent definitions for colorized output on different terminals
        # that support, for example, ANSI escape sequences. The assumption
        # is made the Mac and Linux targets support ANSI colors, but even
        # so debugger terminals may not. Note that the line-wrapping
        # function also doesn't account for non-printing characters.
        #
        # static struct {
        #    ctmbstr tag;
        #    ctmbstr replacement;
        #
        replacements: List[dict] = [
            dict(tag="lt",  replacement="<"),
            dict(tag="gt",  replacement=">"),
            dict(tag="br/", replacement="\n\n"),
        ]
        if is_linux or is_macos:  # defined(MAC_OS_X)
            replacements.extend([
                dict(tag="code",    replacement="\x1b[36m"),
                dict(tag="/code",   replacement="\x1b[0m"),
                dict(tag="em",      replacement="\x1b[4m"),
                dict(tag="/em",     replacement="\x1b[0m"),
                dict(tag="strong",  replacement="\x1b[31m"),
                dict(tag="/strong", replacement="\x1b[0m"),
            ])

        if not description:
            return None

        result: str | None = None

        name:   str | None = None  # current tag name
        writer: str | None = None  # output
        # Pump Setup
        state: cls.States = cls.States.DATA
        # Process the HTML Snippet
        i: int = 0
        while True:
            ch = description[i] if description[i:] else ""

            # Determine secondary state.
            charstate: Tidy.CharStates
            if ch == "":
                charstate = Tidy.CharStates.EOF
            elif ch in ("<", "&"):
                charstate = Tidy.CharStates.BRACKET_OPEN
            elif ch in (">", ";"):
                charstate = Tidy.CharStates.BRACKET_CLOSE
            else:
                charstate = Tidy.CharStates.OTHER

            # Find the correct instruction
            for transition in Tidy.transitions:
                if (transition.state == state
                   and transition.charstate == charstate):

                    # This action is building the name of an HTML tag.
                    if transition.action == cls.Actions.BUILD_NAME:

                        if name is None:
                            name = ""
                        name += ch
                        i += 1

                        # This character will be emitted into the output
                        # stream. The only purpose of this action is to
                        # ensure that `writer` is NULL as a flag that we
                        # will output the current `ch`

                    elif transition.action == cls.Actions.EMIT:

                        writer = None  # flag to use ch

                        # Now that we've consumed a tag, we will emit the
                        # substitution if any has been specified in
                        # `replacements`.

                    elif transition.action == cls.Actions.EMIT_SUBS:

                        writer = ""
                        for repl in replacements:
                            if repl["tag"] == name:
                                writer = repl["replacement"]

                        name = ""

                        # This action will add to our `result` string, expanding
                        # the buffer as necessary in reasonable chunks.

                    elif transition.action == cls.Actions.WRITE:

                        if result is None:
                            result = ""
                        # Add current writer to the buffer
                        result += (ch if writer is None else writer)
                        i += 1

                        # This action could be more robust but it serves the
                        # current purpose. Cross our fingers and count on our
                        # localizers not to give bad HTML descriptions.

                    elif transition.action == cls.Actions.ERROR:

                        print("<Error> The localized string probably has bad HTML.")
                        return result
                        # Just a NOP.

                    elif transition.action == cls.Actions.NIL:

                        # The default case also handles the CONSUME action.
                        pass

                    else:
                        i += 1

                    state = transition.next_state
                    break

            if not description[i:]: break
        # } while ( description[i] );

        return result

    @staticmethod
    def print1column(fmt:    str,   # The format string for formatting the output.
                     width1: int,   # The width of the column.
                     col1:   str):  # The content of the column.
        """Outputs one column of text."""
        while True:
            col1, c1buf = Tidy.cut_to_whitespace(col1, width1)
            print(fmt % c1buf, end="")
            if not col1: break

    @staticmethod
    def print2columns(fmt:    str,   # The format string for formatting the output.
                      width1: int,   # The width of column 1.
                      width2: int,   # The width of column 2.
                      col1:   str,   # The contents of column 1.
                      col2:   str):  # The contents of column 2.
        """Outputs two columns of text."""
        while True:
            col1, c1buf = Tidy.cut_to_whitespace(col1, width1)
            col2, c2buf = Tidy.cut_to_whitespace(col2, width2)
            print(fmt % (width1, width1, c1buf,
                         width2, width2, c2buf), end="")
            if not (col1 or col2): break

    @staticmethod
    def print3columns(fmt:    str,   # The format string for formatting the output.
                      width1: int,   # Width of column 1.
                      width2: int,   # Width of column 2.
                      width3: int,   # Width of column 3.
                      col1:   str,   # Content of column 1.
                      col2:   str,   # Content of column 2.
                      col3:   str):  # Content of column 3.
        """Outputs three columns of text."""
        while True:
            col1, c1buf = Tidy.cut_to_whitespace(col1, width1)
            col2, c2buf = Tidy.cut_to_whitespace(col2, width2)
            col3, c3buf = Tidy.cut_to_whitespace(col3, width3)
            print(fmt % (c1buf,
                         c2buf,
                         c3buf), end="")
            if not (col1 or col2 or col3): break

    @staticmethod
    def cut_to_whitespace(string: str,  # starting point of desired string to output
                          width:  int) -> Tuple[str, str]:  # column width desired
        """Used by `print1column`, `print2columns` and `print3columns` to manage \
        wrapping text within columns.

        @result The pointer to the next part of the string to output and
                the buffer to output.
        """
        if not string:
            return None, ""
        elif len(string) <= width:
            return None, string[:]
        else:
            # scan forward looking for newline
            j = 0
            while j < width and string[j] != "\n": j += 1
            if j == width:
                # scan backward looking for first space
                j = width
                while j and string[j] != " ": j -= 1
                l, n = ((j, j + 1) if j != 0
                        else (width, width))  # no white space
            else:
                l, n = j, j + 1
            return string[n:] or None, string[:l]

    # @} end service_help_option group

    # MARK: - Provide the -lang help Service
    # **************************************************************************** #
    # @defgroup service_lang_help Provide the -lang help Service
    # **************************************************************************** #
    # @{

    def lang_help(self):
        """Handles the -lang help service.

        @remark We will not support console word wrapping for the tables. If users
                really have a small console, then they should make it wider or
                output to a file.
        """
        print()
        print("%s" % self.TC_TXT_HELP_LANG_1)
        self.print_tidy_windows_language_names("  %-20s -> %s\n")
        print()
        print("%s" % self.TC_TXT_HELP_LANG_2)
        self.print_tidy_language_names("  %s\n")
        print()
        print(self.TC_TXT_HELP_LANG_3 % tidy.GetLanguage().decode("utf-8"))

    @staticmethod
    def print_tidy_windows_language_names(format: str | None = None):  # noqa: A002
        """Prints the Windows language names that Tidy recognizes, using the specified \
        format string.

        @param format A format string used to display the Windows language names,
               or None to use the built-in default format.
        """
        it: TidyIterator = tidy.getWindowsLanguageList()
        while it:
            item = tidy.getNextWindowsLanguage(ct.byref(it))
            win_name   = tidy.LangWindowsName(item).decode("utf-8")
            posix_name = tidy.LangPosixName(item).decode("utf-8")
            if format is not None:
                print(format % (win_name, posix_name), end="")
            else:
                print("%-20s -> %s" % (win_name, posix_name))

    @staticmethod
    def print_tidy_language_names(format: str | None = None):  # noqa: A002
        """Prints the languages the are currently built into Tidy, using the specified \
        format string.

        @param format A format string used to display the Windows language names,
               or None to use the built-in default format.
        """
        it: TidyIterator = tidy.getInstalledLanguageList()
        while it:
            item = tidy.getNextInstalledLanguage(ct.byref(it)).decode("utf-8")
            if format is not None:
                print(format % item, end="")
            else:
                print("%s" % item)

    # @} end service_lang_help group

    # MARK: - Provide the -show-config Service
    # **************************************************************************** #
    # @defgroup service_show_config Provide the -show-config Service
    # **************************************************************************** #
    # @{

    def option_values(self):
        """Handles the -show-config service.

        @remark We will not support console word wrapping for the table. If users
                really have a small console, then they should make it wider or
                output to a file.
        """
        print()
        print("%s" % self.TC_STRING_CONF_HEADER)
        print(self.FMT % (self.TC_STRING_CONF_NAME,
                          self.TC_STRING_CONF_TYPE,
                          self.TC_STRING_CONF_VALUE), end="")
        print(self.FMT % (self.ULINE, self.ULINE, self.ULINE), end="")

        self.for_each_sorted_option(self.print_option_values)

    def print_option_values(self,
                            topt: TidyOption,   # The option for which to show values.
                            desc: OptionDesc):  # The OptionDesc array.
        """Prints the option value for a given option."""
        if tidy.OptGetCategory(topt) == tidy.TidyInternalCategory:
            return

        topt_id: tidy.TidyOptionId = tidy.OptGetId(topt)

        if topt_id in [tidy.TidyInlineTags,
                       tidy.TidyBlockTags,
                       tidy.TidyEmptyTags,
                       tidy.TidyPreTags]:

            it: TidyIterator = tidy.OptGetDeclTagList(self.tdoc)
            while it:
                desc.deflt = self.bytes2str(tidy.OptGetNextDeclTag(self.tdoc, topt_id,
                                                                   ct.byref(it)))
                if it:
                    print(self.FMT % (desc.name, desc.type, desc.deflt), end="")
                    desc.name = ""
                    desc.type = ""

        elif topt_id in [tidy.TidyPriorityAttributes]:  # Is #697 - This case seems missing

            it_attr: TidyIterator = tidy.OptGetPriorityAttrList(self.tdoc)
            if it_attr and it_attr != ct.cast(-1, TidyIterator):
                while it_attr:
                    desc.deflt = self.bytes2str(tidy.OptGetNextPriorityAttr(self.tdoc,
                                                                            ct.byref(it_attr)))
                    if it_attr:
                        print(self.FMT % (desc.name, desc.type, desc.deflt), end="")
                        desc.name = ""
                        desc.type = ""
        else:
            pass

        # fix for http://tidy.sf.net/bug/873921
        if desc.name or desc.type or desc.deflt:
            if not desc.deflt: desc.deflt = ""
            print(self.FMT % (desc.name, desc.type, desc.deflt), end="")

    # @} end service_show_config group

    # MARK: - Provide the -export-config Services
    # **************************************************************************** #
    # @defgroup service_export_config Provide the -export-config Services
    # **************************************************************************** #
    # @{

    def export_option_values(self):
        """Handles the -export-config service."""
        self.for_each_sorted_option(self.print_option_export_values)

    def export_default_option_values(self):
        """Handles the -export-default-config service."""
        tidy.OptResetAllToDefault(self.tdoc)
        self.for_each_sorted_option(self.print_option_export_values)

    def print_option_export_values(self,
                                   topt: TidyOption,   # The option for which to show values.
                                   desc: OptionDesc):  # The OptionDesc array.
        """Prints the option value for a given option."""
        if tidy.OptGetCategory(topt) == tidy.TidyInternalCategory:
            return

        NUL = b"\0"
        SP  = b" "

        topt_id: tidy.TidyOptionId = tidy.OptGetId(topt)

        if topt_id in [tidy.TidyInlineTags,
                       tidy.TidyBlockTags,
                       tidy.TidyEmptyTags,
                       tidy.TidyPreTags]:

            it: TidyIterator = tidy.OptGetDeclTagList(self.tdoc)
            if it:  # Is #697 - one or more values
                # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", bool(it))
                buf1 = TidyBuffer()
                buf2 = TidyBuffer()
                tidy.BufInit(ct.byref(buf1))
                tidy.BufInit(ct.byref(buf2))
                while it:
                    desc.deflt = self.bytes2str(tidy.OptGetNextDeclTag(self.tdoc, topt_id,
                                                                       ct.byref(it)))
                    if desc.deflt is not None:
                        if buf1.size:
                            tidy.BufAppend(ct.byref(buf1), SP, 1)
                        buffer = self.str2bytes(desc.deflt)
                        tidy.BufAppend(ct.byref(buf1), buffer, len(buffer))
                self.invert_buffer(buf1, buf2)  # Is #697 - specialised service to invert words
                tidy.BufAppend(ct.byref(buf2), NUL, 1)  # is this really required?
                print("%s: %s" % (desc.name, bytes(buf2.bp[0:buf2.size]).decode("utf-8")))
                desc.name  = ""
                desc.type  = ""
                desc.deflt = None
                tidy.BufFree(ct.byref(buf1))
                tidy.BufFree(ct.byref(buf2))

        elif topt_id in [tidy.TidyPriorityAttributes]:  # Is #697 - This case seems missing

            it: TidyIterator = tidy.OptGetPriorityAttrList(self.tdoc)
            if it and it != ct.cast(-1, TidyIterator):
                # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$", bool(it))
                buf1 = TidyBuffer()
                tidy.BufInit(ct.byref(buf1))
                while it:
                    desc.deflt = self.bytes2str(tidy.OptGetNextPriorityAttr(self.tdoc,
                                                                            ct.byref(it)))
                    if desc.deflt is not None:
                        if buf1.size:
                            tidy.BufAppend(ct.byref(buf1), SP, 1)
                        buffer = self.str2bytes(desc.deflt)
                        tidy.BufAppend(ct.byref(buf1), buffer, len(buffer))
                tidy.BufAppend(ct.byref(buf1), NUL, 1)  # is this really required?
                print("%s: %s" % (desc.name, bytes(buf1.bp[0:buf1.size]).decode("utf-8")))
                desc.name  = ""
                desc.type  = ""
                desc.deflt = None
                tidy.BufFree(ct.byref(buf1))

        else:
            pass

        # fix for http://tidy.sf.net/bug/873921
        if desc.name or desc.type or desc.deflt:
            if not desc.deflt: desc.deflt = ""
            print("%s: %s" % (desc.name, desc.deflt))

    # NOK
    @staticmethod
    def invert_buffer(src: TidyBuffer, dst: TidyBuffer):
        """Is #697 - specialised service to 'invert' a buffers content \
        split on a space character."""
        NUL = b"\0" ; C_NUL = ord(NUL)
        SP  = b" "  ; C_SP  = ord(SP)
        inp = src.bp
        if not inp: return
        idx = src.size
        for idx in range(src.size - 1, -1, -1):
            uc = inp[idx]
            if uc == C_SP:
                inp[idx] = C_NUL
                cp = bytes(inp[idx + 1:src.size])
                if dst.size: tidy.BufAppend(ct.byref(dst), SP, 1)
                tidy.BufAppend(ct.byref(dst), cp, Tidy.strlen(cp))
        if dst.size: tidy.BufAppend(ct.byref(dst), SP, 1)
        tidy.BufAppend(ct.byref(dst), src.bp, Tidy.strlen(src.bp[0:src.size]))

    # @} end service_export_config group

    # MARK: - Provide the -version Service
    # **************************************************************************** #
    # @defgroup service_version Provide the -version Service
    # **************************************************************************** #
    # @{

    def version(self):
        """Handles the -version service."""
        if self.tidy_platform is not None:
            print(self.TC_STRING_VERS_A % (self.tidy_platform,
                                           self.library_version))
        else:
            print(self.TC_STRING_VERS_B % self.library_version)

    # @} end service_version group

    # MARK: - Provide the -xml-config Service
    # **************************************************************************** #
    # @defgroup service_xml_config Provide the -xml-config Service
    # **************************************************************************** #
    # @{

    def XML_option_help(self):
        """Handles the -xml-config service."""

        print('<?xml version="1.0"?>\n'
              '<config version="%s">' %  self.library_version)

        self.for_each_option(self.print_XML_option)

        print('</config>')

    def print_XML_option(self,
                         topt: TidyOption,   # The option.
                         desc: OptionDesc):  # The OptionDesc for the option.
        """Prints for XML an option."""

        if tidy.OptGetCategory(topt) == tidy.TidyInternalCategory:
            return

        print(' <option class="%s">' % desc.categ)
        print('  <name>%s</name>' % desc.name)
        print('  <type>%s</type>' % desc.type)
        if desc.deflt is not None:
            print('  <default>%s</default>' % desc.deflt)
        else:
            print('  <default />')
        if desc.have_vals:
            print('  <example>', end="")
            self.print_allowed_values(topt, desc)
            print('</example>')
        else:
            print('  <example />')
        self.print_XML_description(topt)
        self.print_XML_cross_ref(topt)
        self.print_XML_cross_ref_eqconsole(topt)
        print(' </option>')

    @staticmethod
    def print_allowed_values(topt: TidyOption,   # The Tidy option.
                             desc: OptionDesc):  # The OptionDesc for the option.
        """Prints an option's allowed values."""
        if desc.vals is not None:
            print("%s" % desc.vals, end="")
        else:
            Tidy.print_allowed_values_from_pick(topt)

    @staticmethod
    def print_allowed_values_from_pick(topt: TidyOption):  # The Tidy option.
        """Prints an option's allowed value as specified in its pick list.

        @param topt The Tidy option.
        """
        first = True
        it: TidyIterator = tidy.OptGetPickList(topt)
        while it:
            if first: first = False
            else: print(", ", end="")
            pdef = tidy.OptGetNextPick(topt, ct.byref(it))
            if pdef: print("%s" % pdef.decode("utf-8"), end="")

    def print_XML_description(self,
                              topt: TidyOption):  # The option.
        """Prints for XML an option's <description>."""
        doc = self.bytes2str(tidy.OptGetDoc(self.tdoc, topt))
        if doc is not None:
            print('  <description>%s</description>' % doc)
        else:
            print('  <description />')
            print(self.TC_STRING_OPT_NOT_DOCUMENTED %
                  tidy.OptGetName(topt).decode("utf-8"), file=sys.stderr)

    def print_XML_cross_ref(self,
                            topt: TidyOption):  # The option.
        """Prints for XML an option's `<seealso>`."""
        it: TidyIterator = tidy.OptGetDocLinksList(self.tdoc, topt)
        while it:
            opt_linked: TidyOption = tidy.OptGetNextDocLinks(self.tdoc,
                                                             ct.byref(it))
            print('  <seealso>%s</seealso>' %
                  tidy.OptGetName(opt_linked).decode("utf-8"))

    def print_XML_cross_ref_eqconsole(self,
                                      topt: TidyOption):  # The option.
        """Prints for XML an option's `<eqconfig>`."""
        topt_name = "%s:" % tidy.OptGetName(topt).decode("utf-8")
        hit: Tidy.CmdOptDesc = next((cdesc for cdesc in self.cmdopt_defs
                                     if cdesc.eqconfig is not None
                                        and cdesc.eqconfig.startswith(topt_name)), None)
        if hit:
            local_hit: Tidy.CmdOptDesc = copy.deepcopy(hit)
            self.localize_option_names(local_hit)

            print("  <eqconsole>%s</eqconsole>" % Tidy.get_escaped_name(local_hit.name1))
            if local_hit.name2 is not None:
                print("  <eqconsole>%s</eqconsole>" % Tidy.get_escaped_name(local_hit.name2))
            if local_hit.name3 is not None:
                print("  <eqconsole>%s</eqconsole>" % Tidy.get_escaped_name(local_hit.name3))
        else:
            print("  %s" % "  <eqconsole />")

    # @} end service_xml_config group

    # MARK: - Provide the -xml-error-strings Service
    # **************************************************************************** #
    # @defgroup service_xml_error_strings Provide the -xml-error-strings Service
    # **************************************************************************** #
    # @{

    def xml_error_strings(self):
        """Handles the -xml-error-strings service.

        This service is primarily helpful to developers who need to generate an
        updated list of strings to expect when using one of the message callbacks.
        Included in the output is the current string associated with the error
        symbol.
        """
        print('<?xml version="1.0"?>')
        print('<error_strings version="%s">' % self.library_version)

        j: TidyIterator = tidy.getErrorCodeList()
        while j:
            error_code: int  = tidy.getNextErrorCode(ct.byref(j))
            localized_string = tidy.LocalizedString(error_code)
            print(' <error_string>')
            print('  <name>%s</name>' %
                  tidy.ErrorCodeAsKey(error_code).decode("utf-8"))
            if localized_string is not None:
                print('  <string class="%s"><![CDATA[%s]]></string>' %
                      (tidy.GetLanguage().decode("utf-8"),
                       localized_string.decode("utf-8")))
            else:
                print('  <string class="%s">NULL</string>' %
                      tidy.GetLanguage().decode("utf-8"))
            print(' </error_string>')

        print('</error_strings>')

    # @} end service_xml_error_strings group

    # MARK: - Provide the -xml-help Service
    # **************************************************************************** #
    # @defgroup service_xmlhelp Provide the -xml-help Service
    # **************************************************************************** #
    # @{

    def xml_help(self):
        """Provides the -xml-help service."""

        print('<?xml version="1.0"?>\n'
              '<cmdline version="%s">' % self.library_version)

        for cdesc in self.cmdopt_defs:
            local_cdesc: Tidy.CmdOptDesc = copy.deepcopy(cdesc)
            self.localize_option_names(local_cdesc)

            print(' <option class="%s">' % self.cmdopt_catname[cdesc.categ]["mnemonic"])
            self.print_xml_help_option_element("name", local_cdesc.name1)
            self.print_xml_help_option_element("name", local_cdesc.name2)
            self.print_xml_help_option_element("name", local_cdesc.name3)
            description = tidy.LocalizedString(cdesc.key)
            self.print_xml_help_option_element("description", self.bytes2str(description))
            if cdesc.eqconfig is not None:
                self.print_xml_help_option_element("eqconfig", local_cdesc.eqconfig)
            else:
                print('  <eqconfig />')
            print(' </option>')

        print('</cmdline>')

    @staticmethod
    def print_xml_help_option_element(element: str,          # XML element name.
                                      name: str | None):  # The contents of the element.
        """Outputs an XML element for a CLI option, escaping special characters as required.

        For example, it might print `<name>-output &lt;file&gt;</name>`.
        """
        if name is None:
            return
        print('  <%s>%s</%s>' % (element, Tidy.get_escaped_name(name), element))

    # @} end service_xmlhelp group

    # MARK: - Provide the -xml-options-strings Service
    # **************************************************************************** #
    # @defgroup service_xml_opts_strings Provide the -xml-options-strings Service
    # **************************************************************************** #
    # @{

    def xml_options_strings(self):
        """Handles the -xml-options-strings service.

        This service is primarily helpful to developers and localizers to test
        that option description strings as represented on screen output are
        correct and do not break tidy.
        """
        print('<?xml version="1.0"?>\n'
              '<options_strings version="%s">' % self.library_version)

        self.for_each_option(self.print_XML_option_string)

        print('</options_strings>')

    def print_XML_option_string(self,
                                topt: TidyOption,   # The option.
                                desc: OptionDesc):  # The OptionDesc array.
        """Handles printing of option description for -xml-options-strings service."""
        if tidy.OptGetCategory(topt) == tidy.TidyInternalCategory:
            return

        doc = self.bytes2str(tidy.OptGetDoc(self.tdoc, topt))

        print(' <option>')
        print('  <name>%s</name>' % desc.name)
        print('  <string class="%s"><![CDATA[%s]]></string>' %
              (tidy.GetLanguage().decode("utf-8"), doc or ""))
        print(' </option>')

    # @} end service_xml_opts_strings group

    @staticmethod
    def localize_option_names(cdesc: CmdOptDesc):
        """Option names aren't localized, but the sample fields should be localized. \
        For example, `<file>` should be `<archivo>` in Spanish.

        @param cdesc A CmdOptDesc array with fields that must be localized.
        """
        file_string = Tidy.bytes2str(tidy.LocalizedString(cdesc.subkey))
        cdesc.name1 = Tidy.string_with_format(cdesc.name1, file_string)
        if cdesc.name2 is not None:
            cdesc.name2 = Tidy.string_with_format(cdesc.name2, file_string)
        if cdesc.name3 is not None:
            cdesc.name3 = Tidy.string_with_format(cdesc.name3, file_string)
        if cdesc.eqconfig is not None:
            cdesc.eqconfig = Tidy.string_with_format(cdesc.eqconfig, file_string)

    @staticmethod
    def string_with_format(fmt: str, *args) -> str:
        """Create a new string with a format an arguments."""
        try:
            return fmt % args
        except TypeError:
            return fmt

    # MARK: - Provide the -xml-strings Service
    # **************************************************************************** #
    # @defgroup service_xml_strings Provide the -xml-strings Service
    # **************************************************************************** #
    # @{

    def xml_strings(self):
        """Handles the -xml-strings service.

        This service was primarily helpful to developers and localizers to compare
        localized strings to the built in `en` strings. It's probably better to use
        our POT/PO workflow with your favorite tools, or simply diff the language
        header files directly.

        @note The attribute `id` is not a specification, promise, or part of an
              API. You must not depend on this value. For strings meant for error
              output, the `label` attribute will contain the stringified version of
              the internal key for the string.
        """
        current_language = tidy.GetLanguage().decode("utf-8")
        skip_current     = (current_language in ["en"])

        print('<?xml version="1.0"?>\n'
              '<localized_strings version="%s">' % self.library_version)

        j: TidyIterator = tidy.getStringKeyList()
        while j:
            i: int = tidy.getNextStringKey(ct.byref(j))
            current_label = tidy.ErrorCodeAsKey(i).decode("utf-8")
            if current_label == "UNDEFINED": current_label = ""
            default_string = tidy.DefaultString(i).decode("utf-8")
            print('<localized_string id="%u" label="%s">' %
                  (i, current_label))
            print(' <string class="%s">' % "en", end="")
            print("%s" % default_string, end="")
            print('</string>')
            if not skip_current:
                localized_string = tidy.LocalizedString(i).decode("utf-8")
                matches_base = (localized_string == default_string)
                print(' <string class="%s" same_as_base="%s">' %
                      (tidy.GetLanguage().decode("utf-8"),
                       ("yes" if matches_base else "no")), end="")
                print("%s" % localized_string, end="")
                print('</string>')
            print('</localized_string>')

        print('</localized_strings>')

    # @} end service_xml_strings group

    # MARK: - Output Helping Functions
    # **************************************************************************** #
    # @defgroup utilities_output Output Helping Functions
    # This group functions that aid the formatting of output.
    # **************************************************************************** #
    # @{

    def unknown_option(self,
                       c: str):  # The unknown option.
        """Provides the `unknown option` output to the current errout."""
        print(self.TC_STRING_UNKNOWN_OPTION % c[0], file=self.errout)

    # @} end utilities_output group

    @staticmethod
    def get_escaped_name(name: str) -> str:
        """Escape a name for XML output.

        For example, `-output <file>` becomes
        `-output &lt;file&gt;` for use in XML.

        @param name The option name to escape.
        @result Returns an allocated string.
        """
        # TODO: !!! better performance with table translate, orreplace !!!
        escp_name = ""
        for ch in name:
            if ch == "<":
                escp_name += "&lt;"
            elif ch == ">":
                escp_name += "&gt;"
            elif ch == '"':
                escp_name += "&quot;"
            else:
                escp_name += ch
        return escp_name

    @staticmethod
    def bytes2str(buffer: bytes | None, encoding="utf8") -> str | None:
        return buffer.decode(encoding) if buffer is not None else None

    @staticmethod
    def str2bytes(string: str | None, encoding="utf8") -> bytes | None:
        return string.encode(encoding) if string is not None else None

    @staticmethod
    def strlen(str):  # noqa: A002
        bstr = bytes(str)
        try:
            return bstr.index(b'\0')
        except ValueError:
            return len(bstr)

# MARK: - Experimental Stuff
# **************************************************************************** #
# @defgroup experimental_stuff Experimental Stuff
# From time to time the developers might leave stuff here that you can use
# to experiment on their own, or that they're using to experiment with.
# **************************************************************************** #
# @{

@tidy.TidyMessageCallback
def report_callback(tmessage: tidy.TidyMessage) -> bool:
    """This callback from LibTidy allows the console application to examine an \
    error message before allowing LibTidy to display it.

    Currently the body of the function is not compiled into Tidy, but if you're
    interested in how to use the new message API, then enable it.
    Possible applications in future console Tidy might be to do things like:
    - allow user-defined filtering
    - sort the report output by line number
    - other things that are user facing and best not put into LibTidy
      proper.
    """
    if 0:
        print("FILTER: %s\n%s\n%s" %
              (tidy.GetMessageKey(tmessage).decode("utf-8"),
               tidy.GetMessageOutput(tmessage).decode("utf-8"),
               tidy.GetMessageOutputDefault(tmessage).decode("utf-8")))

        # loop through the arguments, if any, and print their details
        it: TidyIterator = tidy.GetMessageArguments(tmessage)
        while it:
            arg: tidy.TidyMessageArgument = tidy.GetNextMessageArgument(tmessage,
                                                                        ct.byref(it))
            message_type: tidy.TidyFormatParameterType = tidy.GetArgType(tmessage,
                                                                         ct.byref(arg))
            message_format: str = tidy.GetArgFormat(tmessage,
                                                    ct.byref(arg)).decode("utf-8")
            print("  Type = %u, Format = %s, Value = " %
                  (message_type, message_format), end="")
            if message_type == tidy.TidyFormatType_STRING:
                print("%s" % tidy.GetArgValueString(tmessage,
                                                    ct.byref(arg)).decode("utf-8"))
            elif message_type == tidy.TidyFormatType_INT:
                print("%d" % tidy.GetArgValueInt(tmessage, ct.byref(arg)))
            elif message_type == tidy.TidyFormatType_UINT:
                print("%u" % tidy.GetArgValueUInt(tmessage, ct.byref(arg)))
            elif message_type == tidy.TidyFormatType_DOUBLE:
                print("%g" % tidy.GetArgValueDouble(tmessage, ct.byref(arg)))
            else:
                print("%s" % "unknown so far")

        return False  # suppress LibTidy's own output of this message
    else:
        return True   # needed so Tidy will not block output of this message

# @} end experimental_stuff group

# MARK: - Miscellaneous Utilities
# **************************************************************************** #
# @defgroup utilities_misc Miscellaneous Utilities
# This group contains general utilities used in the console application.
# **************************************************************************** #
# @{

def samefile(filename1: str,           # First filename
             filename2: str) -> bool:  # Second filename
    """Indicates whether or not two filenames are the same.

    @result Returns a bool indicating whether the filenames are the same.
    """
    return ((filename1 == filename2)
            if tidy.FILENAMES_CASE_SENSITIVE else
            (filename1.lower() == filename2.lower()))

def tidy_cleanup():
    """Handles exit cleanup."""
    if is_windows:
        # Restore original Windows code page.
        if not win32.SetConsoleOutputCP(win_cp):
            raise ct.WinError(win32.GetLastError())
    # endif

# @} end utilities_misc group

# MARK: - main()
# **************************************************************************** #
# @defgroup main Main
# Let's do something here!
# **************************************************************************** #
# @{

# NOK
def main(argv=sys.argv[1:]):

    prog = sys.argv[0]

    status: int = 0

    content_errors   = 0
    content_warnings = 0
    access_warnings  = 0

    err_file: str | None = None

    if defined("ENABLE_DEBUG_LOG") and is_windows and defined("_CRTDBG_MAP_ALLOC"):
        _CrtSetDbgFlag(_CRTDBG_ALLOC_MEM_DF | _CRTDBG_LEAK_CHECK_DF)  # noqa: F821
    # endif

    tapp = Tidy()
    tapp.errout = sys.stderr  # initialize to stderr

    tidy.SetMessageCallback(tapp.tdoc, report_callback)  # experimental
    # Set an atexit handler.
    atexit.register(tidy_cleanup)

    if is_windows:
        # Force Windows console to use UTF, otherwise many characters will
        # be garbage. Note that East Asian languages *are* supported, but
        # only when Windows OS locale (not console only!) is set to an
        # East Asian language.
        global win_cp
        win_cp = win32.GetConsoleOutputCP()
        if not win32.SetConsoleOutputCP(win32.CP_UTF8):
            raise ct.WinError(win32.GetLastError())
    # endif

    # Look for default configuration files using any of
    # the following possibilities:
    #  - TIDY_CONFIG_FILE - from tidyplatform.h, typically /etc/tidy.conf
    #  - HTML_TIDY        - environment variable
    #  - TIDY_USER_CONFIG_FILE - from tidyplatform.h, typically ~/tidy.conf

    if (hasattr(tidy, "TIDY_CONFIG_FILE")
       and tidy.FileExists(tapp.tdoc, tidy.TIDY_CONFIG_FILE)):
        status = tidy.LoadConfig(tapp.tdoc, tidy.TIDY_CONFIG_FILE)
        if status != 0:
            print(tapp.TC_MAIN_ERROR_LOAD_CONFIG %
                  (tidy.TIDY_CONFIG_FILE, status), file=tapp.errout)

    cfg_file = os.environ.get("HTML_TIDY")
    if cfg_file is not None:
        status = tidy.LoadConfig(tapp.tdoc, tapp.str2bytes(cfg_file))
        if status != 0:
            print(tapp.TC_MAIN_ERROR_LOAD_CONFIG %
                  (cfg_file, status), file=tapp.errout)
    elif (hasattr(tidy, "TIDY_USER_CONFIG_FILE")
         and tidy.FileExists(tapp.tdoc, tidy.TIDY_USER_CONFIG_FILE)):
        status = tidy.LoadConfig(tapp.tdoc, tidy.TIDY_USER_CONFIG_FILE)
        if status != 0:
            print(tapp.TC_MAIN_ERROR_LOAD_CONFIG %
                  (tidy.TIDY_USER_CONFIG_FILE, status), file=tapp.errout)

    #
    # Read command line
    #

    while True:

        if argv and argv[0].startswith("-"):

            # support -foo and --foo
            arg  = argv[0]
            arg1 = argv[1] if len(argv) >= 2 else None
            opt  = arg.lower()

            if opt in ["-xml"]:

                tidy.OptSetBool(tapp.tdoc, tidy.TidyXmlTags, True)

            elif opt in ["-asxml", "-asxhtml"]:

                tidy.OptSetBool(tapp.tdoc, tidy.TidyXhtmlOut, True)

            elif opt in ["-ashtml"]:

                tidy.OptSetBool(tapp.tdoc, tidy.TidyHtmlOut, True)

            elif opt in ["-indent"]:

                tidy.OptSetInt(tapp.tdoc, tidy.TidyIndentContent, tidy.TidyAutoState)
                if tidy.OptGetInt(tapp.tdoc, tidy.TidyIndentSpaces) == 0:
                    tidy.OptResetToDefault(tapp.tdoc, tidy.TidyIndentSpaces)

            elif opt in ["-omit"]:

                tidy.OptSetBool(tapp.tdoc, tidy.TidyOmitOptionalTags, True)

            elif opt in ["-upper"]:

                tidy.OptSetBool(tapp.tdoc, tidy.TidyUpperCaseTags, True)

            elif opt in ["-clean"]:

                tidy.OptSetBool(tapp.tdoc, tidy.TidyMakeClean, True)

            elif opt in ["-gdoc"]:

                tidy.OptSetBool(tapp.tdoc, tidy.TidyGDocClean, True)

            elif opt in ["-bare"]:

                tidy.OptSetBool(tapp.tdoc, tidy.TidyMakeBare, True)

            elif opt in ["-raw", "-ascii", "-latin0", "-latin1", "-utf8",
                         # ifndef NO_NATIVE_ISO2022_SUPPORT
                         "-iso2022",
                         # endif
                         "-utf16le", "-utf16be", "-utf16", "-shiftjis",
                         "-big5", "-mac", "-win1252", "-ibm858"]:

                tidy.SetCharEncoding(tapp.tdoc, opt[1:])

            elif opt in ["-numeric"]:

                tidy.OptSetBool(tapp.tdoc, tidy.TidyNumEntities, True)

            elif opt in ["-modify",
                         "-change",   # obsolete
                         "-update"]:  # obsolete

                tidy.OptSetBool(tapp.tdoc, tidy.TidyWriteBack, True)

            elif opt in ["-errors"]:

                tidy.OptSetBool(tapp.tdoc, tidy.TidyShowMarkup, False)

            elif opt in ["-quiet"]:

                tidy.OptSetBool(tapp.tdoc, tidy.TidyQuiet, True)

            # Currently user must specify a language
            # prior to anything that causes output
            elif opt in ["-language", "-lang"]:

                if arg1 is not None:
                    if arg1.lower() == "help":
                        tapp.lang_help()
                        return 0
                    ok = tidy.SetLanguage(tapp.str2bytes(arg1))
                    if not ok:
                        print(tapp.TC_STRING_LANG_NOT_FOUND %
                              (arg1, tidy.GetLanguage().decode("utf-8")))
                    else:
                        tapp.set_localized_strings()
                    argv = argv[1:]
                else:
                    print("%s" % tapp.TC_STRING_LANG_MUST_SPECIFY)

            elif opt in ["-help", "--help", "-h"] or opt.startswith("-?"):

                tapp.help(prog)
                return 0  # success

            elif opt in ["-xml-help"]:

                tapp.xml_help()
                return 0  # success

            elif opt in ["-xml-error-strings"]:

                tapp.xml_error_strings()
                return 0  # success

            elif opt in ["-xml-options-strings"]:

                tapp.xml_options_strings()
                return 0  # success

            elif opt in ["-xml-strings"]:

                tapp.xml_strings()
                return 0  # success

            elif opt in ["-help-config"]:

                tapp.option_help()
                return 0  # success

            elif opt in ["-help-env"]:

                tapp.help_env()
                return 0  # success

            elif opt in ["-help-option"]:

                if arg1 is not None:
                    tapp.option_describe(arg1)
                else:
                    print("%s" % tapp.TC_STRING_MUST_SPECIFY)
                return 0  # success

            elif opt in ["-xml-config"]:

                tapp.XML_option_help()
                return 0  # success

            elif opt in ["-show-config"]:

                tapp.option_values()
                return 0  # success

            elif opt in ["-export-config"]:

                tapp.export_option_values()
                return 0  # success

            elif opt in ["-export-default-config"]:

                tapp.export_default_option_values()
                return 0  # success

            elif opt in ["-config"]:

                if arg1 is not None:
                    tidy.LoadConfig(tapp.tdoc, tapp.str2bytes(arg1))
                    # Set new error output stream if setting changed
                    post = tidy.OptGetValue(tapp.tdoc, tidy.TidyErrFile)
                    if post is not None and (err_file is None
                       or not samefile(err_file, post.decode("utf-8"))):
                        err_file = post.decode("utf-8")
                        errout = tidy.SetErrorFile(tapp.tdoc,  # noqa: F841 !!!
                                                   tapp.str2bytes(err_file))
                    argv = argv[1:]

            elif opt in ["-output", "--output-file", "-o"]:

                if arg1 is not None:
                    tidy.OptSetValue(tapp.tdoc, tidy.TidyOutFile, tapp.str2bytes(arg1))
                    argv = argv[1:]

            elif opt in ["-file", "--file", "-f"]:

                if arg1 is not None:
                    err_file = arg1
                    errout = tidy.SetErrorFile(tapp.tdoc,  # noqa: F841 !!!
                                               tapp.str2bytes(err_file))
                    argv = argv[1:]

            elif opt in ["-wrap", "--wrap", "-w"]:

                if arg1 is not None:
                    try:
                        wrap_len = int(arg1)
                    except ValueError:
                        wrap_len = 0
                    else:
                        argv = argv[1:]
                    tidy.OptSetInt(tapp.tdoc, tidy.TidyWrapLen, wrap_len)

            elif opt in ["-version", "--version", "-v"]:

                tapp.version()
                return 0  # success

            elif opt.startswith("--"):

                if tidy.OptParseValue(tapp.tdoc, arg[2:].encode("utf-8"),
                                      arg1.encode("utf-8") if arg1 is not None else None):
                    # Set new error output stream if setting changed
                    post = tidy.OptGetValue(tapp.tdoc, tidy.TidyErrFile)
                    if post is not None and (err_file is None
                       or not samefile(err_file, post.decode("utf-8"))):
                        err_file = post.decode("utf-8")
                        errout = tidy.SetErrorFile(tapp.tdoc,  # noqa: F841 !!!
                                                   tapp.str2bytes(err_file))
                    argv = argv[1:]

            elif opt in ["-access"]:

                if arg1 is not None:
                    try:
                        acc_level = int(arg1)
                    except ValueError:
                        acc_level = 0
                    else:
                        argv = argv[1:]
                    tidy.OptSetInt(tapp.tdoc, tidy.TidyAccessibilityCheckLevel, acc_level)

            else:

                for c in arg[1:]:  # while ( (c = *++s) != '\0' )
                    if c == "i":
                        tidy.OptSetInt(tapp.tdoc, tidy.TidyIndentContent, tidy.TidyAutoState)
                        if tidy.OptGetInt(tapp.tdoc, tidy.TidyIndentSpaces) == 0:
                            tidy.OptResetToDefault(tapp.tdoc, tidy.TidyIndentSpaces)
                    elif c == "u":
                        tidy.OptSetBool(tapp.tdoc, tidy.TidyUpperCaseTags, True)
                    elif c == "c":
                        tidy.OptSetBool(tapp.tdoc, tidy.TidyMakeClean, True)
                    elif c == "g":
                        tidy.OptSetBool(tapp.tdoc, tidy.TidyGDocClean, True)
                    elif c == "b":
                        tidy.OptSetBool(tapp.tdoc, tidy.TidyMakeBare, True)
                    elif c == "n":
                        tidy.OptSetBool(tapp.tdoc, tidy.TidyNumEntities, True)
                    elif c == "m":
                        tidy.OptSetBool(tapp.tdoc, tidy.TidyWriteBack, True)
                    elif c == "e":
                        tidy.OptSetBool(tapp.tdoc, tidy.TidyShowMarkup, False)
                    elif c == "q":
                        tidy.OptSetBool(tapp.tdoc, tidy.TidyQuiet, True)
                    else:
                        tapp.unknown_option(c)

            argv = argv[1:]
            continue

        if argv:
            html_file = argv[0]
            if defined("ENABLE_DEBUG_LOG"):
                sprtf("Tidy: '%s'" % html_file)
            else:  # not ENABLE_DEBUG_LOG #
                # Is #713 - show-filename option
                if tidy.OptGetBool(tapp.tdoc, tidy.TidyShowFilename):
                    print("Tidy: '%s'" % html_file, file=tapp.errout)
            # endif # ENABLE_DEBUG_LOG yes/no #
            if (tidy.OptGetBool(tapp.tdoc, tidy.TidyEmacs)
               or tidy.OptGetBool(tapp.tdoc, tidy.TidyShowFilename)):
                tidy.SetEmacsFile(tapp.tdoc, tapp.str2bytes(html_file))

            status = tidy.ParseFile(tapp.tdoc, tapp.str2bytes(html_file))
        else:
            html_file = "stdin"  # ??? !!!
            status = tidy.ParseStdin(tapp.tdoc)

        if status >= 0:
            status = tidy.CleanAndRepair(tapp.tdoc)

        if status >= 0:
            status = tidy.RunDiagnostics(tapp.tdoc)
        if status > 1:  # If errors, do we want to force output?
            if not tidy.OptGetBool(tapp.tdoc, tidy.TidyForceOutput):
                status = -1

        if status >= 0 and tidy.OptGetBool(tapp.tdoc, tidy.TidyShowMarkup):
            if tidy.OptGetBool(tapp.tdoc, tidy.TidyWriteBack) and argv:
                status = tidy.SaveFile(tapp.tdoc, tapp.str2bytes(html_file))
            else:
                out_file = tidy.OptGetValue(tapp.tdoc, tidy.TidyOutFile)
                if out_file is not None:
                    status = tidy.SaveFile(tapp.tdoc, out_file)
                else:
                    if defined("ENABLE_DEBUG_LOG"):
                        out_file = "%s.html" % get_log_file()  # noqa: F821
                        status = tidy.SaveFile(tapp.tdoc, tapp.str2bytes(out_file))
                        sprtf("Saved tidied content to '%s'" % out_file)
                    else:
                        status = tidy.SaveStdout(tapp.tdoc)
                    # endif

        content_errors   += tidy.ErrorCount(tapp.tdoc)
        content_warnings += tidy.WarningCount(tapp.tdoc)
        access_warnings  += tidy.AccessWarningCount(tapp.tdoc)

        argv = argv[1:]
        if not argv: break

    # end of read command line loop

    # blank line for screen formatting
    if (tapp.errout is sys.stderr and content_errors == 0
       and not tidy.OptGetBool(tapp.tdoc, tidy.TidyQuiet)):
        print(file=tapp.errout)

    # footnote printing only if errors or warnings
    if content_errors + content_warnings > 0:
        tidy.ErrorSummary(tapp.tdoc)

    # prints the general info, if applicable
    tidy.GeneralInfo(tapp.tdoc)

    # called to free hash tables etc.
    tidy.Release(tapp.tdoc)

    # return status can be used by scripts
    if content_errors > 0:
        return 2
    elif content_warnings > 0:
        return 1
    else:
        # 0 signifies all is ok
        return 0

# @} end main group

# @} end console_application group


if __name__.rpartition(".")[-1] == "__main__":
    sys.exit(main())
