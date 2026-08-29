# Metodologia BMAD — Arquitetura de Engenharia de Prescrição

> **BMAD (Behavioral & Multi-Agent Architecture for Development & Prescription)**  
> *Como o FitCoach Pro adapta a metodologia de desenvolvimento de software mais avançada para criar uma "Junta Técnica de Especialistas" dentro do seu chat.*

---

## 🏛️ 1. O que é a Metodologia BMAD?

No desenvolvimento de software profissional, a metodologia **BMAD** resolve o problema de qualidade dividindo a construção de um sistema em papéis especializados com **portões de qualidade (Quality Gates)** e **auditoria adversarial**:

* ❌ **O Chat de IA Comum (Monolítico):** Uma única instrução tenta triar a saúde, inventar exercícios, somar séries e formatar o texto ao mesmo tempo. O resultado é alucinação, esquecimento de lesões e números aproximados.
* ✅ **O FitCoach Pro com BMAD (Multi-Especialista):** O atendimento passa por um **pipeline sequencial de 5 agentes virtuais**, onde cada etapa possui critérios de aceitação estritos e uma etapa de **QA (Garantia de Qualidade)** que audita a prescrição antes de entregar ao personal.

---

## 👥 2. Os 5 Agentes do Pipeline FitCoach Pro

```
  ┌─────────────────────────────────────────────────────────────────────────────────┐
  │                           PIPELINE BMAD FITCOACH PRO                            │
  ├─────────────────────────────────────────────────────────────────────────────────┤
  │                                                                                 │
  │  📋 AGENTE 1: ANALISTA CLÍNICO & TRIAGEM (Intake Screener)                     │
  │     └─► Valida PAR-Q+, restrições articulares, status hormonal (AAS/TRT)        │
  │         e inventário real da academia. Se faltar dado, PAUSAR e perguntar.      │
  │                                                                                 │
  │  📐 AGENTE 2: ARQUITETO BIOMECÂNICO & CINÉTICO (Movement Architect)            │
  │     └─► Mapeia padrões motores, seleciona exercícios em comprimento             │
  │         alongado (LML) e elimina vetores de sobrecarga axial.                   │
  │                                                                                 │
  │  🧮 AGENTE 3: ENGENHEIRO METABÓLICO (Metabolic Engine)                         │
  │     └─► Executa a matemática determinística: TMB, TDEE, déficit/superávit       │
  │         e distribuição de macronutrientes sem chute.                            │
  │                                                                                 │
  │  🔍 AGENTE 4: AUDITOR ADVERSARIAL / QA (Safety & Volume Linter) ⚠️             │
  │     └─► Executa os testes de validação:                                         │
  │         ✔ Volume semanal está entre MEV e MRV?                                  │
  │         ✔ Aluno com dor no joelho recebeu agachamento profundo? (CORRIGIR)      │
  │         ✔ Aluno hormonizado recebeu séries <5 RM de alto impacto? (CORRIGIR)    │
  │         ✔ Todos os exercícios existem no inventário da academia? (CORRIGIR)     │
  │                                                                                 │
  │  📱 AGENTE 5: DESIGNER DE ENTREGA & EXPERIÊNCIA (UX & Delivery)                 │
  │     └─► Empacota a ficha interativa do celular (`sheet.html`) e redige          │
  │         o feedback empático e claro pronto para colar no WhatsApp.              │
  │                                                                                 │
  └─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛡️ 3. O Portão de Qualidade Adversarial (QA Gate)

O grande diferencial do BMAD é o **Agente 4 (Auditor QA)**. Ele atua como um "linter" de programação. Ele recebe o rascunho do treino e roda uma bateria de testes determinísticos:

### Tabela de Testes do QA Linter:

| Teste de QA | Regra de Verificação | Ação em Caso de Falha |
| :--- | :--- | :--- |
| **Teste 1: Inventário Físico** | O exercício prescrito consta na lista de equipamentos da academia? | **REJEITAR.** Substituir por variação compatível do catálogo. |
| **Teste 2: Faixa de Volume** | As séries válidas semanais estão entre MEV (Mínimo) e MRV (Máximo)? | **REJEITAR.** Ajustar número de séries para a faixa ótima (MAV). |
| **Teste 3: Carga Axial em Lesões** | Aluno com protusão/hérnia lombar recebeu agachamento livre ou terra? | **REJEITAR.** Substituir por exercício com suporte torácico. |
| **Teste 4: Proteção de Tendão (AAS)** | Aluno hormonizado recebeu séries de 1 a 5 RM com tranco articular? | **REJEITAR.** Subir repetições para 8–12 e exigir excêntrica de 3s. |
| **Teste 5: Balanço Agudo:Crônico** | O ACWR da semana passou de 1.5? | **ALERTA.** Sinalizar risco e sugerir redução de 20% no volume. |
| **Teste 6: Aritmética Calórica** | A soma de macros bate exatamente com a meta calórica? | **REJEITAR.** Recalcular usando o motor determinístico. |

---

## 💬 4. Como Usar o Pipeline no seu Chat

Você não precisa de comandos complexos. O assistente já executa esse pipeline internamente. Porém, se você quiser forçar uma revisão passo a passo em um caso de alta complexidade (ex: atleta de elite ou aluno com múltiplas lesões), basta digitar:

> **"FitCoach, execute o pipeline BMAD completo para este aluno: faça a triagem clínica, a arquitetura de treino, o cálculo metabólico e passe pelo auditor de QA antes de me entregar a ficha e a mensagem de WhatsApp."**

O assistente responderá mostrando o parecer de cada especialista e a aprovação final do QA.

---

## 🚀 5. Por que isso coloca sua consultoria em outro nível:

1. **Zero Erros Críticos:** Nenhuma restrição física é ignorada por esquecimento do modelo.
2. **Autoridade Científica Inabalável:** Cada decisão tem um parecer técnico justificado.
3. **Escala sem Perda de Qualidade:** Você atende 50 alunos mantendo o mesmo padrão de excelência de uma equipe multidisciplinar presencial.
