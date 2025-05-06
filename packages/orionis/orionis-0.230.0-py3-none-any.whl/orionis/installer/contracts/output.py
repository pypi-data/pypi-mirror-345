from abc import ABC, abstractmethod

class IInstallerOutput(ABC):

    @abstractmethod
    def printHelp(self):
        """
        Prints the help message with available commands.

        If the ASCII file is not found, it falls back to a basic message.
        """
        pass

    @abstractmethod
    def printIcon(self):
        """
        Prints the Orionis icon with a motivational message.

        If the ASCII file is not found, it falls back to a basic message.
        """
        pass

    @abstractmethod
    def printStartInstallation(self):
        """
        Prints the start of the installation message.

        Displays the Orionis icon and a thank you message.
        """
        pass

    @abstractmethod
    def printEndInstallation(self):
        """
        Prints the end of the installation message.

        Displays a welcome message and encourages the user to start using the framework.
        """
        pass