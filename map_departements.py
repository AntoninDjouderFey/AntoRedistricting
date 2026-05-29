import pandas as pd
import geopandas as gpd
import folium
import webbrowser

# Charger les données
df = pd.read_csv('Data/PremierTour2024/resultats-definitifs-par-circonscriptions-legislatives(1).csv', sep=';')

nuance_cols = [col for col in df.columns if "Nuance candidat" in col]
voix_cols = [col for col in df.columns if "Voix" in col and "exprimés" not in col and "%" not in col]


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
df.rename(columns={"Code circonscription législative": "codeCirconscription"}, inplace=True)
df["codeCirconscription"] = df["codeCirconscription"].astype(str).str.zfill(4)
df["nuance_majoritaire"] = df.apply(get_nuance_majoritaire, axis=1)
df["groupe_majoritaire"] = df["nuance_majoritaire"].map(nuance_to_group)
df["couleur"] = df["groupe_majoritaire"].map(couleurs)

df.to_csv("resultats_paris.csv", index=False)

gdf = gpd.read_file("Data/circonscriptions-legislatives-p10.geojson")

if "properties" in gdf.columns:
    # Extraire le code depuis les propriétés
    gdf["codeCirconscription"] = gdf["properties"].apply(lambda x: x.get("Code circonscription législative", None))

gdf["codeCirconscription"] = gdf["codeCirconscription"].astype(str)
df["codeCirconscription"] = df["codeCirconscription"].astype(str)

# Dans la fusion, ajouter groupe_majoritaire :
gdf = gdf.merge(
    df[["codeCirconscription", "nuance_majoritaire", "groupe_majoritaire", "couleur"]],  # <-- Ajout de groupe_majoritaire
    on="codeCirconscription",
    how="left"
)

departements = {
    # Métropole
    "01": "Ain",
    "02": "Aisne",
    "03": "Allier",
    "04": "Alpes-de-Haute-Provence",
    "05": "Hautes-Alpes",
    "06": "Alpes-Maritimes",
    "07": "Ardèche",
    "08": "Ardennes",
    "09": "Ariège",
    "10": "Aube",
    "11": "Aude",
    "12": "Aveyron",
    "13": "Bouches-du-Rhône",
    "14": "Calvados",
    "15": "Cantal",
    "16": "Charente",
    "17": "Charente-Maritime",
    "18": "Cher",
    "19": "Corrèze",
    "2A": "Corse-du-Sud",
    "2B": "Haute-Corse",
    "21": "Côte-d'Or",
    "22": "Côtes-d'Armor",
    "23": "Creuse",
    "24": "Dordogne",
    "25": "Doubs",
    "26": "Drôme",
    "27": "Eure",
    "28": "Eure-et-Loir",
    "29": "Finistère",
    "30": "Gard",
    "31": "Haute-Garonne",
    "32": "Gers",
    "33": "Gironde",
    "34": "Hérault",
    "35": "Ille-et-Vilaine",
    "36": "Indre",
    "37": "Indre-et-Loire",
    "38": "Isère",
    "39": "Jura",
    "40": "Landes",
    "41": "Loir-et-Cher",
    "42": "Loire",
    "43": "Haute-Loire",
    "44": "Loire-Atlantique",
    "45": "Loiret",
    "46": "Lot",
    "47": "Lot-et-Garonne",
    "48": "Lozère",
    "49": "Maine-et-Loire",
    "50": "Manche",
    "51": "Marne",
    "52": "Haute-Marne",
    "53": "Mayenne",
    "54": "Meurthe-et-Moselle",
    "55": "Meuse",
    "56": "Morbihan",
    "57": "Moselle",
    "58": "Nièvre",
    "59": "Nord",
    "60": "Oise",
    "61": "Orne",
    "62": "Pas-de-Calais",
    "63": "Puy-de-Dôme",
    "64": "Pyrénées-Atlantiques",
    "65": "Hautes-Pyrénées",
    "66": "Pyrénées-Orientales",
    "67": "Bas-Rhin",
    "68": "Haut-Rhin",
    "69": "Rhône",
    "70": "Haute-Saône",
    "71": "Saône-et-Loire",
    "72": "Sarthe",
    "73": "Savoie",
    "74": "Haute-Savoie",
    "75": "Paris",
    "76": "Seine-Maritime",
    "77": "Seine-et-Marne",
    "78": "Yvelines",
    "79": "Deux-Sèvres",
    "80": "Somme",
    "81": "Tarn",
    "82": "Tarn-et-Garonne",
    "83": "Var",
    "84": "Vaucluse",
    "85": "Vendée",
    "86": "Vienne",
    "87": "Haute-Vienne",
    "88": "Vosges",
    "89": "Yonne",
    "90": "Territoire de Belfort",
    "91": "Essonne",
    "92": "Hauts-de-Seine",
    "93": "Seine-Saint-Denis",
    "94": "Val-de-Marne",
    "95": "Val-d'Oise",
}

