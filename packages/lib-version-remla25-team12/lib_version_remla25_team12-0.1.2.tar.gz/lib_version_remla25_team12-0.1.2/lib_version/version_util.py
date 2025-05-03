import importlib.metadata

class VersionUtil:
    @staticmethod
    def get_version():
        try:
            return importlib.metadata.version("lib-version-remla25-team12")
        except importlib.metadata.PackageNotFoundError:
            return "dev"
