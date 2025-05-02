from octo.handler.command import Command
from octo.commands.generate.repositories.octo_launch import OctoLaunch
from octo.handler.cache import CloneCache


templates = {
    "octo-launch": OctoLaunch,
}


class StartProject(Command):
    """Create a project from existing templates"""

    def __init__(self):
        super().__init__()
        self.use_django = False
        self.template = "octo-launch"
        self.set_hooks(
            {
                "--octo-launch": "set_octo_launch",
            }
        )

    def handle(self):
        # === import =====================================
        from colorama import Fore, Style, init

        init()
        # === Logic ======================================

        if len(self._argv) > 2:
            project_name = self._argv[2]
            template = templates.get(self.template)

            assert issubclass(template, CloneCache)
            template(project_name=str(project_name)).clone()

        else:
            print(
                Fore.RED
                + "\n"
                + "You must enter the project name"
                + Fore.GREEN
                + "\n"
                + "octo startproject project_name"
                + Style.RESET_ALL
            )

    def set_octo_launch(self):
        """Selects the octo-launch template, which is the default option"""
        self.template = "octo-launch"
