function onEachFeature(feature, layer) {
	if (feature.properties && feature.properties.link) {
		layer.on("click", function () {
			window.open(feature.properties.link, "_blank");
		});
	}
}

L.geoJSON(departements_avec_couleur.geojson, {
	onEachFeature: onEachFeature,
}).addTo(map);
