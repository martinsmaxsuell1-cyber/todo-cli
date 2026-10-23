# 📋 Todo CLI

Um gerenciador de tarefas moderno, elegante e de alta performance com banco de dados **SQLite**, projetado especificamente para **Termux**, **Android** e **Linux**.

Zero dependências externas obrigatórias, ultraleve, com suporte a prioridades, tags, prazos, notas, métricas de produtividade e exportação para Markdown e JSON.

---

## ⚡ Instalação & Uso Global

Você pode usar o comando completo `todo` ou o atalho rápido `td`:

```bash
# Adicionar tarefa rápida
td "Comprar café torrado"

# Adicionar tarefa detalhada com prioridade, tags e prazo
td add "Finalizar documentação da API" -p high -t dev,doc -d "2026-10-31" -n "Revisar endpoints de autenticação"
```

---

## 🚀 Comandos Principais

### 1. Visualizar Tarefas
```bash
# Listar tarefas pendentes
td

# Listar todas (incluindo concluídas)
td list --all

# Filtrar por prioridade (urgent, high, medium, low)
td list -p high

# Filtrar por tag
td list -t dev
```

### 2. Concluir ou Reabrir
```bash
# Concluir tarefas (pode passar múltiplos IDs)
td done 1 2

# Reabrir tarefa que foi concluída por engano
td undo 1
```

### 3. Editar Tarefas
```bash
td edit 1 --title "Novo título" -p urgent -t sprint,urgente
```

### 4. Buscar e Excluir
```bash
# Buscar tarefas por texto
td search "documentação"

# Remover tarefas por ID
td rm 3

# Limpar definitivamente todas as tarefas concluídas
td clear
```

### 5. Métricas e Produtividade
Exibe uma barra de progresso visual no terminal com taxa de conclusão e tarefas críticas:
```bash
td stats
```

### 6. Exportação
```bash
# Exportar para formato Markdown (ideal para Obsidian, Notion ou GitHub)
td export --markdown > tarefas.md

# Exportar para JSON (para integrações e automações)
td export --json > tarefas.json
```

---

## 🏷️ Prioridades Disponíveis

| Prioridade | Flag | Indicador Visual |
| :--- | :--- | :--- |
| **Urgente** | `-p urgent` | 🔥 `URGENTE` (Vermelho) |
| **Alta** | `-p high` | ⚡ `ALTA` (Amarelo) |
| **Média** | `-p medium` | 🔹 `MÉDIA` (Azul) *(Padrão)* |
| **Baixa** | `-p low` | ▫️ `BAIXA` (Cinza) |

---

## 🗄️ Armazenamento Seguro

Os dados são salvos localmente em um banco de dados SQLite ACID em:
`~/.local/share/todo-cli/todos.db`

- Não polui a raiz `~`
- Resistente a falhas e encerramentos repentinos do aplicativo no Android
- Extremamente rápido com baixíssimo consumo de memória RAM

---

## 🧪 Testes Automatizados

Para executar os testes unitários do projeto:
```bash
cd ~/projects/todo-cli
python3 -m unittest discover -s tests
```
