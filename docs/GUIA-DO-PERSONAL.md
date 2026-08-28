# Guia do personal trainer

**Para quem nunca instalou nada parecido.** Não presume que você saiba o que é terminal, arquivo `.zip` ou linha de comando. Se em algum ponto você travar, o problema é este guia, não você — abra uma issue dizendo onde travou.

English version: [`TRAINER-GUIDE.md`](TRAINER-GUIDE.md)

---

## 1. O que é isto, em uma página

Você já deve ter pedido um treino ao ChatGPT ou ao Claude. Provavelmente veio uma lista de doze exercícios, quatro séries cada, sem perguntar em que academia o aluno treina, quantos dias ele tem, ou se o ombro dele dói. Bonito de ler, inútil de aplicar.

![IA Genérica vs FitCoach Pro](assets/ai-vs-fitcoach.jpg)

Isto aqui muda o comportamento do assistente. É um conjunto de instruções e ferramentas que você instala uma vez e que faz a inteligência artificial trabalhar do seu jeito: **perguntar antes de prescrever, escolher exercício pelo equipamento que existe de verdade, conferir o volume por grupo muscular, e admitir quando não sabe.**

Três coisas que ele passa a fazer e que nenhum chat comum faz:

**Ele se recusa a prescrever sem anamnese.** Peça um programa sem informar dias, equipamento, histórico e lesões, e ele pergunta primeiro. Chato? É. É também o motivo de o plano servir para o aluno real em vez de para um aluno imaginário.

**Ele não faz as contas de cabeça.** Calorias, macros, soma de séries — tudo isso vem de programas de computador testados que vêm junto, não da "cabeça" da IA. Isso importa porque **inteligência artificial erra conta com uma cara de quem acertou**, e você não tem como perceber olhando.

**Ele diz quando não tem dado suficiente.** Em vez de inventar um número, ele responde coisas como: *"ainda não dá para calcular seu gasto real — são 6 dias de alimentação registrada e o cálculo precisa de 10."* Parece limitação. É o contrário: é a única forma de você confiar nos números que ele dá.

### O que ele nunca faz

Ele não é o responsável técnico. **Quem prescreve é você.** Ele não diagnostica, não lê exame, não libera ninguém para treinar e não substitui nutricionista. E, apesar de tudo acima, **ele ainda pode errar** — por isso você confere tudo antes de mandar para o aluno. Leia o [`DISCLAIMER.pt-BR.md`](DISCLAIMER.pt-BR.md) uma vez, com calma.

---

## 2. Escolha o seu caminho

Existem três formas de usar. Escolha uma — não precisa das três.

| | **ChatGPT** | **Claude** | **Claude Code** |
| :--- | :--- | :--- | :--- |
| Dificuldade | Fácil | Fácil | Precisa de terminal |
| Precisa instalar programa? | Não | Não | Sim |
| Precisa de plano pago? | Sim | Sim | Sim |
| Faz as contas sozinho? | Às vezes | Quase sempre | Sempre |
| Guarda os dados do aluno | Você anexa os arquivos | Você anexa os arquivos | No seu computador, sozinho |
| Gera o painel de gráficos | Não | Não | Sim |

**Recomendação honesta:** comece pelo **Claude**. É onde as instruções foram escritas e onde mais coisa funciona sem esforço. Se você já paga ChatGPT e não quer trocar, o caminho do ChatGPT resolve a maior parte.

**Claude Code** é para quem se sente confortável digitando comandos. Ele é o único que faz tudo — incluindo o painel de gráficos e o cálculo garantido. Se você tem um sobrinho que "mexe com computador", é aí que ele ajuda em vinte minutos.

---

## 3. Baixar os arquivos

![Guia de Instalação Rápida](assets/quickstart-guide.jpg)

Vale para qualquer caminho.

1. Abra **https://github.com/danilogj/fitcoach-pro**
2. Clique no botão verde escrito **`Code`**
3. Clique em **`Download ZIP`**
4. O arquivo cai na sua pasta de Downloads. **Clique duas vezes nele** para descompactar — no Windows, clique com o botão direito e escolha "Extrair tudo"

Você vai ver uma pasta chamada `fitcoach-pro-main` com várias pastas dentro. As que interessam:

```
claude/
   fitcoach-pro-pt-BR/    ← a versão em português
gpt/
   pt-BR/                 ← para o ChatGPT, em português
```

Não precisa entender o resto.

---

## 4. Instalar no Claude

