#!/usr/bin/env python3
"""Generate 10 realistic, clinically rich client showcase folders for FitCoach Pro."""
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

# Add tools to path
TOOLS_DIR = Path(__file__).resolve().parent.parent / "claude" / "fitcoach-pro" / "tools"
ASSETS_DIR = Path(__file__).resolve().parent.parent / "claude" / "fitcoach-pro" / "assets"
sys.path.insert(0, str(TOOLS_DIR))

import logstore
import dashboard as dash_mod
import metrics as m
import volume as vol

OUTPUT_DIR = Path(__file__).resolve().parent / "carteira-10-alunos"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TEMPLATE_HTML = (ASSETS_DIR / "client-sheet.template.html").read_text(encoding="utf-8")

CLIENTS = [
    {
        "slug": "joao-silva",
        "name": "João Silva",
        "age": 34,
        "sex": "male",
        "weight_start": 94.5,
        "weight_current": 91.2,
        "height_cm": 178,
        "goal": "loss",
        "profile": "Iniciante · Emagrecimento · Hérnia de disco L4-L5 (Sem carga axial na coluna)",
        "split": "Full Body 3x (Seg / Qua / Sex)",
        "summary": "Advogado, 34 anos. Sedentário há 5 anos, protrusão discal lombar L4-L5 assintomática com suporte. Foco: perda de gordura (-0.7 kg/sem) e fortalecimento do core com suporte torácico.",
        "status": "ok",
        "days_logged": 28,
        "exercises": [
            {"n": "Leg press 45", "s": 3, "r": "10-12", "rir": "2", "t": "hold", "d": 120, "dl": "2 min", "cue": "Pés médios, não arredondar a lombar no fundo."},
            {"n": "Chest-supported dumbbell row", "s": 3, "r": "10-12", "rir": "2", "t": "hold", "d": 90, "dl": "90 s", "cue": "Peito firme no banco inclinado a 30°."},
            {"n": "Dumbbell bench press", "s": 3, "r": "8-10", "rir": "2", "t": "hold", "d": 120, "dl": "2 min", "cue": "Escápulas retraídas e pés firmes no chão."},
            {"n": "Seated leg curl", "s": 3, "r": "12-15", "rir": "1-2", "t": "hold", "d": 90, "dl": "90 s", "cue": "Tronco inclinado à frente para maior alongamento."},
            {"n": "Cable lateral raise", "s": 3, "r": "12-15", "rir": "1-2", "t": "go", "d": 60, "dl": "60 s", "cue": "Polia na altura do joelho, plano escapular."},
            {"n": "Plank", "s": 3, "r": "45-60 s", "rir": "", "t": "hold", "f": "tempo", "d": 60, "dl": "60 s", "cue": "Glúteos e abdômen contraídos, sem hiperlordose."}
        ],
        "weight_series": [94.5 - (i * 0.12) + ((i % 3 - 1) * 0.15) for i in range(28)]
    },
    {
        "slug": "maria-santos",
        "name": "Dra. Maria Santos",
        "age": 29,
        "sex": "female",
        "weight_start": 63.8,
        "weight_current": 62.4,
        "height_cm": 165,
        "goal": "gain",
        "profile": "Intermediária · Hipertrofia de Glúteos/Inferiores · Plantonista (Sessões de 45 min)",
        "split": "Upper / Lower 4x (Seg / Ter / Qui / Sex)",
        "summary": "Médica emergencista, 29 anos. Rotina de plantões noturnos. Foco: hipertrofia de glúteos e quadríceps com treinos densos de 45 min e gestão de sono.",
        "status": "ok",
        "days_logged": 28,
        "exercises": [
            {"n": "Barbell hip thrust", "s": 4, "r": "8-10", "rir": "1-2", "t": "hold", "d": 120, "dl": "2 min", "cue": "Pausa de 1s no topo com retroversão pélvica."},
            {"n": "Bulgarian split squat", "s": 3, "r": "10-12", "side": "/lado", "rir": "1-2", "t": "hold", "d": 90, "dl": "90 s", "cue": "Tronco levemente inclinado para foco em glúteo."},
            {"n": "Seated leg curl", "s": 3, "r": "10-12", "rir": "1", "t": "go", "d": 75, "dl": "75 s", "cue": "Alongamento máximo na fase excêntrica."},
            {"n": "Leg extension", "s": 3, "r": "12-15", "rir": "1", "t": "go", "d": 75, "dl": "75 s", "cue": "Pausa de 1s na extensão completa."},
            {"n": "Standing calf raise", "s": 4, "r": "12-15", "rir": "1", "t": "go", "d": 60, "dl": "60 s", "cue": "Pausa de 2s no fundo para tirar o reflexo elástico."}
        ],
        "weight_series": [63.8 - (i * 0.05) + ((i % 4 - 2) * 0.1) for i in range(28)]
    },
    {
        "slug": "carlos-mendes",
        "name": "Carlos Mendes",
        "age": 42,
        "sex": "male",
        "weight_start": 89.2,
        "weight_current": 86.8,
        "height_cm": 176,
        "goal": "loss",
        "profile": "Iniciante/Intermediário · Recomposição Corporal · Pré-diabetes & Cardio Zona 2",
        "split": "Full Body 3x + 150 min Cardio Z2",
        "summary": "Empresário, 42 anos. Glicemia de jejum 108 mg/dL (resistência à insulina). Foco em captação de glicose muscular (GLUT4), perda de gordura visceral e saúde cardiovascular.",
        "status": "ok",
        "days_logged": 28,
        "exercises": [
            {"n": "Goblet squat", "s": 3, "r": "10-12", "rir": "2", "t": "hold", "d": 90, "dl": "90 s", "cue": "Halter junto ao peito, amplitude total controlada."},
            {"n": "Lat pulldown", "s": 3, "r": "10-12", "rir": "2", "t": "hold", "d": 90, "dl": "90 s", "cue": "Puxar a barra em direção à clavícula."},
            {"n": "Incline dumbbell bench press", "s": 3, "r": "10-12", "rir": "2", "t": "hold", "d": 90, "dl": "90 s", "cue": "Banco a 30°, cotovelos a 45° do tronco."},
            {"n": "Romanian deadlift (dumbbells)", "s": 3, "r": "10-12", "rir": "2", "t": "hold", "d": 90, "dl": "90 s", "cue": "Empurrar o quadril para trás, coluna neutra."},
            {"n": "Cable seated row", "s": 3, "r": "12-15", "rir": "2", "t": "hold", "d": 75, "dl": "75 s", "cue": "Pegada neutra, esmagar as escápulas atrás."}
        ],
        "weight_series": [89.2 - (i * 0.08) + ((i % 3 - 1) * 0.1) for i in range(28)]
    },
    {
        "slug": "fernanda-lima",
        "name": "Fernanda Lima",
        "age": 24,
        "sex": "female",
        "weight_start": 53.5,
        "weight_current": 54.2,
        "height_cm": 160,
        "goal": "gain",
        "profile": "Iniciante Total · Hipertrofia · Academia de Prédio (Apenas Halteres e Polia)",
        "split": "Full Body 3x (Adaptado para Maquinário Básico)",
        "summary": "Estudante universitária, 24 anos. Ectomorfa, dificuldade para ganhar peso. Treina no condomínio (apenas halteres de 1 a 20 kg e polia dupla). Foco: ganho de massa magra.",
        "status": "ok",
        "days_logged": 28,
        "exercises": [
            {"n": "Goblet squat", "s": 3, "r": "12-15", "rir": "1-2", "t": "hold", "d": 90, "dl": "90 s", "cue": "Segurar halter pesado na vertical."},
            {"n": "Romanian deadlift (dumbbells)", "s": 3, "r": "10-12", "rir": "1-2", "t": "hold", "d": 90, "dl": "90 s", "cue": "Foco na extensão de quadril com glúteo."},
            {"n": "Lat pulldown", "s": 3, "r": "10-12", "rir": "1-2", "t": "hold", "d": 75, "dl": "75 s", "cue": "Na polia do prédio, puxada aberta."},
            {"n": "Dumbbell bench press", "s": 3, "r": "10-12", "rir": "1-2", "t": "hold", "d": 75, "dl": "75 s", "cue": "No banco reto com halteres."},
            {"n": "Cable lateral raise", "s": 3, "r": "12-15", "rir": "1", "t": "go", "d": 60, "dl": "60 s", "cue": "Elevação unilateral na polia baixa."}
        ],
        "weight_series": [53.5 + (i * 0.03) + ((i % 2 - 1) * 0.08) for i in range(28)]
    },
    {
        "slug": "rodrigo-alves",
        "name": "Rodrigo Alves",
        "age": 38,
        "sex": "male",
        "weight_start": 78.5,
        "weight_current": 78.9,
        "height_cm": 175,
        "goal": "gain",
        "profile": "Avançado · Quebra de Platô em Supino · Upper / Lower 4x",
        "split": "Upper / Lower 4x (Periodização Ondulatória)",
        "summary": "Engenheiro de software, treina há 6 anos. Estagnado em 100 kg no supino reto. Foco: hipertrofia de peitoral superior e deltoides com variação de estímulo e microciclo de deload.",
        "status": "attention",
        "days_logged": 28,
        "exercises": [
            {"n": "Barbell bench press", "s": 4, "r": "5-6", "rir": "1-2", "t": "hold", "d": 180, "dl": "3 min", "cue": "Pausa de 1s no peito, leg drive ativo."},
            {"n": "Incline dumbbell bench press", "s": 3, "r": "8-10", "rir": "1", "t": "hold", "d": 120, "dl": "2 min", "cue": "Foco no feixe clavicular, banco a 30°."},
            {"n": "Barbell bent-over row", "s": 4, "r": "6-8", "rir": "1-2", "t": "hold", "d": 120, "dl": "2 min", "cue": "Tronco a 45°, puxar na direção do umbigo."},
            {"n": "Cable crossover (middle)", "s": 3, "r": "12-15", "rir": "0-1", "t": "go", "d": 75, "dl": "75 s", "cue": "Cruzar as mãos no final da contração."},
            {"n": "Triceps rope pushdown", "s": 3, "r": "10-12", "rir": "1", "t": "go", "d": 75, "dl": "75 s", "cue": "Abrir a corda no final da extensão."}
        ],
        "weight_series": [78.5 + (i * 0.015) + ((i % 3 - 1) * 0.1) for i in range(28)]
    },
    {
        "slug": "juliana-costa",
        "name": "Juliana Costa",
        "age": 48,
        "sex": "female",
        "weight_start": 67.2,
        "weight_current": 66.1,
        "height_cm": 162,
        "goal": "loss",
        "profile": "Menopausa / Osteopenia · Condromalácia Patelar Grau 2 (Proteção de Joelho)",
        "split": "Full Body 3x (Sem flexão profunda de joelho sob carga livre)",
        "summary": "Professora universitária, 48 anos. Osteopenia em colo de fêmur e dor patelar em agachamento profundo. Foco: estímulo osteogênico, hipertrofia de vasto medial e proteção articular.",
        "status": "ok",
        "days_logged": 28,
        "exercises": [
            {"n": "Leg press 45", "s": 3, "r": "10-12", "rir": "2", "t": "hold", "d": 120, "dl": "2 min", "cue": "Pés altos na plataforma, amplitude segura."},
            {"n": "Leg extension", "s": 3, "r": "12-15", "rir": "2", "t": "hold", "d": 90, "dl": "90 s", "cue": "Trabalhar apenas na faixa confortável de extensão."},
            {"n": "Romanian deadlift (dumbbells)", "s": 3, "r": "10-12", "rir": "2", "t": "hold", "d": 90, "dl": "90 s", "cue": "Foco em posterior e glúteo com joelhos fixos."},
            {"n": "Lat pulldown", "s": 3, "r": "10-12", "rir": "2", "t": "hold", "d": 75, "dl": "75 s", "cue": "Puxada com pegada neutra para postura."},
            {"n": "Seated dumbbell shoulder press", "s": 3, "r": "10-12", "rir": "2", "t": "hold", "d": 90, "dl": "90 s", "cue": "Banco a 75° com apoio total da coluna."}
        ],
        "weight_series": [67.2 - (i * 0.04) + ((i % 2 - 1) * 0.09) for i in range(28)]
    },
    {
        "slug": "lucas-pereira",
        "name": "Lucas Pereira",
        "age": 22,
        "sex": "male",
        "weight_start": 68.2,
        "weight_current": 68.0,
        "height_cm": 179,
        "goal": "recomp",
        "profile": "Maratonista Amador · Treinamento Concorrente · Força e Economia de Corrida",
        "split": "Força Funcional 2x (Ter / Sex) + Planilha de Corrida",
        "summary": "Corredor de rua amador (meia maratona em 1h35). Foco: força máxima neural, rigidez de tendão de Aquiles e prevenção de canelite sem hipertrofia excessiva de peso morto.",
        "status": "ok",
        "days_logged": 28,
        "exercises": [
            {"n": "Barbell deadlift", "s": 3, "r": "5-6", "rir": "2", "t": "hold", "d": 150, "dl": "2.5 min", "cue": "Foco em taxa de desenvolvimento de força (RFD)."},
            {"n": "Bulgarian split squat", "s": 3, "r": "6-8", "side": "/lado", "rir": "2", "t": "hold", "d": 120, "dl": "2 min", "cue": "Estabilidade unilateral de quadril e joelho."},
            {"n": "Standing calf raise", "s": 4, "r": "8-10", "side": "/lado", "rir": "1", "t": "hold", "d": 75, "dl": "75 s", "cue": "Pausa isométrica de 2s no topo."},
            {"n": "Lying leg curl", "s": 3, "r": "8-10", "rir": "2", "t": "hold", "d": 120, "dl": "2 min", "cue": "Fase excêntrica controlada de 3 segundos."},
            {"n": "Plank", "s": 3, "r": "45-60 s", "rir": "", "t": "hold", "f": "tempo", "d": 60, "dl": "60 s", "cue": "Anti-extensão de tronco isométrica."}
        ],
        "weight_series": [68.2 - (i * 0.007) + ((i % 4 - 2) * 0.08) for i in range(28)]
    },
    {
        "slug": "beatriz-rocha",
        "name": "Beatriz Rocha",
        "age": 31,
        "sex": "female",
        "weight_start": 66.5,
        "weight_current": 64.8,
        "height_cm": 168,
        "goal": "loss",
        "profile": "Pós-Parto (6 meses) · Diástase Abdominal · Recuperação Postural e Assoalho Pélvico",
        "split": "Full Body 3x (Progressão sem pressão intra-abdominal excessiva)",
        "summary": "Designer, mãe recente. Diástase de 2 cm supraumbilical. Contraindicado flexão de tronco clássica (crunch). Foco em transverso do abdômen, glúteos e cadeia posterior.",
        "status": "ok",
        "days_logged": 28,
        "exercises": [
            {"n": "Barbell hip thrust", "s": 3, "r": "12-15", "rir": "2", "t": "hold", "d": 60, "dl": "60 s", "cue": "Expiração forçada e ativação de assoalho no topo."},
            {"n": "Chest-supported dumbbell row", "s": 3, "r": "10-12", "rir": "2", "t": "hold", "d": 75, "dl": "75 s", "cue": "Apoio total no banco a 30°, retração escapular."},
            {"n": "Goblet squat", "s": 3, "r": "10-12", "rir": "2", "t": "hold", "d": 90, "dl": "90 s", "cue": "Sem manobra de Valsalva, respirar continuamente."},
            {"n": "Cable seated row", "s": 3, "r": "12-15", "rir": "2", "t": "hold", "d": 60, "dl": "60 s", "cue": "Pegada neutra, foco postural."}
        ],
        "weight_series": [66.5 - (i * 0.06) + ((i % 3 - 1) * 0.1) for i in range(28)]
    },
    {
        "slug": "gabriel-souza",
        "name": "Gabriel Souza",
        "age": 54,
        "sex": "male",
        "weight_start": 98.4,
        "weight_current": 95.8,
        "height_cm": 182,
        "goal": "loss",
        "profile": "Hipertenso Controlado (Losartana) · Gordura Visceral · RIR >= 2 (Sem Valsalva)",
        "split": "Upper / Lower 4x com Intervalos de 2 min",
        "summary": "Diretor financeiro, 54 anos. Hipertensão arterial estágio 1 medicada. Prescrição com descanso amplo (>90s) para evitar picos pressóricos agudos e RIR rigorosamente controlado.",
        "status": "ok",
        "days_logged": 28,
        "exercises": [
            {"n": "Leg press 45", "s": 3, "r": "10-12", "rir": "2-3", "t": "hold", "d": 120, "dl": "2 min", "cue": "Não prender a respiração no esforço."},
            {"n": "Dumbbell bench press", "s": 3, "r": "10-12", "rir": "2-3", "t": "hold", "d": 120, "dl": "2 min", "cue": "Movimento ritmado e contínuo."},
            {"n": "Lat pulldown", "s": 3, "r": "10-12", "rir": "2-3", "t": "hold", "d": 90, "dl": "90 s", "cue": "Puxada controlada à frente."},
            {"n": "Seated leg curl", "s": 3, "r": "12-15", "rir": "2", "t": "hold", "d": 90, "dl": "90 s", "cue": "Flexão de joelhos com postura ereta."}
        ],
        "weight_series": [98.4 - (i * 0.09) + ((i % 3 - 1) * 0.12) for i in range(28)]
    },
    {
        "slug": "camila-martins",
        "name": "Camila Martins",
        "age": 27,
        "sex": "female",
        "weight_start": 64.2,
        "weight_current": 63.5,
        "height_cm": 167,
        "goal": "recomp",
        "profile": "Ex-Crossfit · Síndrome do Impacto no Ombro · Sem Desenvolvimento Overhead",
        "split": "Push / Pull / Legs 3x (Estabilidade e Apoio Torácico)",
        "summary": "Advogada, 27 anos. Bursite subacromial e pinçamento no ombro direito após treinos pesados de snatch/desenvolvimento. Foco em musculação com empurrar inclinado e cabos.",
        "status": "ok",
        "days_logged": 28,
        "exercises": [
            {"n": "Incline dumbbell bench press", "s": 3, "r": "10-12", "rir": "2", "t": "hold", "d": 90, "dl": "90 s", "cue": "Pegada neutra (palmas viradas), banco a 30°."},
            {"n": "Chest-supported dumbbell row", "s": 3, "r": "10-12", "rir": "2", "t": "hold", "d": 90, "dl": "90 s", "cue": "Peito apoiado no banco, puxada limpa."},
            {"n": "Cable seated row", "s": 3, "r": "12-15", "rir": "2", "t": "hold", "d": 75, "dl": "75 s", "cue": "Foco em deltoide posterior e romboides."},
            {"n": "Hack squat", "s": 3, "r": "10-12", "rir": "1-2", "t": "hold", "d": 120, "dl": "2 min", "cue": "Coluna totalmente apoiada no encosto."},
            {"n": "Cable lateral raise", "s": 3, "r": "12-15", "rir": "1", "t": "go", "d": 60, "dl": "60 s", "cue": "No plano escapular (30° à frente do corpo)."}
        ],
        "weight_series": [64.2 - (i * 0.025) + ((i % 3 - 1) * 0.08) for i in range(28)]
    }
]

