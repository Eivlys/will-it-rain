import { APIProvider, Map } from '@vis.gl/react-google-maps';

// @ts-ignore
const API_KEY: string = "AIzaSyCHuvlAD3QkDbJXRF4OSy_SM75gLMLUka8" as string;

const Home = () => {
  const position = { lat: 53.54992, lng: 10.00678 };

  return (
    <>
      {/* <APIProvider apiKey={API_KEY}>
        <Map
          style={{ width: '100vw', height: '100vh' }}
          defaultCenter={{ lat: 22.54992, lng: 0 }}
          defaultZoom={3}
          gestureHandling='greedy'
          disableDefaultUI
        />
      </APIProvider> */}
      <iframe
        title="Example Website"
        width="100%"
        height="500px"
        src="https://api.meteomatics.com/2025-07-20T17Z/precip_5min:mm,hail_5min:cm/47.6,7.2_47.2,8:0.001,0.001/html_map"></iframe>
    </>
  );
};

export default Home;