1. Entre em **claude.ai** e faça login
2. Clique na sua foto (canto inferior esquerdo) e vá em **Settings** → procure por **Capabilities** ou **Skills**
3. Procure a opção de **enviar uma skill** (*Upload skill*)
4. Ele pede um arquivo `.zip`. Você precisa compactar **a pasta `fitcoach-pro-pt-BR`** (aquela de dentro da pasta `claude`):
   - **Windows:** clique com o botão direito na pasta → *Enviar para* → *Pasta compactada*
   - **Mac:** clique com o botão direito na pasta → *Comprimir*
5. Envie o `.zip` que apareceu
6. Confirme que a skill aparece na lista, ativada

> A interface do Claude muda de tempos em tempos. Se os nomes dos menus estiverem diferentes, procure por **Skills** nas configurações — é sempre por ali.

### Testar se funcionou

Abra uma conversa nova e escreva exatamente isto:

> anamnese para aluno novo

**Funcionou** se a resposta começar com perguntas de triagem de saúde — dor no peito, tontura, medicação, gravidez.
**Não funcionou** se ele já sair montando um treino. Nesse caso a skill não está ativa; confira o passo 6.

---

## 5. Instalar no ChatGPT

Aqui você vai montar um "GPT personalizado" — é uma versão do ChatGPT com as instruções já dentro.

1. Entre em **chatgpt.com** e faça login
2. No menu lateral, clique em **Explorar GPTs** → **Criar** (botão no canto superior direito)
3. Clique na aba **Configure** (ou *Configurar*)
4. Preencha:
   - **Name:** `FitCoach Pro`
   - **Description:** `Assistente técnico de prescrição de treino e nutrição`
5. **Instructions** — este é o passo mais importante:
   - Na pasta que você baixou, abra `gpt` → `pt-BR` → `instructions.md`
   - Abra o arquivo com o Bloco de Notas (Windows) ou TextEdit (Mac)
   - Selecione tudo (Ctrl+A ou Cmd+A), copie (Ctrl+C ou Cmd+C)
   - Cole no campo **Instructions**
6. **Conversation starters** — abra `conversation-starters.md` da mesma pasta e copie as quatro linhas, uma em cada campo
7. **Knowledge** — clique em *Upload files* e envie **todos os arquivos** de dentro de `gpt/pt-BR/knowledge/`. São 19 arquivos; selecione todos de uma vez
8. **Capabilities** — deixe marcado apenas **Code Interpreter & Data Analysis**. Desmarque navegação na web e geração de imagem: aqui elas só atrapalham
9. Clique em **Create** / **Salvar** e escolha se fica só para você

### Um aviso honesto sobre o ChatGPT

Os programas que fazem as contas estão entre os arquivos que você enviou, mas o ChatGPT nem sempre consegue executá-los. **Quando ele não conseguir, ele foi instruído a dizer isso e dar faixas em vez de números exatos** — "manutenção por volta de 2.200 a 2.400 kcal" em vez de "2.273 kcal".

Se você quiser garantir o cálculo numa conversa específica, anexe o arquivo `cli.py` e o `metrics.py` direto no chat e peça: *"roda o cálculo usando esses arquivos"*.

No Claude isso costuma funcionar sozinho. É a razão da recomendação.

---

## 6. Seu primeiro aluno, do começo ao fim

![Fluxo de Trabalho do Personal Trainer](assets/trainer-workflow.jpg)

Aqui está uma conversa real, do jeito que acontece. **O que você digita está em negrito.**

---

**> tenho um aluno novo, quero começar a anamnese**

Ele responde com as sete perguntas de triagem de saúde. Você faz as perguntas ao aluno e traz as respostas.

---

**> todas as respostas foram não. Homem, 34 anos, 1,75m, 92 kg. Quer emagrecer. Nunca treinou de forma consistente. Consegue 3 dias, uma hora por sessão. A academia tem halteres até 40kg, barra, banco, polia alta e baixa, leg press, extensora, flexora e barra fixa. Trabalha sentado, dorme 6 horas.**

Ele classifica o aluno como iniciante, monta a divisão de três dias, escolhe os exercícios pelo equipamento que você listou, confere o volume por grupo muscular e apresenta o programa. Também vai apontar o sono de 6 horas — porque isso muda a prescrição.

---

**> o que falta para eu fechar isso?**

Ele diz o que estimou e o que você precisa conferir: a carga inicial de cada exercício, se os halteres realmente chegam a 40 kg, o alvo calórico.

---

**> monta o alvo nutricional dele**

Ele calcula (ou pede os dados que faltam) e entrega calorias e macros como faixa, não como número mágico.

---

**> escreve a ficha para ele levar na academia**

Você recebe a ficha pronta.

