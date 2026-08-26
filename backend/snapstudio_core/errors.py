class SnapStudioError(Exception): ...
class PartNotFound(SnapStudioError): ...
class PreservationError(SnapStudioError): ...
class FilamentLimitError(SnapStudioError): ...


class UnsoundOutput(SnapStudioError):
    """Studio built a prepared copy whose own descriptions disagree.

    A prepared project states the same structure three times — the root model's
    components, the mesh objects they point at, and the part records in
    `model_settings.config`. If those drift apart the file is wrong even though
    each part of it is well-formed, and Snapmaker Orca should not be the first
    thing to notice. Raised instead of handing over the file; the original is
    untouched either way, because preparing never writes to it.
    """

    def __init__(self, problems: list[str]) -> None:
        self.problems = list(problems)
        super().__init__(
            "Studio built a prepared copy it cannot vouch for and did not save it: "
            + "; ".join(self.problems))


class UnsafeArchive(SnapStudioError):
    """A 3MF that Studio refuses to open: too many entries, or it decompresses to
    more data than the reader budget allows (a zip bomb, or a corrupt file that
    looks like one). The message is safe to show a user verbatim."""
