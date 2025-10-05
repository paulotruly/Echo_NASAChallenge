import './App.css'
import RankCard from './components/RankCard'
import FilterCard from './components/FilterCard'
import Map from './components/Map'
import Header from './components/Header'
import SelectionBar from './components/SelectionBar'
import PopUpSuggestion from './components/PopUpSuggestion'
import PopUpNotification from './components/PopUpNotification'
import AboutUs from './components/AboutUs'
import { useState, useEffect, useRef } from "react"; 
import HowItWorks from './components/HowItWorks'

function App() {
  const [showSuggestion, setShowSuggestion] = useState(false);
  const [showNotification, setShowNotification] = useState(false);
  const [showAboutUs, setShowAboutUs] = useState(false);
  const [showHowItWorks, setShowHowItWorks] = useState(false);

  const [vulnerabilityData, setVulnerabilityData] = useState(null);  
  const [loading, setLoading] = useState(true);  
  const [selectedSector, setSelectedSector] = useState(null);  
  const [analysisText, setAnalysisText] = useState('');  
  const [activeFilter, setActiveFilter] = useState('Heat'); 
  const [selectedBairro, setSelectedBairro] = useState(null);

    const mapRef = useRef(null); 

    const handleScrollToMap = () => {
      if (mapRef.current) {
        // Faz o scroll suave até a seção principal (o 'main')
        mapRef.current.scrollIntoView({ behavior: 'smooth' });
      }
    };

  // Fetch inicial do backend
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:5001/api/data');
        if (!response.ok) throw new Error('Erro no backend');
        const data = await response.json();
        setVulnerabilityData(data);  
        setLoading(false);
      } catch (error) {
        console.error('Falha fetch:', error);
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // --- NOVO CÓDIGO 1: LÓGICA DE BUSCA DO SETOR MAIS VULNERÁVEL ---
  const findBestSectorInBairro = (bairro) => {
    if (!vulnerabilityData || !bairro) return null;
    
    const sectorsInBairro = vulnerabilityData.features.filter(feature => 
        feature.properties?.NM_BAIRRO === bairro
    );

    if (sectorsInBairro.length === 0) return null;

    sectorsInBairro.sort((a, b) => 
        (b.properties?.indice_vulnerabilidade || 0) - (a.properties?.indice_vulnerabilidade || 0)
    );

    return sectorsInBairro[0].properties;
  };

  // --- NOVO CÓDIGO 2: useEffect para Sincronizar selectedBairro com selectedSector e Resetar ---
  useEffect(() => {
    // 1. Lógica de Reset/Limpeza
    if (!selectedBairro) {
        setSelectedSector(null); 
        return; // Sai da função
    }
    
    // 2. Lógica de Seleção Automática (Habilitando a LLM)
    const bestSectorProps = findBestSectorInBairro(selectedBairro);
    setSelectedSector(bestSectorProps); 
    
  }, [selectedBairro, vulnerabilityData]); 


  const handleFilterClick = (filterType) => {  // Passe filterType como prop
    setActiveFilter(filterType); 
    setShowNotification(true);
    // Opcional: Refetch com filtro, ex: /api/data?filter=heat
  };

  const handleSuggestionClick = async () => {
    setShowNotification(false);
    // O selectedSector AGORA é preenchido automaticamente pelo useEffect, 
    // então se selectedBairro foi escolhido, selectedSector não será null.
    if (selectedSector) {
      try {
        const response = await fetch('http://localhost:5001/api/llm', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          // --- NOVO CÓDIGO 3: CORREÇÃO DO PAYLOAD DA LLM ---
          body: JSON.stringify({ 
                ...selectedSector, 
                selected_bairro: selectedBairro, 
                filter: 'Heat' 
            })
        });
        const result = await response.json();
        setAnalysisText(result.analysis_text || 'Análise gerada pela IA.');
        setShowSuggestion(true);
      } catch (error) {
        console.error('Erro LLM:', error);
        setAnalysisText('Erro na análise. Tente novamente.');
        setShowSuggestion(true);
      }
    } else {
      setAnalysisText('Selecione um setor no mapa primeiro!');
      setShowSuggestion(true);
    }
  };

  const handleCloseNotification = () => {
    setShowNotification(false);
    setShowSuggestion(false);
  };

  if (loading) {
    return <div className="flex justify-center items-center h-screen text-white">Carregando dados do backend...</div>;
  }

  // Top 5 distritos por HVI
  const rankedDistricts = vulnerabilityData?.features
    ?.sort((a, b) => (b.properties?.indice_vulnerabilidade || 0) - (a.properties?.indice_vulnerabilidade || 0))
    ?.slice(0, 5) || [];

  return (
    <div className='relative bg-space-background min-h-screen'>
      <Header onOpenAboutUs={setShowAboutUs} onOpenHowItWorks={setShowHowItWorks} onScrollToMap={handleScrollToMap}/>
      
      <main ref={mapRef} className='my-10'>
        <SelectionBar onBairroSelect={setSelectedBairro} />  
        <div className='grid grid-cols-4 h-auto my-2'>
          <div className='flex flex-col col-span-3 ml-2'>
            <div className='flex justify-center items-center text-white h-full w-full bg-blue-950'>
              <Map geoJsonData={vulnerabilityData} onSectorSelect={setSelectedSector} selectedBairro={selectedBairro}/>
            </div>
          </div>
          
          <div className='col-span-1 h-auto mx-2'>
            <div className='h-auto mt-4 mx-2'>
              <div className='grid grid-cols-2 gap-1'>
                <h3 className='col-span-2 font-bold text-lg text-white py-2 border-b-2 border-white/20 mb-4'> Filtration </h3>
                <FilterCard 
                  title="Heat • ECOSTRESS" 
                  description="Temperature, heat, urban heat, islands, comfort, energy" 
                  colorClass="bg-our-orange" 
                  onClick={() => handleFilterClick('heat')} 
                />
                <FilterCard 
                  title="Flood • SRTM+GPM" 
                  description="Flooding, rain, terrain, drainage, vulnerability" 
                  colorClass="bg-our-purple" 
                  onClick={() => handleFilterClick('flood')} 
                />
                <FilterCard 
                  title="Green • NDVI" 
                  description="Vegetation, green cover, urban health, sustainability" 
                  colorClass="bg-our-green" 
                  onClick={() => handleFilterClick('green')} 
                />
                <FilterCard 
                  title="Air • OMI/TEMPO" 
                  description="Pollution, quality, emissions, atmosphere, health" 
                  colorClass="bg-our-white" 
                  onClick={() => handleFilterClick('air')} 
                />
              </div>
            </div>

            <div className='flex flex-col h-auto'>
              <h3 className='font-bold text-lg text-white mx-2 py-2 mt-4 mb-1 border-b-2 border-white/20'> Most affected areas </h3>
              {rankedDistricts.map((district, index) => (
                <RankCard 
                  key={index} 
                  rank={index + 1}
                  name={district.properties?.NM_BAIRRO || 'Desconhecido'}
                  score={district.properties?.indice_vulnerabilidade || 0}
                  onClick={() => setSelectedSector(district.properties)}  // Seleciona pra LLM
                />
              ))}
            </div>
          </div>
        </div>

        {showNotification && (
          <PopUpNotification onClick={handleSuggestionClick} onClose={handleCloseNotification} />
        )}
        {showSuggestion && (
          <PopUpSuggestion onClose={handleCloseNotification} analysisText={analysisText} />  // Passe texto da LLM
        )}

        {showAboutUs && (
          <AboutUs onClose={() => setShowAboutUs(false)} /> 
        )}

        {showHowItWorks && (
          <HowItWorks onClose={() => setShowHowItWorks(false)} /> 
        )}

      </main>

    <footer className='flex flex-col justify-center items-center bg-gray-900 w-full h-[100px] text-gray-500 p-2'>
        <p className='text-sm mb-1'>
            Developed for the NASA International Space Apps Challenge 2025
        </p>
        <a 
            href="https://github.com/kaikinattandossantos/NASA_Hacka"
            target='_blank' 
            className='text-xs underline hover:text-white transition-colors duration-300'
        > 
            Access source code on GitHub
        </a>
    </footer>
    </div>
  );
}

export default App;