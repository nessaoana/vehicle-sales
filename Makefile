# A infraestrutura compartilhada (LocalStack, EKS e API Gateway) fica no
# repositório vehicle-core: suba com "make localstack cluster" lá. Aqui só
# publicamos e testamos o vehicle-sales no cluster atual do kubectl.

IMAGE_TAG ?= main

.PHONY: deploy smoke-test load-test

deploy: ## Publica o vehicle-sales no cluster atual do kubectl
	scripts/deploy.sh $(IMAGE_TAG)

smoke-test: ## Confere a API e o banco do vehicle-sales no cluster
	scripts/smoke-test.sh

load-test: ## Carga na listagem pelo gateway: make load-test GATEWAY_URL=<url>
	scripts/load-test.sh $(GATEWAY_URL)
