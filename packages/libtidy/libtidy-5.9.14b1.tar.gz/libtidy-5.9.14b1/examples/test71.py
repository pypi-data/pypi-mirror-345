# Copyright (c) 2024 Adam Karpierz
# SPDX-License-Identifier: HTMLTIDY

# 20150206 - Test app for Issue #71
#
# A simple API example of getting the body text, first as html,
# and then as a raw stream.
#
# Note: This simple test app has no error checking

import sys
import ctypes as ct

import libtidy as tidy
from libtidy import TidyDoc, TidyNode, TidyBuffer

sample = """\
<!DOCTYPE html>
<head>
<meta charset="utf-8">
<title>Test app for Issue #71</title>
<body>something &amp; escaped</body>
</html>"""


def main(argv=sys.argv[1:]):

    print("\nSimple example of HTML Tidy API use.")
    tdoc: TidyDoc = tidy.Create()
    buff = TidyBuffer()
    tidy.BufInit(ct.byref(buff))
    bsample = sample.encode("utf-8")
    tidy.BufAppend(ct.byref(buff), bsample, len(bsample))
    tidy.ParseBuffer(tdoc, ct.byref(buff))
    body: TidyNode = tidy.GetBody(tdoc)
    text_node: TidyNode = tidy.GetChild(body)
    buff2 = TidyBuffer()
    tidy.BufInit(ct.byref(buff2))
    print("This is the 'escaped' text, from tidy.NodeGetText(...), suitable "
          "for html use...")
    tidy.NodeGetText(tdoc, text_node, ct.byref(buff2))
    sys.stdout.write(bytes(buff2.bp[0:buff2.size]).decode("utf-8"))
    print("This is the 'raw' lexer values, from tidy.NodeGetValue(...).")
    tidy.NodeGetValue(tdoc, text_node, ct.byref(buff2))
    sys.stdout.write(bytes(buff2.bp[0:buff2.size]).decode("utf-8"))
    print()

    return 0


if __name__.rpartition(".")[-1] == "__main__":
    sys.exit(main())