def generate_log(client_folder: Path, c: dict):
    log_file = client_folder / "log.jsonl"
    today = date(2026, 8, 28)
    start_day = today - timedelta(days=c["days_logged"] - 1)
    
    events = []
    # 1. Baseline body_comp
    events.append({
        "type": "body_comp",
        "ts": f"{start_day.isoformat()}T07:00:00+00:00",
        "weight_kg": float(c["weight_start"]),
        "fat_mass_kg": round(float(c["weight_start"]) * (0.22 if c["sex"] == "female" else 0.19), 1),
        "ffm_kg": round(float(c["weight_start"]) * (0.78 if c["sex"] == "female" else 0.81), 1),
        "method": "bioimpedance",
        "protocol_ok": True
    })
    
    # 2. Daily weights, steps, sleep, sessions
    for i, w in enumerate(c["weight_series"]):
        cur_day = start_day + timedelta(days=i)
        events.append({
            "type": "weight",
            "ts": f"{cur_day.isoformat()}T07:15:00+00:00",
            "kg": round(float(w), 2),
            "source": "scale"
        })
        # steps
        steps_val = 8000 + ((i * 37) % 3000)
        events.append({
            "type": "steps",
            "ts": f"{cur_day.isoformat()}T22:00:00+00:00",
            "count": int(steps_val),
            "source": "smartwatch"
        })
        # sleep
        sleep_hours = 7.0 + ((i % 5 - 2) * 0.4)
        events.append({
            "type": "sleep",
            "ts": f"{cur_day.isoformat()}T07:00:00+00:00",
            "hours": round(float(sleep_hours), 1),
            "source": "smartwatch"
        })
        
        # training sessions (Mon, Wed, Fri)
        if cur_day.weekday() in [0, 2, 4]:
            sess_exercises = []
            for ex in c["exercises"]:
                base_load = 40.0 if "press" in ex["n"].lower() or "squat" in ex["n"].lower() else 15.0
                load_prog = base_load + (i // 7) * 2.5
                sess_exercises.append({
                    "name": ex["n"],
                    "sets": [{"load_kg": float(load_prog), "reps": 10, "rir": 2} for _ in range(ex["s"])]
                })
            events.append({
                "type": "session",
                "ts": f"{cur_day.isoformat()}T19:30:00+00:00",
                "session_id": f"sess-{cur_day.isoformat()}",
                "duration_min": 50,
                "exercises": sess_exercises
            })
            
    with open(log_file, "w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")

def generate_sheet_html(client_folder: Path, c: dict):
    program_array = [
        {
            "name": f"Treino A — {c['split'].split('(')[0].strip()}",
            "exercises": c["exercises"]
        }
    ]
    
    html = TEMPLATE_HTML
    html = html.replace("{{CLIENT}}", c["name"])
    html = html.replace("{{SLUG}}", c["slug"])
    html = html.replace("{{SUBTITLE}}", f"{c['split']} · Bloco de 8 Semanas")
    html = html.replace("{{CLIENT_SUMMARY}}", f"{c['sex'].title()}, {c['age']} anos, {c['weight_current']} kg · {c['profile']}")
    html = html.replace("/* {{PROGRAM}} */", f"var PROGRAM = {json.dumps(program_array, ensure_ascii=False, indent=2)};")
    html = html.replace("{{START}}", "2026-08-03")
    html = html.replace("{{TOTAL_WEEKS}}", "8")
    html = html.replace("{{INTRO_UNTIL}}", "2")
    html = html.replace("{{DELOAD_WEEK}}", "8")
    html = html.replace("{{TRAINER}}", "Danilo Jorge")
    html = html.replace("{{CERT}}", "CREF 123456-G/SP")
    
    (client_folder / "sheet.html").write_text(html, encoding="utf-8")

def generate_intake(client_folder: Path, c: dict):
    content = f"""# Anamnese & Triagem Inicial — {c['name']}

**Data de Início:** 2026-08-01 · **Status:** Aprovado para Treinamento (com adaptações)

---

## 1. Perfil & Objetivos
* **Nome:** {c['name']}
* **Idade:** {c['age']} anos · **Sexo:** {'Masculino' if c['sex'] == 'male' else 'Feminino'}
* **Estatura:** {c['height_cm']} cm · **Peso Inicial:** {c['weight_start']} kg (Atual: {c['weight_current']} kg)
* **Objetivo Primário:** {c['goal'].upper()} ({c['profile']})
* **Disponibilidade:** {c['split']}

---

## 2. Triagem de Saúde & Red Flags (PAR-Q+ Adaptado)
* **Histórico Cardiovascular:** Negativo para dor no peito, tonturas ou síncopes em repouso/esforço.
* **Medicamentos em uso:** Conforme histórico clínico reportado.
* **Restrições / Lesões:** {c['summary']}
* **Conduta do Personal:** Prescrição adaptada com exercícios guiados/suportados e monitoramento de RIR.

---

## 3. Estratégia de Prescrição do Bloco
* **Divisão:** {c['split']}
* **Duração do Bloco:** 8 semanas (Semanas 1-2 Introdução, 3-6 Sobrecarga Progressiva, 7 Pico, 8 Deload)
* **Diretriz de Segurança:** Auditoria de volume semanal dentro de MEV/MAV e blindagem articular.
"""
    (client_folder / "intake.md").write_text(content, encoding="utf-8")

def generate_program(client_folder: Path, c: dict):
    ex_lines = ""
    for ex in c["exercises"]:
        ex_lines += f"- **{ex['n']}:** {ex['s']} séries × {ex['r']} reps | RIR {ex['rir']} | Descanso: {ex['dl']}\n  *Obs:* {ex['cue']}\n"
    
    content = f"""# Programa de Treinamento — {c['name']}
### Bloco de 8 Semanas · {c['profile']}

---

## Estrutura da Sessão

{ex_lines}

---

## Regras de Progressão
1. **Duplo Critério:** Só subir a carga quando atingir o topo das repetições em todas as séries prescritas.
2. **RIR Obrigatório:** Manter {c['exercises'][0]['rir']} repetições na reserva. Não levar séries à falha concêntrica prematura.
3. **Semana de Deload:** Na Semana 8, reduzir o volume em 50% mantendo as cargas.
"""
    (client_folder / "program.md").write_text(content, encoding="utf-8")

def generate_state(client_folder: Path, c: dict):
    content = f"""# Estado Consolidado — {c['name']}
> *Arquivo de Memória do Aluno (Anexe este arquivo em qualquer chat novo com a IA)*

- **Aluno:** {c['name']} ({c['age']} anos, {c['height_cm']} cm)
- **Peso Atual:** {c['weight_current']} kg (Início: {c['weight_start']} kg)
- **Meta:** {c['goal']} · **Bloco Atual:** Semana 4 de 8
- **Restrições Clínicas:** {c['profile']}
- **Divisão:** {c['split']}

### Histórico Resumido das Últimas Semanas:
| Semana | Adesão | Peso Médio | Tendência | Cargas Principais | Diagnóstico |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Semana 1** | 3/3 treinos | {round(c['weight_start'] - 0.5, 1)} kg | -0.5 kg | Calibração de RIR | Fase de Introdução concluída |
| **Semana 2** | 3/3 treinos | {round(c['weight_start'] - 1.2, 1)} kg | -0.7 kg | +2.5 kg compostos | Boa recuperação |
| **Semana 3** | 3/3 treinos | {round(c['weight_start'] - 2.0, 1)} kg | -0.8 kg | +2.5 kg compostos | Ótima progressão |
| **Semana 4** | 3/3 treinos | {c['weight_current']} kg | -0.6 kg | Cargas consolidadas | **Em andamento (Plano mantido)** |

---
**Próximo Ajuste:** Avaliação de deload na Semana 7 ou manutenção calórica conforme evolução.
"""
    (client_folder / "estado.md").write_text(content, encoding="utf-8")

def main():
    print(f"Generating 10 client showcase folders in {OUTPUT_DIR}...")
    for c in CLIENTS:
        client_dir = OUTPUT_DIR / c["slug"]
        client_dir.mkdir(parents=True, exist_ok=True)
        generate_log(client_dir, c)
        generate_intake(client_dir, c)
        generate_program(client_dir, c)
        generate_state(client_dir, c)
        generate_sheet_html(client_dir, c)
        
        # Render dashboard HTML
        try:
            res = dash_mod.render(
                client_dir / "log.jsonl",
                client_dir / "dashboard.html",
                client=c["name"],
                goal=c["goal"],
                target_kg=c["weight_current"] - 3.0 if c["goal"] == "loss" else c["weight_current"] + 2.0
            )
            print(f"  [{c['slug']}] Dashboard & Pocket Sheet rendered OK.")
        except Exception as e:
            print(f"  [{c['slug']}] Dashboard render error: {e}")
            
    print("\n✅ All 10 client folders generated successfully!")

if __name__ == "__main__":
    main()
