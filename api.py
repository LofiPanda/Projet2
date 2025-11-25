import requests
URL = "https://pax.ulaval.ca/quoridor/api/a25"


def creer_une_partie(idul, secret):
    rep = requests.post(f"{URL}/jeux", auth=(idul, secret))
    if rep.status_code == 200:
        data = rep.json()
        return data["id"], data["état"]
    if rep.status_code == 401:
        raise PermissionError(rep.json().get("message"))
    if rep.status_code == 406:
        raise RuntimeError(rep.json().get("message"))
    raise ConnectionError


def appliquer_un_coup(id_partie, coup, position, idul, secret):
    rep = requests.put(
        f"{URL}/jeux/{id_partie}",
        auth=(idul, secret),
        json={"coup": coup, "position": position},
    )

    if rep.status_code == 200:
        data = rep.json()
        if data.get("partie") == "terminée":
            raise StopIteration(data.get("gagnant"))
        return data["coup"], data["position"]

    if rep.status_code == 401:
        raise PermissionError(rep.json().get("message"))
    if rep.status_code == 404:
        raise ReferenceError(rep.json().get("message"))
    if rep.status_code == 406:
        raise RuntimeError(rep.json().get("message"))
    raise ConnectionError


def recuperer_une_partie(id_partie, idul, secret):
    rep = requests.get(f"{URL}/jeux/{id_partie}", auth=(idul, secret))

    if rep.status_code == 200:
        data = rep.json()
        return data["id"], data["état"]

    if rep.status_code == 401:
        raise PermissionError(rep.json().get("message"))
    if rep.status_code == 404:
        raise ReferenceError(rep.json().get("message"))
    if rep.status_code == 406:
        raise RuntimeError(rep.json().get("message"))

    raise ConnectionError
