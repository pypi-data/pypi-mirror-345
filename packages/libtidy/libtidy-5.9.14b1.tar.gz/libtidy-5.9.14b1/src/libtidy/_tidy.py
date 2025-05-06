# **************************************************************************** #
# @file
# Defines HTML Tidy public API implemented by LibTidy.
#
# This public interface provides the entire public API for LibTidy, and
# is the sole interface that you should use when implementing LibTidy in
# your own applications.
#
# See tidy.c as an example application implementing the public API.
#
# This API is const-correct and doesn't explicitly depend on any globals.
# Thus, thread-safety may be introduced without changing the interface.
#
# The API limits all exposure to internal structures and provides only
# accessors that return simple types such as C strings and integers, which
# makes it quite suitable for integration with any number of other languages.
#
# @author  Dave Raggett [dsr@w3.org]
# @author  HTACG, et al (consult git log)
#
# @remarks The contributing author(s) would like to thank all those who
#          helped with testing, bug fixes and suggestions for improvements.
#          This wouldn't have been possible without your help.
#
# @copyright
#     Copyright (c) 1998-2017 World Wide Web Consortium (Massachusetts
#     Institute of Technology, European Research Consortium for Informatics
#     and Mathematics, Keio University).
# @par
#     All Rights Reserved.
# @par
#     This software and documentation is provided "as is," and the copyright
#     holders and contributing author(s) make no representations or warranties,
#     express or implied, including but not limited to, warranties of
#     merchantability or fitness for any particular purpose or that the use of
#     the software or documentation will not infringe any third party patents,
#     copyrights, trademarks or other rights.
#     @par
#     The copyright holders and contributing author(s) will not be held liable
#     for any direct, indirect, special or consequential damages arising out of
#     any use of the software or documentation, even if advised of the
#     possibility of such damage.
# @par
#     Permission is hereby granted to use, copy, modify, and distribute this
#     source code, or portions hereof, documentation and executables, for any
#     purpose, without fee, subject to the following restrictions:
# @par
#        1. The origin of this source code must not be misrepresented.
#        2. Altered versions must be plainly marked as such and must not be
#           misrepresented as being the original source.
#        3. This Copyright notice may not be removed or altered from any source
#           or altered source distribution.
# @par
#     The copyright holders and contributing author(s) specifically permit,
#     without fee, and encourage the use of this source code as a component for
#     supporting the Hypertext Markup Language in commercial products. If you
#     use this source code in a product, acknowledgment is not required but
#     would be appreciated.
#
# @date Created 2001-05-20 by Charles Reitzel
# @date Updated 2002-07-01 by Charles Reitzel - 1st Implementation
# @date Updated 2015-06-09 by Geoff R. McLane - Add more doxygen syntax
# @date Additional updates: consult git log
# **************************************************************************** #

import ctypes as ct

from ._platform import CFUNC
from ._dll      import dll

from ._tidyplatform import byte, tmbstr, ctmbstr, TidyIterator
from ._tidyplatform import *  # noqa
from ._tidyenum     import (TidyOptionId, TidyConfigCategory, TidyTagId,
                            TidyOptionType, TidyNodeType, TidyReportLevel,
                            TidyAttrId, TidyFormatParameterType)

class FILE(ct.Structure): pass

va_list = ct.c_void_p  # temporary  # noqa: E305

# **************************************************************************** #
# @defgroup internal_api Internal API
# The Internal API is used exclusively within LibTidy. If you are an
# HTML Tidy developer, then the internals API will be of especial
# importance to you.
#
# @note Always check first to determine whether or not an internal API
#       representation exists for a public API function before invoking a
#       public API function internally. In most cases, the public API
#       functions simply call an internal function.
# - - -
# @note This documentation _is not_ a substitute for browsing the source
#       code. Although the public API is fairly well documented, the
#       internal API is a very long, very slow, work-in-progress.
# **************************************************************************** #

# **************************************************************************** #
# @defgroup public_api External Public API
# The Public API is the API that LibTidy programmers must access in order
# to harness HTML Tidy as a library. The API limits all exposure to internal
# structures and provides only accessors that return simple types such as
# C strings and integers, which makes it quite suitable for integration with
# any number of other languages.
# @{
# **************************************************************************** #

# MARK: - Opaque Types
# **************************************************************************** #
# @defgroup Opaque Opaque Types
#
# Instances of these types are returned by LibTidy API functions, however
# they are opaque; you cannot see into them, and must use accessor functions
# to access the contents. This ensures that interfacing to LibTidy remains
# as universal as possible.
#
# @note Internally LibTidy developers will cast these to internal
#       implementation types with access to all member fields.
# @{
# **************************************************************************** #

# @struct TidyDoc
# Instances of this represent a Tidy document, which encapsulates everything
# there is to know about a single Tidy session. Many of the API functions
# return instance of TidyDoc, or expect instances as parameters.
#
class _TidyDoc(ct.Structure): pass  # { int _opaque; }
TidyDoc = ct.POINTER(_TidyDoc)  # noqa: E305

# @struct TidyOption
# Instances of this represent a Tidy configuration option, which contains
# useful data about these options. Functions related to configuration options
# return or accept instances of this type.
#
class _TidyOption(ct.Structure): pass  # { int _opaque; }
TidyOption = ct.POINTER(_TidyOption)  # noqa: E305

# @struct TidyNode
# Single nodes of a TidyDocument are represented by this datatype. It can be
# returned by various API functions, or accepted as a function argument.
#
class _TidyNode(ct.Structure): pass  # { int _opaque; }
TidyNode = ct.POINTER(_TidyNode)  # noqa: E305

# @struct TidyAttr
# Attributes of a TidyNode are represented by this data type. The public API
# functions related to attributes work with this type.
#
class _TidyAttr(ct.Structure): pass  # { int _opaque; }
TidyAttr = ct.POINTER(_TidyAttr)  # noqa: E305

# @struct TidyMessage
# Instances of this type represent messages generated by Tidy in reference
# to your document. This API is available in some of Tidy's message callback
# functions.
#
class _TidyMessage(ct.Structure): pass  # { int _opaque; }
TidyMessage = ct.POINTER(_TidyMessage)  # noqa: E305

# @struct TidyMessageArgument
# Instances of this type represent the arguments that compose part of the
# message represented by TidyMessage. These arguments have an API to query
# information about them.
#
class _TidyMessageArgument(ct.Structure): pass  # { int _opaque; }
TidyMessageArgument = ct.POINTER(_TidyMessageArgument)  # noqa: E305

# @} end Opaque group

# MARK: - Memory Allocation
# **************************************************************************** #
# @defgroup Memory Memory Allocation
#
# Tidy can use a user-provided allocator for all memory allocations.  If this
# allocator is not provided, then a default allocator is used which simply
# wraps standard C malloc()/free() calls. These wrappers call the panic()
# function upon any failure. The default panic function prints an out of
# memory message to **stderr**, and calls `exit(2)`.
#
# For applications in which it is unacceptable to abort in the case of memory
# allocation, then the panic function can be replaced with one which
# `longjmps()` out of the LibTidy code. For this to clean up completely, you
# should be careful not to use any Tidy methods that open files as these will
# not be closed before `panic()` is called.
#
# Calling the `xxxWithAllocator()` family (`tidyCreateWithAllocator`,
# `tidyBufInitWithAllocator`, `tidyBufAllocWithAllocator`) allow setting
# custom allocators.
#
# All parts of the document use the same allocator. Calls that require a
# user-provided buffer can optionally use a different allocator.
#
# For reference in designing a plug-in allocator, most allocations made by
# LibTidy are less than 100 bytes, corresponding to attribute names and
# values, etc.
#
# There is also an additional class of much larger allocations which are where
# most of the data from the lexer is stored. It is not currently possible to
# use a separate allocator for the lexer; this would be a useful extension.
#
# In general, approximately 1/3rd of the memory used by LibTidy is freed
# during the parse, so if memory usage is an issue then an allocator that can
# reuse this memory is a good idea.
#
# **To create your own allocator, do something like the following:**
# @code{.c}
# typedef struct _MyAllocator {
#    TidyAllocator base;
#    // ...other custom allocator state...
# } MyAllocator;
#
# ct.c_void_p MyAllocator_alloc(TidyAllocator *base, void *block, size_t nBytes) {
#     MyAllocator *self = (MyAllocator*)base;
#     // ...
# }
# // etc.
#
# static const TidyAllocatorVtbl MyAllocatorVtbl = {
#     MyAllocator_alloc,
#     MyAllocator_realloc,
#     MyAllocator_free,
#     MyAllocator_panic
# };
#
# myAllocator allocator;
# TidyDoc doc;
#
# allocator.base.vtbl = &MyAllocatorVtbl;
# //...initialise allocator specific state...
# doc = tidyCreateWithAllocator(&allocator);
# @endcode
#
# Although this looks slightly long-winded, the advantage is that to create a
# custom allocator you simply need to set the vtbl pointer correctly. The vtbl
# itself can reside in static/global data, and hence does not need to be
# initialised each time an allocator is created, and furthermore the memory
# is shared amongst all created allocators.
#
# @{
# **************************************************************************** #

class TidyAllocatorVtbl(ct.Structure):
    # This structure is the function table for an allocator.
    # Note that all functions in this table must be provided.
    #
    pass

class TidyAllocator(ct.Structure):
    # Tidy's built-in default allocator.
    _fields_ = [
    ("vtbl", ct.POINTER(TidyAllocatorVtbl)),  # The allocator's function table.
]

TidyAllocatorVtbl._fields_ = [  # noqa: E305

    # Called to allocate a block of nBytes of memory
    #
    ("*alloc",  CFUNC(ct.c_void_p,
                      ct.POINTER(TidyAllocator),  # self   # TidyAllocator to use to alloc memory.
                      ct.c_size_t)),              # nBytes # The number of bytes to allocate.

    # Called to resize (grow, in general) a block of memory.
    # Must support being called with `NULL`.
    #
    ("realloc", CFUNC(ct.c_void_p,
                      ct.POINTER(TidyAllocator),  # self,  # TidyAllocator to use to realloc mem.
                      ct.c_void_p,                # block  # The pointer to the existing block.
                      ct.c_size_t)),              # nBytes # The number of bytes to allocate.

    # Called to free a previously allocated block of memory.
    #
    ("free",    CFUNC(None,
                      ct.POINTER(TidyAllocator),  # self, # TidyAllocator to use to free memory.
                      ct.c_void_p)),              # block # The block to free.

    # Called when a panic condition is detected. Must support `block == NULL`.
    # This function is not called if either alloc() or realloc() fails; it is
    # up to the allocator to do this. Currently this function can only be
    # called if an error is detected in the tree integrity via the internal
    # function CheckNodeIntegrity(). This is a situation that can only arise
    # in the case of a programming error in LibTidy. You can turn off node
    # integrity checking by defining the constant `NO_NODE_INTEGRITY_CHECK`
    # during the build.
    #
    ("panic",   CFUNC(None,
                      ct.POINTER(TidyAllocator),  # self # TidyAllocator to use to panic.
                      ctmbstr)),                  # msg  # The panic message.
]

# Callback for `malloc` replacement
TidyMalloc = CFUNC(ct.c_void_p,
                   ct.c_size_t)  # len

# Callback for `realloc` replacement
TidyRealloc = CFUNC(ct.c_void_p,
                    ct.c_void_p,  # buf
                    ct.c_size_t)  # len

# Callback for `free` replacement
TidyFree = CFUNC(None,
                 ct.c_void_p)  # buf

# Callback for out of memory panic state
TidyPanic = CFUNC(None,
                  ctmbstr)  # mssg

# Give Tidy a `malloc()` replacement
SetMallocCall = CFUNC(ct.c_bool,
    TidyMalloc)(
    ("tidySetMallocCall", dll), (
    (1, "fmalloc"),))

# Give Tidy a `realloc()` replacement
SetReallocCall = CFUNC(ct.c_bool,
    TidyRealloc)(
    ("tidySetReallocCall", dll), (
    (1, "frealloc"),))

# Give Tidy a `free()` replacement
SetFreeCall = CFUNC(ct.c_bool,
    TidyFree)(
    ("tidySetFreeCall", dll), (
    (1, "ffree"),))

