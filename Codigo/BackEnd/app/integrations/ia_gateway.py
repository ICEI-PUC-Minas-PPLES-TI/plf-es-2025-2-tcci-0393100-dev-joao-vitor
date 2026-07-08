"""IAGateway — camada de Integrations (padrão Adapter).

Conforme a Seção 3.4 da documentação, o acesso ao serviço externo de
IA é mediado por um componente adaptador, responsável por traduzir as
chamadas internas para o formato exigido pelo provedor externo e por
tratar as respostas recebidas. Isso garante que mudanças no serviço de
IA não impactem as demais camadas do sistema.

Dois adaptadores são fornecidos:

- ``OpenAIGateway``: adaptador para a GPT API (provedor externo),
  habilitado quando a variável de ambiente ``OPENAI_API_KEY`` está
  configurada.
- ``LocalIAGateway``: adaptador local baseado em regras, usado como
  padrão/fallback quando não há provedor externo configurado, mantendo
  o sistema funcional em ambiente acadêmico ou offline.
"""

import json
import os
from abc import ABC, abstractmethod
from typing import Optional


class IAGateway(ABC):
    """Interface do gateway de IA (porta de integração externa)."""

    nome: str

    @abstractmethod
    def gerar_resposta(self, prompt: str, contexto: dict) -> Optional[str]:
        """Gera uma resposta em linguagem natural. Retorna None em falha."""


class OpenAIGateway(IAGateway):
    """Adaptador para a GPT API (serviço externo de IA)."""

    nome = "gpt_api"

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def esta_configurado(self) -> bool:
        return bool(self.api_key)

    def gerar_resposta(self, prompt: str, contexto: dict) -> Optional[str]:
        if not self.esta_configurado():
            return None

        try:
            import urllib.request

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Você é o assistente analítico do sistema DashVendas. "
                            "Responda em português, de forma objetiva e interpretativa, "
                            "baseando-se exclusivamente nos dados fornecidos no contexto."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Contexto (KPIs e metas): {json.dumps(contexto, ensure_ascii=False, default=str)}\n\nSolicitação: {prompt}",
                    },
                ],
                "max_tokens": 500,
            }

            request = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                },
                method="POST",
            )

            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]

        except Exception:
            # Falha na integração externa: o serviço fará fallback local.
            return None


class LocalIAGateway(IAGateway):
    """Adaptador local baseado em regras (fallback offline)."""

    nome = "local"

    def gerar_resposta(self, prompt: str, contexto: dict) -> Optional[str]:
        # A composição da resposta local é feita pelo IAService com base
        # no contexto estruturado; este adaptador apenas sinaliza que a
        # resposta deve ser construída localmente.
        return None
