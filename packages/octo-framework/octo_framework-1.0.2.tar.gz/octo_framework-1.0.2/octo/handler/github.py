import git
import os
import requests
import re
from colorama import Fore, Style, init


class GitHubRepositorie:
    """
    A class to handle operations related to GitHub repositories such as cloning
    and fetching repository details via GitHub API.
    """

    output_path: str = None
    project_name: str = None
    repo_url: str = None
    repo_data: dict = None

    def __init__(
        self,
        project_name: str | None = None,
        repo_url: str | None = None,
        output_path: str | None = None,
    ) -> None:
        """
        Initialize the GitHubRepositorie instance.

        Args:
            project_name (str | None): The name of the project to be created.
            repo_url (str | None): The URL of the GitHub repository.
            output_path (str | None): The directory where the repository should be cloned.
        """
        self.get_project_name(name=project_name)
        self.set_repo_url(repo_url)
        self.set_output_path(output_path)
        init()

    def get_latest_release_tag(self) -> str:
        """
        Fetch the latest release tag from the GitHub API.

        Returns:
            str: The latest release tag or None if no tag is found.
        """
        if not self._repo_url:
            raise ValueError(
                Fore.RED
                + Style.BRIGHT
                + "Repository URL has not been set."
                + Style.RESET_ALL
            )

        api_url = (
            self._repo_url.replace(
                "https://github.com/", "https://api.github.com/repos/"
            )
            + "/releases/latest"
        )
        response = requests.get(api_url)

        if response.status_code == 404:
            return None

        response.raise_for_status()
        return response.json().get("tag_name")

    def get_repo_data(self) -> str:
        """
        Fetch repository data from the GitHub API.
        """
        api_url = self._repo_url.replace(
            "https://github.com/", "https://api.github.com/repos/"
        )
        response = requests.get(api_url)

        try:
            response.raise_for_status()
            self.repo_data = response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                raise ValueError(
                    Fore.RED
                    + "GitHub repository not found. Please check the repository URL."
                    + Style.RESET_ALL
                )
            else:
                raise ValueError(e)

    @staticmethod
    def validate_path(output_path, dir_name):
        # Validate the output path to ensure it does not already exist
        if os.path.exists(output_path):
            raise ValueError(
                Fore.RED
                + Style.BRIGHT
                + "\n"
                + f"The directory {dir_name} already exists. Please choose a different project name."
                + Style.RESET_ALL
            )

    def clone(self):
        """
        Clone the repository from GitHub.
        """
        output_path = os.path.join(self.output_path, self.project_name)
        self.validate_path(output_path, self.project_name)

        if not self.repo_data:
            self.get_repo_data()

        latest_tag = self.get_latest_release_tag()

        if not latest_tag:
            branch = self.repo_data.get("default_branch", "main")
        else:
            branch = latest_tag

        print(
            Fore.GREEN
            + Style.BRIGHT
            + "\n"
            + f"Cloning {self.project_name}"
            + Fore.CYAN
            + "\n"
            + f"version: [{branch}]"
            + Style.RESET_ALL
            + "\n"
        )

        try:
            git.Repo.clone_from(self._repo_url, output_path, branch=branch)
            print(
                Fore.GREEN
                + Style.BRIGHT
                + self.project_name
                + " has been installed"
                + Style.RESET_ALL
                + "\n"
            )
        except Exception as e:
            print(
                Fore.RED
                + f"An error occurred while cloning the repository: {e}"
                + Style.RESET_ALL
            )

    def get_project_name(self, name: str | None = None):
        """
        Get the project name from the user if not provided.

        Args:
            name (str | None): The name of the project to be created.
        """
        self.project_name = name

        if not self.project_name:
            self.project_name = input(Fore.YELLOW + "Project Name: " + Style.RESET_ALL)

            if not self.project_name:
                self.get_project_name()

    def set_repo_url(self, repo_url: str | None):
        """
        Set the repository URL after validating it.

        Args:
            repo_url (str): The repository URL to be set.

        Raises:
            ValueError: If the URL is not a valid GitHub repository URL.
        """
        first_invalid = False
        while not repo_url or not self.is_valid_github_url(repo_url):
            if first_invalid:
                print(Fore.RED + "Invalid GitHub repository URL" + Style.RESET_ALL)
            first_invalid = True
            repo_url = input(Fore.YELLOW + "Repo URL: " + Style.RESET_ALL)

        self._repo_url = repo_url

    def set_output_path(self, path: str | None = None):
        """
        Set the output path where the repository will be cloned.

        Args:
            path (str | None): The output path to be set.
        """
        if path:
            if not os.path.exists(path):
                msg = "The path appears to be incorrect. Please verify that the path is correct"
                raise ValueError(msg)
            self.output_path = path
        else:
            self.output_path = os.getcwd()

    @staticmethod
    def is_valid_github_url(url: str) -> bool:
        """
        Validate the given GitHub repository URL.

        Args:
            url (str): The URL to be validated.

        Returns:
            bool: True if the URL is valid, False otherwise.
        """
        pattern = re.compile(
            r"^(https:\/\/github\.com\/)" r"[A-Za-z0-9_.-]+\/" r"[A-Za-z0-9_.-]+\/?$"
        )
        return bool(pattern.match(url))
