# **************************************************************************** #
# @file
# Separated public enumerations header providing important indentifiers for
# LibTidy and internal users, as well as code-generator macros used to
# generate many of them.
#
# The use of enums simplifies enum re-use in various wrappers, e.g. SWIG,
# generated wrappers, and COM IDL files.
#
# This file also contains macros to generate additional enums for use in
# Tidy's language localizations and/or to access Tidy's strings via the API.
# See detailed information elsewhere in this file's documentation.
#
# @note LibTidy does *not* guarantee the value of any enumeration member,
# including the starting integer value, except where noted. Always use enum
# members rather than their values!
#
# Enums that have starting values have starting values for a good reason,
# mainly to prevent string key overlap.
#
# @author  Dave Raggett [dsr@w3.org]
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

# MARK: - Public Enumerations
# **************************************************************************** #
# @defgroup public_enumerations Public Enumerations
# @ingroup public_api
#
# @copybrief tidyenum.h
# **************************************************************************** #

# @addtogroup public_enumerations

# @name Configuration Options Enumerations
#
# These enumerators are used to define available configuration options and
# their option categories.

# Option IDs are used used to get and/or set configuration option values and
#        retrieve their descriptions.
#
# @remark These enum members all have associated localized strings available
#         which describe the purpose of the option. These descriptions are
#         available via their enum values only.
#
# @sa     `config.c:option_defs[]` for internal implementation details; that
#         array is where you will implement options defined in this enum; and
#         it's important to add a string describing the option to
#         `language_en.h`, too.
#
TidyOptionId = ct.c_int
(
    TidyUnknownOption,       # Unknown option!

    TidyAccessibilityCheckLevel,  # Accessibility check level
    TidyAltText,             # Default text for alt attribute
    TidyAnchorAsName,        # Define anchors as name attributes
    TidyAsciiChars,          # Convert quotes and dashes to nearest ASCII char
    TidyBlockTags,           # Declared block tags
    TidyBodyOnly,            # Output BODY content only
    TidyBreakBeforeBR,       # Output newline before <br> or not?
    TidyCharEncoding,        # In/out character encoding
    TidyCoerceEndTags,       # Coerce end tags from start tags where probably intended
    TidyCSSPrefix,           # CSS class naming for clean option
    # ifndef DOXYGEN_SHOULD_SKIP_THIS
    TidyCustomTags,          # Internal use ONLY
    # endif
    TidyDecorateInferredUL,  # Mark inferred UL elements with no indent CSS
    TidyDoctype,             # User specified doctype
    # ifndef DOXYGEN_SHOULD_SKIP_THIS
    TidyDoctypeMode,         # Internal use ONLY
    # endif
    TidyDropEmptyElems,      # Discard empty elements
    TidyDropEmptyParas,      # Discard empty p elements
    TidyDropPropAttrs,       # Discard proprietary attributes
    TidyDuplicateAttrs,      # Keep first or last duplicate attribute
    TidyEmacs,               # If true, format error output for GNU Emacs
    # ifndef DOXYGEN_SHOULD_SKIP_THIS
    TidyEmacsFile,           # Internal use ONLY
    # endif
    TidyEmptyTags,           # Declared empty tags
    TidyEncloseBlockText,    # If yes text in blocks is wrapped in P's
    TidyEncloseBodyText,     # If yes text at body is wrapped in P's
    TidyErrFile,             # File name to write errors to
    TidyEscapeCdata,         # Replace <![CDATA[]]> sections with escaped text
    TidyEscapeScripts,       # Escape items that look like closing tags in script tags
    TidyFixBackslash,        # Fix URLs by replacing \ with /
    TidyFixComments,         # Fix comments with adjacent hyphens
    TidyFixUri,              # Applies URI encoding if necessary
    TidyForceOutput,         # Output document even if errors were found
    TidyGDocClean,           # Clean up HTML exported from Google Docs
    TidyHideComments,        # Hides all (real) comments in output
    TidyHtmlOut,             # Output plain HTML, even for XHTML input.
    TidyInCharEncoding,      # Input character encoding (if different)
    TidyIndentAttributes,    # Newline+indent before each attribute
    TidyIndentCdata,         # Indent <!CDATA[ ... ]]> section
    TidyIndentContent,       # Indent content of appropriate tags
    TidyIndentSpaces,        # Indentation n spaces/tabs
    TidyInlineTags,          # Declared inline tags
    TidyJoinClasses,         # Join multiple class attributes
    TidyJoinStyles,          # Join multiple style attributes
    TidyKeepFileTimes,       # If yes last modied time is preserved
    TidyKeepTabs,            # If yes keep input source tabs
    TidyLiteralAttribs,      # If true attributes may use newlines
    TidyLogicalEmphasis,     # Replace i by em and b by strong
    TidyLowerLiterals,       # Folds known attribute values to lower case
    TidyMakeBare,            # Replace smart quotes, em dashes, etc with ASCII
    TidyMakeClean,           # Replace presentational clutter by style rules
    TidyMark,                # Add meta element indicating tidied doc
    TidyMergeDivs,           # Merge multiple DIVs
    TidyMergeEmphasis,       # Merge nested B and I elements
    TidyMergeSpans,          # Merge multiple SPANs
    TidyMetaCharset,         # Adds/checks/fixes meta charset in the head, based on document type
    TidyMuteReports,         # Filter these messages from output.
    TidyMuteShow,            # Show message ID's in the error table
    TidyNCR,                 # Allow numeric character references
    TidyNewline,             # Output line ending (default to platform)
    TidyNumEntities,         # Use numeric entities
    TidyOmitOptionalTags,    # Suppress optional start tags and end tags
    TidyOutCharEncoding,     # Output character encoding (if different)
    TidyOutFile,             # File name to write markup to
    TidyOutputBOM,           # Output a Byte Order Mark (BOM) for UTF-16 encodings
    TidyPPrintTabs,          # Indent using tabs instead of spaces
    TidyPreserveEntities,    # Preserve entities
    TidyPreTags,             # Declared pre tags
    TidyPriorityAttributes,  # Attributes to place first in an element
    TidyPunctWrap,           # consider punctuation and breaking spaces for wrapping
    TidyQuiet,               # No 'Parsing X', guessed DTD or summary
    TidyQuoteAmpersand,      # Output naked ampersand as &amp;
    TidyQuoteMarks,          # Output " marks as &quot;
    TidyQuoteNbsp,           # Output non-breaking space as entity
    TidyReplaceColor,        # Replace hex color attribute values with names
    TidyShowErrors,          # Number of errors to put out
    TidyShowFilename,        # If true, the input filename is displayed with the error messages
    TidyShowInfo,            # If true, info-level messages are shown
    TidyShowMarkup,          # If false, normal output is suppressed
    TidyShowMetaChange,      # show when meta http-equiv content charset was changed - compatib.
    TidyShowWarnings,        # However errors are always shown
    TidySkipNested,          # Skip nested tags in script and style CDATA
    TidySortAttributes,      # Sort attributes
    TidyStrictTagsAttr,      # Ensure tags and attributes match output HTML version
    TidyStyleTags,           # Move style to head
    TidyTabSize,             # Expand tabs to n spaces
    TidyUpperCaseAttrs,      # Output attributes in upper not lower case
    TidyUpperCaseTags,       # Output tags in upper not lower case
    TidyUseCustomTags,       # Enable Tidy to use autonomous custom tags
    TidyVertSpace,           # degree to which markup is spread out vertically
    TidyWarnPropAttrs,       # Warns on proprietary attributes
    TidyWord2000,            # Draconian cleaning for Word2000
    TidyWrapAsp,             # Wrap within ASP pseudo elements
    TidyWrapAttVals,         # Wrap within attribute values
    TidyWrapJste,            # Wrap within JSTE pseudo elements
    TidyWrapLen,             # Wrap margin
    TidyWrapPhp,             # Wrap consecutive PHP pseudo elements
    TidyWrapScriptlets,      # Wrap within JavaScript string literals
    TidyWrapSection,         # Wrap within <![ ... ]> section tags
    TidyWriteBack,           # If true then output tidied markup
    TidyXhtmlOut,            # Output extensible HTML
    TidyXmlDecl,             # Add <?xml?> for XML docs
    TidyXmlOut,              # Create output as XML
    TidyXmlPIs,              # If set to yes PIs must end with ?>
    TidyXmlSpace,            # If set to yes adds xml:space attr as needed
    TidyXmlTags,             # Treat input as XML
    N_TIDY_OPTIONS           # Must be last

) = range(0, 105)

