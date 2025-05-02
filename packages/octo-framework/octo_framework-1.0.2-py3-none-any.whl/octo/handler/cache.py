from appdirs import user_cache_dir
import os
import sys
from octo.base import _error_structure
from requests.exceptions import HTTPError
import shutil
from colorama import Fore, Style, init
from octo.handler.clean import CleanTemplate
from octo.handler.github import GitHubRepositorie


class CloneCache:
    """Caching for faster project creation"""

    cache_dir: str = None
    project_name_cache: str = None
    project_name: str = None
    repo_url: str = None
    clean_class: CleanTemplate = None

    def __init__(self, project_name: str | None) -> None:
        """Initialize the CloneCache instance with a project name
        and setup the cache directory and repository"""
        self.get_cache_dir()
        self.project_name = project_name
        self.get_repo()

    def get_cache_dir(self):
        """Get the cache directory path for the application
        and create it if it does not exist"""
        cache_dir = user_cache_dir(appname="octo_framework", appauthor=False)

        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        self.cache_dir = cache_dir

    def clone(self):
        """Clone the repository if it does not exist in the cache"""
        clone = False
        project_cache = os.path.join(self.cache_dir, self.project_name_cache)

        if os.path.exists(project_cache):
            # Check if the cached version is up-to-date
            clone = self.get_verion()

        if not clone:
            # If not up-to-date, remove the old cache and clone anew
            if os.path.exists(project_cache):
                shutil.rmtree(project_cache)

            self.repo.clone()

        self.clone_from_cache()

    def get_repo(self) -> GitHubRepositorie:
        """Create a GitHub repository object for the project"""
        repo = GitHubRepositorie(
            project_name=self.project_name_cache,
            repo_url=self.repo_url,
            output_path=self.cache_dir,
        )
        self.repo = repo

    def get_verion(self):
        """Check the version of the cached repository against the latest release"""
        path = os.path.join(self.cache_dir, self.project_name_cache + "/config")

        sys.path.append(path)
        try:
            from app import version  # type: ignore

            release = self.repo.get_latest_release_tag()
            return release == version
        except ImportError:
            raise ValueError(_error_structure)
        except HTTPError:
            return True

    @staticmethod
    def validate_path(output_path, dir_name):
        """Validate the output path to ensure it does not already exist"""
        if os.path.exists(output_path):
            raise ValueError(
                Fore.RED
                + Style.BRIGHT
                + "\n"
                + f"The directory {dir_name} already exists. Please choose a different project name."
                + Style.RESET_ALL
            )

    def clone_from_cache(self):
        """Clone from the cache directory to the current working directory."""
        init()

        repo_cache = os.path.join(self.cache_dir, self.project_name_cache)
        new_path = os.path.join(os.getcwd(), self.project_name)

        self.validate_path(new_path, self.project_name)

        shutil.copytree(repo_cache, new_path)
        self.clean_class(project_path=new_path).clean()
        print(
            Fore.MAGENTA
            + Style.BRIGHT
            + "\n"
            + f"A {self.project_name} has been created"
            + Style.RESET_ALL
        )
