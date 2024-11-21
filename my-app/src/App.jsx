import logo from "./logo.svg";
import "./App.css";
import Modal from "react-bootstrap/Modal";
import "bootstrap/dist/css/bootstrap.min.css";
import TrafficLight from "./components/TrafficLight";
import { useState } from "react";
import Button from "react-bootstrap/Button";
import { InputGroup, Form } from "react-bootstrap";
import Dropdown from "react-bootstrap/Dropdown";
import DropdownButton from "react-bootstrap/DropdownButton";

function App() {
  const [deviceList, setDeviceList] = useState({});
  const fetchAllDevices = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/getDevice/`);
      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json(); // Await the JSON data
      console.log(data); // Log the data
      setDeviceList(data); // Update the state with the fetched data
    } catch (err) {
      console.log(err.message); // Log the error message
    }
  };
  //Mode States
  const [modeModal, setModeModal] = useState(false);

  const openModeModal = () => {
    setModeModal(true);
  };
  const closeModeModal = () => {
    setModeModal(false);
  };
  const [mode, setMode] = useState("Manual");
  const handleModeChange = (newMode) => {
    setMode(newMode);
    closeModeModal();
  };
  //Add Device States
  const [addModal, setAddModal] = useState(false);
  const openAddModal = () => {
    setAddModal(true);
  };
  const closeAddModal = () => {
    setAddModal(false);
  };
  const handleAddDevice = (newMode) => {
    //Code to add device
    closeModeModal();
  };

  //Close Device States
  const [closeModal, setCloseModal] = useState(false);
  const openCloseModal = () => {
    setCloseModal(true);
  };
  const closeCloseModal = () => {
    setCloseModal(false);
  };

  const handleDeleteDevice = (deviceId) => {
    //Code to delete device
    closeCloseModal();
  };

  return (
    <div className="App">
      <div className="controlHeader">
        <Button onClick={openAddModal} variant="primary">
          Add Device
        </Button>
        <Button onClick={openCloseModal} variant="danger">
          Remove Device
        </Button>
      </div>
      <div className="ManualControls">
        <div className="header">
          <span className="modeLabel">{mode} mode</span>
        </div>

        <TrafficLight className="M" device="0" />
        <TrafficLight className="1" device="1" />
        <TrafficLight className="2" device="2" />
        <TrafficLight className="3" device="3" />
        <TrafficLight className="4" device="4" />
        <TrafficLight className="5" device="5" />
        <div className="footer">
          <Button variant="secondary" onClick={openModeModal}>
            Select Mode
          </Button>
          <Button variant="primary">Save</Button>
        </div>
      </div>

      {/* Mode selection popup */}
      <Modal
        keyboard={false}
        show={modeModal}
        backdrop="static"
        onHide={closeModeModal}
        centered
      >
        <Modal.Header className="bg-dark text-light">
          <Modal.Title>Select Mode</Modal.Title>
        </Modal.Header>
        <Modal.Body className="bg-dark text-light">
          <Button
            variant="dark"
            onClick={() => handleModeChange("Auto")}
            className="w-100 mb-2"
          >
            Auto
          </Button>
          <Button
            variant="dark"
            onClick={() => handleModeChange("Manual")}
            className="w-100"
          >
            Manual
          </Button>
        </Modal.Body>
      </Modal>

      {/* Add Device popup */}
      <Modal
        show={addModal}
        onHide={closeAddModal}
        backdrop="static"
        keyboard={false}
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>Add Device</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <InputGroup size="sm" className="mb-3">
            <InputGroup.Text id="inputGroup-sizing-sm">
              IP Address
            </InputGroup.Text>
            <Form.Control
              placeholder="0.0.0.0"
              aria-label="small"
              aria-describedby="inputGroup-sizing-sm"
            />
          </InputGroup>
          <DropdownButton id="dropdown-basic-button" title="Select Device">
            <Dropdown.Item href="#/action-1">Action</Dropdown.Item>
            <Dropdown.Item href="#/action-2">Another action</Dropdown.Item>
            <Dropdown.Item href="#/action-3">Something else</Dropdown.Item>
          </DropdownButton>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={closeAddModal}>
            Close
          </Button>
          <Button variant="primary">Understood</Button>
        </Modal.Footer>
      </Modal>

      {/* Remove Device popup */}
      <Modal
        show={closeModal}
        onHide={closeCloseModal}
        backdrop="static"
        keyboard={false}
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>Close Device</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          I will not close if you click outside me. Do not even try to press
          escape key.
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={closeCloseModal}>
            Close
          </Button>
          <Button variant="primary">Understood</Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
}

export default App;
