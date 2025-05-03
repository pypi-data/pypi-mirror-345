import subprocess
import time

import subprocess
import time
import platform

import subprocess
import time
import platform
import json

def boucle_workflow(ip_port="127.0.0.1:8000", workflow_id="untitled.ows", temporisation=0.3):
    """
    Exécute une boucle de requêtes POST/GET vers un serveur, en attendant que le workflow soit terminé.

    Conditions de sortie de la boucle GET :
    - Code HTTP 200
    - Champ "_statut" == "Finished" dans le JSON retourné

    Paramètres :
    - ip_port (str) : IP et port du serveur (ex : "127.0.0.1:8000")
    - workflow_id (str) : nom du fichier workflow (ex : "untitled.ows")
    - temporisation (float) : délai entre chaque tentative (en secondes)
    """

    null_file = "NUL" if platform.system() == "Windows" else "/dev/null"

    while True:
        try:
            # 1. Envoi de la requête POST
            post_command = [
                "curl", "--silent", "--show-error", "--location",
                f"{ip_port}/input-workflow",
                "--header", "Content-Type: application/json",
                "--data", f'''{{
                    "workflow_id": "{workflow_id}",
                    "front_id": "11OO1O1O1",
                    "data": [
                        {{
                            "num_input": 0,
                            "values": [
                                ["col1"],
                                ["float"],
                                [[3]]
                            ]
                        }}
                    ]
                }}'''
            ]

            print(f"[POST] → {ip_port}/input-workflow (workflow : {workflow_id})")
            result = subprocess.run(post_command, capture_output=True, text=True)

            if result.returncode != 0:
                print("❌ Erreur POST :", result.stderr)
                break

            # 2. Attente de la complétion du workflow via GET
            while True:
                get_command = [
                    "curl", "--silent", "--show-error",
                    "-X", "GET",
                    f"http://{ip_port}/output-workflow/{workflow_id}",
                    "-H", "accept: application/json"
                ]

                get_result = subprocess.run(get_command, capture_output=True, text=True)

                if get_result.returncode != 0:
                    print("❌ Erreur GET :", get_result.stderr)
                    return

                try:
                    response_json = json.loads(get_result.stdout)
                except json.JSONDecodeError:
                    print("❌ Réponse non JSON. Attente...")
                    time.sleep(temporisation)
                    continue

                statut = response_json.get("_statut", "")
                print(f"[GET] _statut = {statut}")

                if statut == "Finished":
                    print("✅ Workflow terminé avec succès.")
                    break

                time.sleep(temporisation)

            # Pause avant de recommencer un nouveau cycle
            time.sleep(temporisation)

        except Exception as e:
            print("❌ Erreur inattendue :", e)
            break

if __name__ == "__main__":
    boucle_workflow()