from abc import ABC, abstractmethod

class IInstallerSetup(ABC):
    """
    Interface for the InstallerSetup class.
    """

    @abstractmethod
    def handle(self):
        """
        Executes the setup process for initializing the Orionis project.

        This process includes:
        1. Cloning the repository.
        2. Creating a virtual environment.
        3. Installing dependencies from requirements.txt.
        4. Setting up the .env file.
        5. Generating an API key.
        6. Cleaning up temporary files and .git remote origin.

        Raises
        ------
        ValueError
            If there is an error during any subprocess execution.
        Exception
            If any unexpected error occurs.
        """
        pass