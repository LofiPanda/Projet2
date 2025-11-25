import copy
import argparse
from graphe import construire_graphe
from quoridor_error import QuoridorError
import networkx as nx


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

    def ligne_inter():
        return f"  |{' ' * 35}|"

    lignes = []
    lignes.append("   " + "-" * 35)
    for y in range(9, 0, -1):
        lignes.append(ligne_cases(y))
        if y > 1:
            lignes.append(ligne_inter())
    lignes.append("--|" + "-" * 35)
    lignes.append("  | " + "   ".join(str(i) for i in range(1, 10)))

    grid = [list(L) for L in lignes]

    # murs verticaux
    for x, y in murs["verticaux"]:
        col = 4 * (x - 1)
        row = 1 + 2 * (9 - y)
        abs_col = 3 + col
        grid[row][abs_col] = "|"
        if y > 1:
            grid[row + 1][abs_col] = "|"

    # murs horizontaux
    for x, y in murs["horizontaux"]:
        if y > 1:
            row = 1 + 2 * (9 - y) + 1
            start = 4 * x - 3
            for k in range(7):
                abs_col = 3 + start + k
                grid[row][abs_col] = "-"

    return "\n".join("".join(r) for r in grid)


def formater_le_jeu(etat):
    return formater_entete(etat["joueurs"]) + "\n" + formater_le_damier(
        etat["joueurs"], etat["murs"]
    )


def interpreter_ligne_de_commande():
    parser = argparse.ArgumentParser(prog="main.py", description="Quoridor")
    parser.add_argument("idul", help="IDUL du joueur")
    return parser.parse_args()


