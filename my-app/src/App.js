import logo from './logo.svg';
import './App.css';
import TrafficLight from './components/TrafficLight'; 

function App() {
  return (
    <div className="App">
      <div className='ManualControls'>
      <TrafficLight />
      <TrafficLight />
      <TrafficLight />
      <TrafficLight />
      <TrafficLight />
      <TrafficLight />
      </div>
    </div>
  );
}

export default App;
