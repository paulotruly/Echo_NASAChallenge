import Logo from '../assets/logo.png'

const HowItWorks = ({ onClose }) => {
  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center backdrop-blur-md bg-black/40">
      <div className="relative flex flex-col bg-white rounded-2xl shadow-2xl w-1/3 max-h-[80vh] animate-fadeIn overflow-hidden">

        <img 
            src={Logo} 
            alt="Logo" 
            className="absolute top-4 left-4 w-[50px] h-auto"
            />

            <button
            onClick={onClose}
            className="absolute top-4 right-4 bg-red-500 text-white px-3 py-1 rounded-lg hover:bg-red-600 transition-all z-10"
            >
            X
        </button>

        <div className="flex flex-col items-center gap-5 p-8 pt-16 pb-8 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-200 rounded-b-2xl">

          <h5 className='text-[24px] font-extrabold text-gray-800'>How the analysis works</h5>
          <p className='text-sm text-center text-gray-600'>
            Our platform simplifies decision-making in 3 steps, combining geospatial data and artificial intelligence.
          </p>
          
          <div className='flex flex-col gap-6 w-full mt-4'>
            
            {/* Step 1: Selection */}
            <div className='flex items-center gap-4 p-4 border-b border-gray-200'>
                <div>
                    <h6 className="font-bold text-lg">1. Sector selection</h6>
                    <p className='text-sm text-gray-700'>
                        Use the <span className='font-semibold'>dropdown</span> to focus on a location or <span className='font-semibold'>click directly</span> on any polygon on the map.
                    </p>
                </div>
            </div>

            {/* Step 2: Filtering */}
            <div className='flex items-center gap-4 p-4 border-b border-gray-200'>
                <div>
                    <h6 className="font-bold text-lg">2. Filter application</h6>
                    <p className='text-sm text-gray-700'>
                        Click one of the <span className='font-semibold'>filters</span> (heat, flood, etc.) in the side panel. This triggers the analysis notification.
                    </p>
                </div>
            </div>

            {/* Step 3: AI Analysis */}
            <div className='flex items-center gap-4 p-4 border-b border-gray-200'>
                <div>
                    <h6 className="font-bold text-lg">3. AI analysis </h6>
                    <p className='text-sm text-gray-700'>
                        Click in the pop-up notification. This action sends the selected sector's data and the chosen filter to the AI. The AI processes this context and generates a tailored intervention recommendation for that specific region.
                    </p>
                </div>
            </div>
            
          </div>
        </div>
      </div>
    </div>
  )
}

export default HowItWorks;