class Quoridor:
    def __init__(self, joueurs=None, murs=None, tour=0):
        # cas: joueurs = dict venant du serveur ou état_partie()
        if isinstance(joueurs, dict):
            self.joueurs = copy.deepcopy(joueurs["joueurs"])
            self.murs = copy.deepcopy(joueurs["murs"])
            self.tour = joueurs.get("tour", 0)
        else:
            # nouvelle partie
            if joueurs is None:
                self.joueurs = [
                    {"nom": "idul", "murs": 7, "position": [5, 1]},
                    {"nom": "automate", "murs": 7, "position": [5, 9]},
                ]
            else:
                self.joueurs = copy.deepcopy(joueurs)

            self.murs = {"horizontaux": [], "verticaux": []} if murs is None else copy.deepcopy(murs)
            self.tour = tour

    def état_partie(self):
        return self.etat_partie()

    def etat_partie(self):
        return {
            "joueurs": copy.deepcopy(self.joueurs),
            "murs": copy.deepcopy(self.murs),
            "tour": self.tour,
        }

    def formater_entête(self):
        return self.formater_entete()

    def formater_entete(self):
        return formater_entete(self.joueurs)

    def formater_le_damier_(self):
        return self.formater_le_damier()

    def formater_le_damier(self):
        return formater_le_damier(self.joueurs, self.murs)

    def __str__(self):
        return self.formater_entete() + "\n" + self.formater_le_damier()

    def déplacer_un_joueur(self, nom_joueur, destination):
        return self.deplacer_un_joueur(nom_joueur, destination)

    def deplacer_un_joueur(self, nom_joueur, destination):
        joueur = None
        for j in self.joueurs:
            if j["nom"] == nom_joueur:
                joueur = j
                break

        if joueur is None:
            raise QuoridorError("Le joueur n'existe pas.")

        x, y = destination
        if not (1 <= x <= 9 and 1 <= y <= 9):
            raise QuoridorError("La position est invalide.")

        g = construire_graphe(
            [p["position"] for p in self.joueurs],
            self.murs["horizontaux"],
            self.murs["verticaux"],
        )

        pos_actuelle = tuple(joueur["position"])
        dest = tuple(destination)
        moves = list(g.successors(pos_actuelle))

        if dest not in moves:
            raise QuoridorError("La position est invalide pour l'état actuel du jeu.")

        joueur["position"] = [x, y]

    def placer_un_mur(self, nom_joueur, destination, orientation):
        joueur = None
        for j in self.joueurs:
            if j["nom"] == nom_joueur:
                joueur = j
                break

        if joueur is None:
            raise QuoridorError("Le joueur n'existe pas.")

        if joueur["murs"] <= 0:
            raise QuoridorError("Le joueur a déjà placé tous ses murs.")

        x, y = destination
        if not (1 <= x <= 8 and 2 <= y <= 9):
            raise QuoridorError("La position est invalide.")

        if orientation not in ["H", "V"]:
            raise QuoridorError("Le type de coup est invalide.")

        # mur existe déjà ?
        if orientation == "H" and [x, y] in self.murs["horizontaux"]:
            raise QuoridorError("Un mur occupe déjà cette position.")

        if orientation == "V" and [x, y] in self.murs["verticaux"]:
            raise QuoridorError("Un mur occupe déjà cette position.")

        # tentative de placement
        new_h = copy.deepcopy(self.murs["horizontaux"])
        new_v = copy.deepcopy(self.murs["verticaux"])

        if orientation == "H":
            new_h.append([x, y])
        else:
            new_v.append([x, y])

        g = construire_graphe(
            [p["position"] for p in self.joueurs],
            new_h,
            new_v
        )

        # verif chemin pour chaque joueur
        pos1 = tuple(self.joueurs[0]["position"])
        pos2 = tuple(self.joueurs[1]["position"])

        if not nx.has_path(g, pos1, "B1") or not nx.has_path(g, pos2, "B2"):
            raise QuoridorError("Vous ne pouvez pas enfermer un joueur.")

        # OK: appliquer
        if orientation == "H":
            self.murs["horizontaux"].append([x, y])
        else:
            self.murs["verticaux"].append([x, y])

        joueur["murs"] -= 1

    def appliquer_un_coup(self, nom_joueur, type_coup, position):
        # joueur existe ?
        joueur = None
        for j in self.joueurs:
            if j["nom"] == nom_joueur:
                joueur = j
                break
        if joueur is None:
            raise QuoridorError("Le joueur n'existe pas.")

        if self.partie_terminee():
            raise QuoridorError("La partie est déjà terminée.")

        # normalisation du type
        if type_coup in ["MH", "H"]:
            type_coup = "H"
        elif type_coup in ["MV", "V"]:
            type_coup = "V"
        elif type_coup != "D":
            raise QuoridorError("Le type de coup est invalide.")

        # appliquer
        if type_coup == "D":
            self.deplacer_un_joueur(nom_joueur, position)
        elif type_coup == "H":
            self.placer_un_mur(nom_joueur, position, "H")
        elif type_coup == "V":
            self.placer_un_mur(nom_joueur, position, "V")

        # incrément du tour si joueur2
        if nom_joueur == self.joueurs[1]["nom"]:
            self.tour += 1

        return type_coup, position

    def sélectionner_un_coup(self, nom_joueur):
        return self.selectionner_un_coup(nom_joueur)

    def selectionner_un_coup(self, nom_joueur):
        while True:
            coup = input("type coup (D, H, V): ").strip().upper()
            pos = input("pos x y: ").split()

            try:
                position = [int(pos[0]), int(pos[1])]
            except:
                print("Position invalide.")
                continue

            copie = Quoridor(joueurs=self.etat_partie())

            try:
                copie.appliquer_un_coup(nom_joueur, coup, position)
                return coup, position
            except QuoridorError as e:
                print(e)

    def partie_terminée(self):
        return self.partie_terminee()

    def partie_terminee(self):
        if self.joueurs[0]["position"][1] == 9:
            return self.joueurs[0]["nom"]
        if self.joueurs[1]["position"][1] == 1:
            return self.joueurs[1]["nom"]
        return False

    def jouer_un_coup(self, nom_joueur):
        return self.jouer_coup_auto(nom_joueur)

    def jouer_coup_auto(self, nom_joueur):
        if self.partie_terminee():
            raise QuoridorError("La partie est déjà terminée.")

        joueur = None
        idx = None
        for i, j in enumerate(self.joueurs):
            if j["nom"] == nom_joueur:
                joueur = j
                idx = i
                break

        if joueur is None:
            raise QuoridorError("Le joueur n'existe pas.")

        g = construire_graphe(
            [p["position"] for p in self.joueurs],
            self.murs["horizontaux"],
            self.murs["verticaux"],
        )

        pos = tuple(joueur["position"])
        but = "B1" if idx == 0 else "B2"

        chemin = nx.shortest_path(g, pos, but)
        prochain = list(chemin[1])

        return self.appliquer_un_coup(nom_joueur, "D", prochain)
