# **************************************************************************** #
# @file
# Treat buffer as a stream that Tidy can use for I/O operations. It offers
# the ability for the buffer to grow as bytes are added, and keeps track
# of current read and write points.
#
# @author
#     HTACG, et al (consult git log)
#
# @copyright
#     Copyright (c) 1998-2017 World Wide Web Consortium (Massachusetts
#     Institute of Technology, European Research Consortium for Informatics
#     and Mathematics, Keio University).
# @copyright
#     See tidy.h for license.
#
# @date
#     Consult git log.
# **************************************************************************** #

import ctypes as ct

from ._platform import CFUNC
from ._dll      import dll

from ._tidyplatform import byte
from ._tidyplatform import *  # noqa
from ._tidy import TidyBuffer, TidyAllocator, TidyInputSource, TidyOutputSink

# A TidyBuffer is chunk of memory that can be used for multiple I/O purposes
# within Tidy.
# @ingroup IO
#
# TidyBuffer has been moved to _tidy.py due to cyclic rference

# Initialize data structure using the default allocator
BufInit = CFUNC(None,
    ct.POINTER(TidyBuffer))(
    ("tidyBufInit", dll), (
    (1, "buf"),))

# Initialize data structure using the given custom allocator
BufInitWithAllocator = CFUNC(None,
    ct.POINTER(TidyBuffer),
    ct.POINTER(TidyAllocator))(
    ("tidyBufInitWithAllocator", dll), (
    (1, "buf"),
    (1, "allocator"),))

# Free current buffer, allocate given amount, reset input pointer,
# use the default allocator
BufAlloc = CFUNC(None,
    ct.POINTER(TidyBuffer),
    ct.c_uint)(
    ("tidyBufAlloc", dll), (
    (1, "buf"),
    (1, "allocSize"),))

# Free current buffer, allocate given amount, reset input pointer,
# use the given custom allocator
BufAllocWithAllocator = CFUNC(None,
    ct.POINTER(TidyBuffer),
    ct.POINTER(TidyAllocator),
    ct.c_uint)(
    ("tidyBufAllocWithAllocator", dll), (
    (1, "buf"),
    (1, "allocator"),
    (1, "allocSize"),))

# Expand buffer to given size.
# Chunk size is minimum growth. Pass 0 for default of 256 bytes.
BufCheckAlloc = CFUNC(None,
    ct.POINTER(TidyBuffer),
    ct.c_uint,
    ct.c_uint)(
    ("tidyBufCheckAlloc", dll), (
    (1, "buf"),
    (1, "allocSize"),
    (1, "chunkSize"),))

# Free current contents and zero out
BufFree = CFUNC(None,
    ct.POINTER(TidyBuffer))(
    ("tidyBufFree", dll), (
    (1, "buf"),))

# Set buffer bytes to 0
BufClear = CFUNC(None,
    ct.POINTER(TidyBuffer))(
    ("tidyBufClear", dll), (
    (1, "buf"),))

# Attach to existing buffer
BufAttach = CFUNC(None,
    ct.POINTER(TidyBuffer),
    ct.POINTER(byte),
    ct.c_uint)(
    ("tidyBufAttach", dll), (
    (1, "buf"),
    (1, "bp"),
    (1, "size"),))

# Detach from buffer.  Caller must free.
BufDetach = CFUNC(None,
    ct.POINTER(TidyBuffer))(
    ("tidyBufDetach", dll), (
    (1, "buf"),))

# Append bytes to buffer.  Expand if necessary.
BufAppend = CFUNC(None,
    ct.POINTER(TidyBuffer),
    ct.c_void_p,
    ct.c_uint)(
    ("tidyBufAppend", dll), (
    (1, "buf"),
    (1, "vp"),
    (1, "size"),))

# Append one byte to buffer.  Expand if necessary.
BufPutByte = CFUNC(None,
    ct.POINTER(TidyBuffer),
    byte)(
    ("tidyBufPutByte", dll), (
    (1, "buf"),
    (1, "bv"),))

# Get byte from end of buffer
BufPopByte = CFUNC(ct.c_int,
    ct.POINTER(TidyBuffer))(
    ("tidyBufPopByte", dll), (
    (1, "buf"),))

# Get byte from front of buffer.  Increment input offset.
BufGetByte = CFUNC(ct.c_int,
    ct.POINTER(TidyBuffer))(
    ("tidyBufGetByte", dll), (
    (1, "buf"),))

# At end of buffer?
BufEndOfInput = CFUNC(ct.c_bool,
    ct.POINTER(TidyBuffer))(
    ("tidyBufEndOfInput", dll), (
    (1, "buf"),))

# Put a byte back into the buffer.  Decrement input offset.
BufUngetByte = CFUNC(None,
    ct.POINTER(TidyBuffer),
    byte)(
    ("tidyBufUngetByte", dll), (
    (1, "buf"),
    (1, "bv"),))

# ************* #
#    TIDY       #
# ************* #

# Initialize a buffer input source
InitInputBuffer = CFUNC(None,
    ct.POINTER(TidyInputSource),
    ct.POINTER(TidyBuffer))(
    ("tidyInitInputBuffer", dll), (
    (1, "inp"),
    (1, "buf"),))

# Initialize a buffer output sink
InitOutputBuffer = CFUNC(None,
    ct.POINTER(TidyOutputSink),
    ct.POINTER(TidyBuffer))(
    ("tidyInitOutputBuffer", dll), (
    (1, "outp"),
    (1, "buf"),))

# eof
