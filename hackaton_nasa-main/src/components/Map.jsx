// src/components/Map.jsx
import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Recebe a nova prop: selectedBairro
const Map = ({ geoJsonData, onSectorSelect, selectedBairro }) => { 
  const [geoJsonLayer, setGeoJsonLayer] = useState(null);
  const initialPosition = [-8.0578, -34.8827];
  const zoomLevel = 12;
  const darkModeTiles = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';

  // ESTILO ATUALIZADO (HIGHLIGHT/DESATURAÇÃO)
  const style = (feature) => {
    const bairroPoligono = feature.properties?.NM_BAIRRO;
    
    // Verifica se o polígono pertence ao bairro selecionado
    const isSelected = selectedBairro && (bairroPoligono === selectedBairro);
    
    // Se NENHUM bairro foi selecionado, ou se for o bairro SELECIONADO:
    if (!selectedBairro || isSelected) {
        // Estilo Colorido (Baseado na Vulnerabilidade)
        const hvi = feature.properties?.indice_vulnerabilidade || 0;
        const color = hvi > 0.7 ? '#dc2626' : hvi > 0.4 ? '#f59e0b' : '#10b981'; 
        return {
          fillColor: color,
          weight: isSelected ? 3 : 2, // Borda mais grossa no selecionado
          opacity: 1,
          color: 'white',
          dashArray: '0',
          fillOpacity: 0.8 // Destaque total
        };
    } else {
        // Estilo Desaturado (Preto e Branco / Neutro)
        return {
            fillColor: '#505050', // Cor Cinza Escuro
            weight: 1,
            opacity: 1,
            color: '#A0A0A0', // Borda Cinza Claro
            dashArray: '4',
            fillOpacity: 0.1 // Transparência alta para o efeito "apagar"
        };
    }
  };

  // Clique no setor (Mantenha o onEachFeature original)
  const onEachFeature = (feature, layer) => {
    layer.on({
      click: () => onSectorSelect(feature.properties) 
    });
    layer.bindPopup(
      `<b>${feature.properties?.NM_BAIRRO || 'Setor'}</b><br>
       HVI: ${(feature.properties?.indice_vulnerabilidade || 0).toFixed(2)}<br>
       Temp: ${feature.properties?.temperatura_media_estimada?.toFixed(1)}°C<br>
       Densidade: ${feature.properties?.densidade_pop?.toFixed(0)} hab/km²`
    );
  };

  // ATUALIZAÇÃO DO useEffect: A camada precisa ser recriada quando a seleção muda
  useEffect(() => {
    if (geoJsonData?.features) {
        // A função L.geoJSON usa o estilo ATUAL. 
        // Se selectedBairro mudar, precisamos refazer a camada.
        const layer = L.geoJSON(geoJsonData, { style, onEachFeature });
        setGeoJsonLayer(layer);
    }
  // Adiciona selectedBairro como dependência para que o mapa atualize
  }, [geoJsonData, selectedBairro]); 

  return (
    <MapContainer center={initialPosition} zoom={zoomLevel} scrollWheelZoom={true} style={{ height: '100%', width: '100%' }} className="rounded-lg shadow-xl">
      <TileLayer attribution='&copy; OpenStreetMap & CARTO' url={darkModeTiles} />
      {geoJsonLayer && <GeoJSON data={geoJsonLayer.toGeoJSON()} style={style} onEachFeature={onEachFeature} />}
    </MapContainer>
  );
};

export default Map;