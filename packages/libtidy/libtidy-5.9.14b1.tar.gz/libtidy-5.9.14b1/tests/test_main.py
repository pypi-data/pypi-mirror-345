# Copyright (c) 2024 Adam Karpierz
# SPDX-License-Identifier: HTMLTIDY

import unittest
import sys
from pathlib import Path
import subprocess

import libtidy

here = Path(__file__).resolve().parent
data_dir = here/"data"


class MainTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # cls.maxDiff = None
        cls.org_executable = str(data_dir/"tidy.exe")

    def setUp(self):
        pass

    def test_main(self):
        mod_output = subprocess.run([sys.executable, "-m", "libtidy.tidy", "--version"],
                                    capture_output=True, text=True)
        org_output = subprocess.run([self.org_executable, "--version"],
                                    capture_output=True, text=True)
        self.assertEqual(mod_output.returncode, org_output.returncode)
        self.assertEqual(mod_output.stdout, org_output.stdout)
        mod_output = subprocess.run([sys.executable, "-m", "libtidy.tidy", "--help"],
                                    capture_output=True, text=True)
        org_output = subprocess.run([self.org_executable, "--help"],
                                    capture_output=True, text=True)
        self.assertEqual(mod_output.returncode, org_output.returncode)
        self.assertEqual(mod_output.stdout, org_output.stdout.replace("tidy.exe", "tidy.py"))
        mod_output = subprocess.run([sys.executable, "-m", "libtidy.tidy", "-language", "help"],
                                    capture_output=True, text=True)
        org_output = subprocess.run([self.org_executable, "-language", "help"],
                                    capture_output=True, text=True)
        self.assertEqual(mod_output.returncode, org_output.returncode)
        self.assertEqual(mod_output.stdout, org_output.stdout)
        mod_output = subprocess.run([sys.executable, "-m", "libtidy.tidy", "-xml-help"],
                                    capture_output=True, text=True)
        org_output = subprocess.run([self.org_executable, "-xml-help"],
                                    capture_output=True, text=True)
        self.assertEqual(mod_output.returncode, org_output.returncode)
        self.assertEqual(mod_output.stdout, org_output.stdout)
        mod_output = subprocess.run([sys.executable, "-m", "libtidy.tidy", "-xml-error-strings"],
                                    capture_output=True, text=True)
        org_output = subprocess.run([self.org_executable, "-xml-error-strings"],
                                    capture_output=True, text=True)
        self.assertEqual(mod_output.returncode, org_output.returncode)
        self.assertEqual(mod_output.stdout, org_output.stdout)
        mod_output = subprocess.run([sys.executable, "-m", "libtidy.tidy", "-xml-options-strings"],
                                    capture_output=True, text=True)
        org_output = subprocess.run([self.org_executable, "-xml-options-strings"],
                                    capture_output=True, text=True)
        self.assertEqual(mod_output.returncode, org_output.returncode)
        self.assertEqual(mod_output.stdout, org_output.stdout)
        mod_output = subprocess.run([sys.executable, "-m", "libtidy.tidy", "-xml-strings"],
                                    capture_output=True, text=True)
        org_output = subprocess.run([self.org_executable, "-xml-strings"],
                                    capture_output=True, text=True)
        self.assertEqual(mod_output.returncode, org_output.returncode)
        self.assertEqual(mod_output.stdout, org_output.stdout)
        mod_output = subprocess.run([sys.executable, "-m", "libtidy.tidy", "-help-config"],
                                    capture_output=True, text=True)
        org_output = subprocess.run([self.org_executable, "-help-config"],
                                    capture_output=True, text=True)
        self.assertEqual(mod_output.returncode, org_output.returncode)
        self.assertEqual(mod_output.stdout, org_output.stdout)
        mod_output = subprocess.run([sys.executable, "-m", "libtidy.tidy", "-help-env"],
                                    capture_output=True, text=True)
        org_output = subprocess.run([self.org_executable, "-help-env"],
                                    capture_output=True, text=True)
        self.assertEqual(mod_output.returncode, org_output.returncode)
        self.assertEqual(mod_output.stdout, org_output.stdout)
        mod_output = subprocess.run([sys.executable, "-m", "libtidy.tidy", "-help-option"],
                                    capture_output=True, text=True)
        org_output = subprocess.run([self.org_executable, "-help-option"],
                                    capture_output=True, text=True)
        self.assertEqual(mod_output.returncode, org_output.returncode)
        self.assertEqual(mod_output.stdout, org_output.stdout)
        mod_output = subprocess.run([sys.executable, "-m", "libtidy.tidy", "-xml-config"],
                                    capture_output=True, text=True)
        org_output = subprocess.run([self.org_executable, "-xml-config"],
                                    capture_output=True, text=True)
        self.assertEqual(mod_output.returncode, org_output.returncode)
        self.assertEqual(mod_output.stdout, org_output.stdout)
        mod_output = subprocess.run([sys.executable, "-m", "libtidy.tidy", "-show-config"],
                                    capture_output=True, text=True)
        org_output = subprocess.run([self.org_executable, "-show-config"],
                                    capture_output=True, text=True)
        self.assertEqual(mod_output.returncode, org_output.returncode)
        self.assertEqual(mod_output.stdout, org_output.stdout)
        mod_output = subprocess.run([sys.executable, "-m", "libtidy.tidy", "-export-config"],
                                    capture_output=True, text=True)
        org_output = subprocess.run([self.org_executable, "-export-config"],
                                    capture_output=True, text=True)
        self.assertEqual(mod_output.returncode, org_output.returncode)
        self.assertEqual(mod_output.stdout, org_output.stdout)
        mod_output = subprocess.run([sys.executable, "-m", "libtidy.tidy", "-export-default-config"],
                                    capture_output=True, text=True)
        org_output = subprocess.run([self.org_executable, "-export-default-config"],
                                    capture_output=True, text=True)
        self.assertEqual(mod_output.returncode, org_output.returncode)
        self.assertEqual(mod_output.stdout, org_output.stdout)

    def test_regression(self):
        pass
