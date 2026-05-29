import folium

#carte centrée sur la France
m=folium.Map(location=[46.603354, 1.888334], zoom_start=6)

folium.GeoJson(
    "departements_avec_couleur.geojson",
    name="Départements",
    style_function=lambda feature: {
        "fillColor": feature["properties"]["couleur"],  # Utilise la couleur définie dans le GeoJSON
        "color": "black",  # Couleur de la bordure
        "weight": 1,       # Épaisseur de la bordure
        "fillOpacity": 0.7, # Opacité de la couleur de remplissage
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["nom", "nuance_majoritaire"],  # Champs à afficher dans l'infobulle
        aliases=["<b>Département :</b> ", "<b>Nuance majoritaire :</b> "],  # Noms affichés dans l'infobulle
        localize=True,
        sticky=True,
    ),
).add_to(m)

m.save("carte_departements.html")

