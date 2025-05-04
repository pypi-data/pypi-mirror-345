from cdktf import TerraformOutput
from cdktf_cdktf_provider_aws.ecr_repository import EcrRepository
from cdktf_cdktf_provider_aws.ecr_repository_policy import EcrRepositoryPolicy
from cdktf_cdktf_provider_aws.ecr_lifecycle_policy import EcrLifecyclePolicy


class AwsEcr:
    """
    Manages ECR repositories for container images.

    This class provides functionality to create new ECR repositories,
    configure lifecycle policies, and manage permissions.
    """

    def __init__(
        self,
        stack,
        ns,
        repository_name,
        image_tag_mutability="MUTABLE",
        scan_on_push=True,
    ):
        """Initialize an AWS ECR Repository."""
        self.stack = stack
        self.ns = ns
        self.repository = EcrRepository(
            self.stack,
            f"{self.ns}_repo",
            name=repository_name,
            image_tag_mutability=image_tag_mutability,
            image_scanning_configuration={"scan_on_push": scan_on_push},
            force_delete=False,
        )

        TerraformOutput(self.stack, f"{self.ns}_ecr_arn", value=self.repository.arn)

        TerraformOutput(
            self.stack, f"{self.ns}_ecr_url", value=self.repository.repository_url
        )

    def attach_lifecycle_policy(self, max_image_count=30):
        """Add a lifecycle policy to manage the number of images."""
        policy = {
            "rules": [
                {
                    "rulePriority": 1,
                    "description": f"Keep only {max_image_count} images",
                    "selection": {
                        "tagStatus": "any",
                        "countType": "imageCountMoreThan",
                        "countNumber": max_image_count,
                    },
                    "action": {"type": "expire"},
                }
            ]
        }

        EcrLifecyclePolicy(
            self.stack,
            f"{self.ns}_lifecycle_policy",
            repository=self.repository.name,
            policy=str(policy).replace("'", '"'),
        )

        return self

    def attach_repository_policy(self, policy_json):
        """Add a repository policy to manage access permissions."""
        EcrRepositoryPolicy(
            self.stack,
            f"{self.ns}_repo_policy",
            repository=self.repository.name,
            policy=policy_json,
        )

        return self
