# Domain Context Template for Metalscribe

<!--
Este arquivo fornece contexto de domínio para melhorar a qualidade da
transcrição e formatação de reuniões. Preencha as seções relevantes e
remova os exemplos/comentários antes de usar.

Uso:
  metalscribe run-meeting --input audio.m4a --context meu-contexto.md

Dica: Use uma LLM para ajudar a preencher este template. Cole o template
e descreva seu domínio de conhecimento, área profissional ou tipo de reunião.
-->

---

## Área de Conhecimento

<!--
Descreva brevemente o domínio, disciplina ou área profissional.
Isso ajuda a LLM a interpretar termos ambíguos corretamente.
-->

**Domínio:** [Ex: Medicina, Direito Tributário, Desenvolvimento de Software, Filosofia, etc.]

**Descrição:**
[Breve parágrafo descrevendo o contexto. Ex: "Reuniões de sprint de um time
de desenvolvimento ágil que trabalha com e-commerce em Python/Django."]

---

## Glossário de Termos

<!--
Liste termos técnicos, siglas e jargões específicos do seu domínio.
A coluna "Erros ASR comuns" ajuda a corrigir erros de transcrição automática.
-->

| Termo | Significado | Erros ASR comuns |
|-------|-------------|------------------|
| [termo] | [definição curta] | [como o ASR costuma errar] |

<!--
EXEMPLOS (remova antes de usar):

| Termo | Significado | Erros ASR comuns |
|-------|-------------|------------------|
| sprint | Ciclo de desenvolvimento de 2 semanas | spring, print |
| deploy | Publicação de código em produção | de ploy, the ploy |
| PR | Pull Request (revisão de código) | pier, P.R. |
| tech lead | Líder técnico do time | tec lid, techlit |
| staging | Ambiente de testes pré-produção | stating, stage in |
-->

---

## Siglas e Acrônimos

<!--
Liste siglas usadas frequentemente. Separe do glossário para facilitar consulta.
-->

| Sigla | Significado completo |
|-------|---------------------|
| [sigla] | [significado] |

<!--
EXEMPLOS (remova antes de usar):

| Sigla | Significado completo |
|-------|---------------------|
| API | Application Programming Interface |
| MVP | Minimum Viable Product |
| QA | Quality Assurance |
| CI/CD | Continuous Integration / Continuous Deployment |
| OKR | Objectives and Key Results |
-->

---

## Nomes e Entidades

<!--
Liste nomes de pessoas, empresas, produtos ou projetos que aparecem
frequentemente. Isso evita erros de transcrição em nomes próprios.
-->

| Nome/Entidade | Tipo | Erros ASR comuns |
|---------------|------|------------------|
| [nome] | [pessoa/empresa/projeto/produto] | [variações] |

<!--
EXEMPLOS (remova antes de usar):

| Nome/Entidade | Tipo | Erros ASR comuns |
|---------------|------|------------------|
| Marina Silva | Scrum Master | marina selva, Mariana |
| Projeto Phoenix | Projeto interno | phoenix, fênix |
| Stripe | Gateway de pagamento | strip, stripe |
| Kubernetes | Plataforma de containers | kubernetes, cubernetes |
-->

---

## Estrutura Típica da Reunião

<!--
Descreva a estrutura padrão das reuniões deste tipo.
Ajuda a LLM a identificar seções e transições.
-->

**Tipo de reunião:** [Ex: Daily standup, Retrospectiva, Review, 1:1, etc.]

**Estrutura típica:**
1. [Fase 1 - Ex: Abertura e check-in]
2. [Fase 2 - Ex: Revisão de tarefas]
3. [Fase 3 - Ex: Discussão de bloqueios]
4. [Fase 4 - Ex: Próximos passos]
5. [Fase 5 - Ex: Encerramento]

**Duração média:** [Ex: 15 minutos, 1 hora, etc.]

---

## Papéis e Funções

<!--
Liste os papéis típicos dos participantes. Ajuda a identificar
quem é quem quando nomes não são mencionados explicitamente.
-->

| Papel | Descrição | Comportamento típico |
|-------|-----------|---------------------|
| [papel] | [descrição] | [como identificar na conversa] |

<!--
EXEMPLOS (remova antes de usar):

| Papel | Descrição | Comportamento típico |
|-------|-----------|---------------------|
| Facilitador | Conduz a reunião | Abre/fecha, dá a palavra, controla tempo |
| Tech Lead | Líder técnico | Responde dúvidas técnicas, valida soluções |
| PO | Product Owner | Traz requisitos, prioriza features |
| Dev | Desenvolvedor | Reporta status, levanta bloqueios |
-->

---

## Notas de Interpretação

<!--
Adicione notas sobre termos ambíguos ou que têm significado específico
no seu contexto, diferente do uso comum.
-->

- [Termo X] neste contexto significa [Y], não [Z comum]
- Quando mencionam "[expressão]", refere-se a [explicação]
- [Qualquer nota relevante para interpretação correta]

<!--
EXEMPLOS (remova antes de usar):

- "Subir" neste contexto significa fazer deploy, não upload de arquivo
- "Quebrou" geralmente indica que um teste falhou ou build não passou
- "Rodar local" significa executar o código na máquina do desenvolvedor
- Quando falam em "prod", referem-se ao ambiente de produção
-->

---

## Contexto Adicional (opcional)

<!--
Qualquer informação adicional que possa ajudar na interpretação.
-->

[Espaço livre para contexto adicional relevante]

---

<!--
CHECKLIST ANTES DE USAR:

[ ] Removi todos os exemplos e comentários
[ ] Preenchi pelo menos: Área de Conhecimento + Glossário
[ ] Revisei erros ASR comuns baseado em transcrições anteriores
[ ] Adicionei nomes próprios relevantes (pessoas, projetos)
[ ] Salvei o arquivo e testei com: metalscribe run-meeting --context meucontexto.md
-->
