from typing import List, Optional, Dict


class Fone:
    def __init__(self, id: str, number: str):
        self.id = id
        self.number = number

    def isValid(self) -> bool:
        return all(ch.isdigit() for ch in self.number)

    def __str__(self) -> str:
        return f"{self.id}:{self.number}"


class Contact:
    def __init__(self, name: str):
        self.name = name
        self.fones: List[Fone] = []
        self.favorite: bool = False

    def addFone(self, id: str, number: str):
        f = Fone(id, number)
        if f.isValid():
            # avoid duplicate ids
            ids = [fone.id for fone in self.fones]
            if f.id not in ids:
                self.fones.append(f)
        else:
            print(f"fail: fone {id}:{number} invalido")

    def __str__(self) -> str:
        phones = ", ".join(str(f) for f in self.fones)
        return f"- {self.name} [{phones}]"


class Agenda:
    def __init__(self):
        self.contacts: Dict[str, Contact] = {}

    def find(self, name: str) -> Optional[Contact]:
        return self.contacts.get(name)

    def addContact(self, name: str, fones: List[Fone]):
        c = self.find(name)
        if c:
            for f in fones:
                if f.isValid():
                    c.addFone(f.id, f.number)
        else:
            c = Contact(name)
            for f in fones:
                if f.isValid():
                    c.addFone(f.id, f.number)
            self.contacts[name] = c

    # convenience alias used by the CLI
    def add(self, name: str, fones: List[Fone]):
        self.addContact(name, fones)

    def toggle_fav(self, name: str):
        c = self.find(name)
        if c:
            c.favorite = not c.favorite

    def favs(self) -> List[str]:
        res: List[str] = []
        for name in sorted(self.contacts.keys()):
            c = self.contacts[name]
            if c.favorite:
                phones = ", ".join(str(f) for f in c.fones)
                res.append(f"@ {c.name} [{phones}]")
        return res

    def search(self, pattern: str) -> List[str]:
        pat = pattern.lower()
        res: List[str] = []
        for name in sorted(self.contacts.keys()):
            c = self.contacts[name]
            in_name = pat in c.name.lower()
            in_fone = any(pat in f.number for f in c.fones)
            if in_name or in_fone:
                prefix = "@ " if c.favorite else "- "
                phones = ", ".join(str(f) for f in c.fones)
                res.append(f"{prefix}{c.name} [{phones}]")
        return res

    def rm_fone(self, name: str, idx: int) -> bool:
        c = self.find(name)
        if not c:
            return False
        if idx < 0 or idx >= len(c.fones):
            return False
        c.fones.pop(idx)
        return True

    def rm(self, name: str) -> bool:
        if name in self.contacts:
            del self.contacts[name]
            return True
        return False

    def __str__(self) -> str:
        return "\n".join(str(c) for c in self.contacts)

def main():
    import sys

    agenda = Agenda()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        cmd = parts[0]
        # echo command prefixed by $
        print(f"${line}")
        if cmd == "end":
            break
        elif cmd == "add":
            # add name fone1 fone2 ...
            if len(parts) >= 2:
                name = parts[1]
                fones = [parse_fone(t) for t in parts[2:]]
                # filter out None (invalid parse)
                fones = [f for f in fones if f is not None]
                agenda.add(name, fones)
        elif cmd == "show":
            for name in sorted(agenda.contacts.keys()):
                c = agenda.contacts[name]
                prefix = "@ " if c.favorite else "- "
                phones = ", ".join(str(f) for f in c.fones)
                print(f"{prefix}{c.name} [{phones}]")
        elif cmd == "tfav":
            if len(parts) >= 2:
                agenda.toggle_fav(parts[1])
        elif cmd == "favs":
            for l in agenda.favs():
                print(l)
        elif cmd == "search":
            if len(parts) >= 2:
                res = agenda.search(" ".join(parts[1:]))
                for l in res:
                    print(l)
        elif cmd == "rmFone":
            if len(parts) >= 3:
                name = parts[1]
                try:
                    idx = int(parts[2])
                except ValueError:
                    print("fail: indice de telefone invalido")
                    continue
                ok = agenda.rm_fone(name, idx)
                if not ok:
                    print("fail: indice de telefone invalido")
        elif cmd == "rm":
            if len(parts) >= 2:
                agenda.rm(parts[1])


def parse_fone(token: str) -> Optional[Fone]:
    if ":" not in token:
        print(f"fail: formato fone invalido '{token}'")
        return None
    id, number = token.split(":", 1)
    return Fone(id, number)


if __name__ == "__main__":
    main()