# Give Tidy an "out of memory" handler
SetPanicCall = CFUNC(ct.c_bool,
    TidyPanic)(
    ("tidySetPanicCall", dll), (
    (1, "fpanic"),))

# @} end Memory group

# MARK: - Basic Operations
# **************************************************************************** #
# @defgroup Basic Basic Operations
#
# For an excellent example of how to invoke LibTidy, please consult
# `console/tidy.c:main()` for in-depth implementation details. A simplified
# example can be seen on our site: https://www.html-tidy.org/developer/
#
# @{
# **************************************************************************** #

# @name Instantiation and Destruction
# @{

# The primary creation of a document instance. Instances of a TidyDoc are used
# throughout the API as a token to represent a particular document. You must
# create at least one TidyDoc instance to initialize the library and begin
# interaction with the API. When done using a TidyDoc instance, be sure to
# `tidyRelease(myTidyDoc);` in order to free related memory.
# @result Returns a TidyDoc instance.
#
Create = CFUNC(TidyDoc)(
    ("tidyCreate", dll),)

# Create a document supplying your own, custom TidyAllocator instead of using
# the built-in default. See the @ref Memory module if you want to create and
# use your own allocator.
# @param allocator The allocator to use for creating the document.
# @result Returns a TidyDoc instance.
#
CreateWithAllocator = CFUNC(TidyDoc,
    ct.POINTER(TidyAllocator))(
    ("tidyCreateWithAllocator", dll), (
    (1, "allocator"),))

# Free all memory and release the TidyDoc. The TidyDoc can not be used after
# this call.
# @param tdoc The TidyDoc to free.
#
Release = CFUNC(None,
    TidyDoc)(
    ("tidyRelease", dll), (
    (1, "tdoc"),))

# @}
# @name Host Application Data
# @{

# Allows the host application to store a chunk of data with each TidyDoc
# instance. This can be useful for callbacks, such as saving a reference to
# `self` within the document.
#
SetAppData = CFUNC(None,
    TidyDoc,       # The document in which to store the data.
    ct.c_void_p)(  # The pointer to a block of data to store.
    ("tidySetAppData", dll), (
    (1, "tdoc"),
    (1, "appData"),))

# Returns the data previously stored with `tidySetAppData()`.
# @param tdoc  document where data has been stored.
# @result The pointer to the data block previously stored.
#
GetAppData = CFUNC(ct.c_void_p,
    TidyDoc)(
    ("tidyGetAppData", dll), (
    (1, "tdoc"),))

# @}
# @name LibTidy Version Information
# @{

# Get the release date for the current library.
# @result The string representing the release date.
#
ReleaseDate = CFUNC(ctmbstr)(
    ("tidyReleaseDate", dll),)

# Get the version number for the current library.
# @result The string representing the version number.
#
LibraryVersion = CFUNC(ctmbstr)(
    ("tidyLibraryVersion", dll),)

# Get the platform for which Tidy was built.
# @result The string representing the version number.
#
Platform = CFUNC(ctmbstr)(
    ("tidyPlatform", dll),)

# @}
# @name Diagnostics and Repair
# @{

# Get status of current document.
# @param tdoc An instance of a TidyDoc to query.
# @result Returns the highest of `2` indicating that errors were present in
#         the document, `1` indicating warnings, and `0` in the case of
#         everything being okay.
#
Status = CFUNC(ct.c_int,
    TidyDoc)(
    ("tidyStatus", dll), (
    (1, "tdoc"),))

# Gets the version of HTML that was output, as an integer, times 100. For
# example, HTML5 will return 500; HTML4.0.1 will return 401.
# @param tdoc An instance of a TidyDoc to query.
# @result Returns the HTML version number (x100).
#
DetectedHtmlVersion = CFUNC(ct.c_int,
    TidyDoc)(
    ("tidyDetectedHtmlVersion", dll), (
    (1, "tdoc"),))

# Indicates whether the output document is or isn't XHTML.
# @param tdoc An instance of a TidyDoc to query.
# @result Returns `yes` if the document is an XHTML type.
#
DetectedXhtml = CFUNC(ct.c_bool,
    TidyDoc)(
    ("tidyDetectedXhtml", dll), (
    (1, "tdoc"),))

# Indicates whether or not the input document was XML. If TidyXml tags is
# true, or there was an XML declaration in the input document, then this
# function will return yes.
# @param tdoc An instance of a TidyDoc to query.
# @result Returns `yes` if the input document was XML.
#
DetectedGenericXml = CFUNC(ct.c_bool,
    TidyDoc)(
    ("tidyDetectedGenericXml", dll), (
    (1, "tdoc"),))

# Indicates the number of TidyError messages that were generated. For any
# value greater than `0`, output is suppressed unless TidyForceOutput is set.
# @param tdoc An instance of a TidyDoc to query.
# @result Returns the number of TidyError messages that were generated.
#
ErrorCount = CFUNC(ct.c_uint,
    TidyDoc)(
    ("tidyErrorCount", dll), (
    (1, "tdoc"),))

# Indicates the number of TidyWarning messages that were generated.
# @param tdoc An instance of a TidyDoc to query.
# @result Returns the number of TidyWarning messages that were generated.
#
WarningCount = CFUNC(ct.c_uint,
    TidyDoc)(
    ("tidyWarningCount", dll), (
    (1, "tdoc"),))

# Indicates the number of TidyAccess messages that were generated.
# @param tdoc An instance of a TidyDoc to query.
# @result Returns the number of TidyAccess messages that were generated.
#
AccessWarningCount = CFUNC(ct.c_uint,
    TidyDoc)(
    ("tidyAccessWarningCount", dll), (
    (1, "tdoc"),))

# Indicates the number of configuration error messages that were generated.
# @param tdoc An instance of a TidyDoc to query.
# @result Returns the number of configuration error messages that were
#         generated.
#
ConfigErrorCount = CFUNC(ct.c_uint,
    TidyDoc)(
    ("tidyConfigErrorCount", dll), (
    (1, "tdoc"),))

# Write more complete information about errors to current error sink.
# @param tdoc An instance of a TidyDoc to query.
#
ErrorSummary = CFUNC(None,
    TidyDoc)(
    ("tidyErrorSummary", dll), (
    (1, "tdoc"),))

# Write more general information about markup to current error sink.
# @param tdoc An instance of a TidyDoc to query.
#
GeneralInfo = CFUNC(None,
    TidyDoc)(
    ("tidyGeneralInfo", dll), (
    (1, "tdoc"),))

# @}
# @name Configuration, File, and Encoding Operations
# @{

# Load an ASCII Tidy configuration file and set the configuration per its
# contents. Reports config option errors, which can be filtered.
# @result Returns 0 upon success, or any other value if there was an option error.
#
LoadConfig = CFUNC(ct.c_int,
    TidyDoc,   # The TidyDoc to which to apply the configuration.
    ctmbstr)(  # The complete path to the file to load.
    ("tidyLoadConfig", dll), (
    (1, "tdoc"),
    (1, "configFile"),))

# Load a Tidy configuration file with the specified character encoding, and
# set the configuration per its contents.  Reports config option errors, which can be filtered.
# @result Returns 0 upon success, or any other value if there was an option error.
#
LoadConfigEnc = CFUNC(ct.c_int,
    TidyDoc,   # The TidyDoc to which to apply the configuration.
    ctmbstr,   # The complete path to the file to load.
    ctmbstr)(  # The encoding to use. See the _enc2iana struct for valid values.
    ("tidyLoadConfigEnc", dll), (
    (1, "tdoc"),
    (1, "configFile"),
    (1, "charenc"),))

# Determine whether or not a particular file exists. On Unix systems, the use
# of the tilde to represent the user's home directory is supported.
# @result Returns `yes` or `no`, indicating whether or not the file exists.
#
FileExists = CFUNC(ct.c_bool,
    TidyDoc,   # The TidyDoc on whose behalf you are checking.
    ctmbstr)(  # The path to the file whose existence you wish to check.
    ("tidyFileExists", dll), (
    (1, "tdoc"),
    (1, "filename"),))

# Set the input/output character encoding for parsing markup. Valid values
# include `ascii`, `latin1`, `raw`, `utf8`, `iso2022`, `mac`, `win1252`,
# `utf16le`, `utf16be`, `utf16`, `big5`, and `shiftjis`. These values are not
# case sensitive.
# @note This is the same as using TidySetInCharEncoding() and
#       TidySetOutCharEncoding() to set the same value.
# @result Returns 0 upon success, or a system standard error number `EINVAL`.
#
SetCharEncoding = CFUNC(ct.c_int,
    TidyDoc,   # The TidyDoc for which you are setting the encoding.
    ctmbstr)(  # The encoding name as described above.
    ("tidySetCharEncoding", dll), (
    (1, "tdoc"),
    (1, "encnam"),))

# Set the input encoding for parsing markup.  Valid values include `ascii`,
# `latin1`, `raw`, `utf8`, `iso2022`, `mac`, `win1252`, `utf16le`, `utf16be`,
# `utf16`, `big5`, and `shiftjis`. These values are not case sensitive.
# @result Returns 0 upon success, or a system standard error number `EINVAL`.
#
SetInCharEncoding = CFUNC(ct.c_int,
    TidyDoc,   # The TidyDoc for which you are setting the encoding.
    ctmbstr)(  # The encoding name as described above.
    ("tidySetInCharEncoding", dll), (
    (1, "tdoc"),
    (1, "encnam"),))

# Set the input encoding for writing markup.  Valid values include `ascii`,
# `latin1`, `raw`, `utf8`, `iso2022`, `mac`, `win1252`, `utf16le`, `utf16be`,
# `utf16`, `big5`, and `shiftjis`. These values are not case sensitive.
# @result Returns 0 upon success, or a system standard error number `EINVAL`.
#
SetOutCharEncoding = CFUNC(ct.c_int,
    TidyDoc,   # The TidyDoc for which you are setting the encoding.
    ctmbstr)(  # The encoding name as described above.
    ("tidySetOutCharEncoding", dll), (
    (1, "tdoc"),
    (1, "encnam"),))

# @}
# @} end Basic group

# MARK: - Configuration Options
# **************************************************************************** #
# @defgroup Configuration Configuration Options
#
# Functions for getting and setting Tidy configuration options.
#
# @note In general, you should expect that options you set should stay set.
#       This isn't always the case, though, because Tidy will adjust options
#       for internal use during the lexing, parsing, cleaning, and printing
#       phases. If you require access to user configuration values at any
#       time after the tidyParseXXX() process, make sure to keep your own
#       copy, or use tidyOptResetToSnapshot() when you no longer need to
#       use any other tidy functions.
# @{
# **************************************************************************** #

# @name Option Callback Functions
# @{

# This typedef represents the required signature for your provided callback
# function should you wish to register one with tidySetOptionCallback().
# Your callback function will be provided with the following parameters.
# Note that this is deprecated and you should instead migrate to
# tidySetConfigCallback().
# @param option The option name that was provided.
# @param value The option value that was provided
# @return Your callback function will return `yes` if it handles the provided
#         option, or `no` if it does not. In the latter case, Tidy will issue
#         an unknown configuration option error.
#
TidyOptCallback = CFUNC(ct.c_bool,
                        ctmbstr,  # option
                        ctmbstr)  # value

# Applications using TidyLib may want to augment command-line and
# configuration file options. Setting this callback allows a LibTidy
# application developer to examine command-line and configuration file options
# after LibTidy has examined them and failed to recognize them.
# Note that this is deprecated and you should instead migrate to
# tidySetConfigCallback().
# @result Returns `yes` upon success.
#
SetOptionCallback = CFUNC(ct.c_bool,
    TidyDoc,           # The document to apply the callback to.
    TidyOptCallback)(  # The name of a function of type TidyOptCallback()
                       # to serve as your callback.
    ("tidySetOptionCallback", dll), (
    (1, "tdoc"),
    (1, "pOptCallback"),))

# This typedef represents the required signature for your provided callback
# function should you wish to register one with tidySetConfigCallback().
# Your callback function will be provided with the following parameters.
# @param tdoc The document instance for which the callback was invoked.
# @param option The option name that was provided.
# @param value The option value that was provided
# @return Your callback function will return `yes` if it handles the provided
#         option, or `no` if it does not. In the latter case, Tidy will issue
#         an unknown configuration option error.
#
TidyConfigCallback = CFUNC(ct.c_bool,
                           TidyDoc,  # tdoc
                           ctmbstr,  # option
                           ctmbstr)  # value

