import dataclasses


@dataclasses.dataclass
class AWSNetwork:
    """Class to store network location information."""

    region: str
    vpc_id: str
    security_group_ids: list[str]
    subnet_ids: list[str] = dataclasses.field(default_factory=list)

    availability_zones: list[str] = dataclasses.field(default_factory=list)
    availability_zone: str | None = None


@dataclasses.dataclass
class Tags:
    Workload: str
    Component: str | None = None
    Name: str | None = None
    Owner: str = "rebelmouse.com"

    def asdict(self):
        """Convert dataclass to dictionary."""
        assert self.Workload, "Workload must be set."
        workload = self.Workload

        assert self.Name, "Name must be set."
        name = self.Name

        data = {
            "Workload": workload,
            "Component": self.Component or name,
            "Name": self.Name or name,
        }

        if self.Owner:
            data["Owner"] = self.Owner

        return data
