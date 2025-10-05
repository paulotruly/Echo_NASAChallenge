import React, {useEffect, useState} from "react";

const API_BASE_URL = 'http://localhost:5001'; 

const SelectionBar = (props) => {
    const [bairros, setBairros] = useState([]);
    const [local, setLocal] = useState("")

    useEffect(() => {
        const fetchBairros = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/api/bairros/summary`);
                const data = await response.json();
                setBairros(data);
            } catch (error) {
                console.error("Erro ao buscar bairros:", error);
            }
        };

        fetchBairros();
    }, []);

    const handleSelectChange = (e) => {
      const selectedBairro = e.target.value;
        setLocal(selectedBairro); 
        
        if (props.onBairroSelect) {
            props.onBairroSelect(selectedBairro);
        }
    };
    
    
  return (
    <div className='bg-bar-degrade border-2 rounded-sm border-white/50 mx-2 backdrop-blur-lg'>
            <article className='flex flex-row justify-center items-center w-full h-auto'>

                <form action="" className='flex flex-row p-5 justify-center items-center'>
                      <label htmlFor="city-select" className='text-[16px] mb-1 font-bold mr-2'> Location </label>
                      <select name="city" id="city-select" className='appearance-none p-1 text-[14px] font-light rounded-md bg-white/60 border-white border-2 shadow-inner hover:bg-white/50 transition-all ease-in-out'
                              onChange={handleSelectChange}>
                          <option value="" disabled selected> Select a location </option>
                          {bairros.map((bairro,index) => (
                            <option key={index} value={bairro.NM_BAIRRO}> {bairro.NM_BAIRRO} </option>
                          ))}
                      </select>


                </form>

            </article>
          </div>
  );
};

export default SelectionBar;