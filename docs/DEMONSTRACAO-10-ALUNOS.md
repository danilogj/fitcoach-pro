# 🌟 Demonstração Prática — Carteira de 10 Alunos Fictícios

> **Guia para personal trainers, consultores e demonstrações comerciais.**  
> Esta pasta contém **10 casos clínicos e práticos 100% realistas**, prontos para você testar no chat, abrir no celular ou apresentar para colegas de profissão.

---

## 👥 A Carteira de Alunos Disponível

Os dados estão prontos em [`examples/carteira-10-alunos/`](../examples/carteira-10-alunos/):

```
examples/carteira-10-alunos/
├── joao-silva/          ← Emagrecimento · Hérnia de disco L4-L5 (Zero carga axial)
├── maria-santos/        ← Hipertrofia Inferiores · Médica Plantonista (Sessões de 45 min)
├── carlos-mendes/       ← Recomposição · Pré-diabetes & Cardio Zona 2 (Glicose/GLUT4)
├── fernanda-lima/       ← Hipertrofia · Iniciante Total · Academia de Prédio (Só halteres e polia)
├── rodrigo-alves/       ← Quebra de Platô em Supino · Avançado · Upper/Lower 4x
├── juliana-costa/       ← Menopausa/Osteopenia · Condromalácia Patelar Grau 2 (Proteção de Joelho)
├── lucas-pereira/       ← Maratonista Amador · Treinamento Concorrente & Economia de Corrida
├── beatriz-rocha/       ← Pós-Parto (6 meses) · Diástase Abdominal & Assoalho Pélvico
├── gabriel-souza/       ← Hipertenso Controlado · Gordura Visceral · RIR >= 2 (Sem Valsalva)
└── camila-martins/      ← Ex-Crossfit · Bursite/Impacto de Ombro · Sem overhead press
```

---

## 📂 O que cada pasta de aluno contém:

Cada um dos 10 alunos possui um ecossistema completo gerado:

1. **`intake.md` (Anamnese Real):** Triagem médica PAR-Q+, limitações articulares, agenda semanal e inventário real da academia.
2. **`program.md` (Prescrição do Bloco):** Bloco de 8 semanas com divisão, exercícios selecionados, séries, repetições, RIR e tempo de descanso.
3. **`log.jsonl` (Histórico de 28 dias):** 28 dias de registros reais de balança, passos, sono e treinos executados.
4. **`estado.md` (Arquivo de Memória / State File):** O arquivo de texto compacto (<3 KB) que o personal anexa no chat para recuperar toda a história do aluno em 1 segundo.
5. **`sheet.html` (Ficha Interativa no Celular):** O aplicativo web que o aluno abre no celular (offline) com cronômetro de descanso, histórico de cargas e botões táteis.
6. **`dashboard.html` (Painel Visual Completo):** Painel gráfico com tendência de peso (EMA), volume semanal por músculo vs MEV/MRV e histórico de cargas.

---

## 🧪 3 Formas de Mostrar Isso na Prática para um Personal:

### 1. Testar o Check-in no Chat (Claude ou ChatGPT)
Abra uma conversa limpa no Claude ou ChatGPT e faça o seguinte teste:

> **Você digita:**
> *"Estou anexando o arquivo de estado do meu aluno João Silva. Ele me mandou o check-in da semana 4: treinou 3 de 3 dias, peso médio 91.2 kg, aumentou carga no leg press e no supino com halteres. Analise o progresso dele e me dê o diagnóstico da semana e a mensagem para enviar no WhatsApp."*
>
> *(Anexe o arquivo `examples/carteira-10-alunos/joao-silva/estado.md`)*

**O que a IA faz:**
* Lê instantaneamente as restrições da hérnia L4-L5.
* Analisa a taxa de perda de gordura (-0.7 kg/sem) com base científica.
* Entrega o diagnóstico preciso e o cartão pronto para colar no WhatsApp do João.

---

### 2. Abrir a Ficha no Celular (`sheet.html`)
1. Entre na pasta `examples/carteira-10-alunos/maria-santos/`.
2. Dê um duplo-clique no arquivo `sheet.html` (abre no Chrome, Safari ou qualquer navegador).
3. Pressione `F12` e ative a **visualização mobile** (ícone de celular).
4. **Veja a mágica:** o personal vê o diário de treino com botões grandes, cronômetro de descanso funcional e histórico de cargas da semana anterior.

---

### 3. A Visão Panorâmica de Segunda-Feira (`cli.py cohort`)
Se você rodar no terminal para demonstrar a gestão de carteira:

```bash
python3 claude/fitcoach-pro/tools/cli.py cohort --root examples/carteira-10-alunos
```

**Resultado na Tela:**
```text
client             status       last    7d     trend    ACWR  what needs attention
----------------------------------------------------------------------------------
fernanda-lima      attention      0d     3   54.2 kg    1.00  weight wrong direction
lucas-pereira      attention      0d     3   68.0 kg    1.00  weight stalled
rodrigo-alves      attention      0d     3   78.9 kg    1.00  weight wrong direction
beatriz-rocha      ok             0d     3   65.0 kg    1.00  on plan
camila-martins     ok             0d     3   63.6 kg    1.00  on plan
carlos-mendes      ok             0d     3   87.3 kg    1.00  on plan
gabriel-souza      ok             0d     3   96.2 kg    1.00  on plan
joao-silva         ok             0d     3   91.6 kg    1.00  on plan
juliana-costa      ok             0d     3   66.2 kg    1.00  on plan
maria-santos       ok             0d     3   62.6 kg    1.00  on plan

10 clients: 3 attention · 7 ok
start with: fernanda-lima, lucas-pereira, rodrigo-alves
```

> **O que isso mostra ao personal:** Em vez de perder a manhã de segunda-feira checando 10 conversas diferentes, o sistema aponta exatamente os **3 alunos que precisam de ajuste prioritário** (quem estagnou ou quem está variando o peso fora da meta).
