# Nina — Agente de IA para Atendimento e Orçamentos Ópticos

Agente conversacional de IA construído para automatizar o atendimento ao cliente de um laboratório óptico, incluindo geração de orçamentos de lentes e transferência inteligente para atendimento humano quando necessário.

> Projeto em produção, desenvolvido para a **Nova Varonil**, laboratório óptico especializado em lentes e tratamentos (Rio de Janeiro, Brasil).

---

## 🎯 Problema

Laboratórios ópticos recebem um volume alto de perguntas repetitivas sobre preços, tipos de lente e tratamentos disponíveis — a maioria antes mesmo de virar um pedido real. Atendimento 100% manual gera:

- Tempo de resposta lento em horários de pico
- Sobrecarga da equipe com perguntas de triagem básica
- Perda de oportunidades de orçamento fora do horário comercial

## 💡 Solução

A Nina é um agente de IA que:

1. **Atende conversas** de clientes em linguagem natural
2. **Gera orçamentos de lentes** consultando uma base de conhecimento com catálogo e tabela de preços real
3. **Processa imagens** (ex: receitas médicas) para extrair informações relevantes ao orçamento
4. **Identifica quando transferir** a conversa para um atendente humano, e faz esse handoff de forma transparente
5. **Mantém o controle de estado** da conversa, sabendo quando a IA deve responder e quando um humano assumiu

## Arquitetura

```
Cliente (WhatsApp/canal de mensagem)
        │
        ▼
   ┌─────────┐
   │  n8n    │  ← Orquestração do workflow
   └────┬────┘
        │
   ┌────┴─────────────────────────────┐
   │                                   │
   ▼                                   ▼
┌────────┐                      ┌─────────────┐
│ OpenAI │  (processamento      │  Vector      │  ← Base de conhecimento
│ Vision │   de imagens/receitas)│  Store       │     (catálogo + preços)
└────────┘                      └─────────────┘
        │                                   │
        └───────────────┬───────────────────┘
                         ▼
                  ┌──────────────┐
                  │   Supabase   │  ← Persistência de estado
                  │  (followup_  │     da conversa
                  │  clientes)   │
                  └──────┬───────┘
                         │
                         ▼
              humano_na_conversa?
              ┌──────┴───────┐
             sim             não
              │               │
              ▼               ▼
        Atendente          Nina responde
         humano             automaticamente
```

### Componentes principais

| Componente | Função |
|---|---|
| **n8n** | Orquestra todo o fluxo: recebe mensagens, decide roteamento, chama IA, atualiza estado |
| **Supabase** | Armazena o estado de cada conversa na tabela `followup_clientes`, incluindo a flag `humano_na_conversa` que controla se a IA deve responder ou ficar em silêncio |
| **OpenAI (Vision)** | Processa imagens enviadas pelo cliente (ex: receita óptica) para extrair grau e outras informações |
| **Vector Store** | Base de conhecimento com o catálogo de produtos e tabela de preços da Nova Varonil, usada para gerar orçamentos precisos via RAG |

##  Como funciona o handoff humano
Um dos pontos centrais do design é o campo `humano_na_conversa` na tabela `followup_clientes` do Supabase. Ele funciona como uma trava:

- Quando `false` (ou equivalente): a Nina responde normalmente
- Quando `true`: o workflow reconhece que um humano assumiu a conversa e a IA para de responder automaticamente, evitando respostas duplicadas ou conflitantes

Esse mecanismo permite que a transição entre IA e humano seja transparente para o cliente, sem necessidade de comandos especiais.

## Geração de orçamentos (RAG)

O catálogo completo de produtos e a tabela de preços/promoções da Nova Varonil foram consolidados em um documento estruturado, convertido em PDF e indexado em um vector store. Isso permite que a Nina:

- Responda perguntas sobre tipos de lente e tratamentos disponíveis
- Gere orçamentos considerando combinações de produtos e promoções vigentes
- Mantenha as respostas ancoradas em dados reais do catálogo, reduzindo alucinações

##  Stack técnica

- **n8n** — orquestração do workflow e lógica de negócio
- **Supabase** (Postgres) — persistência de estado e controle de conversa
- **OpenAI API** — processamento de linguagem natural e visão computacional
- **Vector Store** — busca semântica sobre catálogo/preços (RAG)

##  Estrutura do repositório

```
nina-ai-agent/
├── README.md
├── workflow/
│   └── nina-workflow.json       # Workflow n8n (sanitizado)
├── docs/
│   ├── architecture.md          # Detalhamento da arquitetura
│   └── setup.md                 # Guia de configuração
├── prompts/
│   └── system-prompt-example.md # Versão de exemplo do prompt do sistema
└── .env.example
```

## Como usar este projeto como referência

Este repositório está publicado como **case de portfólio**, não como um produto pronto para instalação imediata — os dados de catálogo, credenciais e configurações específicas do negócio foram removidos ou genericizados. A ideia é servir como referência de arquitetura para quem quer construir um agente de atendimento similar.

Para configurar uma instância própria:

1. Importe `workflow/nina-workflow.json` no seu n8n
2. Configure suas próprias credenciais (OpenAI, Supabase) — veja `.env.example`
3. Crie a tabela `followup_clientes` no seu Supabase (schema em `docs/setup.md`)
4. Monte seu próprio catálogo/tabela de preços e gere o vector store correspondente

## Contexto do projeto

Desenvolvido para a **Nova Varonil**, laboratório óptico no Centro do Rio de Janeiro, especializado exclusivamente em lentes e tratamentos (sem venda de armações). O projeto nasceu da necessidade de escalar o atendimento sem perder a qualidade e o conhecimento técnico do produto.

---

*Este projeto é mantido como parte do portfólio profissional do autor, com foco em automação de processos de negócio usando IA.*
