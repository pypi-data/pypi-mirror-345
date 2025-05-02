from octo.handler.manager import Manager as ManagerTemplate
from .startapp import StartApp
from .startproject import StartProject


class Manager(ManagerTemplate):
    @staticmethod
    def validate_file(): ...

    def help(self):
        from colorama import Fore, Style, init

        init()
        print(Fore.GREEN, Style.BRIGHT, "\n[Manager]", Style.RESET_ALL)
        for command, _class in self._schema.items():
            print(
                "   " + Fore.CYAN,
                command + ":\t",
                Fore.YELLOW,
                _class.__doc__,
                Style.RESET_ALL,
            )
        exit(0)


manager = Manager()
manager.set_schema(
    {
        "startapp": StartApp,
        "startproject": StartProject,
    }
)


def main():
    try:
        import django  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    try:
        return manager.setup()
    except Exception as e:
        if str(e) in "foo":
            manager.help()
        else:
            print(str(e))
    return exit(0)