# Categories of Tidy configuration options, which are used mostly by user
# interfaces to sort Tidy options into related groups.
#
# @remark These enum members all have associated localized strings available
#         suitable for use as a category label, and are available with either
#         the enum value, or a string version of the name.
#
# @sa     `config.c:option_defs[]` for internal implementation details.
#
TidyConfigCategory = ct.c_int
(
    TidyUnknownCategory,   # Unknown Category!
    # Codes for populating TidyConfigCategory enumeration.
    TidyDiagnostics,       # Diagnostics
    TidyDisplay,           # Affecting screen display
    TidyDocumentIO,        # Pertaining to document I/O
    TidyEncoding,          # Relating to encoding
    TidyFileIO,            # Pertaining to file I/O
    TidyMarkupCleanup,     # Cleanup related options
    TidyMarkupEntities,    # Entity related options
    TidyMarkupRepair,      # Document repair related options
    TidyMarkupTeach,       # Teach tidy new things
    TidyMarkupXForm,       # Transform HTML one way or another
    TidyPrettyPrint,       # Pretty printing options
    TidyInternalCategory,  # Option is internal only.

) = range(300, 300 + 13)

# A Tidy configuration option can have one of these data types.
#
TidyOptionType = ct.c_int
(
    TidyString,   # String
    TidyInteger,  # Integer or enumeration
    TidyBoolean,  # Boolean

) = range(0, 3)

# @name Configuration Options Pick List and Parser Enumerations
#
# These enums define enumerated states for the configuration options that
# take values that are not simple yes/no, strings, or simple integers.

# AutoBool values used by ParseBool, ParseTriState, ParseIndent, ParseBOM
# @remark This enum's starting value is guaranteed to remain stable.
#
TidyTriState = ct.c_int
(
    TidyNoState,    # maps to 'no'
    TidyYesState,   # maps to 'yes'
    TidyAutoState,  # Automatic

) = range(0, 3)

# Values used by ParseUseCustomTags, which describes how Autonomous Custom
# tags (ACT's) found by Tidy are treated.
#
# @remark These enum members all have associated localized strings available
#         for internal LibTidy use, and also have public string keys in the
#         form MEMBER_STRING, e.g., TIDYCUSTOMBLOCKLEVEL_STRING
#
# @remark This enum's starting value is guaranteed to remain stable.
#
TidyUseCustomTagsState = ct.c_int
(
    TidyCustomNo,          # Do not allow autonomous custom tags
    TidyCustomBlocklevel,  # ACT's treated as blocklevel
    TidyCustomEmpty,       # ACT's treated as empty tags
    TidyCustomInline,      # ACT's treated as inline tags
    TidyCustomPre,         # ACT's treated as pre tags

) = range(0, 5)

# TidyNewline option values to control output line endings.
# @remark This enum's starting value is guaranteed to remain stable.
#
TidyLineEnding = ct.c_int
(
    TidyLF,    # Use Unix style: LF
    TidyCRLF,  # Use DOS/Windows style: CR+LF
    TidyCR,    # Use Macintosh style: CR

) = range(0, 3)

# TidyEncodingOptions option values specify the input and/or output encoding.
# @remark This enum's starting value is guaranteed to remain stable.
#
TidyEncodingOptions = ct.c_int
(
    TidyEncRaw,
    TidyEncAscii,
    TidyEncLatin0,
    TidyEncLatin1,
    TidyEncUtf8,
    # ifndef NO_NATIVE_ISO2022_SUPPORT
    TidyEncIso2022,
    # endif
    TidyEncMac,
    TidyEncWin1252,
    TidyEncIbm858,
    TidyEncUtf16le,
    TidyEncUtf16be,
    TidyEncUtf16,
    TidyEncBig5,
    TidyEncShiftjis,

) = range(0, 14)

# Mode controlling treatment of doctype
# @remark This enum's starting value is guaranteed to remain stable.
#
TidyDoctypeModes = ct.c_int
(
    TidyDoctypeHtml5,   # <!DOCTYPE html>
    TidyDoctypeOmit,    # Omit DOCTYPE altogether
    TidyDoctypeAuto,    # Keep DOCTYPE in input.  Set version to content
    TidyDoctypeStrict,  # Convert document to HTML 4 strict content model
    TidyDoctypeLoose,   # Convert document to HTML 4 transitional content model
    TidyDoctypeUser,    # Set DOCTYPE FPI explicitly

) = range(0, 6)

# Mode controlling treatment of duplicate Attributes
# @remark This enum's starting value is guaranteed to remain stable.
#
TidyDupAttrModes = ct.c_int
(
    TidyKeepFirst,  # Keep the first instance of an attribute
    TidyKeepLast,   # Keep the last instance of an attribute

) = range(0, 2)

# Mode controlling treatment of sorting attributes
# @remark This enum's starting value is guaranteed to remain stable.
#
TidyAttrSortStrategy = ct.c_int
(
    TidySortAttrNone,   # Don't sort attributes
    TidySortAttrAlpha,  # Sort attributes alphabetically

) = range(0, 2)

# Mode controlling capitalization of things, such as attributes.
# @remark This enum's starting value is guaranteed to remain stable.
#
TidyUppercase = ct.c_int
(
    TidyUppercaseNo,        # Don't uppercase.
    TidyUppercaseYes,       # Do uppercase.
    TidyUppercasePreserve,  # Preserve case.

) = range(0, 3)

#
# @name Document Tree
#

# Node types
#
TidyNodeType = ct.c_int
(
    TidyNode_Root,      # Root
    TidyNode_DocType,   # DOCTYPE
    TidyNode_Comment,   # Comment
    TidyNode_ProcIns,   # Processing Instruction
    TidyNode_Text,      # Text
    TidyNode_Start,     # Start Tag
    TidyNode_End,       # End Tag
    TidyNode_StartEnd,  # Start/End (empty) Tag
    TidyNode_CDATA,     # Unparsed Text
    TidyNode_Section,   # XML Section
    TidyNode_Asp,       # ASP Source
    TidyNode_Jste,      # JSTE Source
    TidyNode_Php,       # PHP Source
    TidyNode_XmlDecl,   # XML Declaration

) = range(0, 14)

