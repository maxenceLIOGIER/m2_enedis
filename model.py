from api import API

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score

class Model:
    def train_DPE_model(df):
        """
        Cette fonction permet de créer un modèle de classification de l'étiquette DPE
        """

        # Chargement des données locales
        df = pd.read_csv('assets/data_69.csv', sep='|')

        # Suppresion des colonnes informatives
        del_col = ['Nom commune', 'Date réception DPE', "Latitude", "Longitude", "Date_réception_DPE_graph"]
        df.drop(columns=del_col, inplace=True, errors='ignore')
        
        # Suppression des lignes avec des valeurs manquantes
        df = df.dropna()

        # Préparation des données pour le modèle
        df = pd.get_dummies(df, columns=[
            'Période construction', 
            'Type bâtiment', 
            'Classe altitude', 
            'Type énergie ECS', 
            'Type énergie chauffage'
        ])

        # Définition des variables explicatives et de la variable cible
        y = df["Étiquette DPE"]
        X = df.drop(columns=["Étiquette DPE"])

        # Sauvegarde des noms des colonnes
        feature_names = X.columns

        # Normalisation des données
        scaler = StandardScaler()
        X = scaler.fit_transform(X)

        # Séparation des données en jeu d'entraînement et jeu de test
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.30, stratify=y, random_state = 0)

        # Création du modèle
        model = MLPClassifier(random_state=0, hidden_layer_sizes=(100, 50), learning_rate_init=0.001, max_iter=300, tol=0.0001)
        model.fit(X_train, y_train)

        # Sauvegarde du modèle, du scaler et des noms des variables
        joblib.dump(model, 'model/model.pkl')
        joblib.dump(scaler, 'model/scaler.pkl')
        joblib.dump(feature_names, 'model/feature_names.pkl')

        # Évaluation du modèle
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Précision du modèle : {accuracy}")

    def predict_DPE_model(data):
        """
        Cette fonction permet de faire une prédiction de la classe énergétique
        """

        # Chargement du modèle, du scaler, et des noms des variables
        model = joblib.load('model/model.pkl')
        scaler = joblib.load('model/scaler.pkl')
        feature_names = joblib.load('model/feature_names.pkl')

        # Transformation de l'information "Année de construction" en "Période de construction"
        data['Période construction'] = data['Période construction'].apply(lambda x: 
            'avant 1948' if x < 1948 else
            '1948-1974' if 1948 <= x <= 1974 else
            '1975-1977' if 1975 <= x <= 1977 else
            '1978-1982' if 1978 <= x <= 1982 else
            '1983-1988' if 1983 <= x <= 1988 else
            '1989-2000' if 1989 <= x <= 2000 else
            '2001-2005' if 2001 <= x <= 2005 else
            '2006-2012' if 2006 <= x <= 2012 else
            '2013-2021' if 2013 <= x <= 2021 else
            'Après 2021'
        )

        # Récupération de l'altitude de la commune
        latitude, longitude = API().get_coordinates(data["Code postal"])
        if latitude and longitude:
            altitude = API.get_altitude(latitude, longitude)
            if altitude is not None:
                # Faire un case de l'ailtude en focntion de l'altitue
                if altitude < 400:
                    data["Classe altitude"] = "inférieur à 400m"
                elif altitude >= 400 and altitude <= 800:
                    data["Classe altitude"] = "400-800m"
                else:
                    data["Classe altitude"] = "supérieur à 800m"
                
            else:
                data["Classe altitude"] = "inférieur à 400m"
        else:
            data["Classe altitude"] = "inférieur à 400m"
        
        # Application des mêmes transformations que lors de l'entraînement
        data = pd.get_dummies(data, columns=[
            'Période construction', 
            'Type bâtiment', 
            'Classe altitude', 
            'Type énergie ECS', 
            'Type énergie chauffage'
        ])
        data = data.reindex(columns=feature_names, fill_value=0)
        data = scaler.transform(data)

        # Prédiction
        prediction = model.predict(data)
        return prediction[0]