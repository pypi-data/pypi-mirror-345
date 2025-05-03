import subprocess
import sys
from orionis.installer.contracts.manager import IInstallerManager
from orionis.installer.contracts.output import IInstallerOutput
from orionis.installer.output import InstallerOutput
from orionis.installer.setup import InstallerSetup

class InstallerManager(IInstallerManager):
    """
    Management class responsible for handling framework-related operations.

    This class provides methods to display the framework version, execute upgrades,
    create new applications, and display additional information.

    Attributes
    ----------
    _output : InstallerOutput
        Instance of InstallerOutput to manage command-line display messages.
    """

    def __init__(self):
        """
        Initialize the Management class with an output handler.
        """
        self._output : IInstallerOutput = InstallerOutput()

    def handleVersion(self) -> str:
        """
        Display the current version of the framework in ASCII format.

        Returns
        -------
        str
            The ASCII representation of the framework version.
        """
        return self._output.printIcon()

    def handleUpgrade(self) -> None:
        """
        Execute the framework upgrade process to the latest version.

        Raises
        ------
        RuntimeError
            If an error occurs during the upgrade process.
        """
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "orionis"])
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Upgrade failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Upgrade failed: {e}")

    def handleNewApp(self, name_app: str = "example-app") -> None:
        """
        Create a new application with the specified name.

        Parameters
        ----------
        name_app : str, optional
            The name of the new application (default is "example-app").

        Raises
        ------
        RuntimeError
            If an error occurs during the application setup.
        """
        try:
            return InstallerSetup(name=name_app, output=self._output).handle()
        except Exception as e:
            raise RuntimeError(f"Failed to create new app: {e}")

    def handleInfo(self) -> None:
        """
        Display additional framework information in ASCII format.

        Raises
        ------
        RuntimeError
            If an error occurs while displaying information.
        """
        try:
            self._output.printHelp()
        except Exception as e:
            raise RuntimeError(f"Failed to display information: {e}")
