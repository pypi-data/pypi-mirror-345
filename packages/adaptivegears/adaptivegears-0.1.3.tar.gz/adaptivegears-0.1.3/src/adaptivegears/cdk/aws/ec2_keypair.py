from cdktf import TerraformOutput
from cdktf_cdktf_provider_aws.data_aws_key_pair import DataAwsKeyPair
from cdktf_cdktf_provider_aws.key_pair import KeyPair
from cdktf_cdktf_provider_tls.private_key import PrivateKey

from .. import dtype


class EC2Keypair:
    def __init__(
        self,
        stack,
        ns: str,
        tags: dtype.Tags,
    ):
        self.stack = stack
        self.ns = ns
        self.tags = tags

        self.keypair = None

    def use(self, key_name: str):
        """Use an existing keypair."""
        self.keypair = DataAwsKeyPair(
            self.stack,
            f"{self.ns}__keypair",
            key_name=key_name,
        )
        TerraformOutput(self.stack, f"{self.ns}_keypair", value=self.keypair.key_name)

    def create(self, key_name: str, algorithm: str = "ED25519"):
        """Create a new keypair."""

        private_key = PrivateKey(self.stack, f"{self.ns}_pk", algorithm="ED25519")
        TerraformOutput(
            self.stack,
            f"{self.ns}_privatekey",
            value=private_key.private_key_openssh,
            sensitive=True,
        )

        self.keypair = KeyPair(
            self.stack,
            f"{self.ns}_kp",
            key_name=key_name,
            tags=self.tags.asdict(),
            public_key=private_key.public_key_openssh,
        )
        TerraformOutput(self.stack, f"{self.ns}_keypair_name", value=self.keypair.key_name)
        TerraformOutput(self.stack, f"{self.ns}_keypair_url", value=self.get_url())

    def get_url(self):
        """Get the URL of the keypair."""
        assert self.keypair, "Keypair not created or used."
        return f"https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#KeyPairs:keyName={self.keypair.key_name};v=3"
