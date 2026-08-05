"""C9 — le harnais. Spécification : `chantiers/C9-harnais.md`.

Quatre pièces : préflight (P0), générateur synthétique (P1), registre (P2),
épreuves (P3). Les seuils viennent d'`05_Protocole_de_selection.md` et de
`decisions/ADR-001` ; en cas d'écart, eux font foi.

Règle de la maison : tout garde-fou est du code qui lève, et sa suite de tests
prouve qu'il PEUT lever. Un contrôle qui ne peut pas échouer ne protège pas.
"""
