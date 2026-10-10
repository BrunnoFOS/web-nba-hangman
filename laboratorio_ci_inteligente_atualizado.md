### Projeto do laboratório

#### 2.1 Stack (tudo gratuito ou acessível)

| Camada                | Escolha                                              | Por quê                                                                                 |
| --------------------- | ---------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Linguagem             | Python 3.12 como versão-alvo; ambiente atual usa Python 3.14 | Ferramentas de métricas simples e de saída legível; padronizar a versão antes de fechar o laboratório |
| CI                    | GitHub Actions (repo público)                        | Gratuito, visual, comentários em PR                                                     |
| Testes                | pytest + pytest-cov                                  | Cobertura em um comando                                                                 |
| Lint                  | Ruff                                                 | Rápido, sem configuração                                                                |
| Complexidade          | Radon (cc, mi) + Xenon (gate)                        | CC por função e nota A–F                                                                |
| Segurança             | Bandit                                               | Padrões de código inseguro                                                              |
| Duplicação            | jscpd (via npx)                                      | Funciona com Python                                                                     |
| Histórico             | Script próprio com git log                           | Commits grandes, mensagens ruins, hotspots                                              |
| Referência industrial | SonarCloud (plano gratuito para repositório público) | Dívida técnica em minutos e dashboard; é o análogo mais próximo do cenário Azure DevOps |
| IA                    | Gemini API como primeira candidata; integração por adaptador | Inferência remota; sem modelo local; verificar limites e condições de uso                 |

**Decisão atual para a IA:** usar uma API hospedada, sem instalar nem executar um modelo localmente. A primeira candidata é a Gemini API, por permitir chamadas remotas a modelos do Google; antes de fixá-la, verificar a disponibilidade do modelo escolhido, os limites, os preços e as condições da camada gratuita na documentação oficial: https://ai.google.dev/gemini-api/docs. Não assumir que o acesso gratuito é ilimitado ou permanente.

O código deve encapsular a integração em `tools/ai_advisor.py` (ou numa interface `advisor.py`), para que o provedor possa ser trocado sem alterar o pipeline. O GitHub Actions envia à API apenas o contexto necessário — relatório de qualidade, diff e trechos relevantes — e recebe uma resposta estruturada. A inferência ocorre no serviço remoto; o runner e o computador do laboratório não precisam carregar os pesos do modelo.

**Papel do Antigravity:** o Google Antigravity pode ser usado como ambiente de desenvolvimento para ajudar a escrever, revisar e depurar o código do laboratório. Ele não deve ser tratado automaticamente como se fosse uma API de inferência diretamente invocável pelo GitHub Actions. Para a execução automatizada do experimento, integrar uma API documentada de um provedor. A documentação do Antigravity e suas opções de modelos/SDK devem ser verificadas caso se queira investigar uma integração mais avançada: https://antigravity.google/docs/models.

Preparar também uma resposta gravada da IA para servir de contingência se a rede, a cota ou a API falhar durante a demonstração. Não usar Ollama ou outro modelo local como requisito do laboratório, pois a prioridade é evitar consumo de RAM/GPU e configuração adicional.

#### 2.2 Projeto-alvo

Um pequeno serviço de checkout/precificação de pedido (\~200 linhas), com uma função calculate_order_total() que aplica descontos, frete, cupons e impostos. É um domínio que qualquer plateia entende e onde regras de negócio se acumulam naturalmente. Estrutura:
lab-ci-inteligente/
├─ src/checkout/pricing.py
├─ tests/                      # incluindo testes de caracterização
├─ tools/
│  ├─ history_analyzer.py      # churn, tamanho de commit, mensagens, hotspots
│  ├─ build_report.py          # consolida tudo em quality_report.json
│  └─ ai_advisor.py            # chama o LLM, valida o patch, gera comentário
├─ .github/workflows/ci.yml
└─ quality_policy.yml          # limiares do gate

**Estado inicial do projeto:** a estrutura local já criada é um protótipo com `checkout/pricing.py`, `testes/test_pricing.py`, `tools/` e o ambiente virtual `smart-ci-venv/`. A árvore acima representa a estrutura-alvo sugerida; os diretórios podem ser reorganizados gradualmente, sem necessidade de recriar o projeto do zero. O ambiente virtual existente está usando Python 3.14. Se o trabalho exigir estritamente Python 3.12, instale essa versão e recrie o ambiente; caso contrário, mantenha uma única versão documentada e valide a compatibilidade das dependências.

#### 2.3 Pipeline

1. checkout com fetch-depth: 0 (necessário para o histórico).
2. Ruff, depois pytest com cobertura.
3. Radon (CC e MI) e Xenon (gate de complexidade).
4. Bandit e jscpd.
5. history_analyzer.py produz métricas de commits e hotspots (churn × CC).
6. build_report.py unifica tudo em um único quality_report.json.
7. ai_advisor.py (só em PR): recebe relatório + diff + trecho do código e retorna sugestões.
8. Verificação do patch: aplica a sugestão em cópia temporária, roda testes e métricas de novo e anexa o delta.
9. Publica comentário no PR e sobe relatório como artefato.
10. Gate final por quality_policy.yml. A IA é consultiva e o gate é determinístico. A chave da API deve ficar em um GitHub Actions Secret (nunca no código, no relatório ou no repositório); o patch proposto não deve ser aplicado nem mesclado automaticamente sem validação e revisão humana.