**É só isso.** Você conversa em português normal. Não existe comando decorado.

---

## 7. A rotina de cada semana

![Painel de Volume e Diário no Celular](assets/dashboard-mobile-preview.jpg)

**Uma vez por semana, por aluno:**

> **> check-in do João. Fez 3 de 3 treinos, recuperação boa, subiu carga no supino e no leg press. Peso médio da semana: 91,2 kg, semana passada 91,8.**

Ele devolve diagnóstico e **um ajuste específico** — não uma lista de sugestões.

**Se o aluno usa relógio ou aplicativo** (Samsung Health, Garmin, Apple Saúde, Strava), você pode exportar os dados dele e o assistente lê tudo de uma vez: peso, passos, sono, batimentos. Está explicado no guia técnico; peça a alguém para configurar uma vez e depois é só arrastar o arquivo.

**A cada 8 semanas:**

> **> fechou o bloco do João. Analisa e monta o próximo.**

---

## 8. Por que ele às vezes se recusa a responder

Você vai encontrar respostas assim:

> Ainda não dá para medir o gasto real dele — são 6 dias de alimentação registrada e o cálculo precisa de 10.

> Preciso de pelo menos 14 dias de pesagem para calcular a tendência. Com 5 dias, o que a balança mostra é água e sal, não gordura.

**Isso não é defeito.** É a diferença entre esta ferramenta e um chat comum. Um chat comum daria um número — e o número estaria errado, com aparência de certo, e você repassaria para o aluno.

Quando aparecer, a resposta certa é: registrar mais alguns dias, ou trabalhar com a estimativa **dizendo ao aluno que é estimativa**.

---

## 9. Quando der problema

| O que acontece | O que fazer |
| :--- | :--- |
| Ele monta treino sem fazer anamnese | A skill não está ativa. No Claude, confira as configurações. No ChatGPT, confirme que você colou o texto no campo *Instructions* |
| Ele dá números com muitas casas decimais ("2.347,5 kcal") | Peça: *"esse número saiu das ferramentas ou você calculou?"* Se ele calculou, peça a faixa |
| Ele responde em inglês | Escreva em português e peça: *"responde em português"*. Ele se ajusta |
| Ele esqueceu o que combinamos antes | Conversas longas perdem o começo. Comece uma conversa nova e anexe o arquivo do aluno |
| Ele prescreve um exercício que a academia não tem | O equipamento não chegou até ele. Repita a lista do que existe e peça para refazer |
| Ele sugere algo que você sabe que está errado | **Você tem razão até prova em contrário.** Diga que está errado e por quê — ele foi instruído a corrigir, não a se defender |

---

## 10. Palavras que vão aparecer

| Termo | O que quer dizer |
| :--- | :--- |
| **RIR** | Quantas repetições ainda dariam ao encerrar a série. RIR 2 = parou faltando duas |
| **Série válida** | Série levada perto da falha. Aquecimento não conta |
| **Volume** | Quantas séries válidas por grupo muscular na semana. É a conta que mais decide resultado |
| **MEV / MRV** | O mínimo que faz efeito e o máximo que dá para recuperar, por músculo |
| **Deload** | Semana de volume reduzido, carga mantida. Recuperação programada, não descanso |
| **Duplo critério** | Só sobe carga quando fecha o topo das repetições em todas as séries |
| **TDEE** | Quanto a pessoa gasta por dia. A fórmula chuta; com dados registrados dá para medir |
| **TMB** | Gasto do corpo em repouso absoluto |
| **NEAT** | Gasto do movimento fora do treino — andar, ficar em pé. É a maior fonte de erro do cálculo |
| **EMA** | Média que suaviza o peso diário e revela a tendência real |
| **ACWR** | Carga dos últimos 7 dias comparada com a dos últimos 28. Acima de 1,5 é onde lesão aparece |
| **Log** | Registro de tudo: cargas, peso, sono, alimentação |
| **Skill** | O pacote de instruções que você instalou |

---

## 11. Antes de mandar qualquer coisa para o aluno

Uma última vez, porque é o que importa:

**Leia o que ele escreveu.** Todo exercício, toda carga, toda conta. Você conhece seu aluno; a ferramenta conhece o que você contou sobre ele.

Ela existe para você gastar seu tempo pensando na decisão em vez de somando série e dividindo caloria. Não existe para decidir no seu lugar — e, se algo der errado com um aluno, quem responde é o seu registro profissional, não este repositório.

---

**Travou em algum passo?** Abra uma issue em https://github.com/danilogj/fitcoach-pro/issues dizendo exatamente onde parou. Guia que trava é guia mal escrito.
