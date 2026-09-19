---
name: commit-batches
description: Commits para Alejo en cualquier repo — batches temáticos, `git add` solo de lo relevante, mensaje con el porqué, NUNCA `git commit`. Usar ante "siguiente", "git add y sugerencia de commit", "commiteemos" o al cerrar una feature.
---

# Commits por batches

Alejo commitea, yo no. Dejo **un** batch staged + mensaje; él commitea y dice "siguiente".

## Loop
1. `git status --porcelain` + `git log --oneline -3`. Si hay algo staged, no agrego: espero.
2. Próximo batch **por tema**. Orden: core → drivers → wiring → bordes → seeds/i18n/docs → tests. Back antes que front.
3. `git add` solo esos archivos. Untracked uno por uno (`??` colapsa carpetas).
4. Tests del área en verde (`pytest <paths> -q`, nunca la raíz sin `src`).
5. Presento: título · 3–6 bullets de *qué mirar* · mensaje en bloque.
6. Espero "siguiente".

## Tamaño
- Una idea completa, legible entera: 5–30 archivos.
- Tema enorme (barrido, rename masivo) → commit propio + cómo verificar por muestreo.
- Patrón nuevo para Alejo → batches más chicos, explicar el porqué.

## No entra
- Archivos de otra sesión en el mismo working tree. Si uno mezcla ambos: avisar, no partir.
- Sueltos en la raíz ajenos al proyecto.
- Generados (`uv.lock`, snapshots) sin su causa.

## Mensaje
- Título: `tipo(scope): qué cambia`, español, ≤72 chars, sin punto. `feat|fix|refactor|docs|test|chore`.
- Cuerpo: **breve**. 2–5 renglones, bullets si son varias ideas. Solo el porqué y la decisión; nada de archivos ni narrativa.
- Bug real → síntoma + causa en un renglón. Alternativa descartada → cuál y por qué, un renglón.
- Sin firmas, `Co-Authored-By` ni emojis.

## Índice roto
- Commit con mensaje ajeno → `--amend` solo si no está pusheado.
- Nunca `git reset` sobre un índice de Alejo; `git restore --staged` de lo mío.
- Nunca `git add -A` / `git add .`.
