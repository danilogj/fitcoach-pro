# Nutrição — alvo calórico, macros e ajuste

> **Palavras-chave:** calorias, TMB, metabolismo basal, Mifflin-St Jeor, Katch-McArdle, TDEE, manutenção, superávit, déficit, macros, proteína, carboidrato, gordura, cardápio, suplementação, creatina, whey, hidratação, ajuste de peso.

**Limite de escopo, antes de tudo.** Prescrição dietética individualizada é ato privativo de nutricionista em vários países, Brasil incluído. O que este módulo produz é **alvo de macronutrientes e educação alimentar** — trabalho legítimo do personal trainer na maior parte das jurisdições. Patologia, medicação, restrição agressiva, gestação, suspeita de transtorno alimentar: encaminhe, e diga isso ao PT com todas as letras.

---

## 1. Estimar a manutenção

Duas equações, porque a convergência entre elas é o que indica confiabilidade.

**Não calcule à mão.** `python3 tools/cli.py metrics targets --weight-kg 71 --height-cm 178 --age 41 --sex male --ffm-kg 57.7 --sessions-per-week 4 --goal gain` devolve a TMB pelas duas equações, a decomposição por componentes, a manutenção com sua faixa e a divisão de macros. As fórmulas estão documentadas aqui para você explicar, não para executar.

**Mifflin-St Jeor** (só precisa de peso, altura, idade, sexo):

```
Homem:   TMB = 10 × peso(kg) + 6,25 × altura(cm) − 5 × idade + 5
Mulher:  TMB = 10 × peso(kg) + 6,25 × altura(cm) − 5 × idade − 161
```

**Katch-McArdle** (precisa de massa livre de gordura — use quando houver medida de composição corporal):

```
TMB = 370 + 21,6 × MLG(kg)
```

Se as duas caem perto uma da outra, a TMB é a parte confiável da conta. Se divergem muito, a estimativa de gordura corporal está errada — não a TMB.

**Da TMB para a manutenção**, somando os componentes em vez de aplicar um multiplicador único (multiplicador de atividade esconde onde está o erro):

| Componente | Estimativa |
| :--- | :--- |
| NEAT — atividade não-exercício | +10 % da TMB para rotina sedentária, até +25 % para trabalho em pé ou muita caminhada |
| Gasto de treino | ~250-400 kcal por sessão de musculação, **diluído nos 7 dias** |
| Efeito térmico dos alimentos | ~10 % da ingestão total |

**A margem de erro real está no NEAT.** Ela é de centenas de kcal e nenhuma fórmula resolve. Por isso a média semanal de peso manda mais que a estimativa — a conta serve para escolher o ponto de partida, não para estar certa.

Comunique como faixa: "manutenção estimada em torno de 2.350 kcal, faixa provável 2.290 a 2.420". Nunca "2.347 kcal".

---

## 2. Definir o alvo

| Objetivo | Ajuste sobre a manutenção | Ritmo esperado |
| :--- | :--- | :--- |
| Hipertrofia, iniciante ou destreinado | +300 a +500 kcal | 0,25 a 0,5 % do peso corporal por semana |
| Hipertrofia, intermediário/avançado | +200 a +350 kcal | 0,2 a 0,35 kg/semana |
| Perda de gordura | −300 a −500 kcal | 0,5 a 1,0 % do peso corporal por semana |
| Perda de gordura, obesidade | −500 a −750 kcal | Até 1 % por semana, com acompanhamento |
| Manutenção / recomposição | ±0 | Peso estável, medidas mudando |

**Pisos que não se atravessam:** nunca abaixo da TMB estimada em déficit prolongado; nunca abaixo de ~1.200 kcal para mulher e ~1.500 para homem sem acompanhamento médico e de nutricionista. Déficit agressivo compra velocidade com massa magra, e é a causa número um de recuperação do peso no ano seguinte.

**Ganho rápido demais é gordura.** Acima de ~0,5 % do peso por semana em superávit, a fração que vem como gordura cresce rápido. Em quem volta de pausa longa, os primeiros 2-3 kg vêm em 6-8 semanas — parte é glicogênio e água, parte é memória muscular real. Não calibre expectativa por esse trecho.

---

## 3. Macros

