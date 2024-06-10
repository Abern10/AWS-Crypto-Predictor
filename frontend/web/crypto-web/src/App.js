import React, { useState, useEffect, useCallback } from 'react';
import Plot from 'react-plotly.js';
import io from 'socket.io-client';
import './App.css';

const socket = io.connect('http://localhost:1111');

function App() {
  const [timescale, setTimescale] = useState('day');
  const [btcData, setBtcData] = useState({ timestamps: [], prices: [], predictions: [] });
  const [ethData, setEthData] = useState({ timestamps: [], prices: [], predictions: [] });

  const fetchData = useCallback((crypto, timescale) => {
    fetch(`http://localhost:1111/api/data?crypto=${crypto}&timescale=${timescale}`)
      .then(response => response.json())
      .then(data => {
        const timestamps = data.timestamps.map(ts => new Date(ts));
        if (crypto === 'bitcoin') {
          setBtcData({ timestamps, prices: data.prices, predictions: data.predictions });
        } else {
          setEthData({ timestamps, prices: data.prices, predictions: data.predictions });
        }
      });
  }, []);

  useEffect(() => {
    fetchData('bitcoin', timescale);
    fetchData('ethereum', timescale);

    socket.on('update_graph', (data) => {
      const timestamps = data.timestamps.map(ts => new Date(ts));
      if (data.crypto === 'bitcoin') {
        setBtcData({ timestamps, prices: data.prices, predictions: data.predictions });
      } else {
        setEthData({ timestamps, prices: data.prices, predictions: data.predictions });
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
          <a onClick={() => handleTimescaleChange('year')}>1 Year</a>
          <a onClick={() => handleTimescaleChange('month')}>1 Month</a>
          <a onClick={() => handleTimescaleChange('day')}>1 Day</a>
          <a onClick={() => handleTimescaleChange('hour')}>1 Hour</a>
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
                x: btcData.timestamps,
                y: btcData.predictions,
                type: 'scatter',
                mode: 'lines',
                line: { dash: 'dash', color: 'gold' },
              },
              {
                x: [btcData.timestamps[btcData.timestamps.length - 1]],
                y: [btcData.prices[btcData.prices.length - 1]],
                type: 'scatter',
                mode: 'markers',
                marker: { color: 'gold', size: 10 },
              },
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
                x: ethData.timestamps,
                y: ethData.predictions,
                type: 'scatter',
                mode: 'lines',
                line: { dash: 'dash', color: 'rgba(54, 162, 235, 1)' },
              },
              {
                x: [ethData.timestamps[ethData.timestamps.length - 1]],
                y: [ethData.prices[ethData.prices.length - 1]],
                type: 'scatter',
                mode: 'markers',
                marker: { color: 'rgba(54, 162, 235, 1)', size: 10 },
              },
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