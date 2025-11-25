from quoridor import interpréter_la_ligne_de_commande, formater_le_jeu, selectionner_un_coup
from api import creer_une_partie, appliquer_un_coup, recuperer_une_partie
import sys

def main():
    args = interpréter_la_ligne_de_commande()
    idul = args.idul
    secret = "76f1df8e-330e-4688-b909-9e40f92a5bdc"

    try:
        id_partie, etat = creer_une_partie(idul, secret)
    except Exception as e:
        print(e)
        sys.exit(1)

    print(formater_le_jeu(etat))

    while True:
        coup, position = selectionner_un_coup()

        try:
            appliquer_un_coup(id_partie, coup, position, idul, secret)
        except StopIteration as gagnant:
            print(f"Partie terminée, le gagnant est {gagnant.value}")
            break
        except Exception as e:
            print(e)
            continue

        try:
            id_partie, etat = recuperer_une_partie(id_partie, idul, secret)
        except Exception as e:
            print(e)
            break

        print(formater_le_jeu(etat))

if __name__ == "__main__":
    main()