Ordem de definição: **proteína → gordura → carboidrato preenche o resto.**

| Macro | Alvo | Observação |
| :--- | :--- | :--- |
| **Proteína** | 1,6 a 2,2 g/kg de peso corporal | Acima de 2,2 g/kg não há benefício adicional demonstrado para hipertrofia. Em déficit agressivo ou em pessoa magra, use o topo da faixa (até 2,4 g/kg de massa magra) para proteger massa. |
| **Gordura** | 0,8 a 1,0 g/kg | Piso de ~0,6 g/kg por função hormonal e absorção de vitaminas. Não desça disso. |
| **Carboidrato** | O resto das calorias | É o combustível do treino de força. Em fase de ganho, é onde a maior parte do superávit deve entrar. |
| **Fibra** | 25 a 38 g/dia | Saciedade e trânsito. Quase sempre esquecido nos planos de déficit. |
| **Água** | 30 a 40 ml/kg | Mais em calor e volume alto de treino. |

**Distribuição de proteína:** 3 a 5 refeições com 0,3-0,4 g/kg cada estimula a síntese proteica melhor que duas refeições grandes. É otimização de segunda ordem — a dose diária total resolve a maior parte do resultado.

**Pré e pós-treino:** a "janela anabólica" de 30 minutos não sobrevive aos dados. O que importa é a ingestão diária e não treinar em jejum prolongado quando o volume é alto. Carboidrato 1-2 h antes melhora o desempenho na sessão, e é isso que gera o estímulo.

---

## 4. Montar o cardápio

Nunca monte cardápio antes de ter as respostas do Bloco 4 da anamnese — quem cozinha, orçamento, alergias, o que ele odeia.

**Estrutura que funciona:** 4 a 5 refeições, cada uma com fonte de proteína definida + fonte de carboidrato definida + vegetais, e uma tabela de conferência somando os macros no fim. Sem a tabela de conferência, o cardápio é chute com aparência de precisão.

**Entregue com alavancas de ajuste rápido**, não com um cardápio novo a cada semana:

| Preciso | Faça |
| :--- | :--- |
| +200 kcal | 1 colher de sopa de azeite + ~50 g de arroz cozido |
| −200 kcal | Corta ~30 g de castanha e ~100 g de arroz cozido |
| Bater a proteína sem enjoar da mesma carne | 1 scoop de whey substitui parte de uma refeição |

**Substituições por grupo** valem mais que a lista fechada. Ensine a troca em vez de reescrever o plano.

### Tabela de equivalência de porções

Alvo de macro não serve para quem não sabe transformar "150 g de proteína" em comida. Estas são as porções que entregam uma unidade de cada macro, para o aluno remontar a refeição sozinho.

**≈ 20 g de proteína**

| Alimento | Porção |
| :--- | :--- |
| Peito de frango cru | 90 g |
| Carne bovina magra crua (patinho, coxão mole) | 95 g |
| Peixe branco (tilápia, merluza) | 100 g |
| Atum em lata, escorrido | 80 g |
| Ovos inteiros | 3 |
| Claras | 6 |
| Whey protein | 1 scoop (~28 g) |
| Queijo cottage | 150 g |
| Iogurte grego (natural, coado) | 200 g |
| Feijão ou lentilha cozidos | 400 g *(traz junto ~55 g de carboidrato)* |
| Tofu firme | 180 g |

**≈ 30 g de carboidrato**

| Alimento | Porção |
| :--- | :--- |
| Arroz branco cozido | 100 g |
| Batata doce cozida | 130 g |
| Batata inglesa cozida | 150 g |
| Macarrão cozido | 110 g |
| Aveia em flocos, crua | 45 g |
| Pão | 60 g (um pão francês) |
| Goma de tapioca | 45 g |
| Banana | 1 grande |
| Feijão cozido | 220 g *(traz junto ~10 g de proteína)* |

**≈ 10 g de gordura**

| Alimento | Porção |
| :--- | :--- |
| Azeite | 1 colher de sopa rasa |
| Castanhas (do-pará, de caju, amêndoa) | 15 g |
| Pasta de amendoim | 20 g |
| Abacate | 60 g |
| Manteiga | 12 g |
| Ovo inteiro | 2 |

