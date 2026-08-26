# Progressão e ajuste — operar o bloco

> **Palavras-chave:** progressão, duplo critério, sobrecarga progressiva, platô, estagnação, análise de log, check-in semanal, deload, ajuste de volume, escada de progressão, fechar bloco, reavaliação.

O programa é uma hipótese. O log é o dado que confirma ou refuta. Esta é a parte do trabalho que o software não faz sozinho e que o PT cobra por.

---

## 1. Critério de progressão de carga

**Duplo critério.** O aluno sobe a carga quando fecha **o topo da faixa de repetições em todas as séries mantendo o RIR alvo**. Não antes.

Exemplo: prescrição 4×6-8 a RIR 1-2. Ele fez 8, 8, 8, 8 com RIR 2 → sobe. Ele fez 8, 8, 7, 6 → repete a carga na semana seguinte.

**Incremento:** 2,5 a 5 kg nos compostos de membro inferior, 1 a 2,5 kg nos de superior, o menor incremento disponível nos isolados. Se a academia só tem halteres de 2 em 2 kg, o salto de 10 para 12 kg é de 20 % — nesse caso segure a carga e suba repetições até o topo da faixa seguinte antes de saltar.

---

## 2. Escada de progressão — quando a carga trava

Uma alavanca por vez, nesta ordem. Pular etapas queima volume que você vai precisar depois.

1. **Carga**, pelo duplo critério. É a alavanca principal e a mais barata.
2. **Faixa de repetições ou cadência**, se a carga travou. Desça a faixa (de 8-10 para 6-8, subindo o peso) ou segure 3 s na fase excêntrica com a mesma carga. Estímulo novo sem volume novo.
3. **Séries**, +1 no grupo que travou, até o teto de ~18-20 semanais.
4. **Exercício novo**, só se o padrão de movimento estagnou de verdade ou incomoda articulação.

**Adicionar exercício não é progressão — é troca. Adicionar série é progressão.** Não confunda os dois quando o aluno pedir "algo diferente".

---

## 3. Analisar o log exportado

Quando o PT colar um log, procure nesta ordem. A ordem importa: aderência explica mais estagnação do que qualquer variável de treino.

1. **Aderência.** Quantas das sessões previstas saíram? Em quais dias da semana ele falha? Se o mesmo dia falha há três semanas, o problema é a agenda, não o programa.
2. **Progressão de carga por exercício**, semana a semana, comparando o mesmo exercício no mesmo dia.
3. **Progressão deixada na mesa.** Fechou o topo da faixa em todas as séries com o RIR alvo e a carga *não* subiu na semana seguinte? É o erro mais comum e o mais fácil de corrigir.
4. **Queda entre a primeira e a última série.** Se a diferença diminui ao longo das semanas com a mesma carga, a capacidade de trabalho está melhorando. É sinal precoce de adaptação e quase ninguém olha.
5. **Exercícios parados há 2+ semanas.** Aplique a escada acima.
6. **Coerência com a fase.** Semanas de entrada devem ter uma série a menos; a semana de deload deve ter carga mantida e RIR alto. Volume acima do previsto na entrada é bandeira vermelha para furo de treino adiante.
7. **Buracos no registro.** Exercício sem carga anotada por várias semanas costuma significar que ele parou de fazer, não que esqueceu de anotar. Pergunte.

Entregue como **diagnóstico + ajuste específico**. "Está indo bem" não é análise.

---

## 4. Check-in semanal — leitura para ação

| Leitura | Ação |
| :--- | :--- |
| Todas as sessões · recuperação boa · desempenho subindo | Progride carga nos compostos principais. Não mexe em mais nada. |
| Todas as sessões · recuperação ruim | **Corta 20 % das séries por 1 semana, mantendo a carga.** Intensidade preserva o estímulo; volume é o que cobra recuperação. |
| Faltaram sessões por agenda | Versões curtas em vez de pular. Aderência vale mais que a sessão perfeita. |
| Desempenho caindo 2 semanas seguidas | Antecipa o deload. |
| Peso parado 3 semanas em fase de ganho | Soma ~200 kcal (`05-nutricao.md`). |
| Peso parado 3 semanas em fase de perda | Confere aderência alimentar antes de cortar caloria. Na dúvida, aumenta passos antes de cortar comida. |
| Ganho de gordura acima do previsto | Corta ~200 kcal. Não mexe no treino. |
| Dor articular nova | Substitui o padrão pela tabela de `03`. Não "treina através". |
| Sono abaixo de 6 h de forma consistente | Corta uma sessão antes de cortar sono. Nesse volume, sono pesa mais que qualquer variável de treino. |

