import threading


class CleanTemplate:
    """This class is responsible for performing all cleaning operations."""

    def __init__(self, project_path: str) -> None:
        self.project_path = project_path

    def clean(self) -> None:
        """Method to execute all cleaning functions in the class."""
        members = dir(self)
        threads = []

        for member in members:
            if member.startswith("clean_"):
                validate_function = getattr(self, member)
                thread = threading.Thread(target=validate_function)
                threads.append(thread)
                thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()
