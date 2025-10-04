import { APIProvider, ControlPosition, Map } from '@vis.gl/react-google-maps';

// @ts-ignore
const API_KEY: string = "AIzaSyCHuvlAD3QkDbJXRF4OSy_SM75gLMLUka8" as string;

const Home = () => {
  const position = { lat: 53.54992, lng: 10.00678 };

  return (
    <>
      <APIProvider apiKey={API_KEY}>
        <Map
          style={{ width: '100vw', height: '100vh' }}
          defaultCenter={{ lat: 22.54992, lng: 0 }}
          defaultZoom={3}
          gestureHandling='greedy'
          disableDefaultUI
        />
      </APIProvider>
    </>
  );
};

export default Home;