# Known HTML element types
#
TidyTagId = ct.c_int
(
    TidyTag_UNKNOWN,     # Unknown tag! Must be first
    TidyTag_A,           # A
    TidyTag_ABBR,        # ABBR
    TidyTag_ACRONYM,     # ACRONYM
    TidyTag_ADDRESS,     # ADDRESS
    TidyTag_ALIGN,       # ALIGN
    TidyTag_APPLET,      # APPLET
    TidyTag_AREA,        # AREA
    TidyTag_B,           # B
    TidyTag_BASE,        # BASE
    TidyTag_BASEFONT,    # BASEFONT
    TidyTag_BDO,         # BDO
    TidyTag_BGSOUND,     # BGSOUND
    TidyTag_BIG,         # BIG
    TidyTag_BLINK,       # BLINK
    TidyTag_BLOCKQUOTE,  # BLOCKQUOTE
    TidyTag_BODY,        # BODY
    TidyTag_BR,          # BR
    TidyTag_BUTTON,      # BUTTON
    TidyTag_CAPTION,     # CAPTION
    TidyTag_CENTER,      # CENTER
    TidyTag_CITE,        # CITE
    TidyTag_CODE,        # CODE
    TidyTag_COL,         # COL
    TidyTag_COLGROUP,    # COLGROUP
    TidyTag_COMMENT,     # COMMENT
    TidyTag_DD,          # DD
    TidyTag_DEL,         # DEL
    TidyTag_DFN,         # DFN
    TidyTag_DIR,         # DIR
    TidyTag_DIV,         # DIF
    TidyTag_DL,          # DL
    TidyTag_DT,          # DT
    TidyTag_EM,          # EM
    TidyTag_EMBED,       # EMBED
    TidyTag_FIELDSET,    # FIELDSET
    TidyTag_FONT,        # FONT
    TidyTag_FORM,        # FORM
    TidyTag_FRAME,       # FRAME
    TidyTag_FRAMESET,    # FRAMESET
    TidyTag_H1,          # H1
    TidyTag_H2,          # H2
    TidyTag_H3,          # H3
    TidyTag_H4,          # H4
    TidyTag_H5,          # H5
    TidyTag_H6,          # H6
    TidyTag_HEAD,        # HEAD
    TidyTag_HR,          # HR
    TidyTag_HTML,        # HTML
    TidyTag_I,           # I
    TidyTag_IFRAME,      # IFRAME
    TidyTag_ILAYER,      # ILAYER
    TidyTag_IMG,         # IMG
    TidyTag_INPUT,       # INPUT
    TidyTag_INS,         # INS
    TidyTag_ISINDEX,     # ISINDEX
    TidyTag_KBD,         # KBD
    TidyTag_KEYGEN,      # KEYGEN
    TidyTag_LABEL,       # LABEL
    TidyTag_LAYER,       # LAYER
    TidyTag_LEGEND,      # LEGEND
    TidyTag_LI,          # LI
    TidyTag_LINK,        # LINK
    TidyTag_LISTING,     # LISTING
    TidyTag_MAP,         # MAP
    TidyTag_MATHML,      # MATH  (HTML5) [i_a]2 MathML embedded in [X]HTML
    TidyTag_MARQUEE,     # MARQUEE
    TidyTag_MENU,        # MENU
    TidyTag_META,        # META
    TidyTag_MULTICOL,    # MULTICOL
    TidyTag_NOBR,        # NOBR
    TidyTag_NOEMBED,     # NOEMBED
    TidyTag_NOFRAMES,    # NOFRAMES
    TidyTag_NOLAYER,     # NOLAYER
    TidyTag_NOSAVE,      # NOSAVE
    TidyTag_NOSCRIPT,    # NOSCRIPT
    TidyTag_OBJECT,      # OBJECT
    TidyTag_OL,          # OL
    TidyTag_OPTGROUP,    # OPTGROUP
    TidyTag_OPTION,      # OPTION
    TidyTag_P,           # P
    TidyTag_PARAM,       # PARAM
    TidyTag_PICTURE,     # PICTURE (HTML5)
    TidyTag_PLAINTEXT,   # PLAINTEXT
    TidyTag_PRE,         # PRE
    TidyTag_Q,           # Q
    TidyTag_RB,          # RB
    TidyTag_RBC,         # RBC
    TidyTag_RP,          # RP
    TidyTag_RT,          # RT
    TidyTag_RTC,         # RTC
    TidyTag_RUBY,        # RUBY
    TidyTag_S,           # S
    TidyTag_SAMP,        # SAMP
    TidyTag_SCRIPT,      # SCRIPT
    TidyTag_SELECT,      # SELECT
    TidyTag_SERVER,      # SERVER
    TidyTag_SERVLET,     # SERVLET
    TidyTag_SMALL,       # SMALL
    TidyTag_SPACER,      # SPACER
    TidyTag_SPAN,        # SPAN
    TidyTag_STRIKE,      # STRIKE
    TidyTag_STRONG,      # STRONG
    TidyTag_STYLE,       # STYLE
    TidyTag_SUB,         # SUB
    TidyTag_SUP,         # SUP
    TidyTag_SVG,         # SVG  (HTML5)
    TidyTag_TABLE,       # TABLE
    TidyTag_TBODY,       # TBODY
    TidyTag_TD,          # TD
    TidyTag_TEXTAREA,    # TEXTAREA
    TidyTag_TFOOT,       # TFOOT
    TidyTag_TH,          # TH
    TidyTag_THEAD,       # THEAD
    TidyTag_TITLE,       # TITLE
    TidyTag_TR,          # TR
    TidyTag_TT,          # TT
    TidyTag_U,           # U
    TidyTag_UL,          # UL
    TidyTag_VAR,         # VAR
    TidyTag_WBR,         # WBR
    TidyTag_XMP,         # XMP
    TidyTag_NEXTID,      # NEXTID

    TidyTag_ARTICLE,     # ARTICLE
    TidyTag_ASIDE,       # ASIDE
    TidyTag_AUDIO,       # AUDIO
    TidyTag_BDI,         # BDI
    TidyTag_CANVAS,      # CANVAS
    TidyTag_COMMAND,     # COMMAND
    TidyTag_DATA,        # DATA
    TidyTag_DATALIST,    # DATALIST
    TidyTag_DETAILS,     # DETAILS
    TidyTag_DIALOG,      # DIALOG
    TidyTag_FIGCAPTION,  # FIGCAPTION
    TidyTag_FIGURE,      # FIGURE
    TidyTag_FOOTER,      # FOOTER
    TidyTag_HEADER,      # HEADER
    TidyTag_HGROUP,      # HGROUP
    TidyTag_MAIN,        # MAIN
    TidyTag_MARK,        # MARK
    TidyTag_MENUITEM,    # MENUITEM
    TidyTag_METER,       # METER
    TidyTag_NAV,         # NAV
    TidyTag_OUTPUT,      # OUTPUT
    TidyTag_PROGRESS,    # PROGRESS
    TidyTag_SECTION,     # SECTION
    TidyTag_SOURCE,      # SOURCE
    TidyTag_SUMMARY,     # SUMMARY
    TidyTag_TEMPLATE,    # TEMPLATE
    TidyTag_TIME,        # TIME
    TidyTag_TRACK,       # TRACK
    TidyTag_VIDEO,       # VIDEO
    TidyTag_SLOT,        # SLOT

    N_TIDY_TAGS,         # Must be last

) = range(0, 154)

