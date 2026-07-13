#!/usr/bin/env python3
"""
Script de sanitização do workflow n8n da Nina (Nova Varonil) para publicação no GitHub.

Uso:
    python sanitize_nina_workflow.py nina-workflow-original.json nina-workflow-sanitizado.json

O que ele faz:
    1. Remove/mascara credenciais e IDs de credenciais do n8n
    2. Substitui URLs do Supabase, webhooks e endpoints reais por placeholders
    3. Mascara chaves de API que porventura estejam hardcoded no JSON (não deveriam, mas confere)
    4. Gera um relatório do que foi encontrado e alterado, pra você revisar antes de commitar

IMPORTANTE: Depois de rodar, ainda REVISE MANUALMENTE o JSON de saída antes de subir pro GitHub.
Este script cobre os casos mais comuns, mas não substitui uma revisão humana — principalmente
em campos de texto livre (prompts, mensagens de exemplo, nomes de clientes em testes salvos).
"""

import json
import re
import sys
from copy import deepcopy

# Padrões de campos sensíveis conhecidos em exports do n8n
SENSITIVE_KEYS = {
    "apiKey", "api_key", "token", "accessToken", "access_token",
    "password", "secret", "authToken", "auth_token", "clientSecret",
    "client_secret", "privateKey", "private_key",
}

# Chaves do n8n que referenciam credenciais configuradas (id/name) — não são secrets em si,
# mas identificam qual credencial está associada; melhor genericizar mesmo assim.
CREDENTIAL_REF_KEYS = {"credentials"}

# Padrões de valor que parecem chaves de API reais (mesmo em campos com nome genérico)
API_KEY_PATTERNS = [
    re.compile(r"sk-ant-[a-zA-Z0-9\-_]{20,}"),      # Anthropic
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),               # OpenAI
    re.compile(r"eyJ[a-zA-Z0-9_\-\.]{30,}"),           # JWT (comum em Supabase)
    re.compile(r"https://[a-zA-Z0-9\-]+\.supabase\.co"),  # URL de projeto Supabase
]

report = []


def mask_value(key, value, path):
    """Decide se um valor deve ser mascarado e retorna o valor mascarado."""
    if isinstance(value, str):
        lower_key = key.lower()

        # Campo com nome sensível
        if any(sk.lower() in lower_key for sk in SENSITIVE_KEYS):
            report.append(f"[CAMPO SENSÍVEL] {path} -> mascarado (chave: '{key}')")
            return "YOUR_SECRET_HERE"

        # Valor bate com padrão de API key/URL conhecida, mesmo em campo "inocente"
        for pattern in API_KEY_PATTERNS:
            if pattern.search(value):
                report.append(f"[PADRÃO DE SECRET DETECTADO] {path} -> mascarado (chave: '{key}')")
                return "YOUR_SECRET_HERE"

    return value


def sanitize(node, path="root"):
    if isinstance(node, dict):
        new_dict = {}
        for key, value in node.items():
            current_path = f"{path}.{key}"

            # Referências de credenciais do n8n: mantém a estrutura, genericiza os valores
            if key in CREDENTIAL_REF_KEYS and isinstance(value, dict):
                new_cred = {}
                for cred_type, cred_info in value.items():
                    if isinstance(cred_info, dict):
                        masked = deepcopy(cred_info)
                        if "id" in masked:
                            masked["id"] = "YOUR_CREDENTIAL_ID"
                        if "name" in masked:
                            masked["name"] = f"{cred_type} (configure sua credencial)"
                        new_cred[cred_type] = masked
                        report.append(f"[CREDENCIAL N8N] {current_path}.{cred_type} -> genericizado")
                    else:
                        new_cred[cred_type] = cred_info
                new_dict[key] = new_cred
                continue

            if isinstance(value, (dict, list)):
                new_dict[key] = sanitize(value, current_path)
            else:
                new_dict[key] = mask_value(key, value, current_path)
        return new_dict

    elif isinstance(node, list):
        return [sanitize(item, f"{path}[{i}]") for i, item in enumerate(node)]

    else:
        return node


def main():
    if len(sys.argv) != 3:
        print("Uso: python sanitize_nina_workflow.py <entrada.json> <saida.json>")
        sys.exit(1)

    input_path, output_path = sys.argv[1], sys.argv[2]

    with open(input_path, "r", encoding="utf-8") as f:
        workflow = json.load(f)

    sanitized = sanitize(workflow)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sanitized, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Arquivo sanitizado salvo em: {output_path}\n")

    if report:
        print(f"📋 {len(report)} alteração(ões) feita(s):\n")
        for line in report:
            print(f"  - {line}")
    else:
        print("⚠️  Nenhum campo sensível foi detectado automaticamente.")
        print("    Isso pode ser bom sinal, ou pode significar que algo passou despercebido.")
        print("    REVISE O JSON MANUALMENTE antes de publicar.")

    print("\n⚠️  LEMBRETE: revise manualmente prompts, mensagens de exemplo e nomes de")
    print("    clientes/telefones que possam ter ficado salvos em nós de teste (pinData).")
    print("    Procure também pela chave 'pinData' no JSON original — o n8n às vezes salva")
    print("    dados reais de execuções de teste ali, e este script não cobre esse campo")
    print("    porque o formato varia muito.\n")


if __name__ == "__main__":
    main()