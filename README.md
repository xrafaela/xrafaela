# Oráculo de Ficheiros (File Oracle)

🔮 **File Oracle** é uma aplicação AI-powered que lê o conteúdo de ficheiros num diretório e executa tarefas com garantia de sucesso, utilizando assistentes de IA da NVIDIA e OpenRouter.

## ✨ Características

- 📁 **Leitura Automática de Ficheiros**: Lê e processa ficheiros de um diretório
- 🤖 **Assistente IA Integrado**: Suporte para APIs da NVIDIA e OpenRouter
- 💾 **Gravação Automática**: Ficheiros gerados/editados são automaticamente guardados no PC
- 🎯 **Execução Garantida**: Processa pedidos com foco em resultados bem-sucedidos
- 🔄 **Processamento Assíncrono**: Leitura e escrita eficiente de múltiplos ficheiros
- 💬 **Modo Interativo**: Interface CLI rica para interação com o assistente
- 🛠️ **Múltiplos Comandos**: Gerar, modificar, analisar e executar tarefas complexas

## 🚀 Instalação

### Requisitos

- Python 3.9 ou superior
- Chave API da NVIDIA ou OpenRouter

### Passos de Instalação

1. Clone o repositório:
```bash
git clone https://github.com/xrafaela/xrafaela.git
cd xrafaela
```

2. Instale as dependências:
```bash
pip install -e .
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
```

4. Edite o ficheiro `.env` e adicione as suas chaves API:
```env
NVIDIA_API_KEY=sua_chave_nvidia_aqui
OPENROUTER_API_KEY=sua_chave_openrouter_aqui
DEFAULT_AI_PROVIDER=nvidia
```

## 📖 Utilização

### Modo Interativo

Inicie o modo interativo para conversar com o assistente IA:

```bash
oraculo interactive
```

Ou especifique diretórios e provider:

```bash
oraculo interactive -d ./meus_ficheiros -o ./saida -p nvidia
```

#### Comandos Disponíveis no Modo Interativo

- `/list` - Lista ficheiros no diretório
- `/read <padrão>` - Lê ficheiros que correspondem ao padrão
- `/generate <nome_ficheiro>` - Gera um novo ficheiro
- `/modify <nome_ficheiro>` - Modifica um ficheiro existente
- `/task` - Executa uma tarefa complexa
- `/quit` - Sai do modo interativo

### Fazer uma Pergunta

```bash
oraculo ask "Qual é o conteúdo dos meus ficheiros Python?"
```

### Gerar um Ficheiro

```bash
oraculo generate "Uma função Python para calcular fibonacci" fibonacci.py -l python
```

### Modificar um Ficheiro

```bash
oraculo modify exemplo.py "Adiciona docstrings a todas as funções"
```

### Listar Ficheiros

```bash
oraculo list-files --pattern "*.py"
```

## 🏗️ Arquitetura

O File Oracle é composto por vários módulos:

- [`src/config.py`](src/config.py) - Gestão de configuração e variáveis de ambiente
- [`src/file_reader.py`](src/file_reader.py) - Leitura assíncrona de ficheiros
- [`src/file_writer.py`](src/file_writer.py) - Escrita e gravação automática de ficheiros
- [`src/ai_assistant.py`](src/ai_assistant.py) - Integração com APIs de IA (NVIDIA/OpenRouter)
- [`src/oracle.py`](src/oracle.py) - Orquestrador principal da aplicação
- [`src/cli.py`](src/cli.py) - Interface de linha de comandos
- [`src/app.py`](src/app.py) - Ponto de entrada da aplicação

## 🔧 Configuração

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `NVIDIA_API_KEY` | Chave API da NVIDIA | - |
| `NVIDIA_API_BASE` | URL base da API NVIDIA | `https://integrate.api.nvidia.com/v1` |
| `NVIDIA_MODEL` | Modelo NVIDIA a usar | `nvidia/llama-3.1-nemotron-70b-instruct` |
| `OPENROUTER_API_KEY` | Chave API do OpenRouter | - |
| `OPENROUTER_API_BASE` | URL base da API OpenRouter | `https://openrouter.ai/api/v1` |
| `OPENROUTER_MODEL` | Modelo OpenRouter a usar | `anthropic/claude-3.5-sonnet` |
| `DEFAULT_AI_PROVIDER` | Provider padrão (nvidia/openrouter) | `nvidia` |
| `WATCH_DIRECTORY` | Diretório a monitorizar | `./workspace` |
| `OUTPUT_DIRECTORY` | Diretório de saída | `./output` |
| `AUTO_SAVE` | Gravar ficheiros automaticamente | `true` |
| `MAX_FILE_SIZE_MB` | Tamanho máximo de ficheiro (MB) | `10` |

## 🧪 Testes

Execute os testes com pytest:

```bash
pytest
```

Com cobertura:

```bash
pytest --cov=src --cov-report=html
```

## 📝 Exemplos

### Exemplo 1: Analisar Código Python

```bash
oraculo interactive
> Analisa todos os ficheiros Python e diz-me quais funções existem
```

### Exemplo 2: Gerar Documentação

```bash
oraculo ask "Gera documentação README para os ficheiros neste diretório"
```

### Exemplo 3: Refatorar Código

```bash
oraculo modify main.py "Refatora o código para usar async/await"
```

### Exemplo 4: Tarefa Complexa

```bash
oraculo interactive
> /task
Describe the task: Cria uma API REST com FastAPI que lê dados de um ficheiro JSON
```

## 🤝 Contribuir

Contribuições são bem-vindas! Por favor:

1. Faça fork do repositório
2. Crie uma branch para a sua feature (`git checkout -b feature/nova-feature`)
3. Commit as suas alterações (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o ficheiro LICENSE para mais detalhes.

## 👩‍💻 Autora

**Rafaela Rodrigues** ([@xrafaela](https://github.com/xrafaela))

- 🎓 Estudante de Engenharia Informática
- 💻 Membro do GitHub Student Developer Pack
- 🌟 Apaixonada por tecnologia e IA

## 🔗 Links

- [Repositório GitHub](https://github.com/xrafaela/xrafaela)
- [NVIDIA API](https://build.nvidia.com/)
- [OpenRouter](https://openrouter.ai/)

---

⭐️ Se este projeto foi útil, considera dar uma estrela!