# Applications using TidyLib may want to augment command-line and
# configuration file options. Setting this callback allows a LibTidy
# application developer to examine command-line and configuration file options
# after LibTidy has examined them and failed to recognize them.
# @result Returns `yes` upon success.
#
SetConfigCallback = CFUNC(ct.c_bool,
    TidyDoc,              # The document to apply the callback to.
    TidyConfigCallback)(  # The name of a function of type TidyConfigCallback()
                          # to serve as your callback.
    ("tidySetConfigCallback", dll), (
    (1, "tdoc"),
    (1, "pConfigCallback"),))

# This typedef represents the required signature for your provided callback
# function should you wish to register one with tidySetConfigChangeCallback().
# Your callback function will be provided with the following parameters.
# @param tdoc The document instance for which the callback was invoked.
# @param option The option that will be changed.
#
TidyConfigChangeCallback = CFUNC(None,
                                 TidyDoc,     # tdoc
                                 TidyOption)  # option

# Applications using TidyLib may want to be informed when changes to options
# are made. Temporary changes made internally by Tidy are not reported, but
# permanent changes made by Tidy (such as indent-spaces or output-encoding)
# will be reported.
# @note This callback is not currently implemented.
# @result Returns `yes` upon success.
#
SetConfigChangeCallback = CFUNC(ct.c_bool,
    TidyDoc,                    # The document to apply the callback to.
    TidyConfigChangeCallback)(  # The name of a function of type
                                # TidyConfigChangeCallback() to serve as
                                # your callback.
    ("tidySetConfigChangeCallback", dll), (
    (1, "tdoc"),
    (1, "pCallback"),))

# @}
# @name Option ID Discovery
# @{

# Get ID of given Option
# @param opt An instance of a TidyOption to query.
# @result The TidyOptionId of the given option.
#
OptGetId = CFUNC(TidyOptionId,
    TidyOption)(
    ("tidyOptGetId", dll), (
    (1, "opt"),))

# Returns the TidyOptionId (enum value) by providing the name of a Tidy
# configuration option.
# @param optnam The name of the option ID to retrieve.
# @result The TidyOptionId of the given `optname`.
#
OptGetIdForName = CFUNC(TidyOptionId,
    ctmbstr)(
    ("tidyOptGetIdForName", dll), (
    (1, "optnam"),))

# @}
# @name Getting Instances of Tidy Options
# @{

# Initiates an iterator for a list of TidyOption instances, which allows you
# to iterate through all of the available options. In order to iterate through
# the available options, initiate the iterator with this function, and then
# use tidyGetNextOption() to retrieve the first and subsequent options. For
# example:
# @code{.c}
#   TidyIterator itOpt = tidyGetOptionList( tdoc );
#   while ( itOpt ) {
#     TidyOption opt = tidyGetNextOption( tdoc, &itOpt );
#     // Use other API to query or set set option values
#   }
# @endcode
# @param tdoc An instance of a TidyDoc to query.
# @result Returns a TidyIterator, which is a token used to represent the
#         current position in a list within LibTidy.
#
GetOptionList = CFUNC(TidyIterator,
    TidyDoc)(
    ("tidyGetOptionList", dll), (
    (1, "tdoc"),))

# Given a valid TidyIterator initiated with tidyGetOptionList(), returns
# the instance of the next TidyOption.
# @note This function will return internal-only option types including
#       `TidyInternalCategory`; you should *never* use these. Always ensure
#       that you use `tidyOptGetCategory()` before assuming that an option
#       is okay to use in your application.
# @result An instance of TidyOption.
#
GetNextOption = CFUNC(TidyOption,
    TidyDoc,                    # The document for which you are retrieving options.
    ct.POINTER(TidyIterator))(  # The TidyIterator (initiated with tidyGetOptionList())
                                # token.
    ("tidyGetNextOption", dll), (
    (1, "tdoc"),
    (1, "pos"),))

# Retrieves an instance of TidyOption given a valid TidyOptionId.
# @result An instance of TidyOption matching the provided TidyOptionId.
#
GetOption = CFUNC(TidyOption,
    TidyDoc,        # The document for which you are retrieving the option.
    TidyOptionId)(  # The TidyOptionId to retrieve.
    ("tidyGetOption", dll), (
    (1, "tdoc"),
    (1, "optId"),))

# Returns an instance of TidyOption by providing the name of a Tidy
# configuration option.
# @result The TidyOption of the given `optname`.
#
GetOptionByName = CFUNC(TidyOption,
    TidyDoc,   # The document for which you are retrieving the option.
    ctmbstr)(  # The name of the Tidy configuration option.
    ("tidyGetOptionByName", dll), (
    (1, "tdoc"),
    (1, "optnam"),))

# @}
# @name Information About Options
# @{

# Get name of given Option
# @param opt An instance of a TidyOption to query.
# @result The name of the given option.
#
OptGetName = CFUNC(ctmbstr,
    TidyOption)(
    ("tidyOptGetName", dll), (
    (1, "opt"),))

# Get datatype of given Option
# @param opt An instance of a TidyOption to query.
# @result The TidyOptionType of the given option.
#
OptGetType = CFUNC(TidyOptionType,
    TidyOption)(
    ("tidyOptGetType", dll), (
    (1, "opt"),))

# Indicates that an option takes a list of items.
# @param opt An instance of a TidyOption to query.
# @result A bool indicating whether or not the option accepts a list.
#
OptionIsList = CFUNC(ct.c_bool,
    TidyOption)(
    ("tidyOptionIsList", dll), (
    (1, "opt"),))

# Is Option read-only? Some options (mainly internal use only options) are
# read-only.
# @deprecated This is no longer a valid test for the public API; instead
#   you should test an option's availability using `tidyOptGetCategory()`
#   against `TidyInternalCategory`. This API will be removed!
# @param opt An instance of a TidyOption to query.
# @result Returns `yes` or `no` depending on whether or not the specified
#         option is read-only.
#
OptIsReadOnly = CFUNC(ct.c_bool,
    TidyOption)(
    ("tidyOptIsReadOnly", dll), (
    (1, "opt"),))

# Get category of given Option
# @param opt An instance of a TidyOption to query.
# @result The TidyConfigCategory of the specified option.
#
OptGetCategory = CFUNC(TidyConfigCategory,
    TidyOption)(
    ("tidyOptGetCategory", dll), (
    (1, "opt"),))

# Get default value of given Option as a string
# @param opt An instance of a TidyOption to query.
# @result A string indicating the default value of the specified option.
#
OptGetDefault = CFUNC(ctmbstr,
    TidyOption)(
    ("tidyOptGetDefault", dll), (
    (1, "opt"),))

# Get default value of given Option as an unsigned integer
# @param opt An instance of a TidyOption to query.
# @result An unsigned integer indicating the default value of the specified
#         option.
#
OptGetDefaultInt = CFUNC(ct.c_ulong,
    TidyOption)(
    ("tidyOptGetDefaultInt", dll), (
    (1, "opt"),))

# Get default value of given Option as a Boolean value
# @param opt An instance of a TidyOption to query.
# @result A boolean indicating the default value of the specified option.
#
OptGetDefaultBool = CFUNC(ct.c_bool,
    TidyOption)(
    ("tidyOptGetDefaultBool", dll), (
    (1, "opt"),))

# Initiates an iterator for a list of TidyOption pick-list values, which
# allows you iterate through all of the available option values. In order to
# iterate through the available values, initiate the iterator with this
# function, and then use tidyOptGetNextPick() to retrieve the first and
# subsequent option values. For example:
# @code{.c}
#   TidyIterator itOpt = tidyOptGetPickList( opt );
#   while ( itOpt ) {
#     printf("%s", tidyOptGetNextPick( opt, &itOpt ));
#   }
# @endcode
# @param opt An instance of a TidyOption to query.
# @result Returns a TidyIterator, which is a token used to represent the
#         current position in a list within LibTidy.
#
OptGetPickList = CFUNC(TidyIterator,
    TidyOption)(
    ("tidyOptGetPickList", dll), (
    (1, "opt"),))

# Given a valid TidyIterator initiated with tidyOptGetPickList(), returns a
# string representing a possible option value.
# @result A string containing the next pick-list option value.
#
OptGetNextPick = CFUNC(ctmbstr,
    TidyOption,                 # An instance of a TidyOption to query.
    ct.POINTER(TidyIterator))(  # The TidyIterator (initiated with
                                # tidyOptGetPickList()) token.
    ("tidyOptGetNextPick", dll), (
    (1, "opt"),
    (1, "pos"),))

# @}
# @name Option Value Functions
# @{

# Get the current value of the option ID for the given document.
# @remark The optId *must* have a @ref TidyOptionType of @ref TidyString!
#
OptGetValue = CFUNC(ctmbstr,
    TidyDoc,        # The tidy document whose option value you wish to check.
    TidyOptionId)(  # The option ID whose value you wish to check.
    ("tidyOptGetValue", dll), (
    (1, "tdoc"),
    (1, "optId"),))

# Set the option value as a string.
# @remark The optId *must* have a @ref TidyOptionType of @ref TidyString!
# @result Returns a bool indicating success or failure.
#
OptSetValue = CFUNC(ct.c_bool,
    TidyDoc,       # The tidy document for which to set the value.
    TidyOptionId,  # The option ID of the value to set.
    ctmbstr)(      # The string value to set.
    ("tidyOptSetValue", dll), (
    (1, "tdoc"),
    (1, "optId"),
    (1, "val"),))

# Set named option value as a string, regardless of the @ref TidyOptionType.
# @remark This is good setter if you are unsure of the type.
# @result Returns a bool indicating success or failure.
#
OptParseValue = CFUNC(ct.c_bool,
    TidyDoc,   # The tidy document for which to set the value.
    ctmbstr,   # The name of the option to set; this is the string value
               # from the UI, e.g., `error-file`.
    ctmbstr)(  # The value to set, as a string.
    ("tidyOptParseValue", dll), (
    (1, "tdoc"),
    (1, "optnam"),
    (1, "val"),))

# Get current option value as an integer.
# @result Returns the integer value of the specified option.
#
OptGetInt = CFUNC(ct.c_ulong,
    TidyDoc,        # The tidy document for which to get the value.
    TidyOptionId)(  # The option ID to get.
    ("tidyOptGetInt", dll), (
    (1, "tdoc"),
    (1, "optId"),))

# Set option value as an integer.
# @result Returns a bool indicating success or failure.
#
OptSetInt = CFUNC(ct.c_bool,
    TidyDoc,       # The tidy document for which to set the value.
    TidyOptionId,  # The option ID to set.
    ct.c_ulong)(   # The value to set.
    ("tidyOptSetInt", dll), (
    (1, "tdoc"),
    (1, "optId"),
    (1, "val"),))

# Get current option value as a Boolean flag.
# @result Returns a bool indicating the value.
#
OptGetBool = CFUNC(ct.c_bool,
    TidyDoc,        # The tidy document for which to get the value.
    TidyOptionId)(  # The option ID to get.
    ("tidyOptGetBool", dll), (
    (1, "tdoc"),
    (1, "optId"),))

# Set option value as a Boolean flag.
# @result Returns a bool indicating success or failure.
#
OptSetBool = CFUNC(ct.c_bool,
    TidyDoc,       # The tidy document for which to set the value.
    TidyOptionId,  # The option ID to set.
    ct.c_bool)(    # The value to set.
    ("tidyOptSetBool", dll), (
    (1, "tdoc"),
    (1, "optId"),
    (1, "val"),))

# Reset option to default value by ID.
# @result Returns a bool indicating success or failure.
#
OptResetToDefault = CFUNC(ct.c_bool,
    TidyDoc,        # The tidy document for which to reset the value.
    TidyOptionId)(  # The option ID to reset.
    ("tidyOptResetToDefault", dll), (
    (1, "tdoc"),
    (1, "opt"),))

# Reset all options to their default values.
# @param tdoc The tidy document for which to reset all values.
# @result Returns a bool indicating success or failure.
#
OptResetAllToDefault = CFUNC(ct.c_bool,
    TidyDoc)(
    ("tidyOptResetAllToDefault", dll), (
    (1, "tdoc"),))

