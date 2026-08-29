# Guia do Personal Trainer — FitCoach Pro

### *A Engenharia de Prescrição que Coloca a sua Consultoria 5 Anos à Frente do Mercado*

**Para quem nunca instalou nada parecido e quer atender melhor seus alunos.** Não presume que você saiba o que é terminal, programação ou linha de comando. Você vai usar a **interface de chat normal** do Claude ou ChatGPT.

English version: [`TRAINER-GUIDE.md`](TRAINER-GUIDE.md)

---

## 1. O que é isto e por que você precisa disso

Enquanto 95% dos personais perdem horas no Excel somando séries de cabeça ou entregam PDFs genéricos de IA que qualquer aluno percebe... você passa a prescrever com **precisão biomecânica cirúrgica, cálculo metabólico determinístico e entrega digital de elite**.

![IA Genérica vs FitCoach Pro](assets/ai-vs-fitcoach.jpg)

### O que o FitCoach Pro faz por você na prática:

```
┌─────────────────────────────────────────────────┬─────────────────────────────────────────────────┐
│ ❌ O PERSONAL TRADICIONAL                       │ ✅ VOCÊ COM FITCOACH PRO                        │
├─────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ 40 minutos somando séries e calorias no papel   │ Prescrição e auditoria de volume em 2 minutos   │
│ Ficha em PDF estático que o aluno esquece       │ Diário interativo no celular com cronômetro     │
│ Chuta calorias e percentuais mágicos            │ Matemática determinística baseada na literatura │
│ Não sabe se o volume está em excesso ou falta   │ Auditoria em tempo real de MEV / MAV / MRV      │
│ Dificuldade para cobrar mais na consultoria     │ Consultoria de Alto Valor Percebido             │
└─────────────────────────────────────────────────┴─────────────────────────────────────────────────┘
```

Três coisas que ele faz direto no seu chat:

1. **Recusa-se a prescrever sem anamnese:** Exige triagem de saúde, rotina, lesões e inventário real da academia do aluno.
2. **Cálculos matemáticos sem alucinação:** Calorias, macros, soma de séries válidas e progressão vêm de algoritmos testados, não de "chutes" da IA.
3. **Auditoria de volume e dor articular:** Avisa se o peitoral está abaixo da Dose Mínima Efetiva (MEV) ou se a carga na coluna está excessiva, sugerindo substituições biomecânicas imediatas.

---

## 2. Escolha o seu caminho

Você usa direto no seu aplicativo ou navegador favorito:

| | **Claude.ai (Recomendado)** | **ChatGPT (Custom GPT)** |
| :--- | :--- | :--- |
| **Dificuldade** | Super Fácil (Chat normal) | Super Fácil (Chat normal) |
| **Precisa de terminal?** | **NÃO** | **NÃO** |
| **Gráficos e Painel** | **Sim** (Artifacts interativos e barras no chat) | **Sim** (Imagens via Code Interpreter e barras) |
| **Ficha para o Aluno** | **Sim** (Gera o app `.html` para mandar no WhatsApp) | **Sim** (Gera o arquivo para download) |
| **Mensagens prontas** | **Sim** (Bloco pronto para copiar para o WhatsApp) | **Sim** (Bloco pronto para copiar para o WhatsApp) |

> 💡 **Recomendação:** Se você já usa o Claude, a experiência com **Artifacts** é perfeita porque ele abre a ficha interativa ao lado do chat para você baixar e mandar para o aluno. Se você usa o ChatGPT Plus, o Custom GPT funciona tão bem quanto.

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
   fitcoach-pro/          ← a skill oficial
