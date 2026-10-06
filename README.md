[![Quality gate status](https://sonarcloud.io/api/project_badges/measure?project=nessaoana_vehicle-sales&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=nessaoana_vehicle-sales)  [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=nessaoana_vehicle-sales&metric=coverage)](https://sonarcloud.io/summary/new_code?id=nessaoana_vehicle-sales)
# vehicle-sales

Serviço de venda de veículos, com API Python, PostgreSQL e LocalStack.

## Arquitetura em camadas

```mermaid
flowchart LR
	HTTP[HTTP / FastAPI]

	subgraph Adapters[Adapters]
		Controllers[Controllers]
		Schemas[Schemas]
		Mappers[Mappers]
	end

	subgraph Application[Application]
		UseCases[Use cases]
		Ports[Repository ports]
		Exceptions[Application exceptions]
	end

	subgraph Domain[Domain]
		Sale[CarSale entity]
		SaleRules[Sale and payment rules]
	end

	subgraph Infrastructure[Infrastructure]
		ORM[SQLAlchemy models]
		Repository[Repositories]
		Logging[Structured logging]
	end

	Database[(PostgreSQL vehicle_sales)]
	Core[vehicle-core HTTP API]

	HTTP --> Controllers --> Schemas
	Controllers --> UseCases
	UseCases --> Sale
	UseCases --> SaleRules
	UseCases --> Ports
	Ports -. implemented by .-> Repository
	Repository --> ORM --> Database
	UseCases -. vehicle availability .-> Core
	Controllers --> Logging
	UseCases --> Logging
```

A comunicação com o `vehicle-core` acontece por HTTP. O serviço de vendas deve
manter seu banco isolado e não acessar diretamente as tabelas do serviço
principal. As pastas de adapters e application já estão preparadas para os
casos de uso de compra, listagem e webhook de pagamento.

## CI/CD

O CI executa build Python, testes com cobertura mínima de 80%, análise SonarCloud,
validação Terraform e `terraform plan` sem apply. Em branches diferentes de
`main`, um Pull Request é criado automaticamente após o CI bem-sucedido.

O CD é acionado somente após o workflow `CI` terminar com sucesso na branch
`main`. Ele publica a imagem `app` no Docker Hub e depois aplica o Terraform no
LocalStack Cloud.

Workflows reutilizáveis usados:

- `_reusable-build-python.yml`
- `_reusable-sonar-python.yml`
- `_reusable-dockerhub.yml`
- `_reusable-terraform.yml`
- `_reusable-create-pr.yml`

Configure no GitHub:

- Repository variable `SONAR_ORG`
- Repository variable `DOCKERHUB_USERNAME`
- Secret `SONAR_TOKEN`
- Secret `DOCKERHUB_TOKEN`
- Secret `LOCALSTACK_AUTH_TOKEN`

No SonarCloud, use o projeto `nessaoana_vehicle-sales` e desabilite Automatic
Analysis para manter a análise via GitHub Actions. Para criação automática de
PRs, habilite `Allow GitHub Actions to create and approve pull requests` nas
configurações do repositório.