# Take a snapshot of current config settings. These settings are stored
# within the tidy document. Note, however, that snapshots do not reliably
# survive the tidyParseXXX() process, as Tidy uses the snapshot mechanism
# in order to store the current configuration right at the beginning of the
# parsing process.
# @param tdoc The tidy document for which to take a snapshot.
# @result Returns a bool indicating success or failure.
#
OptSnapshot = CFUNC(ct.c_bool,
    TidyDoc)(
    ("tidyOptSnapshot", dll), (
    (1, "tdoc"),))

# Apply a snapshot of config settings to a document.
# @param tdoc The tidy document for which to apply a snapshot.
# @result Returns a bool indicating success or failure.
#
OptResetToSnapshot = CFUNC(ct.c_bool,
    TidyDoc)(
    ("tidyOptResetToSnapshot", dll), (
    (1, "tdoc"),))

# Any settings different than default?
# @param tdoc The tidy document to check.
# @result Returns a bool indicating whether or not a difference exists.
#
OptDiffThanDefault = CFUNC(ct.c_bool,
    TidyDoc)(
    ("tidyOptDiffThanDefault", dll), (
    (1, "tdoc"),))

# Any settings different than snapshot?
# @param tdoc The tidy document to check.
# @result Returns a bool indicating whether or not a difference exists.
#
OptDiffThanSnapshot = CFUNC(ct.c_bool,
    TidyDoc)(
    ("tidyOptDiffThanSnapshot", dll), (
    (1, "tdoc"),))

# Copy current configuration settings from one document to another. Note
# that the destination document's existing settings will be stored as that
# document's snapshot prior to having its option values overwritten by the
# source document's settings.
# @result Returns a bool indicating success or failure.
#
OptCopyConfig = CFUNC(ct.c_bool,
    TidyDoc,   # The destination tidy document.
    TidyDoc)(  # The source tidy document.
    ("tidyOptCopyConfig", dll), (
    (1, "tdocTo"),
    (1, "tdocFrom"),))

# Get character encoding name. Used with @ref TidyCharEncoding,
# @ref TidyOutCharEncoding, and @ref TidyInCharEncoding.
# @result The encoding name as a string for the specified option.
#
OptGetEncName = CFUNC(ctmbstr,
    TidyDoc,        # The tidy document to query.
    TidyOptionId)(  # The option ID whose value to check.
    ("tidyOptGetEncName", dll), (
    (1, "tdoc"),
    (1, "optId"),))

# Get the current pick list value for the option ID, which can be useful for
# enum types.
# @result Returns a string indicating the current value of the specified
#         option.
#
OptGetCurrPick = CFUNC(ctmbstr,
    TidyDoc,        # The tidy document to query.
    TidyOptionId)(  # The option ID whose value to check.
    ("tidyOptGetCurrPick", dll), (
    (1, "tdoc"),
    (1, "optId"),))

# Initiates an iterator for a list of user-declared tags, including autonomous
# custom tags detected in the document if @ref TidyUseCustomTags is not set to
# **no**. This iterator allows you to iterate through all of the custom tags.
# In order to iterate through the tags, initiate the iterator with this
# function, and then use tidyOptGetNextDeclTag() to retrieve the first and
# subsequent tags. For example:
# @code{.c}
#   TidyIterator itTag = tidyOptGetDeclTagList( tdoc );
#   while ( itTag ) {
#     printf("%s", tidyOptGetNextDeclTag( tdoc, TidyBlockTags, &itTag ));
#   }
# @endcode
# @param tdoc An instance of a TidyDoc to query.
# @result Returns a TidyIterator, which is a token used to represent the
#         current position in a list within LibTidy.
#
OptGetDeclTagList = CFUNC(TidyIterator,
    TidyDoc)(
    ("tidyOptGetDeclTagList", dll), (
    (1, "tdoc"),))

# Given a valid TidyIterator initiated with tidyOptGetDeclTagList(), returns a
# string representing a user-declared or autonomous custom tag.
# @remark Specifying optId limits the scope of the tags to one of
#         @ref TidyInlineTags, @ref TidyBlockTags, @ref TidyEmptyTags, or
#         @ref TidyPreTags. Note that autonomous custom tags (if used) are
#         added to one of these option types, depending on the value of
#         @ref TidyUseCustomTags.
# @result A string containing the next tag.
#
OptGetNextDeclTag = CFUNC(ctmbstr,
    TidyDoc,                    # The tidy document to query.
    TidyOptionId,               # The option ID matching the type of tag to retrieve.
    ct.POINTER(TidyIterator))(  # The TidyIterator (initiated with
                                # tidyOptGetDeclTagList()) token.
    ("tidyOptGetNextDeclTag", dll), (
    (1, "tdoc"),
    (1, "optId"),
    (1, "iter"),))

# Initiates an iterator for a list of priority attributes. This iterator
# allows you to iterate through all of the priority attributes defined with
# the `priority-attributes` configuration option. In order to iterate through
# the attributes, initiate the iterator with this function, and then use
# tidyOptGetNextPriorityAttr() to retrieve the first and subsequent attributes.
# For example:
# @code{.c}
#   TidyIterator itAttr = tidyOptGetPriorityAttrList( tdoc );
#   while ( itAttr ) {
#     printf("%s", tidyOptGetNextPriorityAttr( tdoc, &itAttr ));
#   }
# @endcode
# @param tdoc An instance of a TidyDoc to query.
# @result Returns a TidyIterator, which is a token used to represent the
#         current position in a list within LibTidy.
#
OptGetPriorityAttrList = CFUNC(TidyIterator,
    TidyDoc)(
    ("tidyOptGetPriorityAttrList", dll), (
    (1, "tdoc"),))

# Given a valid TidyIterator initiated with tidyOptGetPriorityAttrList(),
# returns a string representing a priority attribute.
# @result A string containing the next tag.
#
OptGetNextPriorityAttr = CFUNC(ctmbstr,
    TidyDoc,                    # The tidy document to query.
    ct.POINTER(TidyIterator))(  # The TidyIterator (initiated with
                                # tidyOptGetPriorityAttrList()) token.
    ("tidyOptGetNextPriorityAttr", dll), (
    (1, "tdoc"),
    (1, "iter"),))

# Initiates an iterator for a list of muted messages. This iterator allows
# you to iterate through all of the priority attributes defined with the
# `mute` configuration option. In order to iterate through the list, initiate
# with this function, and then use tidyOptGetNextMutedMessage() to retrieve
# the first and subsequent attributes.
# For example:
# @code{.c}
#   TidyIterator itAttr = tidyOptGetMutedMessageList( tdoc );
#   while ( itAttr ) {
#     printf("%s", tidyOptGetNextMutedMessage( tdoc, &itAttr ));
#   }
# @endcode
# @param tdoc An instance of a TidyDoc to query.
# @result Returns a TidyIterator, which is a token used to represent the
#         current position in a list within LibTidy.
#
OptGetMutedMessageList = CFUNC(TidyIterator,
    TidyDoc)(
    ("tidyOptGetMutedMessageList", dll), (
    (1, "tdoc"),))

# Given a valid TidyIterator initiated with tidyOptGetMutedMessageList(),
# returns a string representing a muted message.
# @result A string containing the next tag.
#
OptGetNextMutedMessage = CFUNC(ctmbstr,
    TidyDoc,                    # The tidy document to query.
    ct.POINTER(TidyIterator))(  # The TidyIterator (initiated with
                                # tidyOptGetMutedMessageList()) token.
    ("tidyOptGetNextMutedMessage", dll), (
    (1, "tdoc"),
    (1, "iter"),))

# @}
# @name Option Documentation
# @{

# Get the description of the specified option.
# @result Returns a string containing a description of the given option.
#
OptGetDoc = CFUNC(ctmbstr,
    TidyDoc,      # The tidy document to query.
    TidyOption)(  # The option ID of the option.
    ("tidyOptGetDoc", dll), (
    (1, "tdoc"),
    (1, "opt"),))

# Initiates an iterator for a list of options related to a given option. This
# iterator allows you to iterate through all of the related options, if any.
# In order to iterate through the options, initiate the iterator with this
# function, and then use tidyOptGetNextDocLinks() to retrieve the first and
# subsequent options. For example:
# @code{.c}
#   TidyIterator itOpt = tidyOptGetDocLinksList( tdoc, TidyJoinStyles );
#   while ( itOpt ) {
#     TidyOption my_option = tidyOptGetNextDocLinks( tdoc, &itOpt );
#     // do something with my_option
#   }
# @endcode
# @result Returns a TidyIterator, which is a token used to represent the
#         current position in a list within LibTidy.
#
try:
    OptGetDocLinksList = CFUNC(TidyIterator,
        TidyDoc,      # The tidy document to query.
        TidyOption)(  # The option whose related options you wish to find.
        ("tidyOptGetDocLinksList", dll), (
        (1, "tdoc"),
        (1, "opt"),))
except: pass  # noqa: E722 # pragma: no cover

# Given a valid TidyIterator initiated with tidyOptGetDocLinksList(), returns
# a TidyOption instance.
# @result Returns in instance of TidyOption.
#
try:
    OptGetNextDocLinks = CFUNC(TidyOption,
        TidyDoc,                    # The tidy document to query.
        ct.POINTER(TidyIterator))(  # The TidyIterator (initiated with
                                    # tidyOptGetDocLinksList()) token.
        ("tidyOptGetNextDocLinks", dll), (
        (1, "tdoc"),
        (1, "pos"),))
except: pass  # noqa: E722 # pragma: no cover

# @}
# @} end Configuration group

# MARK: - I/O and Messages
# **************************************************************************** #
# @defgroup IO I/O and Messages
#
# Tidy provides flexible I/O. By default, Tidy will define, create and use
# instances of input and output handlers for standard C buffered I/O (i.e.,
# `FILE* stdin`, `FILE* stdout`, and `FILE* stderr` for content input,
# content output and diagnostic output, respectively. A `FILE* cfgFile`
# input handler will be used for config files. Command line options will
# just be set directly.
#
# @{
# **************************************************************************** #

# TidyBuffer has been moved from _tidybuffio.py due to cyclic rference
#
# A TidyBuffer is chunk of memory that can be used for multiple I/O purposes
# within Tidy.
# @ingroup IO
#
class TidyBuffer(ct.Structure):
    _fields_ = [
    ("allocator", ct.POINTER(TidyAllocator)),  # Memory allocator
    ("bp",        ct.POINTER(byte)),           # Pointer to bytes
    ("size",      ct.c_uint),                  # Number of bytes currently in use
    ("allocated", ct.c_uint),                  # Number of bytes allocated
    ("next",      ct.c_uint),                  # Offset of current input position
]


# @}
# @name Input Source
# If you wish to write to your own input sources, then these types, structs,
# and functions will allow them to work seamlessly with Tidy.
# @{

# End of input "character"
# define EndOfStream (~0u)

# Input Callback: get next byte of input
TidyGetByteFunc = CFUNC(ct.c_int,
                        ct.c_void_p)  # sourceData

# Input Callback: unget a byte of input
TidyUngetByteFunc = CFUNC(None,
                          ct.c_void_p,  # sourceData
                          byte)         # bt

# Input Callback: is end of input?
TidyEOFFunc = CFUNC(ct.c_bool,
                    ct.c_void_p)  # sourceData

# This type defines an input source capable of delivering raw bytes of input.
#
class TidyInputSource(ct.Structure):
    _fields_ = [
    ("sourceData", ct.c_void_p),        # Input context. Passed to callbacks.
    ("getByte",    TidyGetByteFunc),    # Pointer to "get byte" callback.
    ("ungetByte",  TidyUngetByteFunc),  # Pointer to "unget" callback.
    ("eof",        TidyEOFFunc),        # Pointer to "eof" callback.
]


# Facilitates user defined source by providing an entry point to marshal
# pointers-to-functions. This is needed by .NET, and possibly other language
# bindings.
# @result Returns a bool indicating success or failure.
#
InitSource = CFUNC(ct.c_bool,
    ct.POINTER(TidyInputSource),  # The source to populate with data.
    ct.c_void_p,                  # The input context.
    TidyGetByteFunc,              # Pointer to the "get byte" callback.
    TidyUngetByteFunc,            # Pointer to the "unget" callback.
    TidyEOFFunc)(                 # Pointer to the "eof" callback.
    ("tidyInitSource", dll), (
    (1, "source"),
    (1, "srcData"),
    (1, "gbFunc"),
    (1, "ugbFunc"),
    (1, "endFunc"),))

