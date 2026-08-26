# Entregáveis — ficha, relatório e comunicação

> **Palavras-chave:** ficha de treino, diário de treino, app do aluno, ficha html, relatório de evolução, apresentar resultado, mensagem para o aluno, exportar log, template, entrega.

O que o PT entrega é metade do valor percebido. Prescrição correta em PDF ilegível vira aluno que não executa.

---

## 1. Ficha de treino — o documento de bolso

O aluno usa isso em pé, com o celular na mão, entre séries. Restrições reais:

- **Uma sessão por tela.** Ele não navega entre abas com a mão suada.
- **Carga e repetições da última vez visíveis** ao lado do campo de hoje. Sem isso não existe progressão — ele não lembra.
- Prescrição de série, faixa de reps, RIR e descanso em cada linha.
- Dica de execução curta só nos exercícios em que ela muda o resultado. Dica em todos os exercícios não é lida em nenhum.
- Registro série a série, não "carga do dia".

### Template incluso

`assets/ficha-aluno.template.html` — página única, offline, guarda o registro no próprio celular e exporta o log em Markdown ao fim da semana. Funciona aberta como arquivo local, hospedada, ou publicada como Artifact (nesse caso ganha persistência entre aparelhos).

**Para preencher o template, substitua apenas os blocos marcados:**

| Marcador | O que colocar |
| :--- | :--- |
| `{{ALUNO}}` | Nome do aluno, aparece no cabeçalho, no título e no export |
| `{{SLUG}}` | Identificador sem espaço, ex.: `maria-silva`. Isola o registro deste aluno no navegador |
| `{{SUBTITULO}}` | Ex.: `Upper / Lower · bloco de 8 semanas` |
| `{{RESUMO_ALUNO}}` | Uma linha de perfil que vai no topo do log exportado, ex.: `Mulher, 34 anos, 62 kg → meta 58 kg · perda de gordura` |
| `/* {{PROGRAMA}} */` | O array `PROGRAMA` com as sessões — esquema abaixo |
| `{{INICIO}}` | Segunda-feira da semana 1, formato `AAAA-MM-DD` |
| `{{TOTAL_SEMANAS}}` | Número de semanas do bloco |
| `{{ENTRADA_ATE}}` | Última semana da fase de entrada (0 desliga a fase) |
| `{{DELOAD_EM}}` | Semana de deload (0 desliga) |
| `/* {{DIAS}} */` | Mapa dia-da-semana → índice da sessão |
| `<!-- {{REGRAS}} -->` | As regras do bloco que valem mais que a escolha dos exercícios |
| `{{PROFISSIONAL}}` e `{{CREF}}` | Nome e registro do personal trainer, no rodapé. **Não remova** — é o que deixa claro ao aluno quem prescreveu e revisou |
| `<!-- {{METAS}} -->` | Metas nutricionais do aluno, pares `<dt>`/`<dd>`. Remova o bloco inteiro se não houver |
| `/* {{CABECALHO_EXPORT}} */` | Cabeçalho do log exportado — já monta sozinho a partir de `{{ALUNO}}` e `{{RESUMO_ALUNO}}` |

Antes de preencher, passe o programa por `python3 tools/cli.py volume check --program ARQUIVO.json` — a ficha é o último lugar onde você quer descobrir que a semana tem 4 séries de peito e nenhum empurrar vertical.

Esquema de cada exercício no `PROGRAMA`:

```js
{
  n: "Supino reto com barra",   // nome
  s: 4,                          // séries no volume cheio
  r: "6-8",                      // faixa de reps (ou "45-60 s" em isometria)
  rir: "1-2",                    // RIR alvo — string vazia em isometria e peso corporal
  t: "hold",                     // "hold" = RIR âmbar (segura) · "go" = RIR verde (pode falhar)
  side: "/lado",                 // opcional, para unilateral
  f: "pc",                       // opcional: "pc" = peso corporal (sem campo de carga)
                                 //           "tempo" = isometria (sem campo de reps)
  d: 150,                        // descanso em segundos, para o cronômetro
  dl: "2-3 min",                 // descanso como texto
  ss: true,                      // opcional, marca supersérie com o item seguinte
  cue: "Rampa antes: 50% · 70% · 85%."   // opcional, aceita HTML simples
}
```

**Antes de entregar, confira:** o `PROGRAMA` bate com o `programa.md` do aluno, o `INICIO` é uma segunda-feira, e os exercícios com `f: "pc"` realmente não têm carga externa (campo de carga em exercício de peso corporal é o erro que o aluno reporta primeiro).

