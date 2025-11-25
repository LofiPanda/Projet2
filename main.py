import sys
from quoridor import Quoridor, interpreter_ligne_de_commande
from api import creer_une_partie, appliquer_un_coup, recuperer_une_partie


def main():
    # lire idul via CLI
    args = interpreter_ligne_de_commande()
    idul = args.idul

    secret = "76f1df8e-330e-4688-b909-9e40f92a5bdc"

    try:
        id_partie, etat = creer_une_partie(idul, secret)
    except Exception as e:
        print(e)
        sys.exit(1)

    partie = Quoridor(joueurs=etat)
    print(partie)

    while True:
        coup, position = partie.selectionner_un_coup(idul)

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

        partie = Quoridor(joueurs=etat)
        print(partie)


if __name__ == "__main__":
    main()