# Helper: get next byte from input source.
# @param source A pointer to your input source.
# @result Returns a byte as an unsigned integer.
#
GetByte = CFUNC(ct.c_uint,
    ct.POINTER(TidyInputSource))(
    ("tidyGetByte", dll), (
    (1, "source"),))

# Helper: unget byte back to input source.
UngetByte = CFUNC(None,
    ct.POINTER(TidyInputSource),  # The input source.
    ct.c_uint)(                   # The byte to push back.
    ("tidyUngetByte", dll), (
    (1, "source"),
    (1, "byteValue"),))

# Helper: check if input source at end.
# @param source The input source.
# @result Returns a bool indicating whether or not the source is at EOF.
#
IsEOF = CFUNC(ct.c_bool,
    ct.POINTER(TidyInputSource))(
    ("tidyIsEOF", dll), (
    (1, "source"),))

# @}
# @name Output Sink
# @{

# Output callback: send a byte to output
TidyPutByteFunc = CFUNC(None,
                        ct.c_void_p,  # sinkData
                        byte)         # bt

# This type defines an output destination capable of accepting raw bytes
# of output
#
class TidyOutputSink(ct.Structure):
    _fields_ = [
    ("sinkData", ct.c_void_p),      # Output context. Passed to callbacks.
    ("putByte",  TidyPutByteFunc),  # Pointer to "put byte" callback
]


# Facilitates user defined sinks by providing an entry point to marshal
# pointers-to-functions. This is needed by .NET, and possibly other language
# bindings.
# @result Returns a bool indicating success or failure.
#
InitSink = CFUNC(ct.c_bool,
    ct.POINTER(TidyOutputSink),  # The sink to populate with data.
    ct.c_void_p,                 # The output context.
    TidyPutByteFunc)(            # Pointer to the "put byte" callback function.
    ("tidyInitSink", dll), (
    (1, "sink"),
    (1, "snkData"),
    (1, "pbFunc"),))

# Helper: send a byte to output.
PutByte = CFUNC(None,
    ct.POINTER(TidyOutputSink),  # The output sink to send a byte.
    ct.c_uint)(                  # The byte to be sent.
    ("tidyPutByte", dll), (
    (1, "sink"),
    (1, "byteValue"),))

# @}
# @name Emacs-compatible reporting support.
# If you work with Emacs and prefer Tidy's report output to be in a form
# that is easy for Emacs to parse, then these functions may be valuable.
# @{

# Set the file path to use for reports when `TidyEmacs` is being used. This
# function provides a proper interface for using the hidden, internal-only
# `TidyEmacsFile` configuration option.
#
SetEmacsFile = CFUNC(None,
    TidyDoc,   # The tidy document for which you are setting the filePath.
    ctmbstr)(  # The path of the document that should be reported.
    ("tidySetEmacsFile", dll), (
    (1, "tdoc"),
    (1, "filePath"),))

# Get the file path to use for reports when `TidyEmacs` is being used. This
# function provides a proper interface for using the hidden, internal-only
# `TidyEmacsFile` configuration option.
# @param tdoc The tidy document for which you want to fetch the file path.
# @result Returns a string indicating the file path.
#
GetEmacsFile = CFUNC(ctmbstr,
    TidyDoc)(
    ("tidyGetEmacsFile", dll), (
    (1, "tdoc"),))

# @}
# @name Error Sink
# Send Tidy's output to any of several destinations with these functions.
# @{

# Set error sink to named file.
# @result Returns a file handle.
#
SetErrorFile = CFUNC(ct.POINTER(FILE),
    TidyDoc,   # The document to set.
    ctmbstr)(  # The file path to send output.
    ("tidySetErrorFile", dll), (
    (1, "tdoc"),
    (1, "errfilnam"),))

# Set error sink to given buffer.
# @result Returns 0 upon success or a standard error number.
#
SetErrorBuffer = CFUNC(ct.c_int,
    TidyDoc,                  # The document to set.
    ct.POINTER(TidyBuffer))(  # The TidyBuffer to collect output.
    ("tidySetErrorBuffer", dll), (
    (1, "tdoc"),
    (1, "errbuf"),))

# Set error sink to given generic sink.
# @result Returns 0 upon success or a standard error number.
#
SetErrorSink = CFUNC(ct.c_int,
    TidyDoc,                      # The document to set.
    ct.POINTER(TidyOutputSink))(  # The TidyOutputSink to collect output.
    ("tidySetErrorSink", dll), (
    (1, "tdoc"),
    (1, "sink"),))

# @}
# @name Error and Message Callbacks - TidyReportFilter
# A simple callback to filter or collect messages by diagnostic level,
# for example, TidyInfo, TidyWarning, etc. Its name reflects its original
# purpose as a filter, by which your application can inform LibTidy whether
# or not to output a particular report.
#
# @{

# This typedef represents the required signature for your provided callback
# function should you wish to register one with tidySetReportFilter().
# Your callback function will be provided with the following parameters.
# @param tdoc Indicates the tidy document the message comes from.
# @param lvl Specifies the TidyReportLevel of the message.
# @param line Indicates the line number in the source document the message applies to.
# @param col Indicates the column in the source document the message applies to.
# @param mssg Specifies the complete message as Tidy would emit it.
# @return Your callback function will return `yes` if Tidy should include the
#         report in its own output sink, or `no` if Tidy should suppress it.
#
TidyReportFilter = CFUNC(ct.c_bool,
                         TidyDoc,          # tdoc
                         TidyReportLevel,  # lvl
                         ct.c_uint,        # line
                         ct.c_uint,        # col
                         ctmbstr)          # mssg

# This function informs Tidy to use the specified callback to send reports.
SetReportFilter = CFUNC(ct.c_bool,
    TidyDoc,            # The tidy document for which the callback applies.
    TidyReportFilter)(  # A pointer to your callback function of type TidyReportFilter.
    ("tidySetReportFilter", dll), (
    (1, "tdoc"),
    (1, "filtCallback"),))

# @}
# @name Error and Message Callbacks - TidyReportCallback
# A simple callback to filter or collect messages reported by Tidy.
# Unlike TidyReportFilter, more data are provided (including a `va_list`),
# making this callback suitable for applications that provide more
# sophisticated handling of reports.
# @remark The use of a `va_list` may preclude using this callback from
#         non-C-like languages, which is uncharacteristic of Tidy. For more
#         flexibility, consider using TidyMessageCallback instead.
# @note This callback was previously `TidyMessageFilter3` in older versions
#       of LibTidy.
# @{

# This typedef represents the required signature for your provided callback
# function should you wish to register one with tidySetReportCallback().
# Your callback function will be provided with the following parameters.
# @param tdoc Indicates the tidy document the message comes from.
# @param lvl Specifies the TidyReportLevel of the message.
# @param line Indicates the line number in the source document the message applies to.
# @param col Indicates the column in the source document the message applies to.
# @param code Specifies the message code representing the message. Note that
#        this code is a string value that the API promises to hold constant,
#        as opposed to an enum value that can change at any time. Although
#        this is intended so that you can look up your own application's
#        strings, you can retrieve Tidy's format string with this code by
#        using tidyErrorCodeFromKey() and then the tidyLocalizedString()
#        family of functions.
# @param args Is a `va_list` of arguments used to fill Tidy's message format string.
# @return Your callback function will return `yes` if Tidy should include the
#         report in its own output sink, or `no` if Tidy should suppress it.
#
TidyReportCallback = CFUNC(ct.c_bool,
                           TidyDoc,          # tdoc
                           TidyReportLevel,  # lvl
                           ct.c_uint,        # line
                           ct.c_uint,        # col
                           ctmbstr,          # code
                           va_list)          # args

# This function informs Tidy to use the specified callback to send reports.
SetReportCallback = CFUNC(ct.c_bool,
    TidyDoc,              # The tidy document for which the callback applies.
    TidyReportCallback)(  # A pointer to your callback function of type TidyReportCallback.
    ("tidySetReportCallback", dll), (
    (1, "tdoc"),
    (1, "filtCallback"),))

# @}
# @name Error and Message Callbacks - TidyMessageCallback
# A sophisticated and extensible callback to filter or collect messages
# reported by Tidy. It returns only an opaque type `TidyMessage` for every
# report and dialogue message, and this message can be queried with the
# TidyMessageCallback API, below. Note that unlike the older filters, this
# callback exposes *all* output that LibTidy emits (excluding the console
# application, which is a client of LibTidy).

# This typedef represents the required signature for your provided callback
# function should you wish to register one with tidySetMessageCallback().
# Your callback function will be provided with the following parameters.
# @param tmessage An opaque type used as a token against which other API
#        calls can be made.
# @return Your callback function will return `yes` if Tidy should include the
#         report in its own output sink, or `no` if Tidy should suppress it.
#
TidyMessageCallback = CFUNC(ct.c_bool,
                            TidyMessage)  # tmessage

# This function informs Tidy to use the specified callback to send reports.
SetMessageCallback = CFUNC(ct.c_bool,
    TidyDoc,               # The tidy document for which the callback applies.
    TidyMessageCallback)(  # A pointer to your callback function of type TidyMessageCallback.
    ("tidySetMessageCallback", dll), (
    (1, "tdoc"),
    (1, "filtCallback"),))

# @name TidyMessageCallback API
# When using `TidyMessageCallback` you will be supplied with a TidyMessage
# object, which is used as a token to be interrogated with the following
# API before the callback returns.
# @remark Upon returning from the callback, this object is destroyed so do
# not attempt to copy it, or keep it around, or use it in any way.
#
# @{

# Get the tidy document this message comes from.
# @param tmessage Specify the message that you are querying.
# @result Returns the TidyDoc that generated the message.
#
GetMessageDoc = CFUNC(TidyDoc,
    TidyMessage)(
    ("tidyGetMessageDoc", dll), (
    (1, "tmessage"),))

# Get the message code.
# @param tmessage Specify the message that you are querying.
# @result Returns a code representing the message. This code can be used
#         directly with the localized strings API; however we never make
#         any guarantees about the value of these codes. For code stability
#         don't store this value in your own application. Instead use the
#         enum field or use the message key string value.
#
GetMessageCode = CFUNC(ct.c_uint,
    TidyMessage)(
    ("tidyGetMessageCode", dll), (
    (1, "tmessage"),))

# Get the message key string.
# @param tmessage Specify the message that you are querying.
# @result Returns a string representing the message. This string is intended
#         to be stable by the LibTidy API, and is suitable for use as a key
#         in your own applications.
#
GetMessageKey = CFUNC(ctmbstr,
    TidyMessage)(
    ("tidyGetMessageKey", dll), (
    (1, "tmessage"),))

# Get the line number the message applies to.
# @param tmessage Specify the message that you are querying.
# @result Returns the line number, if any, that generated the message.
#
GetMessageLine = CFUNC(ct.c_int,
    TidyMessage)(
    ("tidyGetMessageLine", dll), (
    (1, "tmessage"),))

# Get the column the message applies to.
# @param tmessage Specify the message that you are querying.
# @result Returns the column number, if any, that generated the message.
#
GetMessageColumn = CFUNC(ct.c_int,
    TidyMessage)(
    ("tidyGetMessageColumn", dll), (
    (1, "tmessage"),))

# Get the TidyReportLevel of the message.
# @param tmessage Specify the message that you are querying.
# @result Returns a TidyReportLevel indicating the severity or status of the
#         message.
#
GetMessageLevel = CFUNC(TidyReportLevel,
    TidyMessage)(
    ("tidyGetMessageLevel", dll), (
    (1, "tmessage"),))

# Get the muted status of the message, that is, whether or not the
# current configuration indicated that this message should be muted.
# @param tmessage Specify the message that you are querying.
# @result Returns a Bool indicating that the config indicates muting this
#         message.
#
GetMessageIsMuted = CFUNC(ct.c_bool,
    TidyMessage)(
    ("tidyGetMessageIsMuted", dll), (
    (1, "tmessage"),))

