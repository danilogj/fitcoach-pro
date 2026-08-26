# Cardio junto com musculação

> **Palavras-chave:** cardio, aeróbio, condicionamento, zona 2, Z2, HIIT, intervalado, efeito interferente, treino concorrente, passos, NEAT, zonas de frequência cardíaca, VO2max, corrida, bicicleta.

A maioria dos alunos que contrata personal quer perder gordura, e a maioria vai fazer cardio esteja prescrito ou não. Deixar de fora do programa não significa que não acontece — significa que acontece sem gestão, ao lado do treino que de fato produz o resultado.

---

## 1. Para que serve, por objetivo

| Objetivo | Papel do cardio | Dose |
| :--- | :--- | :--- |
| Perda de gordura | Soma gasto sem mexer na comida; protege a aderência | 2-4 sessões, majoritariamente fáceis |
| Hipertrofia | Saúde, capacidade de recuperação, regulação do apetite | 2 sessões fáceis e curtas |
| Saúde / sedentário | É a intervenção principal | 150 min/semana moderado, construído aos poucos |
| Força | Mínimo, só fácil | 1-2 sessões curtas |

**Cardio não é a alavanca de emagrecimento que as pessoas imaginam.** Quarenta minutos de corrida compram 350-450 kcal, que uma refeição generosa apaga. O valor está na saúde cardiovascular, na capacidade de trabalho e nos efeitos sobre apetite e humor que tornam o déficit suportável — não nas calorias.

---

## 2. Zonas de intensidade, individualizadas

Prescreva por **zona**, nunca por batimento fixo — prescrição em bpm está errada para todo mundo, exceto para a pessoa para quem foi escrita.

| Zona | Esforço | Teste da fala | Para quê |
| :--- | :--- | :--- | :--- |
| Z1 | Muito fácil | Conversa completa, respiração nasal | Recuperação, aquecimento |
| Z2 | Fácil | Frases inteiras, com leve esforço | Base aeróbia. **É onde mora o volume** |
| Z3 | Moderado | Frases curtas | A zona cinzenta — difícil demais para recuperar, fácil demais para adaptar |
| Z4 | Forte | Poucas palavras | Trabalho de limiar |
| Z5 | Máximo | Não fala | Intervalado de VO2max |

**Sem dado de frequência cardíaca, use o teste da fala.** É mais confiável para aluno destreinado que qualquer fórmula, e custa nada. A FC máxima estimada por idade (220 − idade) tem erro de ±10-12 batimentos por pessoa — diga isso se usar.

---

## 3. Distribuição: muito fácil, pouco forte

Cerca de **80 % do tempo em Z1-Z2 e 20 % em Z4-Z5**, evitando a Z3 como destino padrão.

A zona cinzenta é onde o aluno sem supervisão passa o tempo todo: forte o bastante para acumular fadiga que rouba das sessões de musculação, fácil o bastante para gerar pouca adaptação. Z3 não é proibida — tempo controlado é ferramenta legítima. O erro é chegar lá por correr o dia fácil rápido demais.

**HIIT é ferramenta de eficiência de tempo, não estímulo superior.** O custo de recuperação é real e compete diretamente com o treino de perna. Duas sessões por semana é o teto para quem treina musculação quatro vezes.

---

## 4. O efeito interferente, com honestidade

Treino aeróbio concorrente pode reduzir ganhos de força e hipertrofia. O tamanho desse efeito é rotineiramente exagerado na academia e rotineiramente descartado nos resumos de pesquisa. O que se sustenta:

- **A interferência escala com volume e intensidade do cardio.** Duas sessões fáceis de 30 minutos não interferem em praticamente nada. Seis horas semanais de corrida forte é outra conversa.
- **A modalidade importa.** Bicicleta interfere menos no treino de perna que corrida — menos carga excêntrica, menos dano muscular.
- **A proximidade importa.** Cardio na mesma sessão, logo antes de levantar, compromete o levantamento. Separar por 6 h ou mais, ou colocar o cardio depois, praticamente elimina o conflito.
- **É no membro inferior que aparece.** Hipertrofia de superior é pouco afetada.

**Regras práticas para escrever no programa:**

1. Cardio forte nunca na véspera de sessão pesada de inferior.
2. Se cardio e musculação caírem no mesmo dia, **levante primeiro** — a não ser que o objetivo do aluno seja o cardio.
3. Cardio fácil nos dias de descanso ou depois das sessões de superior.
4. Quando a força estagnar e o volume de cardio tiver subido, corte o cardio antes de cortar volume de musculação.

---

## 5. Passos e NEAT — a alavanca que todo mundo ignora

Para perda de gordura, uma meta diária de passos costuma valer mais que uma sessão de cardio. Está distribuída pelo dia, custa quase nada de recuperação, não interfere no treino e é trivial de acompanhar — o aluno já carrega o sensor.

| Linha de base | Meta |
| :--- | :--- |
| Abaixo de 4.000/dia | 6.000, depois reavalia |
| 4.000-7.000 | 8.000-10.000 |
| Acima de 8.000 | Mantém; acrescenta cardio em vez de mais passos |

**Em déficit, o NEAT cai sozinho.** O aluno se move menos sem perceber, e parte do déficit previsto evapora. A meta de passos é como você percebe isso acontecendo — e é por isso que o `metrics tdee-observed` acaba lendo menos que a fórmula previa. Não é cálculo quebrado: é a adaptação, medida.

**Prefira somar passos a cortar caloria** quando um aluno em perda de gordura estagnar. Comida é recurso finito numa dieta — gastou, não sobra para onde ir.

---

## 6. Modelos de prescrição

**Hipertrofia, 4 dias de musculação:** 2 × 25-30 min Z2 nos dias de descanso ou após superior. Meta de passos. Sem HIIT durante superávit — custa recuperação por calorias que você está deliberadamente comendo de volta.

**Perda de gordura, 4 dias:** meta de passos primeiro, depois 2-3 × 30-40 min Z2, depois opcionalmente 1 × 15-20 min de intervalado em dia sem perna. Acrescente o cardio só depois que a meta de passos estiver sendo cumprida — senão você está prescrevendo sessão para repor movimento que era de graça.

**Sedentário começando:** só caminhada, 3-4 × 20-30 min, construindo até 150 min/semana antes de qualquer coisa mais forte. O objetivo é que ele ainda esteja fazendo isso no mês seis.

**Registro.** Sessões de cardio entram no log como qualquer outra: `log add session --set session_id=z2_run --set duration_min=30`. Contam para a carga de treino, e carga não registrada é carga que você não gerencia.
