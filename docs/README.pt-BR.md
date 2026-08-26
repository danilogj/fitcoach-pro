# FitCoach Pro

**Uma metodologia de prescrição para personal trainers, empacotada como skill de IA — com a aritmética tirada das mãos do modelo.** Roda no Claude e no ChatGPT. English: [`../README.md`](../README.md).

>  ### 👋 Não é programador?
> **[Leia o guia do personal trainer](GUIA-DO-PERSONAL.md)** — instalação sem terminal, uma conversa real do primeiro aluno até a ficha pronta, e um glossário. Escrito para quem nunca instalou nada parecido.

---

A maioria dos prompts de "personal trainer com IA" falha do mesmo jeito: você pede um programa e recebe doze exercícios, quatro séries cada, sem saber em que academia o aluno treina, sem triagem nenhuma, e um percentual de gordura com uma casa decimal saído de um sensor de pulso.

Este repositório aposta no contrário. Ele não tenta substituir o julgamento do profissional — organiza o julgamento. Triagem antes da prescrição. Divisão escolhida pela agenda real do aluno, semana ruim incluída. Exercícios escolhidos pelo equipamento que existe de fato. Volume semanal auditado por grupo muscular. Progressão por critério explícito, não por sensação. E, o tempo todo, uma instrução que o modelo não segue sozinho: **diga quando um número é estimativa.**

## O que muda aqui

**O modelo nunca faz a conta.** Calorias, macros, TMB, TDEE, tendência de peso, séries semanais por músculo, 1RM, carga de treino — todo número vem de Python testado em [`tools/`](../claude/fitcoach-pro/tools), não da cabeça do modelo. É a diferença entre um prompt que avisa sobre alucinação e um pacote que remove a oportunidade dela.

**Ele recusa em vez de chutar.** O `metrics tdee-observed` sai com erro e "6 dos últimos 28 dias têm refeição registrada, o cálculo precisa de 10" em vez de produzir um número confiante a partir de nada. O mesmo para taxa de variação com menos de 14 dias, ou ACWR com menos de 21 dias de histórico. As recusas são testadas.

**Ele se recusa a prescrever sem anamnese.** Peça um programa sem informar dias, equipamento, histórico, idade e lesões, e ele pergunta antes. Plano montado sobre suposição é retrabalho garantido.

**Carregamento progressivo.** O `SKILL.md` é um roteador. O modelo carrega as regras de volume quando está montando um bloco e a crítica da bioimpedância quando está lendo um exame de composição corporal — não os 45 KB inteiros a cada mensagem.

**Ele denuncia o que inventou.** Todo entregável fecha com uma linha nomeando o que foi estimado, inferido ou preenchido — a carga inicial, o exercício que depende de equipamento não confirmado, a conta que partiu de um dado aproximado. É isso que torna a revisão possível em vez de decorativa.

**Saiu de uma auditoria, não de um brainstorm.** A metodologia foi extraída de um bloco real de 8 semanas, construído auditando um relatório de treino gerado por IA que estava cheio de falsa precisão. Várias regras em `references/` estão escritas como advertência por causa de erros específicos daquele relatório. O [`06-avaliacao-corporal.md`](../claude/fitcoach-pro-pt-BR/references/06-avaliacao-corporal.md) existe quase inteiramente por essa razão.

## Os números, deterministicamente

```console
$ python3 tools/cli.py metrics targets --weight-kg 71 --height-cm 178 --age 41 \
      --sex male --ffm-kg 57.7 --sessions-per-week 4 --goal gain
BMR 1619 kcal (Mifflin 1622 / Katch 1616, spread 6)
  NEAT +194 · training +183 · TEF +222
maintenance ~2218 kcal (likely 2085-2351)
target 2518 kcal (+300)
protein 128 g · fat 64 g · carbs 358 g

$ python3 tools/cli.py --client alunos/joao metrics rate --goal loss
cannot answer: need at least 14 days of weight data; have 5. Water and
glycogen noise dominates shorter windows.
```

A manutenção usa o **método por componentes** — TMB + NEAT + treino + efeito térmico — em vez de um multiplicador único, porque o multiplicador esconde qual termo é o chute. É sempre o NEAT.