# Known HTML attributes
#
TidyAttrId = ct.c_int
(
    TidyAttr_UNKNOWN,                # UNKNOWN=
    TidyAttr_ABBR,                   # ABBR=
    TidyAttr_ACCEPT,                 # ACCEPT=
    TidyAttr_ACCEPT_CHARSET,         # ACCEPT_CHARSET=
    TidyAttr_ACCESSKEY,              # ACCESSKEY=
    TidyAttr_ACTION,                 # ACTION=
    TidyAttr_ADD_DATE,               # ADD_DATE=
    TidyAttr_ALIGN,                  # ALIGN=
    TidyAttr_ALINK,                  # ALINK=
    TidyAttr_ALLOWFULLSCREEN,        # ALLOWFULLSCREEN=
    TidyAttr_ALT,                    # ALT=
    TidyAttr_ARCHIVE,                # ARCHIVE=
    TidyAttr_AXIS,                   # AXIS=
    TidyAttr_BACKGROUND,             # BACKGROUND=
    TidyAttr_BGCOLOR,                # BGCOLOR=
    TidyAttr_BGPROPERTIES,           # BGPROPERTIES=
    TidyAttr_BORDER,                 # BORDER=
    TidyAttr_BORDERCOLOR,            # BORDERCOLOR=
    TidyAttr_BOTTOMMARGIN,           # BOTTOMMARGIN=
    TidyAttr_CELLPADDING,            # CELLPADDING=
    TidyAttr_CELLSPACING,            # CELLSPACING=
    TidyAttr_CHAR,                   # CHAR=
    TidyAttr_CHAROFF,                # CHAROFF=
    TidyAttr_CHARSET,                # CHARSET=
    TidyAttr_CHECKED,                # CHECKED=
    TidyAttr_CITE,                   # CITE=
    TidyAttr_CLASS,                  # CLASS=
    TidyAttr_CLASSID,                # CLASSID=
    TidyAttr_CLEAR,                  # CLEAR=
    TidyAttr_CODE,                   # CODE=
    TidyAttr_CODEBASE,               # CODEBASE=
    TidyAttr_CODETYPE,               # CODETYPE=
    TidyAttr_COLOR,                  # COLOR=
    TidyAttr_COLS,                   # COLS=
    TidyAttr_COLSPAN,                # COLSPAN=
    TidyAttr_COMPACT,                # COMPACT=
    TidyAttr_CONTENT,                # CONTENT=
    TidyAttr_COORDS,                 # COORDS=
    TidyAttr_DATA,                   # DATA=
    TidyAttr_DATAFLD,                # DATAFLD=
    TidyAttr_DATAFORMATAS,           # DATAFORMATAS=
    TidyAttr_DATAPAGESIZE,           # DATAPAGESIZE=
    TidyAttr_DATASRC,                # DATASRC=
    TidyAttr_DATETIME,               # DATETIME=
    TidyAttr_DECLARE,                # DECLARE=
    TidyAttr_DEFER,                  # DEFER=
    TidyAttr_DIR,                    # DIR=
    TidyAttr_DISABLED,               # DISABLED=
    TidyAttr_DOWNLOAD,               # DOWNLOAD=
    TidyAttr_ENCODING,               # ENCODING=
    TidyAttr_ENCTYPE,                # ENCTYPE=
    TidyAttr_FACE,                   # FACE=
    TidyAttr_FOR,                    # FOR=
    TidyAttr_FRAME,                  # FRAME=
    TidyAttr_FRAMEBORDER,            # FRAMEBORDER=
    TidyAttr_FRAMESPACING,           # FRAMESPACING=
    TidyAttr_GRIDX,                  # GRIDX=
    TidyAttr_GRIDY,                  # GRIDY=
    TidyAttr_HEADERS,                # HEADERS=
    TidyAttr_HEIGHT,                 # HEIGHT=
    TidyAttr_HREF,                   # HREF=
    TidyAttr_HREFLANG,               # HREFLANG=
    TidyAttr_HSPACE,                 # HSPACE=
    TidyAttr_HTTP_EQUIV,             # HTTP_EQUIV=
    TidyAttr_ID,                     # ID=
    TidyAttr_IS,                     # IS=
    TidyAttr_ISMAP,                  # ISMAP=
    TidyAttr_ITEMID,                 # ITEMID=
    TidyAttr_ITEMPROP,               # ITEMPROP=
    TidyAttr_ITEMREF,                # ITEMREF=
    TidyAttr_ITEMSCOPE,              # ITEMSCOPE=
    TidyAttr_ITEMTYPE,               # ITEMTYPE=
    TidyAttr_LABEL,                  # LABEL=
    TidyAttr_LANG,                   # LANG=
    TidyAttr_LANGUAGE,               # LANGUAGE=
    TidyAttr_LAST_MODIFIED,          # LAST_MODIFIED=
    TidyAttr_LAST_VISIT,             # LAST_VISIT=
    TidyAttr_LEFTMARGIN,             # LEFTMARGIN=
    TidyAttr_LINK,                   # LINK=
    TidyAttr_LONGDESC,               # LONGDESC=
    TidyAttr_LOWSRC,                 # LOWSRC=
    TidyAttr_MARGINHEIGHT,           # MARGINHEIGHT=
    TidyAttr_MARGINWIDTH,            # MARGINWIDTH=
    TidyAttr_MAXLENGTH,              # MAXLENGTH=
    TidyAttr_MEDIA,                  # MEDIA=
    TidyAttr_METHOD,                 # METHOD=
    TidyAttr_MULTIPLE,               # MULTIPLE=
    TidyAttr_NAME,                   # NAME=
    TidyAttr_NOHREF,                 # NOHREF=
    TidyAttr_NORESIZE,               # NORESIZE=
    TidyAttr_NOSHADE,                # NOSHADE=
    TidyAttr_NOWRAP,                 # NOWRAP=
    TidyAttr_OBJECT,                 # OBJECT=
    TidyAttr_OnAFTERUPDATE,          # OnAFTERUPDATE=
    TidyAttr_OnBEFOREUNLOAD,         # OnBEFOREUNLOAD=
    TidyAttr_OnBEFOREUPDATE,         # OnBEFOREUPDATE=
    TidyAttr_OnBLUR,                 # OnBLUR=
    TidyAttr_OnCHANGE,               # OnCHANGE=
    TidyAttr_OnCLICK,                # OnCLICK=
    TidyAttr_OnDATAAVAILABLE,        # OnDATAAVAILABLE=
    TidyAttr_OnDATASETCHANGED,       # OnDATASETCHANGED=
    TidyAttr_OnDATASETCOMPLETE,      # OnDATASETCOMPLETE=
    TidyAttr_OnDBLCLICK,             # OnDBLCLICK=
    TidyAttr_OnERRORUPDATE,          # OnERRORUPDATE=
    TidyAttr_OnFOCUS,                # OnFOCUS=
    TidyAttr_OnKEYDOWN,              # OnKEYDOWN=
    TidyAttr_OnKEYPRESS,             # OnKEYPRESS=
    TidyAttr_OnKEYUP,                # OnKEYUP=
    TidyAttr_OnLOAD,                 # OnLOAD=
    TidyAttr_OnMOUSEDOWN,            # OnMOUSEDOWN=
    TidyAttr_OnMOUSEMOVE,            # OnMOUSEMOVE=
    TidyAttr_OnMOUSEOUT,             # OnMOUSEOUT=
    TidyAttr_OnMOUSEOVER,            # OnMOUSEOVER=
    TidyAttr_OnMOUSEUP,              # OnMOUSEUP=
    TidyAttr_OnRESET,                # OnRESET=
    TidyAttr_OnROWENTER,             # OnROWENTER=
    TidyAttr_OnROWEXIT,              # OnROWEXIT=
    TidyAttr_OnSELECT,               # OnSELECT=
    TidyAttr_OnSUBMIT,               # OnSUBMIT=
    TidyAttr_OnUNLOAD,               # OnUNLOAD=
    TidyAttr_PROFILE,                # PROFILE=
    TidyAttr_PROMPT,                 # PROMPT=
    TidyAttr_RBSPAN,                 # RBSPAN=
    TidyAttr_READONLY,               # READONLY=
    TidyAttr_REL,                    # REL=
    TidyAttr_REV,                    # REV=
    TidyAttr_RIGHTMARGIN,            # RIGHTMARGIN=
    TidyAttr_ROLE,                   # ROLE=
    TidyAttr_ROWS,                   # ROWS=
    TidyAttr_ROWSPAN,                # ROWSPAN=
    TidyAttr_RULES,                  # RULES=
    TidyAttr_SCHEME,                 # SCHEME=
    TidyAttr_SCOPE,                  # SCOPE=
    TidyAttr_SCROLLING,              # SCROLLING=
    TidyAttr_SELECTED,               # SELECTED=
    TidyAttr_SHAPE,                  # SHAPE=
    TidyAttr_SHOWGRID,               # SHOWGRID=
    TidyAttr_SHOWGRIDX,              # SHOWGRIDX=
    TidyAttr_SHOWGRIDY,              # SHOWGRIDY=
    TidyAttr_SIZE,                   # SIZE=
    TidyAttr_SPAN,                   # SPAN=
    TidyAttr_SRC,                    # SRC=
    TidyAttr_SRCSET,                 # SRCSET= (HTML5)
    TidyAttr_STANDBY,                # STANDBY=
    TidyAttr_START,                  # START=
    TidyAttr_STYLE,                  # STYLE=
    TidyAttr_SUMMARY,                # SUMMARY=
    TidyAttr_TABINDEX,               # TABINDEX=
    TidyAttr_TARGET,                 # TARGET=
    TidyAttr_TEXT,                   # TEXT=
    TidyAttr_TITLE,                  # TITLE=
    TidyAttr_TOPMARGIN,              # TOPMARGIN=
    TidyAttr_TRANSLATE,              # TRANSLATE=
    TidyAttr_TYPE,                   # TYPE=
    TidyAttr_USEMAP,                 # USEMAP=
    TidyAttr_VALIGN,                 # VALIGN=
    TidyAttr_VALUE,                  # VALUE=
    TidyAttr_VALUETYPE,              # VALUETYPE=
    TidyAttr_VERSION,                # VERSION=
    TidyAttr_VLINK,                  # VLINK=
    TidyAttr_VSPACE,                 # VSPACE=
    TidyAttr_WIDTH,                  # WIDTH=
    TidyAttr_WRAP,                   # WRAP=
    TidyAttr_XML_LANG,               # XML_LANG=
    TidyAttr_XML_SPACE,              # XML_SPACE=
    TidyAttr_XMLNS,                  # XMLNS=

    TidyAttr_EVENT,                  # EVENT=
    TidyAttr_METHODS,                # METHODS=
    TidyAttr_N,                      # N=
    TidyAttr_SDAFORM,                # SDAFORM=
    TidyAttr_SDAPREF,                # SDAPREF=
    TidyAttr_SDASUFF,                # SDASUFF=
    TidyAttr_URN,                    # URN=

    TidyAttr_ASYNC,                  # ASYNC=
    TidyAttr_AUTOCOMPLETE,           # AUTOCOMPLETE=
    TidyAttr_AUTOFOCUS,              # AUTOFOCUS=
    TidyAttr_AUTOPLAY,               # AUTOPLAY=
    TidyAttr_CHALLENGE,              # CHALLENGE=
    TidyAttr_CONTENTEDITABLE,        # CONTENTEDITABLE=
    TidyAttr_CONTEXTMENU,            # CONTEXTMENU=
    TidyAttr_CONTROLS,               # CONTROLS=
    TidyAttr_CROSSORIGIN,            # CROSSORIGIN=
    TidyAttr_DEFAULT,                # DEFAULT=
    TidyAttr_DIRNAME,                # DIRNAME=
    TidyAttr_DRAGGABLE,              # DRAGGABLE=
    TidyAttr_DROPZONE,               # DROPZONE=
    TidyAttr_FORM,                   # FORM=
    TidyAttr_FORMACTION,             # FORMACTION=
    TidyAttr_FORMENCTYPE,            # FORMENCTYPE=
    TidyAttr_FORMMETHOD,             # FORMMETHOD=
    TidyAttr_FORMNOVALIDATE,         # FORMNOVALIDATE=
    TidyAttr_FORMTARGET,             # FORMTARGET=
    TidyAttr_HIDDEN,                 # HIDDEN=
    TidyAttr_HIGH,                   # HIGH=
    TidyAttr_ICON,                   # ICON=
    TidyAttr_KEYTYPE,                # KEYTYPE=
    TidyAttr_KIND,                   # KIND=
    TidyAttr_LIST,                   # LIST=
    TidyAttr_LOOP,                   # LOOP=
    TidyAttr_LOW,                    # LOW=
    TidyAttr_MANIFEST,               # MANIFEST=
    TidyAttr_MAX,                    # MAX=
    TidyAttr_MEDIAGROUP,             # MEDIAGROUP=
    TidyAttr_MIN,                    # MIN=
    TidyAttr_MUTED,                  # MUTED=
    TidyAttr_NOVALIDATE,             # NOVALIDATE=
    TidyAttr_OPEN,                   # OPEN=
    TidyAttr_OPTIMUM,                # OPTIMUM=
    TidyAttr_OnABORT,                # OnABORT=
    TidyAttr_OnAFTERPRINT,           # OnAFTERPRINT=
    TidyAttr_OnBEFOREPRINT,          # OnBEFOREPRINT=
    TidyAttr_OnCANPLAY,              # OnCANPLAY=
    TidyAttr_OnCANPLAYTHROUGH,       # OnCANPLAYTHROUGH=
    TidyAttr_OnCONTEXTMENU,          # OnCONTEXTMENU=
    TidyAttr_OnCUECHANGE,            # OnCUECHANGE=
    TidyAttr_OnDRAG,                 # OnDRAG=
    TidyAttr_OnDRAGEND,              # OnDRAGEND=
    TidyAttr_OnDRAGENTER,            # OnDRAGENTER=
    TidyAttr_OnDRAGLEAVE,            # OnDRAGLEAVE=
    TidyAttr_OnDRAGOVER,             # OnDRAGOVER=
    TidyAttr_OnDRAGSTART,            # OnDRAGSTART=
    TidyAttr_OnDROP,                 # OnDROP=
    TidyAttr_OnDURATIONCHANGE,       # OnDURATIONCHANGE=
    TidyAttr_OnEMPTIED,              # OnEMPTIED=
    TidyAttr_OnENDED,                # OnENDED=
    TidyAttr_OnERROR,                # OnERROR=
    TidyAttr_OnHASHCHANGE,           # OnHASHCHANGE=
    TidyAttr_OnINPUT,                # OnINPUT=
    TidyAttr_OnINVALID,              # OnINVALID=
    TidyAttr_OnLOADEDDATA,           # OnLOADEDDATA=
    TidyAttr_OnLOADEDMETADATA,       # OnLOADEDMETADATA=
    TidyAttr_OnLOADSTART,            # OnLOADSTART=
    TidyAttr_OnMESSAGE,              # OnMESSAGE=
    TidyAttr_OnMOUSEWHEEL,           # OnMOUSEWHEEL=
    TidyAttr_OnOFFLINE,              # OnOFFLINE=
    TidyAttr_OnONLINE,               # OnONLINE=
    TidyAttr_OnPAGEHIDE,             # OnPAGEHIDE=
    TidyAttr_OnPAGESHOW,             # OnPAGESHOW=
    TidyAttr_OnPAUSE,                # OnPAUSE=
    TidyAttr_OnPLAY,                 # OnPLAY=
    TidyAttr_OnPLAYING,              # OnPLAYING=
    TidyAttr_OnPOPSTATE,             # OnPOPSTATE=
    TidyAttr_OnPROGRESS,             # OnPROGRESS=
    TidyAttr_OnRATECHANGE,           # OnRATECHANGE=
    TidyAttr_OnREADYSTATECHANGE,     # OnREADYSTATECHANGE=
    TidyAttr_OnREDO,                 # OnREDO=
    TidyAttr_OnRESIZE,               # OnRESIZE=
    TidyAttr_OnSCROLL,               # OnSCROLL=
    TidyAttr_OnSEEKED,               # OnSEEKED=
    TidyAttr_OnSEEKING,              # OnSEEKING=
    TidyAttr_OnSHOW,                 # OnSHOW=
    TidyAttr_OnSTALLED,              # OnSTALLED=
    TidyAttr_OnSTORAGE,              # OnSTORAGE=
    TidyAttr_OnSUSPEND,              # OnSUSPEND=
    TidyAttr_OnTIMEUPDATE,           # OnTIMEUPDATE=
    TidyAttr_OnUNDO,                 # OnUNDO=
    TidyAttr_OnVOLUMECHANGE,         # OnVOLUMECHANGE=
    TidyAttr_OnWAITING,              # OnWAITING=
    TidyAttr_PATTERN,                # PATTERN=
    TidyAttr_PLACEHOLDER,            # PLACEHOLDER=
    TidyAttr_PLAYSINLINE,            # PLAYSINLINE=
    TidyAttr_POSTER,                 # POSTER=
    TidyAttr_PRELOAD,                # PRELOAD=
    TidyAttr_PUBDATE,                # PUBDATE=
    TidyAttr_RADIOGROUP,             # RADIOGROUP=
    TidyAttr_REQUIRED,               # REQUIRED=
    TidyAttr_REVERSED,               # REVERSED=
    TidyAttr_SANDBOX,                # SANDBOX=
    TidyAttr_SCOPED,                 # SCOPED=
    TidyAttr_SEAMLESS,               # SEAMLESS=
    TidyAttr_SIZES,                  # SIZES=
    TidyAttr_SPELLCHECK,             # SPELLCHECK=
    TidyAttr_SRCDOC,                 # SRCDOC=
    TidyAttr_SRCLANG,                # SRCLANG=
    TidyAttr_STEP,                   # STEP=
    TidyAttr_ARIA_ACTIVEDESCENDANT,  # ARIA_ACTIVEDESCENDANT
    TidyAttr_ARIA_ATOMIC,            # ARIA_ATOMIC=
    TidyAttr_ARIA_AUTOCOMPLETE,      # ARIA_AUTOCOMPLETE=
    TidyAttr_ARIA_BUSY,              # ARIA_BUSY=
    TidyAttr_ARIA_CHECKED,           # ARIA_CHECKED=
    TidyAttr_ARIA_CONTROLS,          # ARIA_CONTROLS=
    TidyAttr_ARIA_DESCRIBEDBY,       # ARIA_DESCRIBEDBY=
    TidyAttr_ARIA_DISABLED,          # ARIA_DISABLED=
    TidyAttr_ARIA_DROPEFFECT,        # ARIA_DROPEFFECT=
    TidyAttr_ARIA_EXPANDED,          # ARIA_EXPANDED=
    TidyAttr_ARIA_FLOWTO,            # ARIA_FLOWTO=
    TidyAttr_ARIA_GRABBED,           # ARIA_GRABBED=
    TidyAttr_ARIA_HASPOPUP,          # ARIA_HASPOPUP=
    TidyAttr_ARIA_HIDDEN,            # ARIA_HIDDEN=
    TidyAttr_ARIA_INVALID,           # ARIA_INVALID=
    TidyAttr_ARIA_LABEL,             # ARIA_LABEL=
    TidyAttr_ARIA_LABELLEDBY,        # ARIA_LABELLEDBY=
    TidyAttr_ARIA_LEVEL,             # ARIA_LEVEL=
    TidyAttr_ARIA_LIVE,              # ARIA_LIVE=
    TidyAttr_ARIA_MULTILINE,         # ARIA_MULTILINE=
    TidyAttr_ARIA_MULTISELECTABLE,   # ARIA_MULTISELECTABLE=
    TidyAttr_ARIA_ORIENTATION,       # ARIA_ORIENTATION=
    TidyAttr_ARIA_OWNS,              # ARIA_OWNS=
    TidyAttr_ARIA_POSINSET,          # ARIA_POSINSET=
    TidyAttr_ARIA_PRESSED,           # ARIA_PRESSED=
    TidyAttr_ARIA_READONLY,          # ARIA_READONLY=
    TidyAttr_ARIA_RELEVANT,          # ARIA_RELEVANT=
    TidyAttr_ARIA_REQUIRED,          # ARIA_REQUIRED=
    TidyAttr_ARIA_SELECTED,          # ARIA_SELECTED=
    TidyAttr_ARIA_SETSIZE,           # ARIA_SETSIZE=
    TidyAttr_ARIA_SORT,              # ARIA_SORT=
    TidyAttr_ARIA_VALUEMAX,          # ARIA_VALUEMAX=
    TidyAttr_ARIA_VALUEMIN,          # ARIA_VALUEMIN=
    TidyAttr_ARIA_VALUENOW,          # ARIA_VALUENOW=
    TidyAttr_ARIA_VALUETEXT,         # ARIA_VALUETEXT=

    # SVG attributes (SVG 1.1)
    TidyAttr_X,                      # X=
    TidyAttr_Y,                      # Y=
    TidyAttr_VIEWBOX,                # VIEWBOX=
    TidyAttr_PRESERVEASPECTRATIO,    # PRESERVEASPECTRATIO=
    TidyAttr_ZOOMANDPAN,             # ZOOMANDPAN=
    TidyAttr_BASEPROFILE,            # BASEPROFILE=
    TidyAttr_CONTENTSCRIPTTYPE,      # CONTENTSCRIPTTYPE=
    TidyAttr_CONTENTSTYLETYPE,       # CONTENTSTYLETYPE=

    # MathML <math> attributes
    TidyAttr_DISPLAY,                # DISPLAY= (html5)

    # RDFa global attributes
    TidyAttr_ABOUT,                  # ABOUT=
    TidyAttr_DATATYPE,               # DATATYPE=
    TidyAttr_INLIST,                 # INLIST=
    TidyAttr_PREFIX,                 # PREFIX=
    TidyAttr_PROPERTY,               # PROPERTY=
    TidyAttr_RESOURCE,               # RESOURCE=
    TidyAttr_TYPEOF,                 # TYPEOF=
    TidyAttr_VOCAB,                  # VOCAB=

    TidyAttr_INTEGRITY,              # INTEGRITY=

    TidyAttr_AS,                     # AS=

    TidyAttr_XMLNSXLINK,             # svg xmls:xlink="url"
    TidyAttr_SLOT,                   # SLOT=
    TidyAttr_LOADING,                # LOADING=

    # SVG paint attributes (SVG 1.1)
    TidyAttr_FILL,                   # FILL=
    TidyAttr_FILLRULE,               # FILLRULE=
    TidyAttr_STROKE,                 # STROKE=
    TidyAttr_STROKEDASHARRAY,        # STROKEDASHARRAY=
    TidyAttr_STROKEDASHOFFSET,       # STROKEDASHOFFSET=
    TidyAttr_STROKELINECAP,          # STROKELINECAP=
    TidyAttr_STROKELINEJOIN,         # STROKELINEJOIN=
    TidyAttr_STROKEMITERLIMIT,       # STROKEMITERLIMIT=
    TidyAttr_STROKEWIDTH,            # STROKEWIDTH=
    TidyAttr_COLORINTERPOLATION,     # COLORINTERPOLATION=
    TidyAttr_COLORRENDERING,         # COLORRENDERING=
    TidyAttr_OPACITY,                # OPACITY=
    TidyAttr_STROKEOPACITY,          # STROKEOPACITY=
    TidyAttr_FILLOPACITY,            # FILLOPACITY=

    N_TIDY_ATTRIBS,                  # Must be last

) = range(0, 347)

