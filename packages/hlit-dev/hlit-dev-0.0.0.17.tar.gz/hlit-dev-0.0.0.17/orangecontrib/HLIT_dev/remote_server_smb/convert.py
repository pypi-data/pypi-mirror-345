import os
import shutil
import time
import json
import Orange
from Orange.data import Table, Domain, StringVariable, ContinuousVariable
import math

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.HLIT_dev.remote_server_smb import convert
else:
    from orangecontrib.HLIT_dev.remote_server_smb import convert

def is_valid_json_string(data):
    try:
        json_str = json.dumps(data)
        json.loads(json_str)
        return 0
    except json.JSONDecodeError:
        return 1

def convert_json_to_orange_data_table(json_data):
    """
        Convertit une liste de dictionnaires JSON en un objet de données de type data table sous Orange data Mining (.tab)
        Exemple de json_data qui peut etre utilisé pour cette fonction :
        {"ows_path": "toto.ows", "front_id": "11OO1O1O1", "data": [{"num_input": 0, "values": [["col1", "col2", "col3"], ["float", "str", "float"], [[3, "test", 6], [4, "oui", 5]]]}]}

        :param json_data: Chaine json au format d'exemple
        :return: Data Table.
    """
    if is_valid_json_string(json_data) == 1:
        print("La data n'est pas au format json")
        return 1
    json_str = json.dumps(json_data)
    data = json.loads(json_str)
    domain = []
    data_continous = []
    data_metas = []
    table = []
    attributes = []
    metas = []
    for i, d in enumerate(data["values"][1]):
        if d == "str":
            metas.append(StringVariable(data["values"][0][i]))
        if d == "float":
            attributes.append(ContinuousVariable(data["values"][0][i]))
    for elem in data["values"][2]:
        if len(elem) != len(data["values"][1]):
            print("Il manque des données par rapport au nombre de colonnes")
            return 1
        d_metas = []
        d_continous = []
        for i, d in enumerate(data["values"][1]):
            if d == "str":
                d_metas.append(elem[i])
            if d == "float":
                d_continous.append(elem[i])
        data_metas.append(d_metas)
        data_continous.append(d_continous)
    domain = Domain(attributes, metas=metas)
    table = Table.from_numpy(domain, data_continous, metas=data_metas)
    #table.save("table_data.tab")
    return table

def safe_val(val):
    return "" if isinstance(val, float) and math.isnan(val) else val

def convert_data_table_to_json(data):
    """
        Convertit un objet de données de type data table sous Orange data Mining (.tab) en une liste de dictionnaires JSON.

        :param data: Objet contenant les données avec ses attributs et métadonnées.
        :return: Chaîne JSON formatée.
    """

    if data == None or data == []:
        print("Pas de data en entree")
        return 1
    feature_names = [var.name for var in data.domain.attributes]
    meta_names = [var.name for var in data.domain.metas]
    json_data = []
    for row in data:
        row_dict = {col: safe_val(row[i]) for i, col in enumerate(feature_names)}
        for i, col in enumerate(meta_names):
            row_dict[col] = safe_val(row.metas[i])
        # Vérifier si la ligne contient uniquement des types (ex: "continuous", "discrete")
        if all(isinstance(value, str) and value in ["continuous", "discrete"] for value in row_dict.values()):
            continue  # Ignorer cette ligne

        json_data.append(row_dict)
    return json_data

if __name__ == "__main__":
    json_data = {'ows_path': 'toto.ows', 'front_id': '11OO1O1O1', 'data': [{'num_input': 0, 'values': [['col1', 'col2', 'col3'], ['float', 'str', 'float'], [[3, 'test', 6], [4, 'oui', 5]]]}]}
    convert_json_to_orange_data_table(json_data)
    #data = Orange.data.Table("table_data.tab")
    #json = convert_data_table_to_json(data)
    #print(json)


