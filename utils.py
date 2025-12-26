import json
from texts import text_one_dataset, text_sev_dataset, text_one_org, text_sev_orgs


def read_json(file_path):
    """Carga un json en un diccionario"""
    encodings = ['utf-8', 'latin-1', 'windows-1252']
    for encoding in encodings:
     try:
        with open(file_path,"r", encoding=encoding) as f:
            data = json.load(f)
            return data
     except:
        continue


def write_json(file_path, dict_data):
    """Vuelve un diccionario en un json"""
    with open(file_path, "w",encoding="utf-8") as f:
        json.dump(dict_data, f, indent=4, ensure_ascii=False)


def new_data_message(update_df,org_dict):
    """Elige el texto a usar de acuerdo a la cantidad de datasets nuevos"""
    if len(update_df) == 1:
        text = text_one_dataset(update_df, org_dict)
    else:
        text = text_sev_dataset(update_df,org_dict)
    return text


def new_org_message(org_updates, org_inter, ckan_portal):
    """Elige el texto a usar si hay nuevos nodos"""

    if len(org_inter) == 1:
        #alias = next((k for k, v in org_updates.items() if v == org_inter[0]), None)
        alias = org_inter[0]
        org_url = ckan_portal + "dataset?organization=" + alias
        text = text_one_org(alias, org_url, org_updates)
    else:
        text = text_sev_orgs(org_inter, org_updates, ckan_portal)

    return text