coords = {
    # Métropole
    "01": [46.0, 5.2],        # Ain
    "02": [49.5, 3.5],        # Aisne
    "03": [46.5, 3.0],        # Allier
    "04": [44.0, 6.0],        # Alpes-de-Haute-Provence
    "05": [44.5, 5.5],        # Hautes-Alpes
    "06": [43.8, 7.0],        # Alpes-Maritimes
    "07": [44.5, 4.5],        # Ardèche
    "08": [49.7, 4.5],        # Ardennes
    "09": [43.0, 1.5],        # Ariège
    "10": [48.3, 4.0],        # Aube
    "11": [43.2, 2.5],        # Aude
    "12": [44.2, 2.8],        # Aveyron
    "13": [43.5, 5.2],        # Bouches-du-Rhône
    "14": [49.0, -0.2],       # Calvados
    "15": [45.0, 2.5],        # Cantal
    "16": [45.7, 0.0],        # Charente
    "17": [46.0, -1.0],       # Charente-Maritime
    "18": [47.0, 2.5],        # Cher
    "19": [45.3, 1.8],        # Corrèze
    "2A": [41.8, 9.0],        # Corse-du-Sud
    "2B": [42.3, 9.0],        # Haute-Corse
    "21": [47.3, 5.0],        # Côte-d'Or
    "22": [48.5, -2.8],       # Côtes-d'Armor
    "23": [46.0, 2.2],        # Creuse
    "24": [45.0, 0.5],        # Dordogne
    "25": [47.0, 6.2],        # Doubs
    "26": [44.8, 5.0],        # Drôme
    "27": [49.0, 1.0],        # Eure
    "28": [48.5, 1.3],        # Eure-et-Loir
    "29": [48.2, -4.0],       # Finistère
    "30": [44.0, 4.0],        # Gard
    "31": [43.5, 1.5],        # Haute-Garonne
    "32": [43.8, 0.5],        # Gers
    "33": [44.8, -0.5],       # Gironde
    "34": [43.6, 3.5],        # Hérault
    "35": [48.0, -1.8],       # Ille-et-Vilaine
    "36": [46.8, 1.5],        # Indre
    "37": [47.2, 0.8],        # Indre-et-Loire
    "38": [45.3, 5.5],        # Isère
    "39": [46.7, 5.8],        # Jura
    "40": [44.0, -0.8],       # Landes
    "41": [47.6, 1.3],        # Loir-et-Cher
    "42": [45.7, 4.0],        # Loire
    "43": [45.0, 3.8],        # Haute-Loire
    "44": [47.2, -1.5],       # Loire-Atlantique
    "45": [47.9, 2.2],        # Loiret
    "46": [44.5, 1.5],        # Lot
    "47": [44.2, 0.5],        # Lot-et-Garonne
    "48": [44.5, 3.5],        # Lozère
    "49": [47.3, -0.5],       # Maine-et-Loire
    "50": [49.0, -1.2],       # Manche
    "51": [48.9, 4.0],        # Marne
    "52": [48.3, 5.0],        # Haute-Marne
    "53": [48.3, -0.5],       # Mayenne
    "54": [48.7, 6.0],        # Meurthe-et-Moselle
    "55": [49.0, 5.3],        # Meuse
    "56": [47.8, -3.0],       # Morbihan
    "57": [49.0, 6.3],        # Moselle
    "58": [47.0, 3.5],        # Nièvre
    "59": [50.5, 3.0],        # Nord
    "60": [49.4, 2.5],        # Oise
    "61": [48.8, 0.0],        # Orne
    "62": [50.5, 2.5],        # Pas-de-Calais
    "63": [45.8, 3.0],        # Puy-de-Dôme
    "64": [43.3, -0.8],       # Pyrénées-Atlantiques
    "65": [43.0, 0.0],        # Hautes-Pyrénées
    "66": [42.7, 2.5],        # Pyrénées-Orientales
    "67": [48.5, 7.5],        # Bas-Rhin
    "68": [48.0, 7.2],        # Haut-Rhin
    "69": [45.8, 4.8],        # Rhône
    "70": [47.5, 6.0],        # Haute-Saône
    "71": [46.5, 4.8],        # Saône-et-Loire
    "72": [48.0, 0.2],        # Sarthe
    "73": [45.5, 6.0],        # Savoie
    "74": [46.0, 6.3],        # Haute-Savoie
    "75": [48.8566, 2.3522],  # Paris
    "76": [49.6, 0.8],        # Seine-Maritime
    "77": [48.5, 3.0],        # Seine-et-Marne
    "78": [48.7, 1.8],        # Yvelines
    "79": [46.5, -0.3],       # Deux-Sèvres
    "80": [50.0, 2.5],        # Somme
    "81": [43.8, 2.0],        # Tarn
    "82": [44.0, 1.2],        # Tarn-et-Garonne
    "83": [43.3, 6.2],        # Var
    "84": [44.0, 5.2],        # Vaucluse
    "85": [46.7, -1.5],       # Vendée
    "86": [46.5, 0.5],        # Vienne
    "87": [46.0, 1.2],        # Haute-Vienne
    "88": [48.2, 6.5],        # Vosges
    "89": [47.8, 3.8],        # Yonne
    "90": [47.6, 6.8],        # Territoire de Belfort
    "91": [48.5, 2.2],        # Essonne
    "92": [48.7, 2.2],        # Hauts-de-Seine
    "93": [48.9, 2.4],        # Seine-Saint-Denis
    "94": [48.7, 2.5],        # Val-de-Marne
    "95": [49.0, 2.2],        # Val-d'Oise
}

