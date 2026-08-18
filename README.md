# Nina — Agente de IA para Atendimento e Orçamentos Ópticos

Agente conversacional de IA que automatiza o atendimento ao cliente de um laboratório óptico no WhatsApp, incluindo geração de orçamentos de lentes e transferência inteligente para atendimento humano.

Desenvolvido para a **Nova Varonil**, laboratório óptico especializado em lentes e tratamentos, no Rio de Janeiro.

> A documentação detalhada, o workflow e os prompts estão na pasta [`nina Ai/`](./nina%20Ai).

## O problema

Laboratórios ópticos recebem um volume alto de perguntas repetitivas sobre preços, tipos de lente e tratamentos — a maioria antes de virar pedido. Atendimento 100% manual gera resposta lenta no pico, sobrecarga da equipe com triagem básica e perda de orçamentos fora do horário comercial.

## A solução

A Nina:

- Atende conversas em linguagem natural
- **Gera orçamentos** consultando uma base de conhecimento com o catálogo e a tabela de preços reais (RAG)
- **Lê receitas ópticas por foto**, transcrevendo esférico, cilíndrico, eixo e adição
- **Transfere para atendimento humano** quando necessário, de forma transparente
- Mantém o estado da conversa, sabendo quando a IA deve responder e quando um humano assumiu

## Arquitetura

```
Cliente (WhatsApp)
        │
        ▼
     ┌─────┐
     │ n8n │  ← orquestração do fluxo
     └──┬──┘
        │
   ┌────┴────────────────┐
   ▼                     ▼
┌────────┐        ┌──────────────┐
│ OpenAI │        │ Vector Store │  ← catálogo + preços (RAG)
│ Vision │        └──────────────┘
└────────┘                │
   └──────────┬───────────┘
              ▼
       ┌─────────────┐
       │  Supabase   │  ← estado da conversa
       └──────┬──────┘
              ▼
      humano_na_conversa?
        ┌─────┴─────┐
       sim         não
        │           │
   Atendente    Nina responde
```

## O handoff humano

O ponto central do design é o campo `humano_na_conversa`, na tabela `followup_clientes` do Supabase. Ele funciona como uma trava:

- **false** — a Nina responde normalmente
- **true** — o workflow reconhece que um humano assumiu e a IA para de responder, evitando respostas duplicadas ou conflitantes

A transição é invisível para o cliente: não existe comando especial, o atendente simplesmente entra na conversa.

## Geração de orçamentos (RAG)

O catálogo completo e a tabela de preços foram consolidados em um documento estruturado e indexados em um vector store. Isso permite que a Nina responda sobre tipos de lente e tratamentos, gere orçamentos considerando combinações e promoções vigentes, e mantenha as respostas ancoradas em dados reais — reduzindo alucinação.

## Stack

- **n8n** — orquestração do workflow e regra de negócio
- **Supabase (PostgreSQL)** — persistência do estado da conversa
- **OpenAI API** — processamento de linguagem natural e visão computacional
- **Vector store** — busca semântica sobre catálogo e preços

## Sobre este repositório

Publicado como **case de portfólio**, não como produto pronto para instalação: dados de catálogo, credenciais e configurações do negócio foram removidos ou genericizados. Serve como referência de arquitetura para quem queira construir um agente de atendimento parecido.

Para montar uma instância própria: importe o workflow no seu n8n, configure suas credenciais (OpenAI, Supabase), crie a tabela `followup_clientes` e gere seu próprio vector store a partir do seu catálogo.
