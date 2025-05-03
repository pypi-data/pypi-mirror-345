import dataclasses


@dataclasses.dataclass
class NetworkConfig:
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
    Owner: str = "rebelmouse.com"
    Application: str | None = None
    Component: str | None = None
    Name: str | None = None
    Instance: str | None = None

    def asdict(self):
        """Convert dataclass to dictionary."""
        assert self.Workload, "Workload must be set."
        workload = self.Workload

        assert self.Name or self.Instance, "Name or Instance must be set."
        name = self.Name or self.Instance

        data = {
            "Workload": workload,
            "Name": self.Name or name,
            "Application": self.Application or name,
            "Component": self.Component or name,
            "Instance": self.Instance or name,
        }

        if self.Owner:
            data["Owner"] = self.Owner

        return data
