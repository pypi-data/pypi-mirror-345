import os
import platform
import sys
from unittest.mock import MagicMock

# Mock Windows-only modules for docs build
if platform.system() != "Windows":

    class Mock(MagicMock):
        @classmethod
        def __getattr__(cls, name):
            return MagicMock()

    MOCK_MODULES = ["winreg", "clr", "ZOSAPI", "ZOSAPI_NetHelper", "ZOSAPI_Interfaces"]
    for mod_name in MOCK_MODULES:
        sys.modules[mod_name] = Mock()

import winreg
from itertools import islice

import clr

# This boilerplate requires the 'pythonnet' module.
# The following instructions are for installing the 'pythonnet' module via pip:
#    1. Ensure you are running a Python version compatible with PythonNET. Check the article "ZOS-API using Python.NET" or
#    "Getting started with Python" in our knowledge base for more details.
#    2. Install 'pythonnet' from pip via a command prompt (type 'cmd' from the start menu or press Windows + R and type 'cmd' then enter)
#
#        python -m pip install pythonnet


class PythonStandaloneApplication(object):
    class LicenseException(Exception):
        pass

    class ConnectionException(Exception):
        pass

    class InitializationException(Exception):
        pass

    class SystemNotPresentException(Exception):
        pass

    def __init__(self, path=None):
        # determine location of ZOSAPI_NetHelper.dll & add as reference
        aKey = winreg.OpenKey(
            winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER),
            r"Software\Zemax",
            0,
            winreg.KEY_READ,
        )
        zemaxData = winreg.QueryValueEx(aKey, "ZemaxRoot")
        NetHelper = os.path.join(
            os.sep, zemaxData[0], r"ZOS-API\Libraries\ZOSAPI_NetHelper.dll"
        )
        winreg.CloseKey(aKey)
        clr.AddReference(NetHelper)
        import ZOSAPI_NetHelper

        # Find the installed version of OpticStudio
        # if len(path) == 0:
        if path is None:
            isInitialized = ZOSAPI_NetHelper.ZOSAPI_Initializer.Initialize()
        else:
            # Note -- uncomment the following line to use a custom initialization path
            isInitialized = ZOSAPI_NetHelper.ZOSAPI_Initializer.Initialize(path)

        # determine the ZOS root directory
        if isInitialized:
            dir = ZOSAPI_NetHelper.ZOSAPI_Initializer.GetZemaxDirectory()
        else:
            raise PythonStandaloneApplication.InitializationException(
                "Unable to locate Zemax OpticStudio.  Try using a hard-coded path."
            )

        # add ZOS-API referencecs
        clr.AddReference(os.path.join(os.sep, dir, "ZOSAPI.dll"))
        clr.AddReference(os.path.join(os.sep, dir, "ZOSAPI_Interfaces.dll"))
        import ZOSAPI

        # create a reference to the API namespace
        self.ZOSAPI = ZOSAPI

        # create a reference to the API namespace
        self.ZOSAPI = ZOSAPI

        # Create the initial connection class
        self.TheConnection = ZOSAPI.ZOSAPI_Connection()

        if self.TheConnection is None:
            raise PythonStandaloneApplication.ConnectionException(
                "Unable to initialize .NET connection to ZOSAPI"
            )

        self.TheApplication = self.TheConnection.CreateNewApplication()
        if self.TheApplication is None:
            raise PythonStandaloneApplication.InitializationException(
                "Unable to acquire ZOSAPI application"
            )

        if self.TheApplication.IsValidLicenseForAPI == False:
            raise PythonStandaloneApplication.LicenseException(
                "License is not valid for ZOSAPI use"
            )

        self.TheSystem = self.TheApplication.PrimarySystem
        if self.TheSystem is None:
            raise PythonStandaloneApplication.SystemNotPresentException(
                "Unable to acquire Primary system"
            )

    def __del__(self):
        if self.TheApplication is not None:
            self.TheApplication.CloseApplication
            self.TheApplication = None

        self.TheConnection = None

    def OpenFile(self, filepath, saveIfNeeded):
        if self.TheSystem is None:
            raise PythonStandaloneApplication.SystemNotPresentException(
                "Unable to acquire Primary system"
            )
        self.TheSystem.LoadFile(filepath, saveIfNeeded)

    def CloseFile(self, save):
        if self.TheSystem is None:
            raise PythonStandaloneApplication.SystemNotPresentException(
                "Unable to acquire Primary system"
            )
        self.TheSystem.Close(save)

    def SamplesDir(self):
        if self.TheApplication is None:
            raise PythonStandaloneApplication.InitializationException(
                "Unable to acquire ZOSAPI application"
            )

        return self.TheApplication.SamplesDir

    def ExampleConstants(self):
        if (
            self.TheApplication.LicenseStatus
            == self.ZOSAPI.LicenseStatusType.PremiumEdition
        ):
            return "Premium"
        elif (
            self.TheApplication.LicenseStatus
            == self.ZOSAPI.LicenseStatusType.EnterpriseEdition
        ):
            return "Enterprise"
        elif (
            self.TheApplication.LicenseStatus
            == self.ZOSAPI.LicenseStatusType.ProfessionalEdition
        ):
            return "Professional"
        elif (
            self.TheApplication.LicenseStatus
            == self.ZOSAPI.LicenseStatusType.StandardEdition
        ):
            return "Standard"
        elif (
            self.TheApplication.LicenseStatus
            == self.ZOSAPI.LicenseStatusType.OpticStudioHPCEdition
        ):
            return "HPC"
        else:
            return "Invalid"

    def reshape(self, data, x, y, transpose=False):
        """Converts a System.Double[,] to a 2D list for plotting or post processing

        Parameters
        ----------
        data      : System.Double[,] data directly from ZOS-API
        x         : x width of new 2D list [use var.GetLength(0) for dimension]
        y         : y width of new 2D list [use var.GetLength(1) for dimension]
        transpose : transposes data; needed for some multi-dimensional line series data

        Returns
        -------
        res       : 2D list; can be directly used with Matplotlib or converted to
                    a numpy array using numpy.asarray(res)
        """
        if type(data) is not list:
            data = list(data)
        var_lst = [y] * x
        it = iter(data)
        res = [list(islice(it, i)) for i in var_lst]
        if transpose:
            return self.transpose(res)
        return res

    def transpose(self, data):
        """Transposes a 2D list (Python3.x or greater).

        Useful for converting mutli-dimensional line series (i.e. FFT PSF)

        Parameters
        ----------
        data      : Python native list (if using System.Data[,] object reshape first)

        Returns
        -------
        res       : transposed 2D list
        """
        if type(data) is not list:
            data = list(data)
        return list(map(list, zip(*data)))


if __name__ == "__main__":
    pass
