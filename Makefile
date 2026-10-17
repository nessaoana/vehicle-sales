# O cluster, o API Gateway e o smoke test ficam no repositório vehicle-core
# (make localstack cluster lá). Aqui só publicamos o vehicle-sales.

IMAGE_TAG ?= main

.PHONY: deploy

deploy: ## Publica o vehicle-sales no cluster atual do kubectl
	scripts/deploy.sh $(IMAGE_TAG)
