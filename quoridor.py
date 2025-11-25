import argparse
import copy

from quoridor_error import QuoridorError
from graphe import construire_graphe


# fonctions phase 1 pour compatibilite

def formater_entete(joueurs):
    lignes = ["Légende:"]
    max_len = max(len(j["nom"]) for j in joueurs)

    for i, joueur in enumerate(joueurs, start=1):
        murs = "|" * joueur["murs"]
        lignes.append(
            f"   {i}={joueur['nom']}, "
            + f"{' ' * (max_len - len(joueur['nom']))}murs={murs}"
        )
    return "\n".join(lignes)


def formater_le_damier(joueurs, murs):
    def ligne_cases(y):
        inner = [" "] * 35
        for x in range(1, 10):
            inner[4 * (x - 1) + 1] = "."
        for i, j in enumerate(joueurs, start=1):
            xj, yj = j["position"]
            if yj == y:
                inner[4 * (xj - 1) + 1] = str(i)
        return f"{y} |{''.join(inner)}|"

    def ligne_inter(y):
        inner = [" "] * 35
        return f"  |{''.join(inner)}|"

    lignes = []
    lignes.append("   " + "-" * 35)
    for y in range(9, 0, -1):
        lignes.append(ligne_cases(y))
        if y > 1:
            lignes.append(ligne_inter(y))
    lignes.append("--|" + "-" * 35)
    lignes.append("  | " + "   ".join(str(i) for i in range(1, 10)))

    grid = [list(L) for L in lignes]

    for x, y in murs["verticaux"]:
        col = 4 * (x - 1)
        row_cases = 1 + 2 * (9 - y)
        abs_col = 3 + col
        grid[row_cases][abs_col] = "|"
        if y > 1:
            grid[row_cases + 1][abs_col] = "|"

    for x, y in murs["horizontaux"]:
        if y > 1:
            row_inter = 1 + 2 * (9 - y) + 1
            start = 4 * x - 3
            for k in range(7):
                abs_col = 3 + (start + k)
                grid[row_inter][abs_col] = "-"

    return "\n".join("".join(r) for r in grid)


def formater_le_jeu(etat):
    joueurs = etat["joueurs"]
    murs = etat["murs"]
    lignes = ["Légende:"]
    for i, joueur in enumerate(joueurs, start=1):
        lignes.append(f"   {i}={joueur['nom']}, murs={'|' * joueur['murs']}")
    damier = formater_le_damier(joueurs, murs)
    return "\n".join(lignes) + "\n" + damier


def selectionner_un_coup():
    coup = input("Entrez votre coup (D, MH, MV) : ").strip().upper()
    pos = input("Entrez la position (x y) : ").split()
    return coup, [int(pos[0]), int(pos[1])]


def interpréter_la_ligne_de_commande():
    parser = argparse.ArgumentParser(prog="main.py", description="Quoridor")
    parser.add_argument("idul", help="IDUL du joueur")
    args = parser.parse_args(args=["ceche25"])
    return args


# ================================
# classe Quoridor (phase 2)
# ================================

class Quoridor:
    def __init__(self, joueurs=None, murs=None, tour=0):
        if isinstance(joueurs, dict):
            self.joueurs = copy.deepcopy(joueurs["joueurs"])
            self.murs = copy.deepcopy(joueurs["murs"])
            self.tour = joueurs.get("tour", 0)
        else:
            if joueurs is None:
                self.joueurs = [
                    {"nom": "idul", "murs": 7, "position": [5, 1]},
                    {"nom": "automate", "murs": 7, "position": [5, 9]},
                ]
            else:
                self.joueurs = copy.deepcopy(joueurs)

            if murs is None:
                self.murs = {"horizontaux": [], "verticaux": []}
            else:
                self.murs = copy.deepcopy(murs)

            self.tour = tour

    def état_partie(self):
        return {
            "joueurs": copy.deepcopy(self.joueurs),
            "murs": copy.deepcopy(self.murs),
            "tour": self.tour,
        }

    def formater_entête(self):
        return formater_entete(self.joueurs)

    def formater_le_damier(self):
        return formater_le_damier(self.joueurs, self.murs)

    def __str__(self):
        return self.formater_entête() + "\n" + self.formater_le_damier()

    # =======================
    # methodes a completer
    # =======================

    def déplacer_un_joueur(self, nom_joueur, destination):
        raise NotImplementedError

    def placer_un_mur(self, nom_joueur, destination, orientation):
        raise NotImplementedError

    def appliquer_un_coup(self, nom_joueur, type_coup, position):
        raise NotImplementedError

    def sélectionner_un_coup(self, nom_joueur):
        raise NotImplementedError

    def partie_terminée(self):
        raise NotImplementedError

    def jouer_un_coup(self, nom_joueur):
        raise NotImplementedError


if __name__ == "__main__":
    etat = {
        "joueurs": [
            {"nom": "IDUL", "murs": 7, "position": [5, 5]},
            {"nom": "robot", "murs": 3, "position": [8, 6]},
        ],
        "murs": {
            "horizontaux": [[4, 4], [2, 6], [3, 8], [5, 8], [7, 8]],
            "verticaux": [[6, 2], [4, 4], [2, 6], [7, 5], [7, 7]],
        },
    }
    print(formater_le_jeu(etat))

    partie = Quoridor(joueurs=etat)
    print(partie)
