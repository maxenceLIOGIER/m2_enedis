# Importation des librairies nécessaires
import requests
import pandas as pd

class API:
    # Constructeur de la classe
    def __init__(self, base_url):
        self.base_url = base_url

    # Méthode pour charger une page de données
    def get_data(self, url):
        response = requests.get(url)

        # Vérification du statut de la réponse
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erreur lors de la récupération des données : [{response.status_code}] {response.text}")

    # Méthode pour récupérer les données
    def get_all_data(self, query_params):
        all_data = []
        page_number = 1 
        total_lines = 0

        while True:
            try:
                url = self.base_url.format(**query_params)
                data = self.get_data(url)
                lines_added = len(data["results"])
                all_data.extend(data["results"])
                total_lines += lines_added
                
                print(f"Page {page_number} traitée : {lines_added} lignes ajoutées ({total_lines} lignes récupérées au total)")
                
                # Vérifier si 'next' existe pour continuer
                url = data.get("next")
                if not url:
                    break

                page_number += 1
            except Exception as e:
                print(f"Erreur lors du traitement : {str(e)}")
                break

        return all_data