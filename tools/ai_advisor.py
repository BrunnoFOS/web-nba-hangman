#!/usr/bin/env python3
"""
tools/ai_advisor.py
Consome `quality_report.json` + `git diff` e invoca a API do Google Gemini
(ou cai no modo contingência/replay se a API falhar ou a chave não existir).
Gera um comentário formatado em Markdown para o Pull Request.
"""

import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path


SYSTEM_PROMPT = """Você é um especialista em Engenharia de Software e Qualidade de Código atuando como AI Advisor em um pipeline de CI/CD.
Sua tarefa é analisar o relatório de qualidade (quality_report.json) gerado por sensores estáticos (PMD, JaCoCo, Git Churn) e o diff do PR.

REGRAS ESTRITAS:
1. Responda ESTRITAMENTE em formato JSON com o seguinte schema:
{
  "finding": "Título claro do problema identificado",
  "evidence": "Cite explicitamente as métricas recebidas (ex: PMD, linhas, CC ou cobertura)",
  "why_it_matters": "Explicação causal do porquê isso é um problema para a arquitetura ou manutenção",
  "root_cause": "A causa raiz no código",
  "suggested_refactoring": "Descrição textual da melhoria",
  "patch": "Diff unificado aplicável ou trecho de refatoração sugerido",
  "expected_effect": "Qual o ganho esperado nas métricas",
  "risk": "Baixo, Médio ou Alto",
  "confidence": 0.95,
  "priority": "HIGH ou MEDIUM ou LOW"
}
2. Seja objetivo e NUNCA invente números ou métricas que não estejam no relatório.
3. Se faltar contexto, declare incerteza.
"""


def load_report():
    report_file = Path("target/quality_report.json")
    if report_file.exists():
        with open(report_file, "r", encoding="utf-8") as f:
            return f.read()
    return "{}"


def get_git_diff():
    try:
        res = subprocess.run(["git", "diff", "HEAD~1"], capture_output=True, text=True)
        return res.stdout[:3000] # Limita tamanho do diff
    except Exception:
        return ""


def call_gemini(api_key, report_content, diff_content):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    user_prompt = f"""Aqui estão as evidências do projeto:
RELATÓRIO DE QUALIDADE:
{report_content}

DIFF DO COMMIT/PR:
{diff_content}

Analise os code smells mais graves, a complexidade ciclomática e riscos de segurança. Retorne a resposta em JSON."""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": SYSTEM_PROMPT},
                    {"text": user_prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json"
        }
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        text_content = data["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text_content)


def load_contingency():
    contingency_path = Path("tools/fixtures/contingency_response.json")
    if contingency_path.exists():
        with open(contingency_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            data["mode"] = "CONTINGENCY_REPLAY (Chave ausente ou falha de rede)"
            return data
    return {"finding": "Modo de contingência padrão", "mode": "FALLBACK"}


def generate_markdown_comment(advice):
    mode_badge = advice.get("mode", "LIVE_API")
    return f"""### 🤖 AI Quality Advisor Feedback (`{mode_badge}`)

**Achado Principal:** {advice.get('finding')}  
**Prioridade:** `{advice.get('priority', 'MEDIUM')}` | **Risco:** `{advice.get('risk', 'Baixo')}` | **Confiança:** `{advice.get('confidence', 0.9)}`

---

#### 📊 Evidências Encontradas
> {advice.get('evidence')}

#### ⚠️ Por que isso importa?
{advice.get('why_it_matters')}

#### 🔍 Causa Raiz
{advice.get('root_cause')}

#### 🛠️ Sugestão de Refatoração
{advice.get('suggested_refactoring')}

```diff
{advice.get('patch', '')}
```

**Impacto Esperado:** {advice.get('expected_effect')}
"""


def main():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    report = load_report()
    diff = get_git_diff()

    advice = None
    if api_key:
        try:
            print("[ai_advisor] Chamando Gemini API...")
            advice = call_gemini(api_key, report, diff)
            advice["mode"] = "LIVE_GEMINI_API"
        except Exception as e:
            print(f"[ai_advisor] Erro ao chamar API: {e}. Usando contingência.")
            advice = load_contingency()
    else:
        print("[ai_advisor] GEMINI_API_KEY não encontrada. Usando modo contingência.")
        advice = load_contingency()

    # Salva o parecer em JSON
    Path("target").mkdir(exist_ok=True)
    with open("target/ai_advice.json", "w", encoding="utf-8") as f:
        json.dump(advice, f, indent=2, ensure_ascii=False)

    # Gera o comentário em Markdown para o PR
    comment_md = generate_markdown_comment(advice)
    with open("target/pr_comment.md", "w", encoding="utf-8") as f:
        f.write(comment_md)

    print("[ai_advisor] Parecer da IA gerado em target/pr_comment.md")
    print("\n--- PR COMMENT PREVIEW ---")
    print(comment_md)


if __name__ == "__main__":
    main()
