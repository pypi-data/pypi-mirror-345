.DEFAULT_GOAL := help
.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: version
version: ## Set the version
ifndef VERSION
	$(error VERSION is not set. Please specify version with VERSION=x.x.x)
endif
	uvx hatch version $(VERSION)
	git add src/adaptivegears/__init__.py
	git commit -m "Bump version to $(VERSION)"
	git tag v$(VERSION)
	git push origin v$(VERSION)

.PHONY: build
build: ## Build the project
	uvx hatch build

.PHONY: release
release: version build ## Publish the project
	uvx hatch publish