# Get the default format string, which is the format string for the message
# in Tidy's default localization (en_us).
# @param tmessage Specify the message that you are querying.
# @result Returns the default localization format string of the message.
#
GetMessageFormatDefault = CFUNC(ctmbstr,
    TidyMessage)(
    ("tidyGetMessageFormatDefault", dll), (
    (1, "tmessage"),))

# Get the localized format string. If a localized version of the format string
# doesn't exist, then the default version will be returned.
# @param tmessage Specify the message that you are querying.
# @result Returns the localized format string of the message.
#
GetMessageFormat = CFUNC(ctmbstr,
    TidyMessage)(
    ("tidyGetMessageFormat", dll), (
    (1, "tmessage"),))

# Get the message with the format string already completed, in Tidy's
# default localization.
# @param tmessage Specify the message that you are querying.
# @result Returns the message in the default localization.
#
GetMessageDefault = CFUNC(ctmbstr,
    TidyMessage)(
    ("tidyGetMessageDefault", dll), (
    (1, "tmessage"),))

# Get the message with the format string already completed, in Tidy's
# current localization.
# @param tmessage Specify the message that you are querying.
# @result Returns the message in the current localization.
#
GetMessage = CFUNC(ctmbstr,
    TidyMessage)(
    ("tidyGetMessage", dll), (
    (1, "tmessage"),))

# Get the position part part of the message in the default language.
# @param tmessage Specify the message that you are querying.
# @result Returns the positional part of a string as Tidy would display it
#         in the console application.
#
GetMessagePosDefault = CFUNC(ctmbstr,
    TidyMessage)(
    ("tidyGetMessagePosDefault", dll), (
    (1, "tmessage"),))

# Get the position part part of the message in the current language.
# @param tmessage Specify the message that you are querying.
# @result Returns the positional part of a string as Tidy would display it
#         in the console application.
#
GetMessagePos = CFUNC(ctmbstr,
    TidyMessage)(
    ("tidyGetMessagePos", dll), (
    (1, "tmessage"),))

# Get the prefix part of a message in the default language.
# @param tmessage Specify the message that you are querying.
# @result Returns the message prefix part of a string as Tidy would display
#         it in the console application.
#
GetMessagePrefixDefault = CFUNC(ctmbstr,
    TidyMessage)(
    ("tidyGetMessagePrefixDefault", dll), (
    (1, "tmessage"),))

# Get the prefix part of a message in the current language.
# @param tmessage Specify the message that you are querying.
# @result Returns the message prefix part of a string as Tidy would display
#         it in the console application.
#
GetMessagePrefix = CFUNC(ctmbstr,
    TidyMessage)(
    ("tidyGetMessagePrefix", dll), (
    (1, "tmessage"),))

# Get the complete message as Tidy would emit it in the default localization.
# @param tmessage Specify the message that you are querying.
# @result Returns the complete message just as Tidy would display it on the
#         console.
#
GetMessageOutputDefault = CFUNC(ctmbstr,
    TidyMessage)(
    ("tidyGetMessageOutputDefault", dll), (
    (1, "tmessage"),))

# Get the complete message as Tidy would emit it in the current localization.
# @param tmessage Specify the message that you are querying.
# @result Returns the complete message just as Tidy would display it on the
#         console.
#
GetMessageOutput = CFUNC(ctmbstr,
    TidyMessage)(
    ("tidyGetMessageOutput", dll), (
    (1, "tmessage"),))

# @} end subgroup TidyMessageCallback API

# @name TidyMessageCallback Arguments API
# When using `TidyMessageCallback` you will be supplied with a TidyMessage
# object which can be used as a token against which to query using this API.
# This API deals strictly with _arguments_ that a message may or may not have;
# these are the same arguments that Tidy would apply to a format string in
# order to fill in the placeholder fields and deliver a complete report or
# dialogue string to you.
#
# @{

# Initiates an iterator for a list of arguments related to a given message.
# This iterator allows you to iterate through all of the arguments, if any.
# In order to iterate through the arguments, initiate the iterator with this
# function, and then use tidyGetNextMessageArgument() to retrieve the first
# and subsequent arguments. For example:
# @code{.c}
#   TidyIterator itArg = tidyGetMessageArguments( tmessage );
#   while ( itArg ) {
#     TidyMessageArgument my_arg = tidyGetNextMessageArgument( tmessage, &itArg );
#     // do something with my_arg, such as inspect its value or format
#   }
# @endcode
# @param tmessage The message about whose arguments you wish to query.
# @result Returns a TidyIterator, which is a token used to represent the
#         current position in a list within LibTidy.
#
GetMessageArguments = CFUNC(TidyIterator,
    TidyMessage)(
    ("tidyGetMessageArguments", dll), (
    (1, "tmessage"),))

# Given a valid TidyIterator initiated with tidyGetMessageArguments(), returns
# an instance of the opaque type TidyMessageArgument, which serves as a token
# against which the remaining argument API functions may be used to query
# information.
# @result Returns an instance of TidyMessageArgument.
#
GetNextMessageArgument = CFUNC(TidyMessageArgument,
    TidyMessage,                # The message whose arguments you want to access.
    ct.POINTER(TidyIterator))(  # The TidyIterator (initiated with
                                # tidyOptGetDocLinksList()) token.
    ("tidyGetNextMessageArgument", dll), (
    (1, "tmessage"),
    (1, "iter"),))

# Returns the `TidyFormatParameterType` of the given message argument.
# @result Returns the type of parameter of type TidyFormatParameterType.
#
GetArgType = CFUNC(TidyFormatParameterType,
    TidyMessage,                       # The message whose arguments you want to access.
    ct.POINTER(TidyMessageArgument))(  # The argument that you are querying.
    ("tidyGetArgType", dll), (
    (1, "tmessage"),
    (1, "arg"),))

# Returns the format specifier of the given message argument. The memory for
# this string is cleared upon termination of the callback, so do be sure to
# make your own copy.
# @result Returns the format specifier string of the given argument.
#
GetArgFormat = CFUNC(ctmbstr,
    TidyMessage,                       # The message whose arguments you want to access.
    ct.POINTER(TidyMessageArgument))(  # The argument that you are querying.
    ("tidyGetArgFormat", dll), (
    (1, "tmessage"),
    (1, "arg"),))

# Returns the string value of the given message argument. An assertion
# will be generated if the argument type is not a string.
# @result Returns the string value of the given argument.
#
GetArgValueString = CFUNC(ctmbstr,
    TidyMessage,                       # The message whose arguments you want to access.
    ct.POINTER(TidyMessageArgument))(  # The argument that you are querying.
    ("tidyGetArgValueString", dll), (
    (1, "tmessage"),
    (1, "arg"),))

# Returns the unsigned integer value of the given message argument. An
# assertion will be generated if the argument type is not an unsigned int.
# @result Returns the unsigned integer value of the given argument.
#
GetArgValueUInt = CFUNC(ct.c_uint,
    TidyMessage,                       # The message whose arguments you want to access.
    ct.POINTER(TidyMessageArgument))(  # The argument that you are querying.
    ("tidyGetArgValueUInt", dll), (
    (1, "tmessage"),
    (1, "arg"),))

# Returns the integer value of the given message argument. An assertion
# will be generated if the argument type is not an integer.
# @result Returns the integer value of the given argument.
#
GetArgValueInt = CFUNC(ct.c_int,
    TidyMessage,                       # The message whose arguments you want to access.
    ct.POINTER(TidyMessageArgument))(  # The argument that you are querying.
    ("tidyGetArgValueInt", dll), (
    (1, "tmessage"),
    (1, "arg"),))

# Returns the double value of the given message argument. An assertion
# will be generated if the argument type is not a double.
# @result Returns the double value of the given argument.
#
GetArgValueDouble = CFUNC(ct.c_double,
    TidyMessage,                       # The message whose arguments you want to access.
    ct.POINTER(TidyMessageArgument))(  # The argument that you are querying.
    ("tidyGetArgValueDouble", dll), (
    (1, "tmessage"),
    (1, "arg"),))

# @} end subgroup TidyMessageCallback Arguments API

# @name Printing
# LibTidy applications can somewhat track the progress of the tidying process
# by using this provided callback. It relates where something in the source
# document ended up in the output.
# @{

# This typedef represents the required signature for your provided callback
# function should you wish to register one with tidySetMessageCallback().
# Your callback function will be provided with the following parameters.
# @param tdoc Indicates the source tidy document.
# @param line Indicates the line in the source document at this point in the process.
# @param col Indicates the column in the source document at this point in the process.
# @param destLine Indicates the line number in the output document at this point in the process.
#
TidyPPProgress = CFUNC(None,
                       TidyDoc,    # tdoc
                       ct.c_uint,  # line
                       ct.c_uint,  # col
                       ct.c_uint)  # destLine

# This function informs Tidy to use the specified callback for tracking the
# pretty-printing process progress.
#
SetPrettyPrinterCallback = CFUNC(ct.c_bool,
    TidyDoc,
    TidyPPProgress)(
    ("tidySetPrettyPrinterCallback", dll), (
    (1, "tdoc"),
    (1, "callback"),))

# @}
# @} end IO group

# MARK: - Document Parse
# **************************************************************************** #
# @defgroup Parse Document Parse
#
# Functions for parsing markup from a given input source, as well as string
# and filename functions for added convenience. HTML/XHTML version determined
# from input.
#
# @{
# **************************************************************************** #

# Parse markup in named file.
# @result Returns the highest of `2` indicating that errors were present in
#         the document, `1` indicating warnings, and `0` in the case of
#         everything being okay.
#
ParseFile = CFUNC(ct.c_int,
    TidyDoc,   # The tidy document to use for parsing.
    ctmbstr)(  # The filename to parse.
    ("tidyParseFile", dll), (
    (1, "tdoc"),
    (1, "filename"),))

# Parse markup from the standard input.
# @param tdoc The tidy document to use for parsing.
# @result Returns the highest of `2` indicating that errors were present in
#         the document, `1` indicating warnings, and `0` in the case of
#         everything being okay.
#
ParseStdin = CFUNC(ct.c_int,
    TidyDoc)(
    ("tidyParseStdin", dll), (
    (1, "tdoc"),))

# Parse markup in given string. Note that the supplied string is of type
# `ctmbstr` based on `char` and therefore doesn't support the use of
# UTF-16 strings. Use `tidyParseBuffer()` if parsing multibyte strings.
# @result Returns the highest of `2` indicating that errors were present in
#         the document, `1` indicating warnings, and `0` in the case of
#         everything being okay.
#
ParseString = CFUNC(ct.c_int,
    TidyDoc,   # The tidy document to use for parsing.
    ctmbstr)(  # The string to parse.
    ("tidyParseString", dll), (
    (1, "tdoc"),
    (1, "content"),))

# Parse markup in given buffer.
# @result Returns the highest of `2` indicating that errors were present in
#         the document, `1` indicating warnings, and `0` in the case of
#         everything being okay.
#
ParseBuffer = CFUNC(ct.c_int,
    TidyDoc,                  # The tidy document to use for parsing.
    ct.POINTER(TidyBuffer))(  # The TidyBuffer containing data to parse.
    ("tidyParseBuffer", dll), (
    (1, "tdoc"),
    (1, "buf"),))

# Parse markup in given generic input source.
# @result Returns the highest of `2` indicating that errors were present in
#         the document, `1` indicating warnings, and `0` in the case of
#         everything being okay.
#
ParseSource = CFUNC(ct.c_int,
    TidyDoc,                       # The tidy document to use for parsing.
    ct.POINTER(TidyInputSource))(  # A TidyInputSource containing data to parse.
    ("tidyParseSource", dll), (
    (1, "tdoc"),
    (1, "source"),))

# @} End Parse group

# MARK: - Diagnostics and Repair
# **************************************************************************** #
# @defgroup Clean Diagnostics and Repair
#
# After parsing the document, you can use these functions to attempt cleanup,
# repair, get additional diagnostics, and determine the document type.
# @{
# **************************************************************************** #

# Execute configured cleanup and repair operations on parsed markup.
# @param tdoc The tidy document to use.
# @result An integer representing the status.
#
CleanAndRepair = CFUNC(ct.c_int,
    TidyDoc)(
    ("tidyCleanAndRepair", dll), (
    (1, "tdoc"),))

