import argparse
import copy

from quoridor_error import QuoridorError
from graphe import construire_graphe
import networkx as nx



def formater_entete(joueurs):
    lignes = ["Legende:"]
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
    lignes = ["Legende:"]
    for i, joueur in enumerate(joueurs, start=1):
        lignes.append(f"   {i}={joueur['nom']}, murs={'|' * joueur['murs']}")
    damier = formater_le_damier(joueurs, murs)
    return "\n".join(lignes) + "\n" + damier


def selectionner_un_coup():
    coup = input("Entrez votre coup (D, MH, MV) : ").strip().upper()
    pos = input("Entrez la position (x y) : ").split()
    return coup, [int(pos[0]), int(pos[1])]


def interpreter_ligne_de_commande():
    parser = argparse.ArgumentParser(prog="main.py", description="Quoridor")
    parser.add_argument("idul", help="IDUL du joueur")
    args = parser.parse_args(args=["ceche25"])
    return args


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

    def etat_partie(self):
        return {
            "joueurs": copy.deepcopy(self.joueurs),
            "murs": copy.deepcopy(self.murs),
            "tour": self.tour,
        }

    def formater_entete(self):
        return formater_entete(self.joueurs)

    def formater_damier(self):
        return formater_le_damier(self.joueurs, self.murs)

    def __str__(self):
        return self.formater_entete() + "\n" + self.formater_damier()

    def deplacer_un_joueur(self, nom_joueur, destination):
        joueur = None
        for j in self.joueurs:
            if j["nom"] == nom_joueur:
                joueur = j
                break

        if joueur is None:
            raise QuoridorError("joueur existe pas")

        x, y = destination
        if not (1 <= x <= 9 and 1 <= y <= 9):
            raise QuoridorError("pos invalide")

        g = construire_graphe(
            [p["position"] for p in self.joueurs],
            self.murs["horizontaux"],
            self.murs["verticaux"]
        )

        pos_actuelle = tuple(joueur["position"])
        dest = tuple(destination)
        moves = list(g.successors(pos_actuelle))

        if dest not in moves:
            raise QuoridorError("move pas permis")

        joueur["position"] = [x, y]

    def placer_un_mur(self, nom_joueur, destination, orientation):
        joueur = None
        for j in self.joueurs:
            if j["nom"] == nom_joueur:
                joueur = j
                break

        if joueur is None:
            raise QuoridorError("joueur existe pas")

        if joueur["murs"] <= 0:
            raise QuoridorError("plus de murs")

        x, y = destination
        if not (1 <= x <= 8 and 1 <= y <= 8):
            raise QuoridorError("pos mur invalide")

        if orientation == "H":
            if [x, y] in self.murs["horizontaux"]:
                raise QuoridorError("mur existe deja")
            self.murs["horizontaux"].append([x, y])

        elif orientation == "V":
            if [x, y] in self.murs["verticaux"]:
                raise QuoridorError("mur existe deja")
            self.murs["verticaux"].append([x, y])
        else:
            raise QuoridorError("orientation invalide")

        g = construire_graphe(
            [p["position"] for p in self.joueurs],
            self.murs["horizontaux"],
            self.murs["verticaux"]
        )

        for idx, j in enumerate(self.joueurs):
            start = tuple(j["position"])
            goal = "B1" if idx == 0 else "B2"

            if not nx.has_path(g, start, goal):
                if orientation == "H":
                    self.murs["horizontaux"].remove([x, y])
                else:
                    self.murs["verticaux"].remove([x, y])
                raise QuoridorError("mur enferme joueur")

        joueur["murs"] -= 1


    def appliquer_un_coup(self, nom_joueur, type_coup, position):
        joueur = None
        for j in self.joueurs:
            if j["nom"] == nom_joueur:
                joueur = j
                break

        if joueur is None:
            raise QuoridorError("joueur existe pas")

        if self.partie_terminee():
            raise QuoridorError("partie fini")

        if type_coup not in ["D", "H", "V"]:
            raise QuoridorError("type coup invalide")

        if type_coup == "D":
            self.deplacer_un_joueur(nom_joueur, position)

        elif type_coup == "H":
            self.placer_un_mur(nom_joueur, position, "H")

        elif type_coup == "V":
            self.placer_un_mur(nom_joueur, position, "V")

        if nom_joueur == self.joueurs[1]["nom"]:
            self.tour += 1

        return (type_coup, position)

    def selectionner_un_coup(self, nom_joueur):
        while True:
            coup = input("type coup (D, H, V): ").strip().upper()
            pos = input("pos x y: ").split()

            try:
                position = [int(pos[0]), int(pos[1])]
            except:
                print("pos pas bonne")
                continue

            copie = Quoridor(joueurs=self.etat_partie())
            try:
                copie.appliquer_un_coup(nom_joueur, coup, position)
                return coup, position
            except QuoridorError as e:
                print("erreur:", e)
                continue


    def partie_terminee(self):
        if self.joueurs[0]["position"][1] == 9:
            return self.joueurs[0]["nom"]

        if self.joueurs[1]["position"][1] == 1:
            return self.joueurs[1]["nom"]

        return False

    # ========================
    # jouer un coup auto
    # ========================

    def jouer_un_coup(self, nom_joueur):
        joueur = None
        idx = None
        for i, j in enumerate(self.joueurs):
            if j["nom"] == nom_joueur:
                joueur = j
                idx = i
                break

        if joueur is None:
            raise QuoridorError("joueur existe pas")

        if self.partie_terminee():
            raise QuoridorError("partie fini")

        g = construirre_graphe = construire_graphe(
            [p["position"] for p in self.joueurs],
            self.murs["horizontaux"],
            self.murs["verticaux"]
        )

        pos = tuple(joueur["position"])
        but = "B1" if idx == 0 else "B2"

        chemin = nx.shortest_path(g, pos, but)
        prochain = list(chemin[1])

        return self.appliquer_un_coup(nom_joueur, "D", prochain)
