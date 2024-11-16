import logo from './logo.svg';
import './App.css';
import Modal from 'react-bootstrap/Modal';
import 'bootstrap/dist/css/bootstrap.min.css';
import TrafficLight from './components/TrafficLight'; 
import { useState } from 'react';
import Button from 'react-bootstrap/Button';

function App() {
  const [showModal, setShowModal] = useState(true);
  const [mode, setMode] = useState('Manual');

  const openModal = () => {
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
  };

  const handleModeChange = (newMode) => {
    setMode(newMode);
    closeModal();
  };

  return (
    <div className="App">
      <div className='ManualControls'>
        <div className='header'>
          <Button variant="secondary" onClick={openModal}>Select Mode</Button>
          <span className='modeLabel'>{mode} mode</span>
        </div>
        
        <TrafficLight className='M' device='M' />
        <TrafficLight className='1' device='1' />
        <TrafficLight className='2' device='2' />
        <TrafficLight className='3' device='3' />
        <TrafficLight className='4' device='4' />
        <TrafficLight className='5' device='5' />
      </div>

      {/* Mode selection popup */}
      <Modal keyboard={false} show={showModal} backdrop = 'static' onHide={closeModal} centered> 
        <Modal.Header className="bg-dark text-light">
          <Modal.Title>Select Mode</Modal.Title>
        </Modal.Header>
        <Modal.Body className="bg-dark text-light">
          <Button variant="dark" onClick={() => handleModeChange('Auto')} className="w-100 mb-2">Auto</Button>
          <Button variant="dark" onClick={() => handleModeChange('Manual')} className="w-100">Manual</Button>
        </Modal.Body>
      </Modal>
    </div>
  );
}

export default App;
