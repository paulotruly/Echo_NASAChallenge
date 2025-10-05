import Logo from '../assets/logo.png'
import Linkedin from '../assets/linkedin.png'

const AboutUs = ({ onClose }) => {
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

          <h5 className='text-[20px] font-extrabold'>AEcoSpace</h5>
          <p className=''>Our team brings together creative designers and skilled front-end and back-end developers, united by innovation and impact, working collaboratively to turn ideas into smart solutions. We are participating in the{' '}
            <span className="font-bold">NASA International Space Apps Challenge</span>, tackling the challenge of demonstrating how an urban planner can leverage NASA Earth observation data to develop smart city growth strategies that preserve human wellbeing and the environment, taking into account natural resources, ecosystems, and existing infrastructure.</p>

          <h5 className='text-[20px] font-extrabold mb-4'>Our team</h5>

          <div className='grid grid-cols-2 gap-2 w-full'>

            <div className='flex flex-row items-center justify-center bg-main-degrade text-white rounded-lg w-auto h-auto p-5 shadow-lg'>
              <img className='w-[100px] h-[100px] rounded-full mr-4 border-2 border-white/50'
                src="https://media.licdn.com/dms/image/v2/D4D03AQH3CmE7JBNDLA/profile-displayphoto-scale_200_200/B4DZjsyB4XH0AY-/0/1756319197179?e=1762387200&v=beta&t=oOfaKVE-SZKa7Uf4jAe01Fa33ssXew_CqFeuawKEtjw" alt="" />
              <div className='flex flex-col items-start justify-center'>
                <h6 className='font-bold mb-1 text-[15px]'>Paulo Gomes</h6>
                <p className='font-normal text-[12px]'>Front-end developer</p>
                <a href="https://www.linkedin.com/in/paulotruly" target='_blank'>
                  <img src={Linkedin} className='w-auto h-[20px] mt-2' alt=""/>
                </a>
              </div>
            </div>

                <div className='flex flex-row items-center justify-center bg-main-degrade text-white rounded-lg w-auto h-auto p-5 shadow-lg'>
                    <img className='w-[100px] h-[100px] rounded-full mr-4 border-2 border-white/50'
                    src="https://media.licdn.com/dms/image/v2/D4D03AQFjBEpyRu3yXA/profile-displayphoto-crop_800_800/B4DZh6loPpGQAM-/0/1754403341820?e=1762387200&v=beta&t=LGGnpolI1p4MNjNFr7zEoEVkt3t1_FQ3rh345YErtqI" alt="" />
                    <div className='flex flex-col items-start justify-center'>
                        <h6 className='font-bold mb-1 text-[15px]'> Kaiki Nattan </h6>
                        <p className='font-normal text-[12px]'> Full stack developer </p>
                        <a href="https://www.linkedin.com/in/kaikinattan" target='_blank'>
                            <img src={Linkedin} className='w-auto h-[20px] mt-2' alt=""/>
                        </a>
                    </div>
                </div>

                <div className='flex flex-row items-center justify-center bg-main-degrade text-white rounded-lg w-auto h-auto p-5 shadow-lg'>
                    <img className='w-[100px] h-[100px] rounded-full mr-4 border-2 border-white/50'
                    src="https://media.licdn.com/dms/image/v2/D4D03AQFm6buVRyGPeQ/profile-displayphoto-shrink_200_200/B4DZWlP2I1G8AY-/0/1742234152901?e=1762387200&v=beta&t=G_6hsb9xGk2y2d_DcTs6TEQD00cudfQHgkb9dh50dIA" alt="" />
                    <div className='flex flex-col items-start justify-center'>
                        <h6 className='font-bold mb-1 text-[15px]'> João Rafael </h6>
                        <p className='font-normal text-[12px]'> Front-end developer </p>
                        <a href="https://www.linkedin.com/in/joao-rafaell" target='_blank'>
                            <img src={Linkedin} className='w-auto h-[20px] mt-2' alt=""/>
                        </a>
                    </div>
                </div>

                <div className='flex flex-row items-center justify-center bg-main-degrade text-white rounded-lg w-auto h-auto p-5 shadow-lg'>
                    <img className='w-[100px] h-[100px] rounded-full mr-4 border-2 border-white/50'
                    src="https://media.licdn.com/dms/image/v2/D5603AQHGsdXQ6WBFfQ/profile-displayphoto-crop_800_800/B56ZiLpi8HHMAI-/0/1754689581362?e=1762387200&v=beta&t=1pyge3461b0-DE2L3WsQYuTD6lVDGiZi02s4GsAGvQg" alt="" />
                    <div className='flex flex-col items-start justify-center'>
                        <h6 className='font-bold mb-1 text-[15px]'> Ester Santos </h6>
                        <p className='font-normal text-[12px]'> UX/UI designer </p>
                        <a href="https://www.linkedin.com/in/ester-hsnt" target='_blank'>
                            <img src={Linkedin} className='w-auto h-[20px] mt-2' alt=""/>
                        </a>
                    </div>
                </div>

                <div className='flex flex-row items-center justify-center bg-main-degrade text-white rounded-lg w-auto h-auto p-5 shadow-lg'>
                    <img className='w-[100px] h-[100px] rounded-full mr-4 border-2 border-white/50'
                    src="https://media.licdn.com/dms/image/v2/D4E03AQEOtFjcxhP0UA/profile-displayphoto-shrink_200_200/B4EZdk_BPlHcAc-/0/1749745932704?e=1762387200&v=beta&t=TSUDlC6-jyx3DOLnXd9q3d8HHzT-GqAG6BxLWYVBMtA" alt="" />
                    <div className='flex flex-col items-start justify-center'>
                        <h6 className='font-bold mb-1 text-[15px]'> Maximus B. </h6>
                        <p className='font-normal text-[12px]'> Team manager </p>
                        <a href="https://www.linkedin.com/in/maximus-bragança" target='_blank'>
                            <img src={Linkedin} className='w-auto h-[20px] mt-2' alt=""/>
                        </a>
                    </div>
                </div>

          </div>
        </div>
      </div>
    </div>
  )
}

export default AboutUs;
