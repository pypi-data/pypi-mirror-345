import sys
import json
import os
import psutil
import time
from pathlib import Path
if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.utils import MetManagement,subprocess_management
else:
    from orangecontrib.AAIT.utils import MetManagement,subprocess_management





def to_bool(value):
    """Convertit diverses représentations en booléen."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ["true", "1", "yes"]
    if isinstance(value, int):
        return value != 0
    return True  # Valeur par défaut si inconnue

def load_json_and_check_json_agregate(fichier_json, montab=[]):
    try:
        with open(fichier_json, 'r', encoding='utf-8') as file:
            data = json.load(file)

        required_fields = {"name", "ows_file", "html_file", "description"}

        for item in data:
            if not required_fields.issubset(item.keys()):
                return 1  # Erreur si un champ requis manque

            # Traitement des champs optionnels
            item["with_gui"] = to_bool(item.get("with_gui", True))
            item["with_terminal"] = to_bool(item.get("with_terminal", True))

            montab.append(item)

        return 0  # Tout est bon

    except (json.JSONDecodeError, FileNotFoundError, IOError) as e:
        print(f"Erreur: {e}")
        return 1

def read_config_ows_html_file_as_dict(out_put_tab=[]):
    del out_put_tab[:]
    folder_path = Path(MetManagement.get_path_linkHTMLWorkflow())
    le_tab=[]
    for file_path in folder_path.glob('*.json'):
        if 0!=load_json_and_check_json_agregate(file_path,le_tab):
            print("error reading ",file_path)
            return 1
    if len(le_tab)==0:
        print("error no json loaded from", folder_path)
        return 1
    # crate absolute path
    for idx,_ in enumerate(le_tab):
        le_tab[idx]['html_file']=MetManagement.TransfromStorePathToPath(le_tab[idx]['html_file'])
        le_tab[idx]['ows_file']=MetManagement.TransfromStorePathToPath(le_tab[idx]['ows_file'])

    # on verifie que l on a pas deux fois le meme nom
    seen_names = set()
    for item in le_tab:
        if item["name"] in seen_names:
            print("error in json several use of :"+str(item["name"]))
            return 1
        seen_names.add(item["name"])
    for element in le_tab:
        out_put_tab.append(element)
    return 0


def open_local_html(list_config_html_ows,name):
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    a_lancer=""
    try:
        for element in list_config_html_ows:
            print(element)
            if element["name"]==name:
                print(os.name)
                if os.name == "posix":
                    a_lancer=f'file://{element["html_file"]}'
                    print(a_lancer)
                else:
                    a_lancer='"'+edge_path+'" "'+element['html_file']+'"'


    except Exception as e:
        print(e)
        return 1
    if a_lancer=="":
        print("aucun html trouvé")
        return 1
    if os.name == "posix":
        import webbrowser
        webbrowser.open(a_lancer)
        print("Gérer les exceptions correctement sur Mac ici!!!!")
        return 0
    else:
        result,PID=subprocess_management.execute_command(a_lancer,hidden=True)
    return result


def is_process_running(pid):
    return psutil.pid_exists(pid)

def get_process_name(pid):
    try:
        p = psutil.Process(pid)
        return p.name()
    except psutil.NoSuchProcess:
        return None

def write_PID_to_file(name: str, number: int) -> int:
    """
    Writes an integer to a file named "name.txt" inside a folder named "name".
    Handles exceptions related to file operations.
    Returns 0 if successful, 1 if an error occurs.
    """
    try:
        # Create directory if it does not exist

        dirname=MetManagement.get_api_local_folder_admin()
        os.makedirs(dirname, exist_ok=True)
        # Define file path
        file_path = os.path.join(dirname, f"{name}.txt")

        # Write the integer to the file
        with open(file_path, 'w') as file:
            file.write(str(number))

        return 0  # Success
    except Exception as e:
        print(f"Error: {e}")
        return 1  # Error
import subprocess

def is_defunct_or_not_used_only_posix(pid: int) -> bool:
    if os.name !="posix":
        return False
    try:
        # Appel de ps pour obtenir l'état du processus
        result = subprocess.run(
            ['ps', '-o', 'stat=', '-p', str(pid)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )
        state = result.stdout.strip()
        if not state:
            print(f"PID {pid} not found.")
            return True
        if 'Z' in state:
            print(f"PID {pid} is defunct (zombie).")
            return True
        else:
            print(f"PID {pid} is not defunct.")
            return False
    except Exception as e:
        print(f"Error checking PID {pid}: {e}")
        return False


def check_file_and_process(name: str) -> int:
    """
    Checks if "name.txt" exists in the "name" directory.
    If it exists, reads its content as an integer.
    If a process with that integer as PID exists, returns 2.
    If not, deletes the file and returns the integer.
    If the file does not exist return 0
    If an error occurs, returns 1.
    """
    print("a refaire")
    #return 0
    try:
        dirname=MetManagement.get_api_local_folder_admin()
        # Define file path
        file_path = os.path.join(dirname, f"{name}.txt")

        # Check if file exists
        if not os.path.isfile(file_path):
            return 0
        print(file_path+ " existe")
        # Read the integer from the file
        with open(file_path, 'r') as file:
            content = file.read().strip()

        if not content.isdigit():
            return 1

        process_id = int(content)
        print(process_id)
        # processus zombie de mac
        if is_defunct_or_not_used_only_posix(process_id):
            os.remove(file_path)
            return 0
        # Check if a process with this PID exists
        if process_id in [p.pid for p in psutil.process_iter()]:
            print("process deja en existant")
            return 2

        # If no such process exists, delete the file
        os.remove(file_path)

        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


def start_workflow(list_config_html_ows,name):
    """Launch a workflow using the command line and store the process information.
    retun 1 -> erro
    return 0 ->> ok
    retrun 2 -> workflow alrwready used"""
    workflow_path=""
    with_terminal = True
    gui = True
    try:
        for element in list_config_html_ows:
            if element["name"]==name:
                print(element)
                workflow_path=element['ows_file']
                with_terminal=element['with_terminal']
                gui=element['with_gui']

    except Exception as e:
        print(e)
        return 1
    if workflow_path=="":
        print("no ows file found in json config")
        return 1
    if not os.path.isfile(workflow_path):
        print(workflow_path+" doesn t existe")
        return 1
    res=check_file_and_process(name)
    if res==1:
        return 1
    if res==2:
        return 2
    print("je viens jusque ici")
    workflow_directory=Path(os.path.dirname(workflow_path))
    print(workflow_directory)
    # clean file to aviod erreor
    for file in workflow_directory.glob("*.ows.swp.*"):
        file.unlink()
    env = dict(os.environ)
    if not gui:
        if sys.platform.startswith("darwin"):
            # Sur Mac, offscreen peut poser problème si pas dans une session graphique
            # Donc on peut soit afficher un warning soit ne pas forcer offscreen
            print("Attention: 'offscreen' forcé sur Mac peut être instable.")
        else:
            env['QT_QPA_PLATFORM'] = 'offscreen'
    # 2. Construct the command to run the workflow
    python_path = Path(sys.executable)
    print(python_path)
    workflow_path=str(workflow_path)
    print(workflow_path)
    if os.name == "nt":
        workflow_path=workflow_path.replace('/','\\')

    command = str(python_path)+ ' -m Orange.canvas '+ workflow_path
    print(command)


    PID=None
    print(gui)
    try:
        if with_terminal:
            PID = subprocess_management.open_terminal(command, with_qt=gui, env=env)
        else:
            PID = subprocess_management.open_hide_terminal(command, with_qt=gui, env=env)
    except Exception as e:
        print(e)
        return 1

    print("le PID",PID)
    return write_PID_to_file(name,PID)

def check_if_timout_is_reached(chemin_dossier):
    list_config_html_ows = []
    if 0 != read_config_ows_html_file_as_dict(list_config_html_ows):
        return 0
    if os.path.exists(chemin_dossier + "config.json"):
        with open(chemin_dossier + "config.json", "r", encoding="utf-8") as file:
            config_json = json.load(file)
        timeout = None
        for elem in list_config_html_ows:
            if elem["name"] == config_json["workflow_id"]:
                if "timeout" in elem:
                    timeout = elem["timeout"]
                    break
        if timeout:
            if os.path.exists(chemin_dossier + "time.txt"):
                second_file = MetManagement.read_file_time(chemin_dossier + "time.txt")
                second_now = MetManagement.get_second_from_1970()
                second_since_workflow_launch = second_now - second_file
                if second_since_workflow_launch > timeout:
                    MetManagement.reset_folder(chemin_dossier, recreate=False)
                    return 1
                else:
                    return 0
            else:
                return 0
        else:
            return 0
    else:
        return 0

def stream_tokens_from_file(chemin_dossier: str, timeout: float = 5.0):
    filepath = chemin_dossier + "chat_output.txt"
    while not os.path.exists(filepath):
        time.sleep(0.01)
        if 1== check_if_timout_is_reached(chemin_dossier):
            print("timeout reached")
            return

    last_position = 0
    last_activity = time.time()
    buffer = ""

    while True:
        with open(filepath, 'r', encoding='utf-8') as f:
            f.seek(last_position)
            chunk = f.read()
            if chunk:
                buffer += chunk
                last_position = f.tell()
                last_activity = time.time()

                # On attend un espace ou une ponctuation avant d'envoyer
                while True:
                    # Chercher un point de coupure sûr
                    match = None
                    for i in range(len(buffer)-1, -1, -1):
                        if buffer[i] in " \n.,;!?":
                            match = i + 1
                            break

                    if match:
                        to_send = buffer[:match]
                        buffer = buffer[match:]
                        yield f"{to_send}"
                    else:
                        break
            else:
                time.sleep(0.05)

        if time.time() - last_activity > timeout:
            if buffer.strip():
                yield f"{buffer}"
            yield "[DONE]"
            break


def kill_process(file, type="cmd.exe"):
    if not os.path.exists(file):
        print("your file does not exist")
        return "your file does not exist"
    with open(file,"r") as f:
        pid = f.read()
    pid = int(pid)
    if not is_process_running(pid):
        print("process not running")
        return "process not running"
    name = get_process_name(pid)
    if os.name =="posix":
        subprocess_management.kill_process_tree(pid)
        return "Process kill"
    if name == type:
        subprocess_management.kill_process_tree(pid)

    if psutil.pid_exists(pid):
        p = psutil.Process(pid)
        print(f"Nom: {p.name()}")
        print(f"Status: {p.status()}")
        print(f"Executable: {p.exe()}")
        print(f"Parent PID: {p.ppid()}")
    else:
        print("Le processus n'existe pas.")
    return "Process kill"


if __name__ == "__main__":
    list_config_html_ows=[]
    if 0!= read_config_ows_html_file_as_dict(list_config_html_ows):
        print("an error occurs")
        exit(1)
    print(list_config_html_ows)
    # if 0!=open_local_html(list_config_html_ows,"nom simpathique2"):
    #     print("an error occurs")
    #     exit(1)

    pid = os.getpid()
    print(f"Le PID du processus Python en cours est : {pid}")
    exit(0)
    if None!=start_workflow(list_config_html_ows,"toto.ows"):
        print("ok")
        time.sleep(15)
        kill_process(r"C:\Users\max83\Desktop\Orange_4All_AAIT\Orange_4All_AAIT\aait_store\exchangeApi_adm\toto.ows.txt", "cmd.exe")