# @name I/O and Message Handling Interface
#
# Messages used throughout LibTidy and exposed to the public API have
# attributes which are communicated with these enumerations.

# Message severity level, used throughout LibTidy to indicate the severity
# or status of a message
#
# @remark These enum members all have associated localized strings available
#         via their enum values. These strings are suitable for use as labels.
#
TidyReportLevel = ct.c_int
(
    TidyInfo,              # Report: Information about markup usage
    TidyWarning,           # Report: Warning message
    TidyConfig,            # Report: Configuration error
    TidyAccess,            # Report: Accessibility message
    TidyError,             # Report: Error message - output suppressed
    TidyBadDocument,       # Report: I/O or file system error
    TidyFatal,             # Report: Crash!
    TidyDialogueSummary,   # Dialogue: Summary-related information
    TidyDialogueInfo,      # Dialogue: Non-document related information
    TidyDialogueFootnote,  # Dialogue: Footnote

) = range(350, 350 + 10)
TidyDialogueDoc = TidyDialogueFootnote  # Dialogue: Deprecated (renamed)

# Indicates the data type of a format string parameter used when Tidy
# emits reports and dialogue as part of the messaging callback functions.
# See `messageobj.h` for more information on this API.
#
TidyFormatParameterType = ct.c_int
(
    TidyFormatType_INT,      # Argument is signed integer.
    TidyFormatType_UINT,     # Argument is unsigned integer.
    TidyFormatType_STRING,   # Argument is a string.
    TidyFormatType_DOUBLE,   # Argument is a double.
    TidyFormatType_UNKNOWN,  # Argument type is unknown!

) = (*range(0, 4), 20)