# Reports the document type and diagnostic statistics on parsed and repaired
# markup. You must call tidyCleanAndRepair() before using this function.
# @param tdoc The tidy document to use.
# @result An integer representing the status.
#
RunDiagnostics = CFUNC(ct.c_int,
    TidyDoc)(
    ("tidyRunDiagnostics", dll), (
    (1, "tdoc"),))

# Reports the document type into the output sink.
# @param tdoc The tidy document to use.
# @result An integer representing the status.
#
ReportDoctype = CFUNC(ct.c_int,
    TidyDoc)(
    ("tidyReportDoctype", dll), (
    (1, "tdoc"),))

# @} end Clean group

# MARK: - Document Save Functions
# **************************************************************************** #
# @defgroup Save Document Save Functions
#
# Save currently parsed document to the given output sink. File name
# and string/buffer functions provided for convenience.
#
# @{
# **************************************************************************** #

# Save the tidy document to the named file.
# @result An integer representing the status.
#
SaveFile = CFUNC(ct.c_int,
    TidyDoc,   # The tidy document to save.
    ctmbstr)(  # The destination file name.
    ("tidySaveFile", dll), (
    (1, "tdoc"),
    (1, "filename"),))

# Save the tidy document to standard output (FILE*).
# @param tdoc The tidy document to save.
# @result An integer representing the status.
#
SaveStdout = CFUNC(ct.c_int,
    TidyDoc)(
    ("tidySaveStdout", dll), (
    (1, "tdoc"),))

# Save the tidy document to given TidyBuffer object.
# @result An integer representing the status.
#
SaveBuffer = CFUNC(ct.c_int,
    TidyDoc,                  # The tidy document to save.
    ct.POINTER(TidyBuffer))(  # The buffer to place the output.
    ("tidySaveBuffer", dll), (
    (1, "tdoc"),
    (1, "buf"),))

# Save the tidy document to an application buffer. If TidyShowMarkup and the
# document has no errors, or TidyForceOutput, then the current document (per
# the current configuration) will be pretty printed to this application
# buffer. The document byte length (not character length) will be placed into
# *buflen. The document will not be null terminated. If the buffer is not big
# enough, ENOMEM will be returned, else the actual document status.
# @result An integer representing the status.
#
SaveString = CFUNC(ct.c_int,
    TidyDoc,                 # The tidy document to save.
    tmbstr,                  # The buffer to save to.
    ct.POINTER(ct.c_uint))(  # [out] The byte length written.
    ("tidySaveString", dll), (
    (1, "tdoc"),
    (1, "buffer"),
    (1, "buflen"),))

# Save to given generic output sink.
# @result An integer representing the status.
#
SaveSink = CFUNC(ct.c_int,
    TidyDoc,                      # The tidy document to save.
    ct.POINTER(TidyOutputSink))(  # The output sink to save to.
    ("tidySaveSink", dll), (
    (1, "tdoc"),
    (1, "sink"),))

# Save current settings to named file. Only writes non-default values.
# @result An integer representing the status.
#
OptSaveFile = CFUNC(ct.c_int,
    TidyDoc,   # The tidy document to save.
    ctmbstr)(  # The filename to save the configuration to.
    ("tidyOptSaveFile", dll), (
    (1, "tdoc"),
    (1, "cfgfil"),))

# Save current settings to given output sink. Only non-default values are
# written.
# @result An integer representing the status.
#
OptSaveSink = CFUNC(ct.c_int,
    TidyDoc,                      # The tidy document to save.
    ct.POINTER(TidyOutputSink))(  # The output sink to save the configuration to.
    ("tidyOptSaveSink", dll), (
    (1, "tdoc"),
    (1, "sink"),))

# @} end Save group

# MARK: - Document Tree
# **************************************************************************** #
# @defgroup Tree Document Tree
#
# A parsed (and optionally repaired) document is represented by Tidy as a
# tree, much like a W3C DOM. This tree may be traversed using these
# functions. The following snippet gives a basic idea how these functions
# can be used.
#
# @code{.c}
# void dumpNode( TidyNode tnod, int indent ) {
#   TidyNode child;
#
#   for ( child = tidyGetChild(tnod); child; child = tidyGetNext(child) ) {
#     ctmbstr name;
#     switch ( tidyNodeGetType(child) ) {
#     case TidyNode_Root:       name = "Root";                    break;
#     case TidyNode_DocType:    name = "DOCTYPE";                 break;
#     case TidyNode_Comment:    name = "Comment";                 break;
#     case TidyNode_ProcIns:    name = "Processing Instruction";  break;
#     case TidyNode_Text:       name = "Text";                    break;
#     case TidyNode_CDATA:      name = "CDATA";                   break;
#     case TidyNode_Section:    name = "XML Section";             break;
#     case TidyNode_Asp:        name = "ASP";                     break;
#     case TidyNode_Jste:       name = "JSTE";                    break;
#     case TidyNode_Php:        name = "PHP";                     break;
#     case TidyNode_XmlDecl:    name = "XML Declaration";         break;
#
#     case TidyNode_Start:
#     case TidyNode_End:
#     case TidyNode_StartEnd:
#     default:
#       name = tidyNodeGetName( child );
#       break;
#     }
#     assert( name != NULL );
#     printf( "\%*.*sNode: \%s\\n", indent, indent, " ", name );
#     dumpNode( child, indent + 4 );
#   }
# }
#
# void dumpDoc( TidyDoc tdoc ) {
#   dumpNode( tidyGetRoot(tdoc), 0 );
# }
#
# void dumpBody( TidyDoc tdoc ) {
#   dumpNode( tidyGetBody(tdoc), 0 );
# }
# @endcode
#
# @{
# **************************************************************************** #

# @name Nodes for Document Sections
# @{

# Get the root node.
# @param tdoc The document to query.
# @result Returns a tidy node.
#
GetRoot = CFUNC(TidyNode,
    TidyDoc)(
    ("tidyGetRoot", dll), (
    (1, "tdoc"),))

# Get the HTML node.
# @param tdoc The document to query.
# @result Returns a tidy node.
#
GetHtml = CFUNC(TidyNode,
    TidyDoc)(
    ("tidyGetHtml", dll), (
    (1, "tdoc"),))

# Get the HEAD node.
# @param tdoc The document to query.
# @result Returns a tidy node.
#
GetHead = CFUNC(TidyNode,
    TidyDoc)(
    ("tidyGetHead", dll), (
    (1, "tdoc"),))

# Get the BODY node.
# @param tdoc The document to query.
# @result Returns a tidy node.
#
GetBody = CFUNC(TidyNode,
    TidyDoc)(
    ("tidyGetBody", dll), (
    (1, "tdoc"),))

# @}
# @name Relative Nodes
# @{

# Get the parent of the indicated node.
# @param tnod The node to query.
# @result Returns a tidy node.
#
GetParent = CFUNC(TidyNode,
    TidyNode)(
    ("tidyGetParent", dll), (
    (1, "tnode"),))

# Get the child of the indicated node.
# @param tnod The node to query.
# @result Returns a tidy node.
#
GetChild = CFUNC(TidyNode,
    TidyNode)(
    ("tidyGetChild", dll), (
    (1, "tnode"),))

# Get the next sibling node.
# @param tnod The node to query.
# @result Returns a tidy node.
#
GetNext = CFUNC(TidyNode,
    TidyNode)(
    ("tidyGetNext", dll), (
    (1, "tnode"),))

# Get the previous sibling node.
# @param tnod The node to query.
# @result Returns a tidy node.
#
GetPrev = CFUNC(TidyNode,
    TidyNode)(
    ("tidyGetPrev", dll), (
    (1, "tnode"),))

# @}
# @name Miscellaneous Node Functions
# @{

# Remove the indicated node.
# @result Returns the next tidy node.
#
DiscardElement = CFUNC(TidyNode,
    TidyDoc,    # The tidy document from which to remove the node.
    TidyNode)(  # The node to remove
    ("tidyDiscardElement", dll), (
    (1, "tdoc"),
    (1, "tnode"),))

# @}
# @name Node Attribute Functions
# @{

# Get the first attribute.
# @param tnod The node for which to get attributes.
# @result Returns an instance of TidyAttr.
#
AttrFirst = CFUNC(TidyAttr,
    TidyNode)(
    ("tidyAttrFirst", dll), (
    (1, "tnode"),))

# Get the next attribute.
# @param tattr The current attribute, so the next one can be returned.
# @result Returns and instance of TidyAttr.
#
AttrNext = CFUNC(TidyAttr,
    TidyAttr)(
    ("tidyAttrNext", dll), (
    (1, "tattr"),))

# Get the name of a TidyAttr instance.
# @param tattr The tidy attribute to query.
# @result Returns a string indicating the name of the attribute.
#
AttrName = CFUNC(ctmbstr,
    TidyAttr)(
    ("tidyAttrName", dll), (
    (1, "tattr"),))

# Get the value of a TidyAttr instance.
# @param tattr The tidy attribute to query.
# @result Returns a string indicating the value of the attribute.
#
AttrValue = CFUNC(ctmbstr,
    TidyAttr)(
    ("tidyAttrValue", dll), (
    (1, "tattr"),))

# Discard an attribute.
AttrDiscard = CFUNC(None,
    TidyDoc,    # The tidy document from which to discard the attribute.
    TidyNode,   # The node from which to discard the attribute.
    TidyAttr)(  # The attribute to discard.
    ("tidyAttrDiscard", dll), (
    (1, "itdoc"),
    (1, "tnode"),
    (1, "tattr"),))

# Get the attribute ID given a tidy attribute.
# @param tattr The attribute to query.
# @result Returns the TidyAttrId of the given attribute.
#
AttrGetId = CFUNC(TidyAttrId,
    TidyAttr)(
    ("tidyAttrGetId", dll), (
    (1, "tattr"),))

# Indicates whether or not a given attribute is an event attribute.
# @param tattr The attribute to query.
# @result Returns a bool indicating whether or not the attribute is an event.
#
AttrIsEvent = CFUNC(ct.c_bool,
    TidyAttr)(
    ("tidyAttrIsEvent", dll), (
    (1, "tattr"),))

# Get an instance of TidyAttr by specifying an attribute ID.
# @result Returns a TidyAttr instance.
#
AttrGetById = CFUNC(TidyAttr,
    TidyNode,     # The node to query.
    TidyAttrId)(  # The attribute ID to find.
    ("tidyAttrGetById", dll), (
    (1, "tnode"),
    (1, "attId"),))

# @}
# @name Additional Node Interrogation
# @{

# Get the type of node.
# @param tnod The node to query.
# @result Returns the type of node as TidyNodeType.
#
NodeGetType = CFUNC(TidyNodeType,
    TidyNode)(
    ("tidyNodeGetType", dll), (
    (1, "tnode"),))

# Get the name of the node.
# @param tnod The node to query.
# @result Returns a string indicating the name of the node.
#
NodeGetName = CFUNC(ctmbstr,
    TidyNode)(
    ("tidyNodeGetName", dll), (
    (1, "tnode"),))

# Indicates whether or not a node is a text node.
# @param tnod The node to query.
# @result Returns a bool indicating whether or not the node is a text node.
#
NodeIsText = CFUNC(ct.c_bool,
    TidyNode)(
    ("tidyNodeIsText", dll), (
    (1, "tnode"),))

# Indicates whether or not the node is a propriety type.
# @result Returns a bool indicating whether or not the node is a proprietary type.
#
NodeIsProp = CFUNC(ct.c_bool,
    TidyDoc,    # The document to query.
    TidyNode)(  # The node to query
    ("tidyNodeIsProp", dll), (
    (1, "tdoc"),
    (1, "tnode"),))

# Indicates whether or not a node represents and HTML header element, such
# as h1, h2, etc.
# @param tnod The node to query.
# @result Returns a bool indicating whether or not the node is an HTML header.
#
NodeIsHeader = CFUNC(ct.c_bool,
    TidyNode)(
    ("tidyNodeIsHeader", dll), (
    (1, "tnode"),))

# Indicates whether or not the node has text.
# @result Returns the type of node as TidyNodeType.
#
NodeHasText = CFUNC(ct.c_bool,
    TidyDoc,    # The document to query.
    TidyNode)(  # The node to query.
    ("tidyNodeHasText", dll), (
    (1, "tdoc"),
    (1, "tnode"),))

