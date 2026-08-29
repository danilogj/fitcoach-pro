# Princípios — como a prescrição decide

> **Palavras-chave:** princípios, doutrina, volume semanal, frequência, RIR, proximidade da falha, carga axial, dose-resposta, margem de progressão, métrica de decisão, hierarquia de evidência.

Estes seis princípios regem tudo o que os outros arquivos prescrevem. Quando duas regras entrarem em conflito, o princípio decide.

---

## 1. Volume semanal é a variável que decide, não a frequência

Com volume igualado, treinar um grupo 1x, 2x ou 3x por semana produz hipertrofia equivalente (Schoenfeld et al., 2019 [PMID: 30558493]; McLeod et al., 2024 [PMID: 37385345]). A frequência existe para **distribuir** o volume dentro da semana, não para criar estímulo extra.

**Consequência prática:** a pergunta "quantos dias o aluno tem?" não define o resultado — define a divisão. O que define o resultado é quantas séries válidas por grupo cabem na semana, e se o aluno consegue executá-las com qualidade.

**Faixa de trabalho:** 10 a 20 séries válidas por grupo muscular por semana cobre a maior parte dos casos de hipertrofia (Schoenfeld et al., 2017 [PMID: 27433992]). Abaixo de 8 o estímulo é de manutenção ou dose mínima (Androulakis-Korakakis et al., 2020 [PMID: 31797219]). Acima de 20 os retornos caem e o custo de recuperação sobe rápido — e há grande variação individual nos dois extremos.

**Os limiares por músculo** — volume mínimo efetivo, faixa adaptativa e volume máximo recuperável — estão em `tools/volume.py` e saem com `python3 tools/cli.py volume landmarks`. São médias populacionais escaladas pelo perfil de treino, não prescrições individuais.

**Nunca some séries à mão.** `python3 tools/cli.py volume check --program ARQUIVO.json` soma as séries diretas por músculo, reporta as indiretas em separado, julga cada grupo contra os limiares e aponta os padrões de movimento que a semana não cobre. Programa que não passou por isso não está pronto.

**Teto por sessão:** acima de ~8-10 séries para o mesmo grupo numa única sessão, as séries finais rendem pouco. Se o volume alvo não cabe em uma sessão, divida em duas. Citações completas em `09-evidencia-cientifica.md`.

---

## 2. RIR em toda série, calibrado ao custo do exercício

RIR (repetições em reserva) é quantas repetições o aluno **ainda conseguiria fazer** ao encerrar a série. É a variável de intensidade que o log consegue registrar (Robinson et al., 2024 [PMID: 38970765]; Refalo et al., 2023 [PMID: 36334240], 2024 [PMID: 38393985]).

| Tipo de exercício | RIR alvo | Por quê |
| :--- | :-: | :--- |
| Composto pesado com barra, barra fixa, terra | **1-2** | Nunca à falha. A hipertrofia melhora perto da falha, mas falha absoluta aqui gera fadiga sistêmica que compromete o resto da sessão e da semana. |
| Isolado, máquina, polia | **0-1** | Pode ir à falha. Custo de recuperação baixo, risco técnico baixo — é onde se cobra esforço máximo. |
| Iniciante nos 3 primeiros meses | **2-3** em tudo | Ele ainda não sabe estimar RIR e superestima o quanto sobrou. Margem serve de proteção enquanto a técnica assenta. |

**Aviso sobre a medida:** estimativa de RIR de iniciante erra sistematicamente para mais — ele diz "sobrou 2" quando sobraram 5 (Halperin et al., 2021). A correção não é discurso, é vídeo da série ou uma série levada à falha real sob supervisão, uma vez, para calibrar a percepção. Citações completas em `09-evidencia-cientifica.md`.

---

## 3. Carga axial concentrada, não distribuída

Barra nas costas, terra e agachamento pesado carregam a coluna. Distribuir esses padrões por quatro dias da semana é onde nasce a lombalgia que interrompe seis semanas de treino.

**Regra:** concentre carga axial pesada em **um ou dois dias**, e use variações sem compressão de coluna nos demais — unilateral, apoiado, máquina, quadril dominante com carga menor.

**Peso do princípio por perfil:**

| Perfil | Como aplicar |
| :--- | :--- |
| Jovem, sem histórico de dor lombar | Até 2 dias axiais pesados. Margem confortável. |
| Acima de 40 anos, ou destreinado voltando | 1 dia. O limitante deixa de ser músculo e passa a ser articulação e tecido conjuntivo. |
| Histórico de hérnia, lombalgia recorrente, pós-operatório | Zero barra nas costas até liberação. Substitutos em `03-prescricao-treino.md`. |

Regra derivada: não coloque remada curvada livre na véspera do dia de agachamento. Mesmo volume de dorsal sai da remada apoiada, com zero custo de coluna.

---

## 4. Volume com espaço para crescer

Volume é a principal alavanca de progressão dos próximos meses. Se o bloco começa no teto do que o aluno tolera, não sobra nada para adicionar quando ele travar na semana 12.

**Comece na faixa produtiva baixa** — 10 a 14 séries por grupo — e suba conforme a resposta. Um programa que começa em 22 séries por grupo produz resultado rápido e beco sem saída.

Corolário: **adicionar exercício não é progressão, é troca.** Adicionar série é progressão. Não confunda os dois quando o aluno pedir "algo novo".

---

## 5. Log de treino, média de peso e circunferência decidem — o resto confirma

Hierarquia de confiança, nesta ordem:

1. **Log de treino** — carga × reps × RIR por sessão. É o melhor indicador de progresso de força e o proxy mais confiável de hipertrofia no horizonte de semanas. Nenhum sensor bate isso.
2. **Média semanal de peso** — pesagem diária, mesma hora, jejum, pós-micção; compara-se média contra média. Pesagem única semanal erra até 1 kg só por água e sal.
3. **Circunferência de cintura, semanal** — responde à única pergunta que o peso não responde: o superávit está grande demais, ou o déficit está funcionando?
4. **Foto a cada 4 semanas** — mesma luz, local, pose, horário, em jejum.
5. **Bioimpedância a cada 4 semanas, nunca semanal** — sinal de confirmação, jamais métrica de decisão. Ver `06-avaliacao-corporal.md`.

Se 1, 2 e 3 apontam na mesma direção, a bioimpedância é dispensável. Se discordam, ela não resolve — o que resolve é ajustar e esperar três semanas.

---

## 6. Aderência vence otimização

Um programa 20 % pior que o aluno executa 90 % das semanas entrega mais que o programa ótimo que ele executa 50 %. Toda decisão de prescrição passa por este filtro antes de sair:

- O aluno tem esse equipamento **hoje**, na academia dele, no horário que ele treina?
- Cabe no tempo real de sessão, contando descanso?
- Ele consegue executar a técnica sem supervisão constante?
- Ele vai comer isso numa terça-feira comum?

Se a resposta for não em qualquer uma, o plano está errado — por mais correta que seja a fisiologia.

**Nunca existe sessão de recuperação.** Perdeu um treino, o treino está perdido. Empilhar dois no mesmo dia ou treinar três dias seguidos para compensar troca um dia perdido por uma semana comprometida.