#### 2.4 Onde a IA entra e como evitar o “LLM genérico”

A IA recebe um prompt estruturado com evidências (valores das métricas, o trecho da função, o histórico do arquivo, a mensagem do commit) e deve responder em JSON com esquema fixo (temperatura baixa):
finding, evidence (cita as métricas recebidas), why_it_matters, root_cause, suggested_refactoring, patch (diff unificado), expected_effect, risk, confidence, priority.
Regras no prompt: só pode citar números presentes no relatório, e deve declarar incerteza quando faltar contexto.

**Contrato de integração:** `ai_advisor.py` deve ler a chave da API por variável de ambiente, enviar a solicitação ao provedor escolhido e validar a resposta recebida contra um esquema JSON esperado. Se a resposta vier malformada, exceder o limite de tentativas ou a API estiver indisponível, registrar a falha e usar o modo de contingência (resposta gravada), deixando claro no relatório que foi usado replay, e não uma resposta gerada ao vivo. Nunca enviar segredos, tokens ou dados desnecessários do repositório ao modelo.

#### 2.5 Problemas introduzidos propositalmente

Um PR “feat: regras de promoção e frete” com estes defeitos, cada um mapeado a um detector:

| Problema plantado                                          | Detector tradicional              | Valor adicionado pela IA                                                    |
| ---------------------------------------------------------- | --------------------------------- | --------------------------------------------------------------------------- |
| Função monolítica com if aninhados (CC ≈ 20+)              | Radon/Xenon: nota D/E, gate falha | Explica a mistura de responsabilidades e propõe regras em tabela/estratégia |
| Bloco de desconto duplicado em 2 lugares                   | jscpd/Sonar                       | Extrai função comum e mostra onde                                           |
| Números mágicos (0.15, 49.9…) e strings de tipo de cliente | Ruff (parcial)                    | Sugere constantes ou enum nomeados                                          |
| Novos ramos sem teste (cobertura cai)                      | pytest-cov                        | Sugere os casos de teste que faltam                                         |
| Um commit gigante “fix stuff” mexendo em vários módulos    | history_analyzer                  | Relaciona o commit à complexidade criada e sugere divisão                   |
| Um ponto de segurança simples (SQL por concatenação)       | Bandit                            | Explica a exploração e corrige com parâmetro. Opcional, só inclua se couber |

#### 2.6 Correção e comparação antes/depois

Escreva testes de caracterização antes da refatoração, para garantir que o comportamento é preservado. Depois aplique o patch (o sugerido pela IA, revisado por você) e compare:

| Métrica                          | Antes  | Depois |
| -------------------------------- | ------ | ------ |
| CC máxima / nota Radon           | <br>   | <br>   |
| Índice de manutenibilidade       | <br>   | <br>   |
| Duplicação (%)                   | <br>   | <br>   |
| Cobertura (%)                    | <br>   | <br>   |
| Dívida técnica (SonarCloud, min) | <br>   | <br>   |
| Avisos Ruff / Bandit             | <br>   | <br>   |
| Testes de caracterização         | passam | passam |
| Tempo do pipeline                | <br>   | <br>   |

Esse conjunto é a evidência quantitativa. Prints do comentário no PR e do SonarCloud são a evidência visual.

#### 2.7 Comparação entre três configurações

Para sustentar academicamente a diferença “inteligente”, rode o mesmo PR em três modos:

- A. CI tradicional: só os gates. Resultado: “falhou, CC=27 > 10”.
- B. LLM ingênuo: só o diff, sem métricas nem histórico. Tende a feedback genérico.
- C. IA contextualizada e verificada: relatório + histórico + patch validado.

A comparação de B com C mostra o valor do contexto. A de A com C mostra o valor da explicação e da sugestão. Para a primeira versão, priorize A versus C; implemente o modo B apenas se houver tempo, pois ele exige uma execução adicional da API e uma comparação controlada.

---

### 3. Teoria ↔ prática

| Conceito                | Implementação no laboratório                                          |
| ----------------------- | --------------------------------------------------------------------- |
| Integração Contínua     | Workflow do GitHub Actions disparado por PR e push                    |
| Testes automatizados    | pytest + testes de caracterização                                     |
| Gate de qualidade       | quality_policy.yml + Xenon + limite de cobertura                      |
| Análise estática        | Ruff, Bandit                                                          |
| Complexidade            | Complexidade ciclomática e índice de manutenibilidade (Radon)         |
| Duplicação              | jscpd / SonarCloud                                                    |
| Dívida técnica          | Estimativa em minutos (SonarCloud) + relatório consolidado            |
| Padrões ruins de commit | history_analyzer.py (tamanho, mensagem, dispersão)                    |
| Hotspot (risco)         | Churn × CC por arquivo                                                |
| Detecção automática     | quality_report.json único, gerado sem intervenção                     |
| IA em pipeline          | ai_advisor.py como etapa do workflow                                  |
| Explicação do problema  | Campos why_it_matters e root_cause                                    |
| Sugestão de melhoria    | Campo patch + comentário no PR                                        |
| Supervisão humana       | Patch consultivo; revisão humana antes de aplicar                     |
| Mitigação de alucinação | Prompt ancorado em evidência + JSON fixo + verificação por reexecução |
| Resultado mensurável    | Tabela antes/depois                                                   |