**Leia como aproximação.** Os valores vêm de tabelas de composição (TACO, USDA) e variam 10-20 % conforme o corte, a marca e o preparo. Carne está em peso cru porque é assim que se pesa. Aluno que acerta essas porções chega perto o bastante — a média semanal de peso conta o resto.

**Isto é educação alimentar, não dieta.** Entregar uma tabela de equivalências para o aluno comer o que gosta dentro do alvo é trabalho de personal. Prescrever dieta individualizada não é — ver a nota de escopo no topo deste arquivo.

---

## 5. Suplementação — o que tem evidência

| Item | Dose | Veredito |
| :--- | :--- | :--- |
| **Creatina monohidratada** | 3-5 g/dia, todos os dias | O suplemento com melhor evidência para força e hipertrofia. Sem necessidade de saturação, horário indiferente, seguro no uso contínuo em pessoa saudável. Ganho de 1-2 kg de peso na primeira semana é água intramuscular — avise antes, ou o aluno acha que engordou. |
| **Whey / caseína** | Conforme necessidade | Conveniência para fechar a proteína, não necessidade. Comida resolve. |
| **Cafeína** | 3-6 mg/kg, 45 min antes | Melhora desempenho de forma consistente. Cuidado com sono e com quem tem hipertensão. |
| **Vitamina D, ômega 3** | Conforme deficiência | Saúde geral. Efeito direto sobre hipertrofia: não demonstrado. |
| **Beta-alanina** | 3-6 g/dia | Efeito pequeno, restrito a esforços de 1-4 minutos. Pouco relevante para musculação padrão. |
| **BCAA, glutamina, "queimadores"** | — | Não recomende. Com proteína adequada, BCAA isolado não acrescenta. |

Suplemento é a última alavanca da lista, depois de treino, comida, sono e aderência. Um PT que abre pela suplementação está resolvendo o problema errado.

---

## 6. Regras de decisão — quando mexer na caloria

1. **Peso parado por 3 semanas** (comparando médias semanais) em fase de ganho → soma ~200 kcal.
2. **Peso subindo acima do ritmo alvo de forma sustentada** → corta ~200 kcal. Acima disso a fração que vem como gordura cresce rápido.
3. **Ganho de gordura ultrapassou o teto definido antes de o peso chegar à meta** → corta ~200 kcal e reavalia o alvo.
4. **Em déficit, peso parado 3 semanas com aderência confirmada** → corta ~150-200 kcal ou aumenta passos. Prefira os passos: preserva comida para quando você precisar cortar de verdade.
5. **Ao chegar na meta de peso** → a manutenção subiu junto com a massa. Recalcule antes de decidir se estabiliza ou continua.

**Sempre 200 kcal por vez, sempre esperando 3 semanas.** Ajuste grande produz oscilação que você não consegue interpretar no check-in seguinte.

---

## 7. Gasto medido vence a fórmula

Quando houver dado registrado suficiente, pare de discutir com a estimativa e meça:

```
python3 tools/cli.py --client alunos/<nome> metrics tdee-observed --goal-delta -400
```

Ele pega a ingestão média diária numa janela de 28 dias, pega a variação da tendência suavizada de peso na mesma janela, converte essa variação a ~7.700 kcal por quilo e devolve o gasto que concilia as duas. É o número que corrige uma estimativa que derivou — e ela deriva, porque o NEAT é impossível de prever e cai sozinho durante o déficit.

**Ele recusa abaixo de 10 dias de ingestão registrada na janela.** Repasse a recusa em vez de voltar para a fórmula em silêncio: "Ainda não dá para medir seu gasto real — 6 dos últimos 28 dias têm refeição registrada e o cálculo precisa de 10. Até lá trabalhamos com a estimativa, que é uma faixa, não um número."

Duas ressalvas que valem dizer ao profissional:

- **7.700 kcal/kg é convenção de trabalho**, não constante. A variação inicial de peso inclui glicogênio e água a um custo energético muito diferente — por isso a janela é de quatro semanas e não de uma.
- **Vale o que vale o registro alimentar.** Subnotificar ingestão — que é a norma, não a exceção — faz o gasto medido sair menor do que é. Se o número voltar implausivelmente baixo, suspeite do registro antes de suspeitar do metabolismo.
