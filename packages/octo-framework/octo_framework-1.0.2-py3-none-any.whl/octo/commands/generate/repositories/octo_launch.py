from octo.handler.cache import CloneCache
from octo.handler.clean import CleanTemplate
import shutil
import os
from octo.commands.generate.utils import read_file, write_file
from octo.commands.generate.utils import replace_in_files


class OctoLaunchClean(CleanTemplate):
    def clean_dir(self):
        dirs = [
            ".git",
        ]
        for dir in dirs:
            shutil.rmtree(os.path.join(self.project_path, dir))

    def clean_file(self):
        files = [
            "README.rst",
            "docs/index.rst",
            "LICENSE",
            "CONTRIBUTING.md",
        ]
        for file in files:
            os.remove(os.path.join(self.project_path, file))

    def clean_docs(self):
        docs = os.path.join(self.project_path, "docs/")
        for entry in os.scandir(docs):
            if entry.is_dir():
                shutil.rmtree(os.path.join(docs, entry.name))

    def clean_appfile(self):
        """Clears the values of all variables in the file."""
        app_file = os.path.join(self.project_path, "config/app.py")
        content = read_file(app_file)
        cleared_content = []
        for line in content:
            # Check if the line contains an assignment
            if "=" in line:
                # Split the line into variable and value
                parts = line.split("=", 1)
                # Keep the variable part and clear the value part
                cleared_line = parts[0].strip() + ' = ""\n'
                cleared_content.append(cleared_line)
            else:
                cleared_content.append(line)
        write_file(app_file, cleared_content)


class OctoLaunch(CloneCache):
    project_name_cache = "octo-launch"
    repo_url = "https://github.com/caodlly/octo-launch"
    clean_class = OctoLaunchClean

    def clone(self):
        super().clone()
        files = [
            "docker-compose.dev.yml",
            "docker-compose.docs.yml",
            "docker-compose.gunicorn.yml",
            "docker-compose.node.yml",
            "docker-compose.uwsgi.yml",
            os.path.join(".envs", ".env.dev"),
        ]
        replace_in_files(
            files, new_word=self.project_name, project_path=self.project_name
        )