O `volume check` soma as séries semanais por músculo a partir de um arquivo de programa, julga cada grupo contra o volume mínimo efetivo e o máximo recuperável, reporta as indiretas em coluna separada e nomeia qualquer padrão de movimento que a semana não cobre. São 110 exercícios em `data/exercises.json`, com cadeias de substituição para limitação de ombro, lombar, joelho, punho e cotovelo.

O `cohort` ordena a lista inteira de alunos por quem precisa de atenção nesta semana — pico de carga, ritmo inseguro, progresso travado, quem parou de registrar. O `load acwr` pondera cada série pelo custo sistêmico, para uma semana de terra não parecer uma semana de rosca.

Documentação completa em [`tools/README.md`](../claude/fitcoach-pro/tools/README.md). São 109 testes, só biblioteca padrão, sem instalação.

## Dado de wearable, sem API

```console
$ python3 tools/cli.py --client alunos/maria ingest samsung_health_export.zip
source detected: samsung
events found: 7 session, 20 sleep, 20 steps, 20 weight
written: 67 · already present: 0
re-running this import is a no-op.
```

| Fonte | O que entregar | O que entra |
| :--- | :--- | :--- |
| **Samsung Health** | O zip de Configurações → Baixar dados pessoais | Peso, passos, sono, FC, sessões |
| **Garmin** | `Activities.csv` do Connect, ou o export completo | Sessões e arquivos diários |
| **Apple Health** | `export.xml` de Saúde → perfil → Exportar Todos os Dados | Peso, passos, FC de repouso, HRV |
| **Strava** | `activities.csv` do export em massa | Só sessões de cardio |
| **Withings, Oura, Whoop, Fitbit, balança, planilha** | Qualquer CSV | O que reconhecer nas colunas |

**Arquivo, não API** — de propósito. Todo serviço exporta; o Samsung Health não tem API pública desde que o SDK virou parceria fechada; e toda integração OAuth exige credencial e quebra quando o fabricante reorganiza. Importador de arquivo roda offline, não guarda segredo e continua funcionando daqui a cinco anos.

Reimportar o mesmo arquivo não duplica nada. Quando um export não casar, `ingest --inspect` mostra os nomes reais das colunas e `--map 'weight_kg=Massa (kg)'` resolve numa flag.

## O dashboard

O `dashboard` renderiza o log num único HTML autocontido — SVG inline, sem CDN, sem JavaScript, abre offline.

O gráfico que justifica a existência dele é o de **séries diretas por músculo contra os limiares daquele músculo**. Um total de 60 séries na semana pode ser quatro músculos ou doze; só ele diz qual, e destaca o grupo zerado que um total saudável esconde.

Nada é inventado: o que não puder ser calculado vai para um bloco "Not shown yet" nomeando o dado que falta.

## Instalar

Não se sente à vontade com terminal? Use o **[guia do personal trainer](GUIA-DO-PERSONAL.md)** — ele cobre Claude e ChatGPT sem um único comando.

### Claude Code

```bash
git clone https://github.com/danilogj/fitcoach-pro.git
cp -r fitcoach-pro/claude/fitcoach-pro-pt-BR ~/.claude/skills/
```

A skill carrega sozinha quando o assunto for aluno, ficha, prescrição, carga, RIR, volume, check-in, macros ou bioimpedância.

### App do Claude

Configurações → Capabilities → Skills → Upload, com `claude/fitcoach-pro-pt-BR` compactado em `.zip`.

### ChatGPT

1. Explore GPTs → Create → Configure
2. **Instructions:** cole [`../gpt/pt-BR/instructions.md`](../gpt/pt-BR/instructions.md)
3. **Conversation starters:** as quatro linhas de [`../gpt/pt-BR/conversation-starters.md`](../gpt/pt-BR/conversation-starters.md)
4. **Knowledge:** envie os 10 arquivos de [`../gpt/pt-BR/knowledge/`](../gpt/pt-BR/knowledge)
5. **Capabilities:** só Code Interpreter — navegação e geração de imagem não servem aqui

