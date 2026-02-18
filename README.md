# Fishing Dock API

Backend RESTful desenvolvido com FastAPI seguindo os princípios de **Clean Architecture** e **Domain-Driven Design (DDD)**. O projeto foi estruturado para ser modular, testável e facilmente extensível.

## Sumário

- [Arquitetura](#arquitetura)
- [Padrões de Projeto](#padrões-de-projeto)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Stack Tecnológica](#stack-tecnológica)
- [Configuração e Instalação](#configuração-e-instalação)
- [Executando o Projeto](#executando-o-projeto)
- [Testes](#testes)
- [Guia para Novos Módulos](#guia-para-novos-módulos)

---

## Arquitetura

O projeto implementa uma **arquitetura em camadas** com clara separação de responsabilidades. Cada camada tem um papel específico e se comunica apenas com as camadas adjacentes, garantindo baixo acoplamento e alta coesão.

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer                              │
│            (Controllers, Routers, Schemas)                  │
│                                                             │
│   Responsabilidade: Receber requisições HTTP, validar       │
│   dados de entrada e retornar respostas formatadas          │
├─────────────────────────────────────────────────────────────┤
│                    Domain Layer                             │
│          (Entities, Services, Repositories)                 │
│                                                             │
│   Responsabilidade: Regras de negócio puras, independentes  │
│   de frameworks e infraestrutura                            │
├─────────────────────────────────────────────────────────────┤
│                   Database Layer                            │
│          (Models, Repository Implementations)               │
│                                                             │
│   Responsabilidade: Persistência de dados e mapeamento      │
│   objeto-relacional (ORM)                                   │
└─────────────────────────────────────────────────────────────┘
```

### Fluxo de uma Requisição

```
HTTP Request
     │
     ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Router    │ ──▶ │ Controller  │ ──▶ │   Service   │
│  (FastAPI)  │     │  (API/App)  │     │  (Domain)   │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                                              ▼
                                        ┌─────────────┐
                                        │ Repository  │
                                        │ (Interface) │
                                        └─────────────┘
                                              │
                                              ▼
                                        ┌─────────────┐
                                        │ Repository  │
                                        │  (Impl DB)  │
                                        └─────────────┘
                                              │
                                              ▼
                                          Database
```

---

## Padrões de Projeto

### Repository Pattern

Abstrai as operações de acesso a dados, permitindo que a lógica de negócio não dependa diretamente do banco de dados.

```
src/domain/repositories/     → Interfaces (contratos)
src/database/repositories/   → Implementações concretas
```

**Por que usar?**
- Facilita testes unitários com mocks
- Permite trocar o banco de dados sem alterar regras de negócio
- Centraliza a lógica de acesso a dados

**Exemplo de uso:**
```python
# Interface (Domain Layer)
class IUserRepository(ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> UserEntity | None: ...

# Implementação (Database Layer)
class UserRepository(IUserRepository):
    async def get_by_email(self, email: str) -> UserEntity | None:
        # Lógica de acesso ao banco
```

### Service Layer Pattern

Encapsula a lógica de negócio em serviços especializados, coordenando operações entre diferentes componentes.

```
src/domain/services/         → Serviços de domínio (regras de negócio)
src/api/controllers/         → Controllers (orquestração HTTP)
```

**Por que usar?**
- Mantém controllers simples e focados em HTTP
- Regras de negócio ficam isoladas e testáveis
- Facilita reutilização de lógica entre diferentes endpoints

### Dependency Injection

Utiliza o sistema nativo do FastAPI (`Depends()`) para injetar dependências, promovendo baixo acoplamento.

```python
# src/api/dependencies/connections.py
def get_repository(repositorie: T) -> T:
    async def wrapper(session: AsyncSession = Depends(get_transaction_session)):
        return repositorie(session)
    return wrapper
```

**Por que usar?**
- Componentes recebem suas dependências externamente
- Facilita substituição de implementações (ex: mock para testes)
- Código mais modular e testável

### Entity Pattern

Entidades de domínio representam conceitos do negócio com comportamentos próprios.

```python
# src/domain/entities/user.py
@dataclass
class UserEntity:
    nome: str
    email: str

    def authenticated(self, password: str) -> bool:
        # Lógica de autenticação encapsulada na entidade
```

---

## Estrutura do Projeto

```
fishing-dock-api/
├── src/
│   ├── api/                          # Camada de API
│   │   ├── controllers/              # Controllers por módulo
│   │   │   └── <module>/             # Módulo (ex: users)
│   │   │       ├── routers/          # Definição de rotas
│   │   │       ├── schemas/          # Schemas Pydantic (entrada/saída)
│   │   │       └── handlers/         # Handlers de requisição
│   │   ├── dependencies/             # Injeção de dependências
│   │   ├── middlewares/              # Middlewares e exception handlers
│   │   └── app.py                    # Instância FastAPI
│   │
│   ├── domain/                       # Camada de Domínio
│   │   ├── entities/                 # Entidades de negócio
│   │   ├── interfaces/               # Interfaces de provedores externos
│   │   ├── repositories/             # Interfaces de repositórios
│   │   ├── exceptions/               # Exceções de domínio
│   │   └── services/                 # Serviços de domínio por módulo
│   │
│   ├── database/                     # Camada de Dados
│   │   ├── models.py                 # Modelos ORM (SQLModel)
│   │   └── repositories/             # Implementações de repositórios
│   │
│   ├── integrations/                 # Integrações externas
│   │   └── <provider>/               # Provedores (ex: blob_storage)
│   │
│   ├── utils/                        # Utilitários
│   │
│   ├── setup.py                      # Configurações globais
│   └── main.py                       # Ponto de entrada
│
├── tests/                            # Testes
│   └── unit/                         # Testes unitários
│       ├── application/              # Testes de integração API
│       ├── domain/                   # Testes de domínio
│       ├── integrations/             # Testes de integrações
│       └── mock/                     # Mocks para testes
│
├── pyproject.toml                    # Dependências (Poetry)
└── .env.example                      # Template de variáveis
```

### Responsabilidades por Diretório

| Diretório | Responsabilidade |
|-----------|------------------|
| `api/controllers/` | Receber requisições HTTP, validar entrada e formatar resposta |
| `api/dependencies/` | Gerenciar injeção de dependências e ciclo de vida |
| `api/middlewares/` | Middlewares e tratamento global de exceções |
| `domain/entities/` | Representar conceitos de negócio com comportamentos |
| `domain/interfaces/` | Definir contratos para provedores externos |
| `domain/repositories/` | Definir contratos para acesso a dados |
| `domain/services/` | Implementar regras de negócio |
| `database/models.py` | Mapear tabelas do banco (ORM) |
| `database/repositories/` | Implementar acesso ao banco de dados |
| `integrations/` | Implementar integrações com serviços externos |
| `utils/` | Funcionalidades transversais (JWT, validações) |

---

## Stack Tecnológica

| Categoria | Tecnologia | Propósito |
|-----------|------------|-----------|
| Framework Web | FastAPI | API REST assíncrona |
| Servidor ASGI | Uvicorn | Servidor de produção |
| ORM | SQLModel | Mapeamento objeto-relacional |
| Banco de Dados | SQLite + aiosqlite | Persistência (async) |
| Autenticação | PyJWT | Tokens JWT |
| Validação | Pydantic | Validação de dados |
| Testes | pytest + pytest-asyncio | Testes automatizados |
| Logging | Loguru | Logs estruturados |

---

## Configuração e Instalação

### Pré-requisitos

- Python 3.11+
- Poetry

### Instalação

```bash
# Clonar repositório
git clone <repository-url>
cd fishing-dock-api

# Instalar dependências
poetry install

# Configurar variáveis de ambiente
cp .env.example .env
```

### Variáveis de Ambiente

```env
# API
API_PORT=9000
API_HOST=0.0.0.0
API_TITLE=Fishing Dock API
API_DESCRIPTION=Backend API

# JWT
JWT_SECRET_KEY=sua-chave-secreta
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=8900

# Database
DATABASE_SQLITE_PATH=sqlite+aiosqlite:///./databases/db.db
```

---

## Executando o Projeto

```bash
# Desenvolvimento
poetry run python src/main.py

# A API estará disponível em http://localhost:9000
# Documentação Swagger em http://localhost:9000/docs
```

---

## Testes

O projeto utiliza mocks para testes, isolando a lógica de negócio de dependências externas.

```bash
# Executar todos os testes
poetry run pytest

# Com cobertura (falha se < 80%)
poetry run pytest --cov

# Com relatório detalhado
poetry run pytest --cov --cov-report=term-missing
```

---

## Guia para Novos Módulos

Para adicionar um novo módulo (ex: `products`), siga a estrutura estabelecida:

### 1. Criar Entidade de Domínio

```python
# src/domain/entities/product.py
@dataclass
class ProductEntity:
    nome: str
    preco: float
    uuid: str = field(default_factory=lambda: str(uuid4()))
```

### 2. Definir Interface do Repositório

```python
# src/domain/repositories/product.py
class IProductRepository(ABC):
    @abstractmethod
    async def get_by_uuid(self, uuid: str) -> ProductEntity | None: ...

    @abstractmethod
    async def create(self, product: ProductEntity) -> ProductEntity: ...
```

### 3. Criar Serviço de Domínio

```python
# src/domain/services/products/product_service.py
class ProductService:
    def __init__(self, repository: IProductRepository):
        self._repository = repository

    async def create_product(self, product: ProductEntity) -> ProductEntity:
        # Regras de negócio aqui
        return await self._repository.create(product)
```

### 4. Implementar Modelo ORM

```python
# src/database/models.py
class ProductModel(SQLModel, table=True):
    __tablename__ = "produtos"

    id: int | None = Field(default=None, primary_key=True)
    nome: str
    preco: float
    uuid: str = Field(default_factory=lambda: str(uuid4()))
```

### 5. Implementar Repositório

```python
# src/database/repositories/product.py
class ProductRepository(IProductRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_uuid(self, uuid: str) -> ProductEntity | None:
        # Implementação com SQLModel
```

### 6. Criar Controller e Routers

```python
# src/api/controllers/products/routers/product_routers.py
router = APIRouter()

@router.post("/", status_code=201)
async def create_product(
    data: ProductRequestSchema,
    repo: ProductRepository = Depends(get_repository(ProductRepository))
):
    service = ProductService(repo)
    return await service.create_product(...)
```

### 7. Registrar Rotas

```python
# src/api/controllers/products/__init__.py
from .routers.product_routers import router as product_router

# src/api/app.py
app.include_router(product_router, prefix="/products", tags=["Products"])
```

### 8. Criar Testes com Mock

```python
# tests/unit/mock/mock_products.py
class MockProductRepository(IProductRepository):
    # Implementação em memória para testes
```

### Checklist para Novo Módulo

- [ ] Entidade de domínio (`domain/entities/`)
- [ ] Interface do repositório (`domain/repositories/`)
- [ ] Serviço de domínio (`domain/services/<module>/`)
- [ ] Exceções específicas se necessário (`domain/exceptions/`)
- [ ] Modelo ORM (`database/models.py`)
- [ ] Implementação do repositório (`database/repositories/`)
- [ ] Schemas de entrada/saída (`api/controllers/<module>/schemas/`)
- [ ] Handlers e routers (`api/controllers/<module>/`)
- [ ] Registrar rotas em `app.py`
- [ ] Mocks para testes
- [ ] Testes unitários

---

## Endpoints Disponíveis

### Usuários

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/users` | Criar novo usuário |
| POST | `/users/security/login` | Autenticar usuário |
| GET | `/users/security/refresh` | Renovar tokens JWT |

---

## Licença

Este projeto está sob a licença MIT.
