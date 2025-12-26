import json
import pandas as pd
import datetime
import os
import logging
import requests
from requests.exceptions import ChunkedEncodingError, RequestException
import time
from utils import write_json,read_json

logger = logging.getLogger(__name__)




def safe_get(url, retries=3, backoff=5, timeout=30):
    """Hace un GET con reintentos en caso de error de conexión."""
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp
        except ChunkedEncodingError:
            print(f"⚠️ Respuesta interrumpida para {url}, intento {attempt}/{retries}")
        except RequestException as e:
            print(f"⚠️ Error en {url}: {e} (intento {attempt}/{retries})")

        time.sleep(backoff * attempt)  # espera progresiva

    raise RuntimeError(f"No se pudo obtener datos de {url} después de {retries} intentos")



def get_current_datasets(ckan_url, chunk_size=10, max_limit=None):

    full_datasets = {}
    start = 0

    while True:
        url = f"{ckan_url}api/3/action/package_search?rows={chunk_size}&start={start}"
        resp = safe_get(url)
        data = resp.json()

        results = data["result"]["results"]
        if not results:
            break

        for dataset in results:
            full_datasets[dataset["id"]] = {
                k: v for k, v in dataset.items() if k != "resources"
            }

        start += chunk_size

        if max_limit and len(full_datasets) >= max_limit:
            break

    return full_datasets



def get_current_orgs(ckan_url):
    """Trae info de organizaciones del portal. Toma un parámetro: una url de un CKAN. Devuelve
        un diccionario con el alias y el nombre completo de cada organización presente."""

    url = ckan_url + "api/3/action/organization_list?all_fields=true"
    org_list = [
        {"name": org["name"], "display_name": org["display_name"]}
        for org in requests.get(url).json()["result"]
    ]
    return org_list


def scan_organizations(org_list, file_path):
    """Toma el diccionario preexistente de organizaciones y, si hay nuevas,
    le agrega las nuevas y las flagea como True"""

    last_data = read_json(file_path)
    last_org_list = last_data['organizations']
    if len(org_list) > len(last_org_list):
        existing_names = {org["name"] for org in last_org_list}
        merged = list(last_org_list)
        for org in org_list:
            if org["name"] not in existing_names:
                merged.append({
                    "name": org["name"],
                    "display_name": org["display_name"],
                    "new": True
                })
        return merged
    else:
        return last_org_list


def scan_updates(new_data, org_list, file_path, missing_path, ckan_url):
    """
    Guarda en un JSON con el estado de un CKAN (datasets disponibles, organizaciones,etc). Si el
     json ya existe (se creó en interaciones anteriores), se procede a usarlo para comparar
     con el CKAN e identificar adiciones en este.

    Parámetros
    ----------
    new_data: dict -  diccionario con datasets
    org_dict:dict - diccionario con organizaciones
    file_path - string con el nombre o ruta del archivo de persistencia. Si no existe se crea con el
    nombre elegido.
    ckan_url - Enlace a un CKAN.

    Returns
    -------
    pandas.DataFrame or None
        Devuelve un DataFrame con los nuevos datasets detectados, incluyendo su ID, título, organismo
        y contacto. Si no se detectan diferencias, devuelve None.
    """

    new_dataset_list = list(new_data.keys())
    if not os.path.exists(file_path):
        data = {
                    "date": datetime.datetime.now().strftime("%d/%m/%Y"),
                    "total_datasets": len(new_dataset_list),
                    "dataset_ids": {},
                    "organizations": org_list
                }
        for k,v in new_data.items():
            data["dataset_ids"][k] = v['title']
        write_json(file_path, data)
        return None
    last_data = read_json(file_path)
    last_dataset_list = list(last_data['dataset_ids'].keys())
    base_url = ckan_url+"dataset/"
    #Se identifican y obtiene info de datasets en datos.gob.ar que no
    # estaban en estado anterior
    diffs = list(set(new_dataset_list)-set(last_dataset_list))
    diffs_df = pd.DataFrame(columns=["id", "title","maintainer", "org", "link", "contact"])
    for diff in diffs:
        id = new_data[diff]['id']
        title = new_data[diff]['title']
        maintainer = new_data[diff]['maintainer']
        org = new_data[diff]['organization']['name']
        link = base_url+id
        contact = new_data[diff]['author_email']
        row = [id,title,maintainer,org,link,contact]
        row = ["" if x is None else x for x in row]
        diffs_df.loc[len(diffs_df)]=row
    #Se les saca a las novedades las que estén en missing...se actualiza missing
    if os.path.exists(missing_path):
        missings = read_json(missing_path)
        missing_ids = list(missings.keys())
        missing_titles = list(missings.values())
        original_df = diffs_df
        diffs_df = diffs_df.loc[~diffs_df['id'].isin(missing_ids)]
        diffs_df= diffs_df.loc[~diffs_df['title'].isin(missing_titles)]
        present_ids = original_df['id'].tolist()
        present_titles = original_df['title'].tolist()
        found_ids = [i for i in missing_ids if i in present_ids]
        found_titles = [t for t in missing_titles if t in present_titles]
        current_missings = {
                k: v for k, v in missings.items()
                if k not in found_ids and v not in found_titles
            }
        write_json(missing_path,current_missings)

    missing_diffs = list(set(last_dataset_list) - set(new_dataset_list))
    if os.path.exists(missing_path):
        current_missings = read_json(missing_path)
    else:
        current_missings = {}
    for mdiff in missing_diffs:
        current_missings[mdiff] = last_data['dataset_ids'][mdiff]
    write_json(missing_path,current_missings)

    if len(diffs_df)>0:
        return diffs_df
    else:
        return None


def save_ckan_state(data_dict, org_updates, file_path):
    new_dataset_list = list(data_dict.keys())
    new_data = {
        "date": datetime.datetime.now().strftime("%d/%m/%Y"),
        "total_datasets": len(new_dataset_list),
        "dataset_ids": {},
        "organizations": org_updates
    }
    for k, v in data_dict.items():
        new_data["dataset_ids"][k] = v['title']

    write_json(file_path, new_data)
    logger.info("guardando nuevos datasets y organizaciones en memoria")

