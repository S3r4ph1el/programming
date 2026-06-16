# variatype — HackTheBox

Exploits usados na resolução desta máquina.

**Writeup:** https://s3r4ph1el.github.io/acta/hackthebox/variatype/

| Plataforma | Dificuldade | OS |
|---|---|---|
| HackTheBox | Medium | Linux |

## Scripts

- `app.py`
- `build_payload.py` — CVE-2025-66034 — fontTools varLib designspace: arbitrary file write + content injection.
- `build_tar.py` — CVE-2024-25082: FontForge passa o nome do membro do archive a um shell sem sanitizar.
- `config.designspace`
- `install_validator.py`
- `out.ttf`
- `payload_server.py` — Responder que devolve um job de cron para QUALQUER path GET.
- `source-black.ttf`
- `source-regular.ttf`
- `submit.tar.gz`
