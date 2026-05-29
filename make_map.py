import pandas as pd
import geopandas as gpd
import folium

df = pd.read_csv('Data/resultats-definitifs-par-circonscription.csv', sep=';')

nuance_cols = [col for col in df.columns if "Nuance candidat" in col]
voix_cols = [col for col in df.columns if "Voix" in col and "exprimés" not in col and "%" not in col]

couleurs = {
    "UG": "#A11870",
    "RN": "#8D6026",
    "ENS": "#FF9F0E",
    "LR": "#0890C5",
    "UXD": "#8D6026",
    "DVD": "#6387A8",
    "HOR": "#FF9F0E",
    "UDI": "#FF9F0E",
    "DVG": "#DA679E",
    "REG": "#78668D",
    "DVC": "#E1B000",
    "DIV": "#DA679E"
    }

def get_nuance_majoritaire(row):
    max_voix = 0
    nuance_maj = None
    for nuance_col, voix_col in zip(nuance_cols, voix_cols):
        if row[voix_col] == "NaN" or row[nuance_col] == "NaN":
            continue
        if row[voix_col] > max_voix:
            max_voix = row[voix_col]
            nuance_maj = row[nuance_col]
    return nuance_maj

df["nuance_majoritaire"] = df.apply(get_nuance_majoritaire, axis=1)

df["couleur"] = df["nuance_majoritaire"].map(couleurs)

gdf = gpd.read_file("Data/circonscriptions-legislatives-p10.geojson")

if "properties" in gdf.columns:
    # Extraire le code depuis les propriétés
    gdf["codeCirconscription"] = gdf["properties"].apply(lambda x: x.get("Code circonscription législative", None))

df.rename(columns={"Code circonscription législative": "codeCirconscription"}, inplace=True)

gdf["codeCirconscription"] = gdf["codeCirconscription"].astype(str)
df["codeCirconscription"] = df["codeCirconscription"].astype(str)

gdf = gdf.merge(
    df[["codeCirconscription", "nuance_majoritaire", "couleur"]],
    on="codeCirconscription",
    how="left"
)

# Sauvegarder le GeoJSON mis à jour (optionnel)
gdf.to_file("circonscriptions_avec_couleur.geojson", driver="GeoJSON")

#Filtrage

m = folium.Map(location=[46.603354, 1.888334], zoom_start=6)

# Ajouter les circonscriptions colorées
folium.GeoJson(
    gdf,
    style_function=lambda feature: {
        "fillColor": feature["properties"]["couleur"],
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.7,
    },
    tooltip=folium.GeoJsonTooltip(
    fields=["nomCirconscription", "nuance_majoritaire"],
    aliases=["Circonscription:", "Nuance majoritaire:"],
    localize=True,
    )
).add_to(m)


# Générer le HTML de la légende
legend_items = [f'<i style="background:{color}; width:18px; height:18px; display:inline-block; border:1px solid black;"></i> {nuance}'
                for nuance, color in couleurs.items()]
legend_html = f"""
<div style="position: fixed;
     bottom: 50px; left: 50px; width: 250px; height: auto;
     border:2px solid grey; z-index:9999; font-size:14px;
     background-color:white;
     padding: 10px;">
<b>Légende des nuances politiques</b><br>
{'<br>'.join(legend_items)}
</div>
"""

# Ajouter la légende à la carte
m.get_root().html.add_child(folium.Element(legend_html))

# 5. Sauvegarder la carte dans un fichier HTML
m.save("carte_circonscriptions_par_nuance_majoritaire.html")

# 6. Ouvrir automatiquement la carte dans le navigateur (optionnel)
import webbrowser
webbrowser.open("carte_circonscriptions_par_nuance_majoritaire.html")