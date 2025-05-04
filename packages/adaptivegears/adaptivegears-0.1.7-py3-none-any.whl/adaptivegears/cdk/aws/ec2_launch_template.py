from cdktf import TerraformOutput, Token, TerraformIterator
from cdktf_cdktf_provider_aws.launch_template import (
    LaunchTemplate,
    LaunchTemplateTagSpecifications,
    LaunchTemplateMetadataOptions,
    LaunchTemplateMonitoring,
    LaunchTemplateBlockDeviceMappings,
    LaunchTemplateBlockDeviceMappingsEbs,
)
from cdktf_cdktf_provider_aws.data_aws_vpc import DataAwsVpc
from cdktf_cdktf_provider_aws.data_aws_security_groups import DataAwsSecurityGroups
from cdktf_cdktf_provider_aws.data_aws_ami import DataAwsAmi
from cdktf_cdktf_provider_aws.data_aws_iam_instance_profile import (
    DataAwsIamInstanceProfile,
)
from cdktf_cdktf_provider_aws.data_aws_subnets import DataAwsSubnets
from .ec2_keypair import EC2Keypair
from .. import dtype


class EC2LaunchTemplate:
    def __init__(
        self,
        stack,
        ns,
        tags: dtype.Tags,
        network: dtype.AWSNetwork,
        instance_type: str = "m7i.large",
        instance_ami: str = "ami-0779caf41f9ba54f0",
        instance_keypair: EC2Keypair | str | None = None,
        instance_profile="ec2_instance",
        volume_size: int = 25,
        volume_type: str = "gp3",
    ):
        self.stack = stack
        self.ns = ns
        self.tags = tags

        self.network = network
        self.launch_template = None

        self.vpc = DataAwsVpc(
            self.stack,
            f"{ns}__vpc",
            id=self.network.vpc_id,
        )
        TerraformOutput(self.stack, f"{self.ns}_vpc", value=self.vpc.id)

        self.security_groups = DataAwsSecurityGroups(
            self.stack,
            f"{ns}__security_groups",
            filter=[
                {"name": "vpc-id", "values": [self.network.vpc_id]},
                {"name": "group-id", "values": self.network.security_group_ids},
            ],
        )
        TerraformOutput(self.stack, f"{ns}_security_groups", value=self.security_groups.ids)

        subnets_filter = [
            {"name": "vpc-id", "values": [self.network.vpc_id]},
        ]

        if self.network.subnet_ids:
            subnets_filter.append(
                {"name": "subnet-id", "values": self.network.subnet_ids}
            )

        if self.network.availability_zone:
            subnets_filter.append(
                {
                    "name": "availability-zone",
                    "values": [self.network.availability_zone],
                }
            )

        self.subnets = DataAwsSubnets(
            self.stack,
            f"{ns}__subnets",
            filter=subnets_filter,
        )
        TerraformOutput(self.stack, f"{ns}_subnets", value=self.subnets.ids)

        self.ami = DataAwsAmi(
            self.stack,
            f"{ns}__ami",
            filter=[{"name": "image-id", "values": [instance_ami]}],
        )
        TerraformOutput(self.stack, f"{ns}_ami", value=self.ami.id)

        if isinstance(instance_keypair, EC2Keypair):
            self.keypair = instance_keypair
        else:
            self.keypair = EC2Keypair(
                self.stack,
                self.ns,
                tags=self.tags,
            )
            if isinstance(instance_keypair, str):
                self.keypair.use(instance_keypair)
            else:
                self.keypair.create(f"{self.ns}")

        self.instance_type = instance_type

        self.instance_profile = DataAwsIamInstanceProfile(
            self.stack,
            f"{ns}__instance_profile",
            name=instance_profile,
        )
        TerraformOutput(self.stack, f"{ns}_instance_profile", value=self.instance_profile.name)

        self.volume_size = volume_size
        self.volume_type = volume_type

    def create(self):
        """Create an EC2 launch template."""
        assert self.keypair.keypair is not None, (
            "Keypair not found. Cannot create launch template."
        )

        tag_specifications = [
            LaunchTemplateTagSpecifications(
                resource_type="instance",
                tags=self.tags.asdict(),
            ),
            LaunchTemplateTagSpecifications(
                resource_type="volume",
                tags=self.tags.asdict(),
            ),
            LaunchTemplateTagSpecifications(
                resource_type="network-interface",
                tags=self.tags.asdict(),
            ),
        ]

        subnets = TerraformIterator.from_list(list=self.subnets.ids)
        network_interfaces = subnets.dynamic(
            {
                "subnet_id": subnets.value,
                "security_groups": self.security_groups.ids,
            }
        )

        self.launch_template = LaunchTemplate(
            self.stack,
            f"{self.ns}",
            name=self.ns,
            tags=self.tags.asdict(),
            tag_specifications=tag_specifications,
            image_id=self.ami.id,
            instance_type=self.instance_type,
            key_name=self.keypair.keypair.key_name,
            iam_instance_profile={"name": self.instance_profile.name},
            instance_initiated_shutdown_behavior="terminate",
            ebs_optimized=Token.as_string(True),
            disable_api_stop=False,
            disable_api_termination=False,
            metadata_options=LaunchTemplateMetadataOptions(
                http_endpoint="enabled",
                http_tokens="optional",
                http_put_response_hop_limit=1,
                instance_metadata_tags="enabled",
            ),
            monitoring=LaunchTemplateMonitoring(
                enabled=True,
            ),
            network_interfaces=network_interfaces,
            block_device_mappings=[LaunchTemplateBlockDeviceMappings(
                device_name=self.ami.root_device_name,
                ebs=LaunchTemplateBlockDeviceMappingsEbs(
                    volume_size=self.volume_size,
                    volume_type=self.volume_type,
                    delete_on_termination="true",
                    encrypted="true",
                ),
            )]
        )

        TerraformOutput(self.stack, f"{self.ns}_launchtemplate_id", value=self.launch_template.id)
        TerraformOutput(
            self.stack,
            f"{self.ns}_launchtemplate_name",
            value=self.launch_template.name,
        )
        TerraformOutput(self.stack, f"{self.ns}_launchtemplate_url", value=self.get_url())

    def get_url(self):
        assert self.launch_template is not None, "Launch template not created yet."
        return f"https://{self.network.region}.console.aws.amazon.com/ec2/home?region={self.network.region}#LaunchTemplateDetails:launchTemplateId={self.launch_template.id}"