**Confira a instalação** pedindo uma anamnese para aluno novo. Deve começar pelas sete perguntas de triagem, não por um plano de treino.

## O que tem dentro

| | |
| :--- | :--- |
| `01-principios.md` | Os seis princípios que regem todas as outras regras |
| `02-anamnese-triagem.md` | PAR-Q+ adaptado, red flags, classificação de perfil, restrições |
| `03-prescricao-treino.md` | Divisões por dias, seleção por equipamento, auditoria de volume, periodização |
| `04-progressao-e-ajuste.md` | Duplo critério, escada, análise de log, check-in, platô |
| `05-nutricao.md` | Estimativa metabólica, macros, suplementação, regras de ajuste |
| `06-avaliacao-corporal.md` | Bioimpedância desmontada, protocolo, circunferências |
| `07-cardio.md` | Zonas, distribuição de intensidade, efeito interferente, passos e NEAT |
| `08-entregaveis.md` | Ficha, relatório de evolução, mensagens ao aluno |

O `INDEX.md` roteia a pergunta para o arquivo e a seção certos, para o modelo carregar o que precisa em vez de tudo.

Mais os modelos preenchíveis de anamnese, programa e log, e a ficha abaixo.

## A ficha do aluno

[`ficha-aluno.template.html`](../claude/fitcoach-pro-pt-BR/assets/ficha-aluno.template.html) — página única e offline que o aluno usa no celular durante o treino.

Mostra a prescrição de cada série, registra carga e repetições série a série, exibe a linha da semana anterior para comparação, tem cronômetro de descanso, aplica sozinha a fase da semana (entrada, volume cheio, deload) e exporta o log em Markdown — que é exatamente o formato que a skill analisa no check-in.

Funciona como arquivo local, hospedada num link, ou publicada como Artifact do Claude.

## Caso real

[`examples/case-01-hypertrophy-41m`](../examples/case-01-hypertrophy-41m) — um bloco real em andamento, publicado com consentimento e com os números mantidos: anamnese, programa, alvo nutricional e avaliação de linha de base, com o raciocínio por trás de cada decisão. Está em inglês, como o restante da documentação principal.

**O log de treino ainda não está lá**, porque o bloco começou há pouco e o dado não existe. Entra quando existir. Toda metodologia parece convincente num estudo de caso escrito depois que o resultado já é conhecido.

## Leia antes de instalar

**[`DISCLAIMER.pt-BR.md`](DISCLAIMER.pt-BR.md)** — a versão curta:

O responsável técnico é você, sempre. A IA erra, e erra com cara de certeza — inventa cargas, volumes, contas calóricas, contraindicações e referências. Isso é inerente à tecnologia e nenhuma atualização resolve. **Toda saída precisa passar pelos seus olhos antes de chegar a um aluno.** Este projeto não diagnostica, não libera ninguém para treinar e não substitui nutricionista.

## Créditos

A arquitetura deve dívidas específicas a quatro projetos de código aberto, lidos de perto durante a construção:

- **[Yuvasee/trainer](https://github.com/Yuvasee/trainer)** (MIT) — o contrato de "nunca faça conta de cabeça", o log append-only com schema tipado, o TDEE adaptativo a partir da ingestão real e a recusa em vez do chute. A mais forte das skills analisadas.
- **[barcia/running-coach-skill](https://github.com/barcia/running-coach-skill)** (MIT) — gestão de carga quantificada e prescrição por zonas individualizadas em vez de batimento fixo.
- **[revfactory/harness-100](https://github.com/revfactory/harness-100)** (Apache 2.0) — limiares de volume por músculo e modelos de periodização.
- **[H1an1/health-coach](https://github.com/H1an1/health-coach)** (MIT) — padrões de ingestão de wearable e relatório longitudinal.

Nenhum código foi copiado; as ideias foram, e melhoraram este projeto.

## Licença

Apache 2.0 — uso comercial e forks permitidos, atribuição preservada pelo [`NOTICE`](../NOTICE).

Feito por **Danilo Gouveia Jorge**, São Paulo, Brasil.
