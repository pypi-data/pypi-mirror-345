import uvicorn
import time
from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
import json
import socket

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.HLIT_dev.remote_server_smb import convert, hlit_workflow_management
    from Orange.widgets.orangecontrib.AAIT.utils import MetManagement
    from Orange.widgets.orangecontrib.HLIT_dev.widgets.utils import extract_property_ows
else:
    from orangecontrib.HLIT_dev.remote_server_smb import convert, hlit_workflow_management
    from orangecontrib.AAIT.utils import MetManagement
    from orangecontrib.HLIT_dev.widgets.utils import extract_property_ows

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change "*" par une liste de domaines autorisés si besoin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputWorkflowJson(BaseModel):
    workflow_id: str = Field(..., example="toto.ows")
    data: list = Field(..., example=[{"num_input": 0, "values": [["col1", "col2"], ["float", "str"], [[3, "test"],[3, "test"]]]}])


def check_if_uvicorn_is_running():
    port = 8000
    # Verification of port
    if est_port_occupe(port):
        print(f"Le port {port} est déjà utilisé par un autre workflow.")
        return
    else:
        # Start server
        lauch_uvicorn()

def est_port_occupe(port, host="127.0.0.1"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0  # Retourne True si le port est occupé

def lauch_uvicorn():
    chemin_dossier =MetManagement.get_api_local_folder()
    # on purge bien touts les elements c est normal de ne pa mettre de workflow id ici
    if os.path.exists(chemin_dossier):
        MetManagement.reset_folder(chemin_dossier, recreate=False)
    uvicorn.run(app, host="127.0.0.1", port=8000)


@app.get("/read-config-file-ows-html", summary="Récupération du fichier de configuration", description="L'appel a cette route permet la récupération des informations nécéssaires afin de configurer la connexion front-end du ou des workflows avec comme paramètre le workflow id, la description, le timeout ... ")
def read_config_file_ows_html():
    list_config_html_ows=[]
    if 0!= hlit_workflow_management.read_config_ows_html_file_as_dict(list_config_html_ows):
        return JSONResponse(
            status_code=404,
            content={"message": f"Error occurs"}
        )
    return {"message" : list_config_html_ows}

@app.get("/open-local-html/{key_name}", summary="Lancement d'un html", description="L'appel a cette route permet de lancer un html local en passant comme paramètre le 'key_name' correspondant au process")
def open_local_html(key_name):
    list_config_html_ows = []
    if 0!= hlit_workflow_management.read_config_ows_html_file_as_dict(list_config_html_ows):
        return JSONResponse(
            status_code=404,
            content={"message": f"Error occurs"}
        )
    if 0!= hlit_workflow_management.open_local_html(list_config_html_ows, key_name):
        return JSONResponse(
            status_code=404,
            content={"message": f"Error occurs to open local html"}
        )
    return {"message" : "Open local html ok"}


@app.get("/get-worklow-id-list/{key_name}", summary="Workflow information", description="L'appel a cette route permet de récupérer les inputs et outputs nécéssaires au fonctionnement du process correspond au 'key_name' passé en paramètre.")
def get_worklow_id_list(key_name):
    list_config_html_ows = []
    if 0 != hlit_workflow_management.read_config_ows_html_file_as_dict(list_config_html_ows):
        return JSONResponse(
            status_code=404,
            content={"message": f"Error occurs to get json aait store file"}
        )
    workflow_path=""
    try:
        for element in list_config_html_ows:
            if element["name"]==key_name:
                workflow_path=element['ows_file']
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=404,
            content={"message": f"Error occurs when I read ows file path"}
        )
    if workflow_path=="":
        return JSONResponse(
            status_code=404,
            content={"message": f"workflow path not found"}
        )

    try:
        # Simule ici une extraction typique (à adapter selon ton contexte réel)
        json_result = extract_property_ows.extract_property_for_hlit(workflow_path)


        if json_result is None:
            return JSONResponse(
                status_code=500,
                content={"error": "error nodes reading"}
            )

        return JSONResponse(
            status_code=200,
            content=json_result
        )

    except Exception as e:
        print(f"[API ERROR] : {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Servor error"}
        )

@app.get("/start-workflow/{key_name}", summary="Lance un workflow", description="Cette route permet de lancer le workflow correspondant au 'key_name' passé en paramètre.")
def start_workflow(key_name):
    list_config_html_ows = []
    if 0!= hlit_workflow_management.read_config_ows_html_file_as_dict(list_config_html_ows):
        return JSONResponse(
            status_code=404,
            content={"message": f"Error occurs to get json aait store file"}
        )
    res= hlit_workflow_management.start_workflow(list_config_html_ows, key_name)
    if res==1:
        return JSONResponse(
            status_code=404,
            content={"message": f"Error occurs to start workflow"}
        )
    if res == 2:
        return JSONResponse(
            status_code=404,
            content={"message": f"workflow is already running"}
        )
    return {"_message" : "Start workflow ok", "_statut": "Started", "_result": None}

@app.get("/reset-data-folder-workflow", summary="Suppression du dossier API", description="On appelle cette route pour supprimer le dossier 'exchangeApi' présent dans l'IA store et ainsi réinitialiser les données pour relancer le process. Nota si la route /chat est appelé et que le stream n'est pas terminé il ne sera pas possible de reset le dossier")
def reset_data_folder_workflow():
    chemin_dossier = MetManagement.get_api_local_folder()
    if os.path.exists(chemin_dossier):
        MetManagement.reset_folder(chemin_dossier, recreate=False)
        return {"message": "Reset data folder workflow ok"}
    else:
        return {"message": "Error no folder found"}

