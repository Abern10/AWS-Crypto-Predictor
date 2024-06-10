import React, { useState, useEffect, useCallback } from 'react';
import Plot from 'react-plotly.js';
import io from 'socket.io-client';
import './App.css';

const socket = io.connect('http://localhost:1111');

function App() {
  const [timescale, setTimescale] = useState('day');
  const [btcData, setBtcData] = useState({ timestamps: [], prices: [], predictions: { timestamps: [], prices: [] } });
  const [ethData, setEthData] = useState({ timestamps: [], prices: [], predictions: { timestamps: [], prices: [] } });

  const fetchData = useCallback((crypto, timescale) => {
    fetch(`http://localhost:1111/api/data?crypto=${crypto}&timescale=${timescale}`)
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          console.error('Invalid data structure:', data);
          return;
        }

        const timestamps = data.timestamps.map(ts => new Date(ts));
        const predictions = {
          timestamps: data.predictions.timestamps.map(ts => new Date(ts)),
          prices: data.predictions.prices
        };

        if (crypto === 'bitcoin') {
          setBtcData({ timestamps, prices: data.prices, predictions: predictions });
        } else {
          setEthData({ timestamps, prices: data.prices, predictions: predictions });
        }
      })
      .catch(error => console.error('Error fetching data:', error));
  }, []);

  useEffect(() => {
    fetchData('bitcoin', timescale);
    fetchData('ethereum', timescale);

    socket.on('update_graph', (data) => {
      if (data.error) {
        console.error('Invalid data structure from socket:', data);
        return;
      }

      const timestamps = data.timestamps.map(ts => new Date(ts));
      const predictions = {
        timestamps: data.predictions.timestamps.map(ts => new Date(ts)),
        prices: data.predictions.prices
      };

      if (data.crypto === 'bitcoin') {
        setBtcData({ timestamps, prices: data.prices, predictions: predictions });
      } else {
        setEthData({ timestamps, prices: data.prices, predictions: predictions });
      }
    });

    return () => socket.off('update_graph');
  }, [timescale, fetchData]);

  const handleTimescaleChange = (newTimescale) => {
    setTimescale(newTimescale);
    socket.emit('request_update', { crypto: 'bitcoin', timescale: newTimescale });
    socket.emit('request_update', { crypto: 'ethereum', timescale: newTimescale });
  };

  return (
    <div className="App">
      <h1>Crypto Price Predictor</h1>
      <div className="dropdown">
        <button className="dropbtn">Select Timescale</button>
        <div className="dropdown-content">
          <button onClick={() => handleTimescaleChange('year')}>1 Year</button>
          <button onClick={() => handleTimescaleChange('month')}>1 Month</button>
          <button onClick={() => handleTimescaleChange('day')}>1 Day</button>
          <button onClick={() => handleTimescaleChange('hour')}>1 Hour</button>
        </div>
      </div>
      <div className="graph-container">
        <div className="graph">
          <h2 style={{ color: 'gold' }}>Bitcoin</h2>
          <Plot
            data={[
              {
                x: btcData.timestamps,
                y: btcData.prices,
                type: 'scatter',
                mode: 'lines',
                line: { color: 'gold' },
              },
              {
                x: btcData.predictions.timestamps,
                y: btcData.predictions.prices,
                type: 'scatter',
                mode: 'lines',
                line: { color: 'red' },
              }
            ]}
            layout={{
              margin: { t: 0 },
              showlegend: false,
              xaxis: {
                showgrid: false,
                zeroline: false,
              },
              yaxis: {
                showgrid: false,
                zeroline: false,
              },
              paper_bgcolor: '#2e2e2e',
              plot_bgcolor: '#2e2e2e',
              font: { color: 'white' },
              responsive: true
            }}
            useResizeHandler
            style={{ width: '100%', height: '100%' }}
          />
        </div>
        <div className="graph">
          <h2 style={{ color: 'rgba(54, 162, 235, 1)' }}>Ethereum</h2>
          <Plot
            data={[
              {
                x: ethData.timestamps,
                y: ethData.prices,
                type: 'scatter',
                mode: 'lines',
                line: { color: 'rgba(54, 162, 235, 1)' },
              },
              {
                x: ethData.predictions.timestamps,
                y: ethData.predictions.prices,
                type: 'scatter',
                mode: 'lines',
                line: { color: 'red' },
              }
            ]}
            layout={{
              margin: { t: 0 },
              showlegend: false,
              xaxis: {
                showgrid: false,
                zeroline: false,
              },
              yaxis: {
                showgrid: false,
                zeroline: false,
              },
              paper_bgcolor: '#2e2e2e',
              plot_bgcolor: '#2e2e2e',
              font: { color: 'white' },
              responsive: true
            }}
            useResizeHandler
            style={{ width: '100%', height: '100%' }}
          />
        </div>
      </div>
      <div className="table-container">
        <div className="table">
          <h3>Bitcoin Price Data</h3>
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Price (USD)</th>
              </tr>
            </thead>
            <tbody>
              {btcData.timestamps.slice().reverse().map((timestamp, index) => (
                <tr key={index}>
                  <td>{timestamp.toLocaleString()}</td>
                  <td>{btcData.prices.slice().reverse()[index]}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="table">
          <h3>Ethereum Price Data</h3>
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Price (USD)</th>
              </tr>
            </thead>
            <tbody>
              {ethData.timestamps.slice().reverse().map((timestamp, index) => (
                <tr key={index}>
                  <td>{timestamp.toLocaleString()}</td>
                  <td>{ethData.prices.slice().reverse()[index]}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default App;