gdf.to_file("debug_gdf_before_filter.geojson", driver="GeoJSON")

for code_dept, nom_dept in departements.items():
    gdf_filtered = gdf[gdf["codeCirconscription"].str.startswith(code_dept)]

    m = folium.Map(location=coords[code_dept], zoom_start=9)

    folium.GeoJson(
        gdf_filtered,
        style_function=lambda feature: {
            "fillColor": feature["properties"].get("couleur", "#CCCCCC"),
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.7,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["nomCirconscription", "groupe_majoritaire"],
            aliases=["Circonscription:", "Groupe majoritaire:"],
            localize=True,
        ),
    ).add_to(m)

    legend_items = [
        f'<i style="background:{color}; width:18px; height:18px; display:inline-block; border:1px solid black;"></i> {groupe}'
        for groupe, color in couleurs.items()
    ]
    legend_html = f"""
    <div style="position: fixed;
         bottom: 20px; left: 20px; width: 220px; height: auto;
         border:2px solid grey; z-index:9999; font-size:12px;
         background-color:white; padding: 8px; border-radius: 5px;">
    <b>Légende (Groupes politiques)</b><br>
    {'<br>'.join(legend_items)}
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save(f"carte_{nom_dept}.html")
    webbrowser.open(f"carte_{nom_dept}.html")

