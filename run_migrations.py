# Det här skriptet kommer att:
#
# Synkronisera migrationshistoriken om det behövs (t.ex. om vi har skapat en lokal databas och behöver säkerställa att Alembic är i fas).
# Köra alla migreringar som behövs för att uppdatera lokal databas.

import subprocess
import sys

def run_command(command):
    """Kör ett terminalkommando och visa resultatet."""
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    result.check_returncode()

def get_heads():
    """Returnera en lista med alla Alembic head-revisions."""
    print("Letar efter flera migrations-heads...")
    output = run_command(["alembic", "heads"])
    heads = []

    for line in output.splitlines():
        if "head" in line.lower() and "rev:" in line.lower():
            parts = line.strip().split()
            for i, part in enumerate(parts):
                if part.lower() == 'rev:':
                    heads.append(parts[i+1])
    return heads

def auto_merge_heads():
    """Om det finns flera heads – slå ihop dem automatiskt."""
    heads = get_heads()
    if len(heads) > 1:
        print(f"Hittade flera heads: {heads}. Slår ihop dem automatiskt...")
        run_command(["alembic", "merge", "-m", "Auto merge conflicting heads"] + heads)
    else:
        print("Inga konflikter mellan heads – ingen merge behövs.")

def stamp_db():
    """Synkronisera Alembic migrationshistorik med databasen."""
    print("Synkroniserar Alembic migrationshistorik...")
    run_command(["alembic", "stamp", "head"])

def run_migrations():
    """Kör Alembic migrations för att uppdatera databasen."""
    print("Kör Alembic migrations för att uppdatera databasen...")
    run_command(["alembic", "upgrade", "head"])

if __name__ == "__main__":
    # Första gången körs stamp för att synkronisera, sen körs upgrade för att applicera nya migrationer
    stamp_db()
    run_migrations()

# stamp_db synkroniserar Alembic migrationshistorik med databasen.
# Alembic kommer inte att försöka köra migrationer som redan har körts.