# @} end group public_enumerations

# MARK: - Public Enumerations (con't)
# @addtogroup public_enumerations

# @name Messages

# The enumeration contains a list of every possible string that Tidy and the
# console application can output, _except_ for strings from the following
# enumerations:
# - `TidyOptionId`
# - `TidyConfigCategory`
# - `TidyReportLevel`
#
# They are used as keys internally within Tidy, and have corresponding text
# keys that are used in message callback filters (these are defined in
# `tidyStringsKeys[]`, but API users don't require access to it directly).
#
TidyStrings = ct.c_int
(
    # This MUST be present and first.
    TIDYSTRINGS_FIRST,

    # These message codes comprise every possible message that can be output by
    # Tidy that are *not* diagnostic style messages, and are *not* console
    # application specific messages.
    LINE_COLUMN_STRING,           # line %d column %d
    FN_LINE_COLUMN_STRING,        # %s: line %d column %d
    STRING_DISCARDING,            # discarding
    STRING_ERROR_COUNT_ERROR,     # error and errors
    STRING_ERROR_COUNT_WARNING,   # warning and warnings
    STRING_HELLO_ACCESS,          # Accessibility hello message
    STRING_HTML_PROPRIETARY,      # HTML Proprietary
    STRING_PLAIN_TEXT,            # plain text
    STRING_REPLACING,             # replacing
    STRING_SPECIFIED,             # specified
    STRING_XML_DECLARATION,       # XML declaration
    TIDYCUSTOMNO_STRING,          # no
    TIDYCUSTOMBLOCKLEVEL_STRING,  # block level
    TIDYCUSTOMEMPTY_STRING,       # empty
    TIDYCUSTOMINLINE_STRING,      # inline
    TIDYCUSTOMPRE_STRING,         # pre
    # These messages are used to generate additional dialogue style output from
    # Tidy when certain conditions exist, and provide more verbose explanations
    # than the short report.
    FOOTNOTE_TRIM_EMPTY_ELEMENT,
    TEXT_ACCESS_ADVICE1,
    TEXT_ACCESS_ADVICE2,
    TEXT_BAD_FORM,
    TEXT_BAD_MAIN,
    TEXT_HTML_T_ALGORITHM,
    TEXT_INVALID_URI,
    TEXT_INVALID_UTF16,
    TEXT_INVALID_UTF8,
    TEXT_M_IMAGE_ALT,
    TEXT_M_IMAGE_MAP,
    TEXT_M_LINK_ALT,
    TEXT_M_SUMMARY,
    TEXT_SGML_CHARS,
    TEXT_USING_BODY,
    TEXT_USING_FONT,
    TEXT_USING_FRAMES,
    TEXT_USING_LAYER,
    TEXT_USING_NOBR,
    TEXT_USING_SPACER,
    TEXT_VENDOR_CHARS,
    TEXT_WINDOWS_CHARS,
    # These messages are used to generate additional dialogue style output from
    # Tidy when certain conditions exist, and provide more verbose explanations
    # than the short report.
    STRING_ERROR_COUNT,         # TidyDialogueSummary
    STRING_NEEDS_INTERVENTION,  # TidyDialogueSummary
    STRING_NO_ERRORS,           # TidyDialogueSummary
    STRING_NOT_ALL_SHOWN,       # TidyDialogueSummary
    TEXT_GENERAL_INFO_PLEA,     # TidyDialogueInfo
    TEXT_GENERAL_INFO,          # TidyDialogueInfo
    REPORT_MESSAGE_FIRST,
    # These are report messages, i.e., messages that appear in Tidy's table
    # of errors and warnings.
    ADDED_MISSING_CHARSET,
    ANCHOR_NOT_UNIQUE,
    ANCHOR_DUPLICATED,
    APOS_UNDEFINED,
    ATTR_VALUE_NOT_LCASE,
    ATTRIBUTE_IS_NOT_ALLOWED,
    ATTRIBUTE_VALUE_REPLACED,
    BACKSLASH_IN_URI,
    BAD_ATTRIBUTE_VALUE_REPLACED,
    BAD_ATTRIBUTE_VALUE,
    BAD_CDATA_CONTENT,
    BAD_SUMMARY_HTML5,
    BAD_SURROGATE_LEAD,
    BAD_SURROGATE_PAIR,
    BAD_SURROGATE_TAIL,
    CANT_BE_NESTED,
    COERCE_TO_ENDTAG,
    CONTENT_AFTER_BODY,
    CUSTOM_TAG_DETECTED,
    DISCARDING_UNEXPECTED,
    DOCTYPE_AFTER_TAGS,
    DUPLICATE_FRAMESET,
    ELEMENT_NOT_EMPTY,
    ELEMENT_VERS_MISMATCH_ERROR,
    ELEMENT_VERS_MISMATCH_WARN,
    ENCODING_MISMATCH,
    ESCAPED_ILLEGAL_URI,
    FILE_CANT_OPEN,
    FILE_CANT_OPEN_CFG,
    FILE_NOT_FILE,
    FIXED_BACKSLASH,
    FOUND_STYLE_IN_BODY,
    ID_NAME_MISMATCH,
    ILLEGAL_NESTING,
    ILLEGAL_URI_CODEPOINT,
    ILLEGAL_URI_REFERENCE,
    INSERTING_AUTO_ATTRIBUTE,
    INSERTING_TAG,
    INVALID_ATTRIBUTE,
    INVALID_NCR,
    INVALID_SGML_CHARS,
    INVALID_UTF8,
    INVALID_UTF16,
    INVALID_XML_ID,
    JOINING_ATTRIBUTE,
    MALFORMED_COMMENT,
    MALFORMED_COMMENT_DROPPING,
    MALFORMED_COMMENT_EOS,
    MALFORMED_COMMENT_WARN,
    MALFORMED_DOCTYPE,
    MISMATCHED_ATTRIBUTE_ERROR,
    MISMATCHED_ATTRIBUTE_WARN,
    MISSING_ATTR_VALUE,
    MISSING_ATTRIBUTE,
    MISSING_DOCTYPE,
    MISSING_ENDTAG_BEFORE,
    MISSING_ENDTAG_FOR,
    MISSING_ENDTAG_OPTIONAL,
    MISSING_IMAGEMAP,
    MISSING_QUOTEMARK,
    MISSING_QUOTEMARK_OPEN,
    MISSING_SEMICOLON_NCR,
    MISSING_SEMICOLON,
    MISSING_STARTTAG,
    MISSING_TITLE_ELEMENT,
    MOVED_STYLE_TO_HEAD,
    NESTED_EMPHASIS,
    NESTED_QUOTATION,
    NEWLINE_IN_URI,
    NOFRAMES_CONTENT,
    NON_MATCHING_ENDTAG,
    OBSOLETE_ELEMENT,
    OPTION_REMOVED,
    OPTION_REMOVED_APPLIED,
    OPTION_REMOVED_UNAPPLIED,
    PREVIOUS_LOCATION,
    PROPRIETARY_ATTR_VALUE,
    PROPRIETARY_ATTRIBUTE,
    PROPRIETARY_ELEMENT,
    REMOVED_HTML5,
    REPEATED_ATTRIBUTE,
    REPLACING_ELEMENT,
    REPLACING_UNEX_ELEMENT,
    SPACE_PRECEDING_XMLDECL,
    STRING_CONTENT_LOOKS,
    STRING_ARGUMENT_BAD,
    STRING_DOCTYPE_GIVEN,
    STRING_MISSING_MALFORMED,
    STRING_MUTING_TYPE,
    STRING_NO_SYSID,
    STRING_UNKNOWN_OPTION,
    SUSPECTED_MISSING_QUOTE,
    TAG_NOT_ALLOWED_IN,
    TOO_MANY_ELEMENTS_IN,
    TOO_MANY_ELEMENTS,
    TRIM_EMPTY_ELEMENT,
    UNESCAPED_AMPERSAND,
    UNEXPECTED_END_OF_FILE_ATTR,
    UNEXPECTED_END_OF_FILE,
    UNEXPECTED_ENDTAG_ERR,
    UNEXPECTED_ENDTAG_IN,
    UNEXPECTED_ENDTAG,
    UNEXPECTED_EQUALSIGN,
    UNEXPECTED_GT,
    UNEXPECTED_QUOTEMARK,
    UNKNOWN_ELEMENT_LOOKS_CUSTOM,
    UNKNOWN_ELEMENT,
    UNKNOWN_ENTITY,
    USING_BR_INPLACE_OF,
    VENDOR_SPECIFIC_CHARS,
    WHITE_IN_URI,
    XML_DECLARATION_DETECTED,
    XML_ID_SYNTAX,
    BLANK_TITLE_ELEMENT,
    REPORT_MESSAGE_LAST,
    # These are report messages added by Tidy's accessibility module.
    # Note that commented out items don't have checks for them at this time,
    # and it was probably intended that some test would eventually be written.
    IMG_MISSING_ALT,                                # [1.1.1.1]
    IMG_ALT_SUSPICIOUS_FILENAME,                    # [1.1.1.2]
    IMG_ALT_SUSPICIOUS_FILE_SIZE,                   # [1.1.1.3]
    IMG_ALT_SUSPICIOUS_PLACEHOLDER,                 # [1.1.1.4]
    IMG_ALT_SUSPICIOUS_TOO_LONG,                    # [1.1.1.10]
    # IMG_MISSING_ALT_BULLET,                       # [1.1.1.11]
    # IMG_MISSING_ALT_H_RULE,                       # [1.1.1.12]
    IMG_MISSING_LONGDESC_DLINK,                     # [1.1.2.1]
    IMG_MISSING_DLINK,                              # [1.1.2.2]
    IMG_MISSING_LONGDESC,                           # [1.1.2.3]
    # LONGDESC_NOT_REQUIRED,                        # [1.1.2.5]
    IMG_BUTTON_MISSING_ALT,                         # [1.1.3.1]
    APPLET_MISSING_ALT,                             # [1.1.4.1]
    OBJECT_MISSING_ALT,                             # [1.1.5.1]
    AUDIO_MISSING_TEXT_WAV,                         # [1.1.6.1]
    AUDIO_MISSING_TEXT_AU,                          # [1.1.6.2]
    AUDIO_MISSING_TEXT_AIFF,                        # [1.1.6.3]
    AUDIO_MISSING_TEXT_SND,                         # [1.1.6.4]
    AUDIO_MISSING_TEXT_RA,                          # [1.1.6.5]
    AUDIO_MISSING_TEXT_RM,                          # [1.1.6.6]
    FRAME_MISSING_LONGDESC,                         # [1.1.8.1]
    AREA_MISSING_ALT,                               # [1.1.9.1]
    SCRIPT_MISSING_NOSCRIPT,                        # [1.1.10.1]
    ASCII_REQUIRES_DESCRIPTION,                     # [1.1.12.1]
    IMG_MAP_SERVER_REQUIRES_TEXT_LINKS,             # [1.2.1.1]
    MULTIMEDIA_REQUIRES_TEXT,                       # [1.4.1.1]
    IMG_MAP_CLIENT_MISSING_TEXT_LINKS,              # [1.5.1.1]
    INFORMATION_NOT_CONVEYED_IMAGE,                 # [2.1.1.1]
    INFORMATION_NOT_CONVEYED_APPLET,                # [2.1.1.2]
    INFORMATION_NOT_CONVEYED_OBJECT,                # [2.1.1.3]
    INFORMATION_NOT_CONVEYED_SCRIPT,                # [2.1.1.4]
    INFORMATION_NOT_CONVEYED_INPUT,                 # [2.1.1.5]
    COLOR_CONTRAST_TEXT,                            # [2.2.1.1]
    COLOR_CONTRAST_LINK,                            # [2.2.1.2]
    COLOR_CONTRAST_ACTIVE_LINK,                     # [2.2.1.3]
    COLOR_CONTRAST_VISITED_LINK,                    # [2.2.1.4]
    DOCTYPE_MISSING,                                # [3.2.1.1]
    STYLE_SHEET_CONTROL_PRESENTATION,               # [3.3.1.1]
    HEADERS_IMPROPERLY_NESTED,                      # [3.5.1.1]
    POTENTIAL_HEADER_BOLD,                          # [3.5.2.1]
    POTENTIAL_HEADER_ITALICS,                       # [3.5.2.2]
    POTENTIAL_HEADER_UNDERLINE,                     # [3.5.2.3]
    HEADER_USED_FORMAT_TEXT,                        # [3.5.3.1]
    LIST_USAGE_INVALID_UL,                          # [3.6.1.1]
    LIST_USAGE_INVALID_OL,                          # [3.6.1.2]
    LIST_USAGE_INVALID_LI,                          # [3.6.1.4]
    # INDICATE_CHANGES_IN_LANGUAGE,                 # [4.1.1.1]
    LANGUAGE_NOT_IDENTIFIED,                        # [4.3.1.1]
    LANGUAGE_INVALID,                               # [4.3.1.1]
    DATA_TABLE_MISSING_HEADERS,                     # [5.1.2.1]
    DATA_TABLE_MISSING_HEADERS_COLUMN,              # [5.1.2.2]
    DATA_TABLE_MISSING_HEADERS_ROW,                 # [5.1.2.3]
    DATA_TABLE_REQUIRE_MARKUP_COLUMN_HEADERS,       # [5.2.1.1]
    DATA_TABLE_REQUIRE_MARKUP_ROW_HEADERS,          # [5.2.1.2]
    LAYOUT_TABLES_LINEARIZE_PROPERLY,               # [5.3.1.1]
    LAYOUT_TABLE_INVALID_MARKUP,                    # [5.4.1.1]
    TABLE_MISSING_SUMMARY,                          # [5.5.1.1]
    TABLE_SUMMARY_INVALID_NULL,                     # [5.5.1.2]
    TABLE_SUMMARY_INVALID_SPACES,                   # [5.5.1.3]
    TABLE_SUMMARY_INVALID_PLACEHOLDER,              # [5.5.1.6]
    TABLE_MISSING_CAPTION,                          # [5.5.2.1]
    TABLE_MAY_REQUIRE_HEADER_ABBR,                  # [5.6.1.1]
    TABLE_MAY_REQUIRE_HEADER_ABBR_NULL,             # [5.6.1.2]
    TABLE_MAY_REQUIRE_HEADER_ABBR_SPACES,           # [5.6.1.3]
    STYLESHEETS_REQUIRE_TESTING_LINK,               # [6.1.1.1]
    STYLESHEETS_REQUIRE_TESTING_STYLE_ELEMENT,      # [6.1.1.2]
    STYLESHEETS_REQUIRE_TESTING_STYLE_ATTR,         # [6.1.1.3]
    FRAME_SRC_INVALID,                              # [6.2.1.1]
    TEXT_EQUIVALENTS_REQUIRE_UPDATING_APPLET,       # [6.2.2.1]
    TEXT_EQUIVALENTS_REQUIRE_UPDATING_SCRIPT,       # [6.2.2.2]
    TEXT_EQUIVALENTS_REQUIRE_UPDATING_OBJECT,       # [6.2.2.3]
    PROGRAMMATIC_OBJECTS_REQUIRE_TESTING_SCRIPT,    # [6.3.1.1]
    PROGRAMMATIC_OBJECTS_REQUIRE_TESTING_OBJECT,    # [6.3.1.2]
    PROGRAMMATIC_OBJECTS_REQUIRE_TESTING_EMBED,     # [6.3.1.3]
    PROGRAMMATIC_OBJECTS_REQUIRE_TESTING_APPLET,    # [6.3.1.4]
    FRAME_MISSING_NOFRAMES,                         # [6.5.1.1]
    NOFRAMES_INVALID_NO_VALUE,                      # [6.5.1.2]
    NOFRAMES_INVALID_CONTENT,                       # [6.5.1.3]
    NOFRAMES_INVALID_LINK,                          # [6.5.1.4]
    REMOVE_FLICKER_SCRIPT,                          # [7.1.1.1]
    REMOVE_FLICKER_OBJECT,                          # [7.1.1.2]
    REMOVE_FLICKER_EMBED,                           # [7.1.1.3]
    REMOVE_FLICKER_APPLET,                          # [7.1.1.4]
    REMOVE_FLICKER_ANIMATED_GIF,                    # [7.1.1.5]
    REMOVE_BLINK_MARQUEE,                           # [7.2.1.1]
    REMOVE_AUTO_REFRESH,                            # [7.4.1.1]
    REMOVE_AUTO_REDIRECT,                           # [7.5.1.1]
    ENSURE_PROGRAMMATIC_OBJECTS_ACCESSIBLE_SCRIPT,  # [8.1.1.1]
    ENSURE_PROGRAMMATIC_OBJECTS_ACCESSIBLE_OBJECT,  # [8.1.1.2]
    ENSURE_PROGRAMMATIC_OBJECTS_ACCESSIBLE_APPLET,  # [8.1.1.3]
    ENSURE_PROGRAMMATIC_OBJECTS_ACCESSIBLE_EMBED,   # [8.1.1.4]
    IMAGE_MAP_SERVER_SIDE_REQUIRES_CONVERSION,      # [9.1.1.1]
    SCRIPT_NOT_KEYBOARD_ACCESSIBLE_ON_MOUSE_DOWN,   # [9.3.1.1]
    SCRIPT_NOT_KEYBOARD_ACCESSIBLE_ON_MOUSE_UP,     # [9.3.1.2]
    SCRIPT_NOT_KEYBOARD_ACCESSIBLE_ON_CLICK,        # [9.3.1.3]
    SCRIPT_NOT_KEYBOARD_ACCESSIBLE_ON_MOUSE_OVER,   # [9.3.1.4]
    SCRIPT_NOT_KEYBOARD_ACCESSIBLE_ON_MOUSE_OUT,    # [9.3.1.5]
    SCRIPT_NOT_KEYBOARD_ACCESSIBLE_ON_MOUSE_MOVE,   # [9.3.1.6]
    NEW_WINDOWS_REQUIRE_WARNING_NEW,                # [10.1.1.1]
    NEW_WINDOWS_REQUIRE_WARNING_BLANK,              # [10.1.1.2]
    # LABEL_NEEDS_REPOSITIONING_BEFORE_INPUT,       # [10.2.1.1]
    # LABEL_NEEDS_REPOSITIONING_AFTER_INPUT,        # [10.2.1.2]
    # FORM_CONTROL_REQUIRES_DEFAULT_TEXT,           # [10.4.1.1]
    # FORM_CONTROL_DEFAULT_TEXT_INVALID_NULL,       # [10.4.1.2]
    # FORM_CONTROL_DEFAULT_TEXT_INVALID_SPACES,     # [10.4.1.3]
    REPLACE_DEPRECATED_HTML_APPLET,                 # [11.2.1.1]
    REPLACE_DEPRECATED_HTML_BASEFONT,               # [11.2.1.2]
    REPLACE_DEPRECATED_HTML_CENTER,                 # [11.2.1.3]
    REPLACE_DEPRECATED_HTML_DIR,                    # [11.2.1.4]
    REPLACE_DEPRECATED_HTML_FONT,                   # [11.2.1.5]
    REPLACE_DEPRECATED_HTML_ISINDEX,                # [11.2.1.6]
    REPLACE_DEPRECATED_HTML_MENU,                   # [11.2.1.7]
    REPLACE_DEPRECATED_HTML_S,                      # [11.2.1.8]
    REPLACE_DEPRECATED_HTML_STRIKE,                 # [11.2.1.9]
    REPLACE_DEPRECATED_HTML_U,                      # [11.2.1.10]
    FRAME_MISSING_TITLE,                            # [12.1.1.1]
    FRAME_TITLE_INVALID_NULL,                       # [12.1.1.2]
    FRAME_TITLE_INVALID_SPACES,                     # [12.1.1.3]
    ASSOCIATE_LABELS_EXPLICITLY,                    # [12.4.1.1]
    ASSOCIATE_LABELS_EXPLICITLY_FOR,                # [12.4.1.2]
    ASSOCIATE_LABELS_EXPLICITLY_ID,                 # [12.4.1.3]
    LINK_TEXT_NOT_MEANINGFUL,                       # [13.1.1.1]
    LINK_TEXT_MISSING,                              # [13.1.1.2]
    LINK_TEXT_TOO_LONG,                             # [13.1.1.3]
    LINK_TEXT_NOT_MEANINGFUL_CLICK_HERE,            # [13.1.1.4]
    # LINK_TEXT_NOT_MEANINGFUL_MORE,                # [13.1.1.5]
    # LINK_TEXT_NOT_MEANINGFUL_FOLLOW_THIS,         # [13.1.1.6]
    METADATA_MISSING,                               # [13.2.1.1]
    # METADATA_MISSING_LINK,                        # [13.2.1.2]
    METADATA_MISSING_REDIRECT_AUTOREFRESH,          # [13.2.1.3]
    SKIPOVER_ASCII_ART,                             # [13.10.1.1]

    # if SUPPORT_CONSOLE_APP
    # These message codes comprise every message is exclusive to theTidy console
    # application. It it possible to build LibTidy without these strings.
    TC_LABEL_COL,
    TC_LABEL_FILE,
    TC_LABEL_LANG,
    TC_LABEL_LEVL,
    TC_LABEL_OPT,
    TC_MAIN_ERROR_LOAD_CONFIG,
    TC_OPT_ACCESS,
    TC_OPT_ASCII,
    TC_OPT_ASHTML,
    TC_OPT_ASXML,
    TC_OPT_BARE,
    TC_OPT_BIG5,
    TC_OPT_CLEAN,
    TC_OPT_CONFIG,
    TC_OPT_ERRORS,
    TC_OPT_FILE,
    TC_OPT_GDOC,
    TC_OPT_HELP,
    TC_OPT_HELPCFG,
    TC_OPT_HELPENV,
    TC_OPT_HELPOPT,
    TC_OPT_IBM858,
    TC_OPT_INDENT,
    TC_OPT_ISO2022,
    TC_OPT_LANGUAGE,
    TC_OPT_LATIN0,
    TC_OPT_LATIN1,
    TC_OPT_MAC,
    TC_OPT_MODIFY,
    TC_OPT_NUMERIC,
    TC_OPT_OMIT,
    TC_OPT_OUTPUT,
    TC_OPT_QUIET,
    TC_OPT_RAW,
    TC_OPT_SHIFTJIS,
    TC_OPT_SHOWCFG,
    TC_OPT_EXP_CFG,
    TC_OPT_EXP_DEF,
    TC_OPT_UPPER,
    TC_OPT_UTF16,
    TC_OPT_UTF16BE,
    TC_OPT_UTF16LE,
    TC_OPT_UTF8,
    TC_OPT_VERSION,
    TC_OPT_WIN1252,
    TC_OPT_WRAP,
    TC_OPT_XML,
    TC_OPT_XMLCFG,
    TC_OPT_XMLSTRG,
    TC_OPT_XMLERRS,
    TC_OPT_XMLOPTS,
    TC_OPT_XMLHELP,
    TC_STRING_CONF_HEADER,
    TC_STRING_CONF_NAME,
    TC_STRING_CONF_TYPE,
    TC_STRING_CONF_VALUE,
    TC_STRING_CONF_NOTE,
    TC_STRING_OPT_NOT_DOCUMENTED,
    TC_STRING_OUT_OF_MEMORY,
    TC_STRING_FATAL_ERROR,
    TC_STRING_FILE_MANIP,
    TC_STRING_LANG_MUST_SPECIFY,
    TC_STRING_LANG_NOT_FOUND,
    TC_STRING_MUST_SPECIFY,
    TC_STRING_PROCESS_DIRECTIVES,
    TC_STRING_CHAR_ENCODING,
    TC_STRING_MISC,
    TC_STRING_XML,
    TC_STRING_UNKNOWN_OPTION,
    TC_STRING_UNKNOWN_OPTION_B,
    TC_STRING_VERS_A,
    TC_STRING_VERS_B,
    TC_TXT_HELP_1,
    TC_TXT_HELP_2A,
    TC_TXT_HELP_2B,
    TC_TXT_HELP_3,
    TC_TXT_HELP_3A,
    TC_TXT_HELP_CONFIG,
    TC_TXT_HELP_CONFIG_NAME,
    TC_TXT_HELP_CONFIG_TYPE,
    TC_TXT_HELP_CONFIG_ALLW,
    TC_TXT_HELP_ENV_1,
    TC_TXT_HELP_ENV_1A,
    TC_TXT_HELP_ENV_1B,
    TC_TXT_HELP_ENV_1C,
    TC_TXT_HELP_LANG_1,
    TC_TXT_HELP_LANG_2,
    TC_TXT_HELP_LANG_3,
    # endif # SUPPORT_CONSOLE_APP #

    # This MUST be present and last.
    TIDYSTRINGS_LAST,

) = range(500, 500 + 369)

# @} end group public_enumerations

# eof