### Se a ficha for publicada como Artifact — regra que evita perda de dados

A página grava o registro **dentro do próprio HTML**, no bloco `<script id="estado-inicial">`. A cópia local do PT fica desatualizada toda vez que o aluno treina.

Antes de qualquer edição e republicação:

1. Buscar a versão publicada
2. Extrair o conteúdo de `<script id="estado-inicial">`
3. Colar por cima do bloco correspondente na cópia local
4. Só então aplicar as edições e republicar

Publicar sem esse passo **apaga o histórico inteiro do aluno**. Um conflito na publicação significa que ele salvou no meio da edição — mescle e republique, nunca force.

---

## 2. O dashboard

```
python3 tools/cli.py --client alunos/<nome> dashboard --name "Maria Silva" \
    --goal loss --target-kg 62
```

Gera um único HTML autocontido — sem CDN, sem JavaScript, sem build. Abre offline, sobrevive a ser enviado por e-mail e continua funcionando daqui a cinco anos.

O que mostra, quando o dado permite: a tendência de peso com as pesagens diárias atrás e a linha da meta, a taxa de variação com seu veredito de segurança, o gasto medido, o total de séries por semana, **as séries diretas por músculo contra os limiares daquele músculo**, a carga aguda:crônica, sono, passos e a progressão de carga nos exercícios mais treinados.

**O gráfico por músculo é o primeiro a olhar.** Um total de 60 séries na semana pode ser quatro músculos ou doze; só esse gráfico diz qual. Músculo abaixo do volume mínimo efetivo ou acima do máximo recuperável tem o rótulo destacado, então um grupo zerado — o erro de programação mais comum — aparece de imediato em vez de ficar escondido atrás de um total saudável.

**Ele nunca inventa uma seção.** O que não conseguir calcular vai para um bloco "Not shown yet" nomeando o dado que falta: *"Measured expenditure: only 4 days with logged intake in the last 28; need at least 10."* Entregue isso ao profissional como o motivo para registrar mais, não como defeito.

Regenere depois de cada importação ou check-in — ele lê o log na hora de renderizar e não se atualiza sozinho.

## 3. Relatório de evolução

Entregue a cada 4 semanas, e sempre no fim do bloco. Estrutura em cinco partes, nesta ordem:

1. **O que mudou** — duas ou três linhas, números concretos. Carga que subiu, medida que mudou, aderência.
2. **Números** — tabela comparando linha de base, mês anterior e hoje: peso médio, cintura, cargas dos principais exercícios, aderência em porcentagem.
3. **O que explica** — a leitura do PT sobre por que mudou (ou por que não).
4. **O que muda no próximo bloco** — específico, com o motivo de cada mudança.
5. **O que preciso de você** — a ação que depende do aluno. Uma só, no máximo duas.

**Regras de redação:** número antes de adjetivo. "Seu supino saiu de 60 para 72,5 kg em 8 semanas" comunica mais que "sua evolução foi excelente". Se o resultado foi ruim, diga na primeira linha — o aluno já sabe, e esconder custa a confiança que sustenta a renovação.

**A aderência entra sempre no relatório.** É o dado que devolve a responsabilidade ao aluno sem acusação: 22 de 32 sessões é uma frase, não um julgamento.

---

## 4. Mensagens ao aluno

O PT vai pedir que você escreva. Três regras:

- **Uma mensagem, um assunto.** Ajuste de carga e ajuste de dieta na mesma mensagem viram nenhum dos dois.
- **Diga a ação, não a teoria.** "Sobe o supino para 65 kg nesta semana" — o porquê vem depois, em uma linha, se vier.
- **Sem infantilização e sem hype.** Adulto pagando por serviço técnico não precisa de emoji de fogo nem de "vamos com tudo".

Quando o aluno tiver furado semanas seguidas, a mensagem que funciona não cobra: reduz o pedido. Proponha a versão curta da sessão e uma meta de duas sessões na semana. Cobrança produz sumiço; redução de atrito produz retorno.

---

## 5. Estrutura de arquivos do aluno

```
alunos/<nome-do-aluno>/
  anamnese.md    ← assets/modelo-anamnese.md
  programa.md    ← assets/modelo-programa.md
  log.md         ← assets/modelo-log.md
  ficha.html     ← assets/ficha-aluno.template.html preenchido
  relatorios/
    2026-09.md
```

Mantenha `programa.md` como fonte da verdade. A ficha é uma **renderização** dele — quando os dois divergirem, o `programa.md` vence e a ficha é regerada.