# Gets the text of a node and places it into the given TidyBuffer.
# The text will be terminated with a `TidyNewline`.
# If you want the raw utf-8 stream see `tidyNodeGetValue()`.
# @result Returns a bool indicating success or not.
#
NodeGetText = CFUNC(ct.c_bool,
    TidyDoc,                  # The document to query.
    TidyNode,                 # The node to query.
    ct.POINTER(TidyBuffer))(  # [out] A TidyBuffer used to receive the node's text.
    ("tidyNodeGetText", dll), (
    (1, "tdoc"),
    (1, "tnode"),
    (1, "buf"),))

# Get the value of the node. This copies the unescaped value of this node into
# the given TidyBuffer at UTF-8.
# @result Returns a bool indicating success or not.
#
NodeGetValue = CFUNC(ct.c_bool,
    TidyDoc,                  # The document to query
    TidyNode,                 # The node to query
    ct.POINTER(TidyBuffer))(  # [out] A TidyBuffer used to receive the node's value.
    ("tidyNodeGetValue", dll), (
    (1, "tdoc"),
    (1, "tnode"),
    (1, "buf"),))

# Get the tag ID of the node.
# @param tnod The node to query.
# @result Returns the tag ID of the node as TidyTagId.
#
NodeGetId = CFUNC(TidyTagId,
    TidyNode)(
    ("tidyNodeGetId", dll), (
    (1, "tnode"),))

# Get the line number where the node occurs.
# @param tnod The node to query.
# @result Returns the line number.
#
NodeLine = CFUNC(ct.c_uint,
    TidyNode)(
    ("tidyNodeLine", dll), (
    (1, "tnode"),))

# Get the column location of the node.
# @param tnod The node to query.
# @result Returns the column location of the node.
#
NodeColumn = CFUNC(ct.c_uint,
    TidyNode)(
    ("tidyNodeColumn", dll), (
    (1, "tnode"),))

# @}
# @} end Tree group

# MARK: - Message Key Management
# **************************************************************************** #
# @defgroup MessagesKeys Message Key Management
#
# These functions serve to manage message codes, i.e., codes that are used
# Tidy and communicated via its callback filters to represent reports and
# dialogue that Tidy emits.
#
# @remark These codes only reflect complete messages, and are specifically
#         distinct from the internal codes that are used to lookup individual
#         strings for localization purposes.
#
# @{
# **************************************************************************** #

# Given a message code, return the text key that represents it.
# @param code The error code to lookup.
# @result The string representing the error code.
#
ErrorCodeAsKey = CFUNC(ctmbstr,
    ct.c_uint)(
    ("tidyErrorCodeAsKey", dll), (
    (1, "code"),))

# Given a text key representing a message code, return the uint that
# represents it.
#
# @remark We establish that for external purposes, the API will ensure that
#         string keys remain consistent. *Never* count on the integer value
#         of a message code. Always use this function to ensure that the
#         integer is valid if you need one.
# @param code The string representing the error code.
# @result Returns an integer that represents the error code, which can be
#         used to lookup Tidy's built-in strings. If the provided string does
#         not have a matching message code, then UINT_MAX will be returned.
#
ErrorCodeFromKey = CFUNC(ct.c_uint,
    ctmbstr)(
    ("tidyErrorCodeFromKey", dll), (
    (1, "code"),))

# Initiates an iterator for a list of message codes available in Tidy.
# This iterator allows you to iterate through all of the code. In orde to
# iterate through the codes, initiate the iterator with this function, and
# then use getNextErrorCode() to retrieve the first and subsequent codes.
# For example:
# @code{.c}
#   TidyIterator itMessage = getErrorCodeList();
#   while ( itMessage ) {
#     uint code = getNextErrorCode( &itMessage );
#     // do something with the code, such as lookup a string.
#   }
# @endcode
# @result Returns a TidyIterator, which is a token used to represent the
#         current position in a list within LibTidy.
#
getErrorCodeList = CFUNC(TidyIterator)(  # noqa: N816
    ("getErrorCodeList", dll),)

# Given a valid TidyIterator initiated with getErrorCodeList(), returns
# an instance of the opaque type TidyMessageArgument, which serves as a token
# against which the remaining argument API functions may be used to query
# information.
# @param iter The TidyIterator (initiated with getErrorCodeList()) token.
# @result Returns a message code.
#
getNextErrorCode = CFUNC(ct.c_uint,  # noqa: N816
    ct.POINTER(TidyIterator))(
    ("getNextErrorCode", dll), (
    (1, "iter"),))

# @} end MessagesKeys group

# MARK: - Localization Support
# **************************************************************************** #
# @defgroup Localization Localization Support
#
# These functions help manage localization in Tidy.
#
# @{
# **************************************************************************** #

# @name Tidy's Locale
# @{

# Tells Tidy to use a different language for output.
# @param  languageCode A Windows or POSIX language code, and must match
#         a TIDY_LANGUAGE for an installed language.
# @result Indicates that a setting was applied, but not necessarily the
#         specific request, i.e., true indicates a language and/or region
#         was applied. If es_mx is requested but not installed, and es is
#         installed, then es will be selected and this function will return
#         true. However the opposite is not true; if es is requested but
#         not present, Tidy will not try to select from the es_XX variants.
#
SetLanguage = CFUNC(ct.c_bool,
    ctmbstr)(
    ("tidySetLanguage", dll), (
    (1, "languageCode"),))

# Gets the current language used by Tidy.
# @result Returns a string indicating the currently set language.
#
GetLanguage = CFUNC(ctmbstr)(
    ("tidyGetLanguage", dll),)

# @}
# @name Locale Mappings
# @{

# @struct TidyLocaleMapItem
# Represents an opaque type we can use for TidyLocaleMapItem, which
# is used to iterate through the language list, and used to access
# the windowsName() and the posixName().
#
class _tidyLocaleMapItem(ct.Structure): pass  # { int _opaque; }
TidyLocaleMapItem = ct.POINTER(_tidyLocaleMapItem)  # noqa: E305

# Initiates an iterator for a list of Tidy's Windows<->POSIX locale mappings.
# This iterator allows you to iterate through this list. In order to
# iterate through the list, initiate the iterator with this function, and then
# use getNextWindowsLanguage() to retrieve the first and subsequent codes.
# For example:
# @code{.c}
#   TidyIterator itList = getWindowsLanguageList();
#   while ( itList ) {
#     tidyLocaleMapItem *item = getNextWindowsLanguage( &itList );
#     // do something such as get the TidyLangWindowsName(item).
#   }
# @endcode
# @result Returns a TidyIterator, which is a token used to represent the
#         current position in a list within LibTidy.
#
getWindowsLanguageList = CFUNC(TidyIterator)(  # noqa: N816
    ("getWindowsLanguageList", dll),)

# Given a valid TidyIterator initiated with getWindowsLanguageList(), returns
# a pointer to a TidyLocaleMapItem, which can be further interrogated with
# TidyLangWindowsName() or TidyLangPosixName().
# @param iter The TidyIterator (initiated with getWindowsLanguageList()) token.
# @result Returns a pointer to a TidyLocaleMapItem.
#
getNextWindowsLanguage = CFUNC(ct.POINTER(TidyLocaleMapItem),  # noqa: N816
    ct.POINTER(TidyIterator))(
    ("getNextWindowsLanguage", dll), (
    (1, "iter"),))

# Given a `TidyLocaleMapItem`, return the Windows name.
# @param item An instance of TidyLocaleMapItem to query.
# @result Returns a string with the Windows name of the mapping.
#
LangWindowsName = CFUNC(ctmbstr,
    ct.POINTER(TidyLocaleMapItem))(
    ("TidyLangWindowsName", dll), (
    (1, "item"),))

# Given a `TidyLocaleMapItem`, return the POSIX name.
# @param item An instance of TidyLocaleMapItem to query.
# @result Returns a string with the POSIX name of the mapping.
#
LangPosixName = CFUNC(ctmbstr,
    ct.POINTER(TidyLocaleMapItem))(
    ("TidyLangPosixName", dll), (
    (1, "item"),))

# @}
# @name Getting Localized Strings
# @{

# Provides a string given `messageType` in the current localization for
# `quantity`. Some strings have one or more plural forms, and this function
# will ensure that the correct singular or plural form is returned for the
# specified quantity.
# @result Returns the desired string.
#
LocalizedStringN = CFUNC(ctmbstr,
    ct.c_uint,   # The message type.
    ct.c_uint)(  # The quantity.
    ("tidyLocalizedStringN", dll), (
    (1, "messageType"),
    (1, "quantity"),))

# Provides a string given `messageType` in the current localization for the
# single case.
# @param messageType The message type.
# @result Returns the desired string.
#
LocalizedString = CFUNC(ctmbstr,
    ct.c_uint)(
    ("tidyLocalizedString", dll), (
    (1, "messageType"),))

# Provides a string given `messageType` in the default localization for
# `quantity`. Some strings have one or more plural forms, and this function
# will ensure that the correct singular or plural form is returned for the
# specified quantity.
# @result Returns the desired string.
#
DefaultStringN = CFUNC(ctmbstr,
    ct.c_uint,   # The message type.
    ct.c_uint)(  # The quantity.
    ("tidyDefaultStringN", dll), (
    (1, "messageType"),
    (1, "quantity"),))

# Provides a string given `messageType` in the default localization (which
# is `en`).
# @param messageType The message type.
# @result Returns the desired string.
#
DefaultString = CFUNC(ctmbstr,
    ct.c_uint)(
    ("tidyDefaultString", dll), (
    (1, "messageType"),))

# Initiates an iterator for a list of string key codes available in Tidy.
# This iterator allows you to iterate through all of the codes. In order to
# iterate through the codes, initiate the iterator with this function, and
# then use getNextStringKey() to retrieve the first and subsequent codes.
# For example:
# @code{.c}
#   TidyIterator itKey = getErrorCodeList();
#   while ( itKey ) {
#     uint code = getNextStringKey( &itKey );
#     // do something with the code, such as lookup a string.
#   }
# @endcode
# @remark These are provided for documentation generation purposes, and
#         probably aren't of much use to the average LibTidy implementor.
# @result Returns a TidyIterator, which is a token used to represent the
#         current position in a list within LibTidy.
#
getStringKeyList = CFUNC(TidyIterator)(  # noqa: N816
    ("getStringKeyList", dll),)

# Given a valid TidyIterator initiated with getStringKeyList(), returns
# an unsigned integer representing the next key value.
# @remark These are provided for documentation generation purposes, and
#         probably aren't of much use to the average LibTidy implementor.
# @param iter The TidyIterator (initiated with getStringKeyList()) token.
# @result Returns a message code.
#
getNextStringKey = CFUNC(ct.c_uint,  # noqa: N816
    ct.POINTER(TidyIterator))(
    ("getNextStringKey", dll), (
    (1, "iter"),))

# @}
# @name Available Languages
# @{

# Initiates an iterator for a list of Tidy's installed languages. This
# iterator allows you to iterate through this list. In order to iterate
# through the list, initiate the iterator with this function, and then use
# use getNextInstalledLanguage() to retrieve the first and subsequent strings.
# For example:
# @code{.c}
#   TidyIterator itList = getInstalledLanguageList();
#   while ( itList ) {
#     printf("%s",  getNextInstalledLanguage( &itList ));
#   }
# @endcode
# @result Returns a TidyIterator, which is a token used to represent the
#         current position in a list within LibTidy.
#
getInstalledLanguageList = CFUNC(TidyIterator)(  # noqa: N816
    ("getInstalledLanguageList", dll),)

# Given a valid TidyIterator initiated with getInstalledLanguageList(),
# returns a string representing a language name that is installed in Tidy.
# @param iter The TidyIterator (initiated with getInstalledLanguageList())
#        token.
# @result Returns a string indicating the installed language.
#
getNextInstalledLanguage = CFUNC(ctmbstr,  # noqa: N816
    ct.POINTER(TidyIterator))(
    ("getNextInstalledLanguage", dll), (
    (1, "iter"),))

# @}

# @} end MessagesKeys group

# @} end public_api group

del va_list

# eof
