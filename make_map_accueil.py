import pandas as pd
import geopandas as gpd
import folium
import webbrowser

# Charger les données
df = pd.read_csv('Data/PremierTour2024/resultats-definitifs-par-departements.csv', sep=';')

# Colonnes de nuances et voix
nuance_cols = [col for col in df.columns if "Nuance candidat" in col]
voix_cols = [col for col in df.columns if "Voix" in col and "exprimés" not in col and "%" not in col]

# Dictionnaires
couleurs = {
    "Gauche": "#E90000",
    "Centre": "#FF9F0E",
    "Droite": "#0890C5",
    "Régionaliste": "#78668D",
    "Extrême droite": "#8D6026",
    "Autre": "#AF95CC"
}

nuance_to_group = {
    "UG": "Gauche", "DVG": "Gauche",
    "DVC": "Centre", "ENS": "Centre", "HOR": "Centre", "UDI": "Centre",
    "LR": "Droite", "DVD": "Droite",
    "RN": "Extrême droite", "UXD": "Extrême droite", "DSV": "Extrême droite", "REC": "Extrême droite", "EXD": "Extrême droite",
    "REG": "Régionaliste", "DIV": "Autre"
}

"""
# Fonction pour calculer la nuance majoritaire
def get_nuance_majoritaire(row):
    max_voix = 0
    nuance_maj = None
    for nuance_col, voix_col in zip(nuance_cols, voix_cols):
        if pd.isna(row[voix_col]) or pd.isna(row[nuance_col]):
            continue
        if row[voix_col] >= max_voix:
            max_voix = row[voix_col]
            nuance_maj = row[nuance_col]
    return nuance_maj

# Appliquer la fonction
df["nuance_majoritaire"] = df.apply(get_nuance_majoritaire, axis=1)
df["groupe_majoritaire"] = df["nuance_majoritaire"].map(nuance_to_group)
df["couleur"] = df["groupe_majoritaire"].map(couleurs)

# Charger le GeoJSON
gdf = gpd.read_file("Data/departements.geojson")

# Extraire le code département
if "code" in gdf.columns:
    gdf["codeDepartement"] = gdf["code"].astype(str)
elif "properties" in gdf.columns:
    if isinstance(gdf["properties"].iloc[0], dict):
        gdf["codeDepartement"] = gdf["properties"].apply(lambda x: x.get("code", None)).astype(str)
    else:
        import json
        gdf["codeDepartement"] = gdf["properties"].apply(
            lambda x: json.loads(x).get("code") if isinstance(x, str) else None
        ).astype(str)
else:
    raise ValueError("Colonne 'code' ou 'properties' introuvable dans le GeoJSON.")

# Renommer la colonne du CSV si nécessaire
if "Code département" in df.columns:
    df.rename(columns={"Code département": "codeDepartement"}, inplace=True)
df["codeDepartement"] = df["codeDepartement"].astype(str)

# Fusionner les données
gdf = gdf.merge(
    df[["codeDepartement", "groupe_majoritaire", "couleur"]],
    on="codeDepartement",
    how="left"
)

# Vérification
print("Colonnes dans gdf après fusion :", gdf.columns.tolist())
print("Exemple de ligne :\n", gdf[["codeDepartement", "groupe_majoritaire", "couleur"]].head())

# Sauvegarder le GeoJSON
gdf.to_file("departements_avec_couleur.geojson", driver="GeoJSON")
"""

#on évite les problèmes, on modifie que ce qu'on a déjà créer sans toucher à ce qu'on a déjà créer
gdf = gpd.read_file("departements_avec_couleur.geojson")
# Créer la carte
m = folium.Map(location=[46.603354, 1.888334], zoom_start=6)

# Ajouter les départements colorés
folium.GeoJson(
    gdf,
    style_function=lambda feature: {
        "fillColor": feature["properties"].get("couleur", "#CCCCCC"),
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.7,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["nom", "groupe_majoritaire"],  # Remplace "nom" par le bon nom de colonne
        aliases=["Département:", "Groupe majoritaire:"],
        localize=True,
    ),
    id = "departements_layer"
).add_to(m)

# Légende
legend_items = [
    f'<i style="background:{color}; width:18px; height:18px; display:inline-block; border:1px solid black;"></i> {groupe}'
    for groupe, color in couleurs.items()
]
legend_html = f"""
<div style="position: fixed; bottom: 50px; left: 50px; width: 250px; height: auto;
     border:2px solid grey; z-index:9999; font-size:14px; background-color:white; padding: 10px;">
<b>Légende des groupes politiques</b><br>
{'<br>'.join(legend_items)}
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# Sauvegarder et ouvrir
m.save("carte_departements_par_groupe_majoritaire_interactive.html")

webbrowser.open("carte_departements_par_groupe_majoritaire_interactive.html")
