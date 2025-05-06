import os
import datetime
import requests
from orionis.framework import API, NAME, VERSION, DOCS
from orionis.installer.contracts.output import IInstallerOutput

class InstallerOutput(IInstallerOutput):
    """
    A class to handle the output and display messages for the Orionis installer.

    This class provides methods to load ASCII art, format messages with ANSI colors,
    and display installation-related information such as commands, version, and status.

    Attributes
    ----------
    None

    Methods
    -------
    _loadAsciiFile(name: str) -> str
        Loads an ASCII file from the static directory.
    _ansiMessage(message: str) -> str
        Formats a message with green ANSI color.
    _ansiCommands() -> str
        Formats a list of commands with yellow ANSI color.
    _ansiVersion(version: str = None) -> str
        Formats version information with green ANSI color.
    _ansiTextGreen(text: str) -> str
        Wraps text in green ANSI color.
    _year() -> str
        Returns the current year as a string.
    _newVersion() -> str
        Checks for a new version of Orionis and returns a formatted message.
    _replacePlaceholders(content: str, message: str) -> str
        Replaces placeholders in a string with dynamic content.
    _fallbackAscii() -> str
        Provides a fallback ASCII message if the file is not found.
    printHelp()
        Prints the help message with available commands.
    printIcon()
        Prints the Orionis icon with a motivational message.
    printStartInstallation()
        Prints the start of the installation message.
    printEndInstallation()
        Prints the end of the installation message.
    """

    def _loadAsciiFile(self, name: str) -> str:
        """
        Loads an ASCII file from the static directory.

        Parameters
        ----------
        name : str
            The name of the ASCII file (without the .ascii extension).

        Returns
        -------
        str
            The content of the ASCII file.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        """
        dir_path = os.path.dirname(__file__)
        path = os.path.join(dir_path, '..', 'static', 'ascii', f"{name}.ascii")
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File {name}.ascii not found")

    def _ansiMessage(self, message: str) -> str:
        """
        Formats a message with green ANSI color.

        Parameters
        ----------
        message : str
            The message to format.

        Returns
        -------
        str
            The formatted message.
        """
        return "\033[92m{} \033[0m".format(message)

    def _ansiCommands(self) -> str:
        """
        Formats a list of commands with yellow ANSI color.

        Returns
        -------
        str
            The formatted list of commands.
        """
        commands = [
            {'name': 'orionis new <app_name>', 'description': 'Creates a new Orionis app with the specified name.'},
            {'name': 'orionis --version', 'description': 'Displays the current version of Orionis.'},
            {'name': 'orionis --upgrade', 'description': 'Upgrades Orionis to the latest version.'}
        ]
        commands_array = [
            "\033[1m\033[93m- {} :\033[0m {}".format(command['name'], command['description'])
            for command in commands
        ]
        return "\n".join(commands_array)

    def _ansiVersion(self, version: str = None) -> str:
        """
        Formats version information with green ANSI color.

        Parameters
        ----------
        version : str, optional
            The latest version available. If None, assumes the current version is the latest.

        Returns
        -------
        str
            The formatted version message.
        """
        if version:
            return self._ansiTextGreen(f"A new version ({version}) is available. Please consider upgrading from the current version ({VERSION}).")
        return self._ansiTextGreen("You are using the latest stable version available.")

    def _ansiTextGreen(self, text: str) -> str:
        """
        Wraps text in green ANSI color.

        Parameters
        ----------
        text : str
            The text to format.

        Returns
        -------
        str
            The formatted text.
        """
        return f"\u001b[32m{text}\u001b[0m"

    def _year(self) -> str:
        """
        Returns the current year as a string.

        Returns
        -------
        str
            The current year.
        """
        return str(datetime.datetime.now().year)

    def _newVersion(self) -> str:
        """
        Checks for a new version of Orionis and returns a formatted message.

        Returns
        -------
        str
            The formatted version message.
        """
        try:
            response = requests.get(API, timeout=10)
            response.raise_for_status()
            data = response.json()
            latest_version = data.get("info", {}).get("version")
            if not latest_version:
                raise ValueError("Version information not found in API response.")
            if latest_version != VERSION:
                return self._ansiVersion(latest_version)
            return self._ansiVersion()
        except (requests.RequestException, ValueError) as e:
            return self._ansiVersion()

    def _replacePlaceholders(self, content: str, message: str) -> str:
        """
        Replaces placeholders in a string with dynamic content.

        Parameters
        ----------
        content : str
            The string containing placeholders.
        message : str
            The message to replace the {{message}} placeholder.

        Returns
        -------
        str
            The string with placeholders replaced.
        """
        return content.replace('{{version}}', VERSION) \
                      .replace('{{docs}}', DOCS) \
                      .replace('{{year}}', self._year()) \
                      .replace('{{message}}', self._ansiMessage(message)) \
                      .replace('{{commands}}', self._ansiCommands()) \
                      .replace('{{new_version}}', self._newVersion())

    def _fallbackAscii(self) -> str:
        """
        Provides a fallback ASCII message if the file is not found.

        Returns
        -------
        str
            The fallback message.
        """
        return f"{NAME.upper()}\nVersion: {VERSION}\nDocs: {DOCS}"

    def printHelp(self):
        """
        Prints the help message with available commands.

        If the ASCII file is not found, it falls back to a basic message.
        """
        try:
            content = self._loadAsciiFile('info')
            output = self._replacePlaceholders(content, "The list of commands accepted by the Orionis interpreter are:")
            print(output)
        except FileNotFoundError:
            output = self._fallbackAscii()
            print(output)

    def printIcon(self):
        """
        Prints the Orionis icon with a motivational message.

        If the ASCII file is not found, it falls back to a basic message.
        """
        try:
            content = self._loadAsciiFile('icon')
            output = self._replacePlaceholders(content, "Python isn't just powerful; it’s thrilling.")
            print(output)
        except FileNotFoundError:
            output = self._fallbackAscii()
            print(output)

    def printStartInstallation(self):
        """
        Prints the start of the installation message.

        Displays the Orionis icon and a thank you message.
        """
        self.printIcon()
        print(self._ansiTextGreen("Thank you for using the framework!"))

    def printEndInstallation(self):
        """
        Prints the end of the installation message.

        Displays a welcome message and encourages the user to start using the framework.
        """
        print(self._ansiTextGreen("Welcome aboard, the journey starts now. Let your imagination soar!"))
        print("-------------------------------------------")