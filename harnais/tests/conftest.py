import sys
from pathlib import Path

# le dépôt à la racine du chemin d'import : `import harnais` doit marcher
# depuis n'importe quel répertoire de lancement
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