**Uma variável por vez.** Se você mexer em caloria e volume na mesma semana, o próximo check-in não vai conseguir dizer o que funcionou.

**Três semanas antes de concluir.** Ruído de água, sal e glicogênio engana em duas semanas. A não ser que a leitura seja gritante, espere a terceira.

---

## 5. Carga de treino, quantificada

Julgar carga por sensação funciona até a semana do aluno ficar estranha. A razão de carga aguda:crônica compara os últimos 7 dias de treino com os últimos 28, usando séries válidas por dia do log:

```
python3 tools/cli.py --client alunos/<nome> load acwr
```

**As séries são ponderadas pelo custo sistêmico**, não contadas de forma plana. Quatro séries de terra pesado e quatro de elevação lateral não são a mesma semana: composto axial conta 1,4; composto apoiado 1,0; unilateral 0,8; isolado 0,5; core 0,4. Contagem plana permite ao aluno trocar trabalho de braço por terra sem a razão acusar nada — que é exatamente o pico que ela existe para pegar. O `--flat` volta à versão sem peso, se quiser comparar.

| Razão | Leitura | Ação |
| :--- | :--- | :--- |
| Abaixo de 0,8 | Carga aguda abaixo da norma recente | Semana furada, não problema de recuperação. Retoma no volume da semana anterior |
| 0,8 - 1,3 | Faixa produtiva | Onde a sobrecarga progressiva acontece |
| 1,3 - 1,5 | Subiu mais rápido que a adaptação | Segura o volume por uma semana antes de somar |
| Acima de 1,5 | Pico | O padrão que precede lesão por carga. Corta esta semana |

Ele **recusa abaixo de 21 dias de histórico** — antes disso a razão é aritmética sem informação, e a tabela de check-in acima é o instrumento melhor.

### A decisão de deload

```
python3 tools/cli.py load deload --performance-dropping-weeks 2 --sleep-hours-avg 6.1 \
    --soreness-avg 4 --readiness-avg 38 --weeks-since-deload 7
```

**Dois ou mais sinais independentes disparam o deload.** Um sinal é uma semana ruim; dois são um padrão. Passe apenas o que foi de fato medido — um dado ausente nunca conta como sinal, e é isso que impede a ferramenta de fabricar motivo para deload.

Deload significa séries em ~60 % do previsto com piso de 2, **carga mantida**, RIR 3-4. Volume é o que cobra recuperação; intensidade é o que preserva o estímulo.

---

## 6. Platô — diagnóstico antes do ajuste

Antes de mudar o programa, elimine as causas que não são o programa:

| Causa | Como identificar | Correção |
| :--- | :--- | :--- |
| Aderência | Log com buracos | Ajusta agenda ou divisão, não o programa |
| Comida | Peso parado, energia baixa | Ajusta calorias |
| Sono | Relato, desempenho irregular | Sono antes de qualquer coisa |
| Estresse de vida | Contexto | Reduz volume temporariamente, mantém carga |
| Técnica degradando com a carga | Vídeo da série | Volta a carga, arruma a execução |
| Fadiga acumulada | Desempenho caindo em vários exercícios ao mesmo tempo | Deload |
| Estímulo insuficiente de fato | Todo o resto eliminado | Escada de progressão |

O último item é o menos comum e o primeiro que todo mundo assume.

---

## 7. Fechar o bloco

Com 8 semanas de log, a decisão deixa de ser por literatura média e passa a ser pelo caso deste aluno. Avalie:

- **Progressão por grupo muscular** — quais subiram, quais travaram. Grupo que travou ganha série no bloco seguinte; grupo que voou pode ceder volume.
- **Simetria de estímulo** — bíceps e tríceps acompanharam as puxadas e supinos? Deltoide posterior recebeu o que foi prescrito?
- **Composição corporal contra a meta** (`06-avaliacao-corporal.md`).
- **Aderência por dia da semana** — o dado que mais muda o próximo bloco.
- **O que o aluno odiou.** Exercício odiado é exercício mal executado ou pulado. Troque por outro do mesmo padrão.

Monte o bloco seguinte a partir dessas respostas. **Nunca repita o bloco anterior por inércia** — e nunca troque tudo só para parecer novidade. Variação sem razão apaga a comparação que você levou 8 semanas construindo.