---

### 4. Critério de sucesso

O laboratório só pode ser chamado de “Integração Contínua Inteligente com Sugestões de Melhoria” se demonstrar todos os itens abaixo, com evidência registrada:

1. Detecção automática de pelo menos três categorias diferentes (complexidade, duplicação ou cobertura, e padrão de commit) em um PR real, sem intervenção manual.
2. Contexto além da regra: a sugestão cita evidências do projeto (valores das métricas, histórico do arquivo ou mensagem do commit) e não apenas o diff.
3. Explicação causal em linguagem natural: diz por que aquilo é um problema neste código e qual é o custo de mantê-lo.
4. Priorização: os achados saem ordenados por risco e esforço, não em lista plana.
5. Sugestão acionável: um patch concreto e aplicável, não conselho genérico.
6. Verificação automática do patch: o pipeline reexecuta testes e métricas na versão sugerida e reporta o delta. Se o patch quebrar algo, o sistema o rejeita e avisa.
7. Comparação antes/depois com melhoria mensurável em complexidade e/ou dívida técnica e comportamento preservado (testes de caracterização passando).
8. Contraste A/B/C mostrando que a análise tradicional sozinha e o LLM sem contexto entregam menos que a configuração completa.
9. Limites declarados: a IA é consultiva, o gate é determinístico, e há ao menos um exemplo em que a sugestão foi imperfeita ou exigiu ajuste humano. Isso aumenta a credibilidade.

O que NÃO conta como sucesso: apenas Ruff/Radon/Sonar falhando o build, ou um LLM comentando o diff sem usar métricas. Isso é pipeline com análise estática (A) ou assistente genérico (B).
Limitações a registrar no trabalho: o resultado depende de um único projeto pequeno, as saídas de LLM variam entre execuções, e o laboratório demonstra viabilidade, não eficácia em escala. As fontes que afirmam ganhos de 30–40% não têm dados verificáveis, então evite usá-las como prova.

---

Próximo passo de implementação: estabilizar o projeto-alvo e os testes de caracterização; depois criar `build_report.py`, `history_analyzer.py`, `ai_advisor.py` e o workflow do GitHub Actions. A integração com a Gemini API deve ser feita após os sensores locais gerarem um `quality_report.json` válido.
### 5. Ambiente de desenvolvimento e instalação

A instalação inicial é local; o pipeline do GitHub Actions será configurado depois. No Linux, com Python 3.12 instalado e disponível como `python3.12`, a preparação pode ser feita assim:

```bash
mkdir -p lab-ci-inteligente
cd lab-ci-inteligente

python3.12 -m venv smart-ci-venv
source smart-ci-venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pytest pytest-cov ruff radon xenon bandit
```

O `jscpd` depende de Node.js/npm e pode ser executado sem instalação global com:

```bash
npx --yes jscpd --version
```

Se for mantido o ambiente virtual atual (`smart-ci-venv`), confirme a versão com `python --version` e instale as ferramentas com o ambiente ativado. O ambiente mostrado até agora aponta para Python 3.14; não o descreva como Python 3.12 sem recriá-lo ou ajustar a versão-alvo documentada.

Verificações iniciais:

```bash
pytest testes/ -v
pytest --cov=checkout --cov-report=term-missing testes/
ruff check checkout/ testes/
radon cc checkout/ -s -a
radon mi checkout/ -s
xenon --max-absolute B --max-modules B --max-average A checkout/
bandit -r checkout/
```

Esses comandos são uma verificação local inicial. Depois que a estrutura definitiva e o workflow forem criados, os caminhos e comandos deverão ser alinhados com a árvore final do repositório. A execução do SonarCloud exige configuração externa; GitHub Actions também executa remotamente, enquanto `git log` é analisado por um script do projeto.

---

Sources:

- [Identify technical debt (Microsoft Learn)](https://learn.microsoft.com/training/modules/identify-technical-debt)
- [Understand and manage technical debt (Azure for DevOps course)](https://www.lynda.com/Azure-tutorials/Understand-manage-technical-debt/2211313/2227314-4.html)
- [AI-driven insights with Azure DevOps (Aegis Softtech)](https://www.aegissofttech.com/insights/how-ai-driven-insights-with-azure-devops/)
- [How AI-assisted code suggestions will advance DevSecOps (GitLab, 2023)](https://about.gitlab.com/blog/ai-assisted-code-suggestions/)
- [CI Best Practices (Medium, 3d-it.net)](https://medium.com/@dennis_39505/continuous-integration-ci-best-practices-a-practical-guide-for-modern-software-development-90a954030702)
- [Top 12 AI Tools For DevOps in 2026 (Spacelift)](https://spacelift.io/blog/ai-devops-tools)