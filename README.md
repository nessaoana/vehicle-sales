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

```mermaid
flowchart LR
	Push[Push ou PR] --> Tests[Build e testes<br/>cobertura ≥ 80%] --> Sonar[SonarCloud]
	Push --> Plan[Terraform<br/>validate + plan]
	Sonar --> Branch{Branch?}
	Plan --> Branch
	Branch -- outra --> PR[Abre PR para main]
	Branch -- main --> Docker[Publica imagem<br/>no Docker Hub] --> Apply[Terraform apply<br/>no LocalStack]
```

O CI roda em pushes para qualquer branch e em PRs para `main`:

- build e testes, com cobertura mínima de 80%;
- análise no SonarCloud, que bloqueia a alteração se o quality gate falhar;
- `terraform fmt`, `validate` e `plan`, sem apply.

Se o CI passar:

- **em outra branch**, um PR para `main` é aberto automaticamente;
- **na `main`**, o CD publica a imagem no Docker Hub e aplica o Terraform no
  LocalStack Cloud.

Os jobs usam os workflows reutilizáveis de `fiap-soat-grupo36/reusable-actions`.
