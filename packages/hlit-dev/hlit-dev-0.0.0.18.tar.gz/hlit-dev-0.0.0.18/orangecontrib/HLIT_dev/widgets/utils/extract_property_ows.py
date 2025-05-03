import xml.etree.ElementTree as ET
import ast

def extract_node_properties_by_name(ows_path, target_name):
    """🔍 Extraction des propriétés pour un seul type de widget."""
    return extract_node_properties_by_names(ows_path, [target_name])


def extract_node_properties_by_names(ows_path, target_names):
    """🔍 Extraction des propriétés pour plusieurs types de widgets."""
    #print(f"🔍 Lecture du fichier OWS : {ows_path}")
    tree = ET.parse(ows_path)
    root = tree.getroot()

    # Créer un mapping node_id -> name
    #print("📦 Construction du mapping node_id -> node_name...")
    node_id_to_name = {
        node.attrib['id']: node.attrib.get('name', '')
        for node in root.find('nodes')
        if node.tag == 'node'
    }
    #print(node_id_to_name)
    #print(f"✅ {len(node_id_to_name)} nœuds détectés dans la section <nodes>.")

    results = []
    found = 0
    #print(f"\n🔎 Recherche des propriétés pour les widgets : {target_names}")
    for prop in root.find('node_properties'):
        node_id = prop.attrib['node_id']
        node_name = node_id_to_name.get(node_id, '')
        if node_name in target_names:
            found += 1
            prop_text = prop.text.strip()
            #print(f"\n📍 Propriétés trouvées pour node_id={node_id} ({node_name})")
            try:
                parsed_dict = ast.literal_eval(prop_text)
                results.append({
                    "node_id": node_id,
                    "node_name": node_name,
                    "properties": parsed_dict
                })
                #print(f"✅ Contenu extrait (clé(s) : {list(parsed_dict.keys())}):\n{parsed_dict}")
            except Exception as e:
                print(f"❌ Erreur de parsing pour node_id={node_id}: {e}")
                print(f"Texte brut:\n{prop_text}")
                return None

    #print(f"\n🎯 Total de nœuds correspondants : {found}")
    return results



def extract_property_for_hlit(ows_path):
    results=extract_node_properties_by_names(ows_path,["Input Interface","Output Interface"])
    if results is None:
        return None
    if len(results)==0:
        return None
    """
        Extrait les 'Input Interface' et 'Output Interface' dans l'ordre,
        et formate un JSON plat (liste de dictionnaires) avec les champs utiles.

        Args:
            results (list): Liste de nœuds du workflow (type list[dict])

        Returns:
            list or None: Liste ordonnée de dictionnaires JSON, ou None en cas d'erreur.
        """
    try:
        processed = []

        for node in results:
            if not isinstance(node, dict):
                continue  # sécurité : on ignore les objets non conformes

            node_name = node.get("node_name")
            props = node.get("properties", {})

            if node_name == "Input Interface":
                processed.append({
                    "node_name": node_name,
                    "workflow_id": props.get("workflow_id"),
                    "input_id": props.get("input_id"),
                    "help_description": props.get("help_description")
                })

        for node in results:
            if not isinstance(node, dict):
                continue

            node_name = node.get("node_name")
            props = node.get("properties", {})

            if node_name == "Output Interface":
                processed.append({
                    "node_name": node_name,
                    "workflow_id": props.get("workflow_id"),
                    "help_description": props.get("help_description")
                })

        return processed

    except Exception as e:
        print(f"[ERREUR] Impossible de traiter les nœuds : {e}")
        return None
# Exemple d'utilisation
if __name__ == "__main__":
    file = r"C:\test_bug_orange\aait_store\workloawfs_test1\ows\chatbot_1_mini.ows"
    print(extract_property_for_hlit(file))
    # # Pour un seul widget
    # results_one = extract_node_properties_by_name(file, "S3 File Downloader")
    # print(f"\n📋 Résultat [1 widget] : {len(results_one)} entrée(s) extraites.")
    #
    # # Pour plusieurs widgets
    # widget_names = ["S3 File Downloader", "Directory Selector"]
    # results_multi = extract_node_properties_by_names(file, widget_names)
    # print(f"\n📋 Résultat [multi-widget] : {len(results_multi)} entrée(s) extraites.")
