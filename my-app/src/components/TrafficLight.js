import React, { useState } from 'react';
import './TrafficLight.css';

const TrafficLight = () => {
  const [activeLight, setActiveLight] = useState('');

  const [time, setTime] = useState('00:00');


  const handleClick = (color) => {
    setActiveLight(color);
  };

  return (
    <div className="parentContainer">
      <div className="traffic-light-bar">
        <button
          className={`traffic-light red ${activeLight === 'red' ? 'active' : ''}`}
          onClick={() => handleClick('red')}
        ></button>
        <button
          className={`traffic-light yellow ${activeLight === 'yellow' ? 'active' : ''}`}
          onClick={() => handleClick('yellow')}
        ></button>
        <button
          className={`traffic-light green ${activeLight === 'green' ? 'active' : ''}`}
          onClick={() => handleClick('green')}
        ></button>
      </div>

      <div className="timer">
        <div className="timer-label">Time</div> 
        <div className="timer-value">{time}</div> 
      </div>
    </div>
  );
};

export default TrafficLight;