@app.post("/input-workflow", summary="Envoie de donner au process", description="On appelle cette route pour initialiser le process. Lorsqu'elle est appelée le process commence son exécution. Il n'est pas possible de rappeler cette route pour relancer le même process tant que celui ci n'est pas terminé. Pour le rappeler alors qu'il n'a pas fini il faut utiliser la route /reset-data-folder-workflow et ensuite rappeler cette route pour exécuter de nouveau le process.")
def receive_data(input_data: InputWorkflowJson):
    input_data = input_data.dict()
    chemin_dossier =""
    data_config = []
    if input_data["data"] is not None and input_data["workflow_id"] is not None:
        chemin_dossier = MetManagement.get_api_local_folder(workflow_id=input_data["workflow_id"])
        if not os.path.exists(chemin_dossier):
            os.makedirs(chemin_dossier)
        else:
            print(f"Dossier '{chemin_dossier}' existe déjà.")
            return JSONResponse(
                status_code=404,
                content={"_message": f"The workflow is already running"}
            )
        for key, data in enumerate(input_data["data"]):
            table = convert.convert_json_to_orange_data_table(data)
            if table == 1:
                MetManagement.reset_folder(chemin_dossier, recreate=False)
                return JSONResponse(
                    status_code=404,
                    content={"_message": f"The input data table is not a dict"}
                )

            if table is None or table == []:
                MetManagement.reset_folder(chemin_dossier, recreate=False)
                return JSONResponse(
                    status_code=404,
                    content={"_message": f"The input data table is empty"}
                )
            table.save(chemin_dossier + "input_data_" + str(data["num_input"]) + ".tab")
            data_config.append({"num_input": data["num_input"], "path": "input_data_" + str(data["num_input"]) + ".tab"})
    else:
        return JSONResponse(
            status_code=404,
            content={"_message": f"The input data is not at good format"}
        )
    with open(chemin_dossier + "config.json", "w") as fichier:
        json.dump({"workflow_id": input_data["workflow_id"], "data_config": data_config}, fichier, indent=4)
    with open(chemin_dossier + ".ok", "w") as fichier:
        pass
    MetManagement.write_file_time(chemin_dossier+"time.txt")
    return {"_message" : "the input file has been created", "_statut": "Started", "_result": None}



@app.get("/output-workflow/{workflow_id}", summary="Récupération de la sortie d'un process", description="On appelle cette route tant que le process n'a pas fini de générer sa sortie. On lui passe le workflow id d'un process en paramètre. Tant que le process n'a pas fini de générer sa sortie et que le timout n'est pas atteint (définition du timeout optionnel) le process s'éxécute. Lorsque c'est fini il renvoie la table de sortie au format JSON classique de type : {'_message': f'Your workflow is finished.', '_statut': 'Finished', '_result': data} ou data est la table de sortie du workflow formaté aussi au format JSON. Lorsque le process est fini, il supprime le sous dossier dans 'exchangeApi' et on peut donc rappeler le process avec la route /input-workflow .")
def read_root(workflow_id):
    chemin_dossier = MetManagement.get_api_local_folder(workflow_id=workflow_id)
    if not os.path.exists(chemin_dossier):
        return JSONResponse(
            status_code=404,
            content={"_message": f"Error no folder found"}
        )
    ## on check si le timeout est défini et s'il est atteint
    if 0 != hlit_workflow_management.check_if_timout_is_reached(chemin_dossier):
        return JSONResponse(
            status_code=404,
            content={"_message": f"Timeout has been reached.", "_statut":"Timeout",
                     "_result": None}
        )
    if not os.path.exists(chemin_dossier + ".output_ok") and not os.path.exists(chemin_dossier + "output.json"):
        if os.path.exists(chemin_dossier + ".statut_ok"):
            with open(chemin_dossier + "statut.json", "r", encoding="utf-8") as file:
                data = json.load(file)
                return JSONResponse(
                    status_code=200,
                    content={"_message": f"Your data are still being processed.", "_statut": data["value"], "_result": None}
                )
        else:
            return JSONResponse(
                status_code=200,
                content={"_message": f"Your data are still being processed.", "_statut": None, "_result": None}
            )
    if not os.path.exists(chemin_dossier + ".output_ok"):
        with open(chemin_dossier + "output.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        MetManagement.reset_folder(chemin_dossier, recreate=False)
        return JSONResponse(
                    status_code=200,
                    content={"_message": f"Your workflow is finished.", "_statut": "Finished", "_result": data}
                )

@app.get("/chat/{workflow_id}",  summary="Stream pour LLM", description="On passe workflow id d'un process. Cela écoute si le workflow écrit un fichier chat_output.txt. Si oui le retour est stream par cette route. Elle reste ouverte tant que le chat n'a pas fini de générer des tokens.")
def chat(workflow_id):
    chemin_dossier = MetManagement.get_api_local_folder(workflow_id=workflow_id)
    if os.path.exists(chemin_dossier + ".chat_output.txt"):
        os.remove(chemin_dossier + ".chat_output.txt")
    return StreamingResponse(hlit_workflow_management.stream_tokens_from_file(chemin_dossier), media_type="text/event-stream")

@app.get("/kill-process/{key_name}", summary="Kill process", description="On passe la key name pour savoir si un process est en cours, si c'est le cas on le kill")
def kill_process(key_name):
    chemin_dossier = MetManagement.get_api_local_folder_admin()
    chemin_dossier = chemin_dossier + key_name + ".txt"
    message = hlit_workflow_management.kill_process(chemin_dossier,
                 "cmd.exe")
    return JSONResponse(
        status_code=200,
        content={"_statut": message}
    )


if __name__ == "__main__":
    print(MetManagement.get_local_store_path())
    lauch_uvicorn()
