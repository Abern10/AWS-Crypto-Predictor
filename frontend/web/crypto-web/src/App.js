import React, { useState, useEffect, useCallback } from 'react';
import Plot from 'react-plotly.js';
import io from 'socket.io-client';
import './App.css';

const socket = io.connect('http://localhost:1111');

function App() {
  const [btcData, setBtcData] = useState({ timestamps: [], prices: [], predictions: { timestamps: [], prices: [] } });
  const [ethData, setEthData] = useState({ timestamps: [], prices: [], predictions: { timestamps: [], prices: [] } });

  const fetchData = useCallback((crypto) => {
    fetch(`http://localhost:1111/api/data?crypto=${crypto}`)
      .then(response => {
        console.log(`Response status for ${crypto}: ${response.status}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log(`Data received for ${crypto}:`, data);
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
    fetchData('bitcoin');
    fetchData('ethereum');

    socket.on('update_graph', (data) => {
      console.log('Socket data received:', data);
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
  }, [fetchData]);

  return (
    <div className="App">
      <h1>Crypto Price Predictor</h1>
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
                marker: { color: 'gold' },
              },
              {
                x: btcData.predictions.timestamps,
                y: btcData.predictions.prices,
                type: 'scatter',
                mode: 'lines',
                marker: { color: 'red' },
              },
            ]}
            layout={{
              title: '',
              paper_bgcolor: '#1c1c1c',
              plot_bgcolor: '#1c1c1c',
              font: { color: 'white' },
              xaxis: { showgrid: false },
              yaxis: { showgrid: false },
              showlegend: false,
              autosize: true
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
                marker: { color: 'rgba(54, 162, 235, 1)' },
              },
              {
                x: ethData.predictions.timestamps,
                y: ethData.predictions.prices,
                type: 'scatter',
                mode: 'lines',
                marker: { color: 'red' },
              },
            ]}
            layout={{
              title: '',
              paper_bgcolor: '#1c1c1c',
              plot_bgcolor: '#1c1c1c',
              font: { color: 'white' },
              xaxis: { showgrid: false },
              yaxis: { showgrid: false },
              showlegend: false,
              autosize: true
            }}
            useResizeHandler
            style={{ width: '100%', height: '100%' }}
          />
        </div>
      </div>
      <div className="table-container">
        <div className="table">
          <h2 style={{ color: 'gold' }}>Bitcoin</h2>
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Price</th>
              </tr>
            </thead>
            <tbody>
              {btcData.timestamps.slice().reverse().map((timestamp, index) => (
                <tr key={index}>
                  <td>{new Date(timestamp).toLocaleString()}</td>
                  <td>{btcData.prices.slice().reverse()[index]}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="table">
          <h2 style={{ color: 'rgba(54, 162, 235, 1)' }}>Ethereum</h2>
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Price</th>
              </tr>
            </thead>
            <tbody>
              {ethData.timestamps.slice().reverse().map((timestamp, index) => (
                <tr key={index}>
                  <td>{new Date(timestamp).toLocaleString()}</td>
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