gpt/                      ← arquivos para o ChatGPT (instructions.md e knowledge)
```

> **Nota:** As instruções internas e cálculos da skill são estruturados em inglês para que o modelo de inteligência artificial execute o raciocínio matemático e biomecânico com máxima precisão. Mas **a IA conversa com você 100% em português** automaticamente.

---

## 4. Instalar no Claude

1. Entre em **claude.ai** e faça login
2. Clique na sua foto (canto inferior esquerdo) e vá em **Settings** → procure por **Capabilities** ou **Skills**
3. Procure a opção de **enviar uma skill** (*Upload skill*)
4. Ele pede um arquivo `.zip`. Você precisa compactar **a pasta `fitcoach-pro`** (aquela de dentro da pasta `claude`):
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
   - Na pasta que você baixou, abra `gpt` → `instructions.md`
   - Abra o arquivo com o Bloco de Notas (Windows) ou TextEdit (Mac)
   - Selecione tudo (Ctrl+A ou Cmd+A), copie (Ctrl+C ou Cmd+C)
   - Cole no campo **Instructions**
6. **Conversation starters** — abra `conversation-starters.md` da mesma pasta `gpt` e copie as quatro linhas, uma em cada campo
7. **Knowledge** — clique em *Upload files* e envie **todos os arquivos** de dentro de `gpt/knowledge/`. Selecione todos de uma vez
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

## 7. Como você visualiza o painel e entrega a ficha ao aluno (100% no Chat)

![Painel de Volume e Diário no Celular](assets/dashboard-mobile-preview.jpg)

Você não precisa de terminal nem de programação para ver gráficos ou entregar o aplicativo ao aluno:

### 1. Auditoria Visual no Próprio Chat
Quando você pede *"audite o volume do João"*, a IA desenha barras visuais diretamente na conversa para você bater o olho e diagnosticar em 3 segundos:

```text
📊 AUDITORIA DE VOLUME — JOÃO
Peitoral:      ████████████░░░░  12/16 séries  [✅ MAV Ótimo]
Dorsal:        ██████████████░░  14/18 séries  [✅ MAV Ótimo]
Isquiotibiais: ████████░░░░░░░░   8/14 séries  [🟡 MEV Baixo]
```

### 2. Baixar e Enviar a Ficha pelo WhatsApp
* **No Claude:** Ao pedir a ficha, o Claude abre a janela lateral (**Artifact**) com o app pronto. Clique no botão de **Download** (baixa o arquivo `ficha-joao.html`) e arraste no WhatsApp do aluno. O aluno toca no arquivo e ele abre no celular como um app offline com cronômetro e histórico.
* **No ChatGPT:** O ChatGPT gera o arquivo para download direto na conversa.

### 3. Mensagem Pronta para o Aluno
Toda análise gera um bloco formatado para você apenas copiar e mandar:

> 📲 **Copie e cole no WhatsApp do aluno:**
> *"Fala João! Seu treino do novo bloco está pronto com foco em dorsal e peitoral. Dá uma olhada na ficha e me avisa qualquer dúvida nas cargas iniciais. Bora pra cima! 💪"*

---

## 8. A rotina de cada semana

**Uma vez por semana, por aluno:**

> **> check-in do João. Fez 3 de 3 treinos, recuperação boa, subiu carga no supino e no leg press. Peso médio da semana: 91,2 kg, semana passada 91,8.**

Ele devolve diagnóstico e **um ajuste específico** — não uma lista de sugestões.

**Se o aluno usa relógio ou aplicativo** (Samsung Health, Garmin, Apple Saúde, Strava), você pode exportar os dados dele e o assistente lê tudo de uma vez: peso, passos, sono, batimentos. Está explicado no guia técnico; peça a alguém para configurar uma vez e depois é só arrastar o arquivo.

**A cada 8 semanas:**

> **> fechou o bloco do João. Analisa e monta o próximo.**

---

## 9. Por que ele às vezes se recusa a responder

Você vai encontrar respostas assim:

> Ainda não dá para medir o gasto real dele — são 6 dias de alimentação registrada e o cálculo precisa de 10.

> Preciso de pelo menos 14 dias de pesagem para calcular a tendência. Com 5 dias, o que a balança mostra é água e sal, não gordura.

**Isso não é defeito.** É a diferença entre esta ferramenta e um chat comum. Um chat comum daria um número — e o número estaria errado, com aparência de certo, e você repassaria para o aluno.

Quando aparecer, a resposta certa é: registrar mais alguns dias, ou trabalhar com a estimativa **dizendo ao aluno que é estimativa**.

---

## 10. Quando der problema

| O que acontece | O que fazer |
| :--- | :--- |
| Ele monta treino sem fazer anamnese | A skill não está ativa. No Claude, confira as configurações. No ChatGPT, confirme que você colou o texto no campo *Instructions* |
| Ele dá números com muitas casas decimais ("2.347,5 kcal") | Peça: *"esse número saiu das ferramentas ou você calculou?"* Se ele calculou, peça a faixa |
| Ele responde em inglês | Escreva em português e peça: *"responde em português"*. Ele se ajusta |
| Ele esqueceu o que combinamos antes | Conversas longas perdem o começo. Comece uma conversa nova e anexe o arquivo do aluno |
| Ele prescreve um exercício que a academia não tem | O equipamento não chegou até ele. Repita a lista do que existe e peça para refazer |
| Ele sugere algo que você sabe que está errado | **Você tem razão até prova em contrário.** Diga que está errado e por quê — ele foi instruído a corrigir, não a se defender |

---

## 11. Palavras que vão aparecer

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

## 12. Antes de mandar qualquer coisa para o aluno

Uma última vez, porque é o que importa:

**Leia o que ele escreveu.** Todo exercício, toda carga, toda conta. Você conhece seu aluno; a ferramenta conhece o que você contou sobre ele.

Ela existe para você gastar seu tempo pensando na decisão em vez de somando série e dividindo caloria. Não existe para decidir no seu lugar — e, se algo der errado com um aluno, quem responde é o seu registro profissional, não este repositório.

---

**Travou em algum passo?** Abra uma issue em https://github.com/danilogj/fitcoach-pro/issues dizendo exatamente onde parou. Guia que trava é guia mal escrito.
