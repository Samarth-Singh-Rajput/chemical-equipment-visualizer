import React, { useState } from 'react';
import axios from 'axios';
import { Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

function App() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [file, setFile] = useState(null);
  const [history, setHistory] = useState([]);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState('');
  const [selectedSummary, setSelectedSummary] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [downloading, setDownloading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loggedIn, setLoggedIn] = useState(false);

  const api = axios.create({
    baseURL: 'http://127.0.0.1:8000/api/',
    auth: { username, password },
  });

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const res = await api.get('history/');
      setHistory(res.data);
      setLoggedIn(true);
      setError('');
    } catch (err) {
      setError('Login failed or server error');
      setLoggedIn(false);
    }
    setLoading(false);
  };

  const handleLogin = (e) => {
    e.preventDefault();
    fetchHistory();
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await api.post('upload/', formData);
      setSummary(res.data.summary);
      fetchHistory();
      setError('');
    } catch (err) {
      setError('Upload failed');
    }
    setLoading(false);
  };

  const handleDownloadPDF = async (id) => {
    setDownloading(true);
    try {
      const res = await api.get(`report/${id}/`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report_${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError('PDF download failed');
    }
    setDownloading(false);
  };

  const handleLogout = () => {
    setLoggedIn(false);
    setUsername('');
    setPassword('');
    setHistory([]);
    setSummary(null);
    setSelectedSummary(null);
    setSelectedId(null);
    setError('');
  };

  const renderSummary = (summary) => {
    if (!summary) return null;
    return (
      <div style={{ background: '#f7f7f7', borderRadius: 8, padding: 16, margin: '10px 0' }}>
        <div style={{ display: 'flex', gap: 30, flexWrap: 'wrap', justifyContent: 'space-between' }}>
          <div>
            <strong>Total Count:</strong> {summary.total_count}
          </div>
          <div>
            <strong>Averages:</strong>
            <ul style={{ margin: 0, paddingLeft: 18 }}>
              {summary.averages && Object.entries(summary.averages).map(([k, v]) => (
                <li key={k}>{k}: <b>{v}</b></li>
              ))}
            </ul>
          </div>
          <div>
            <strong>Type Distribution:</strong>
            <ul style={{ margin: 0, paddingLeft: 18 }}>
              {summary.type_distribution && Object.entries(summary.type_distribution).map(([k, v]) => (
                <li key={k}>{k}: <b>{v}</b></li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    );
  };

  const renderCharts = (summary) => {
    if (!summary) return null;
    const avg = summary.averages || {};
    const typeDist = summary.type_distribution || {};
    return (
      <div style={{ margin: '20px 0', display: 'flex', gap: 30, flexWrap: 'wrap', justifyContent: 'center' }}>
        {Object.keys(avg).length > 0 && (
          <div style={{ maxWidth: 300, background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px #eee', padding: 16 }}>
            <h5 style={{ textAlign: 'center', margin: 0 }}>Averages</h5>
            <Bar
              data={{
                labels: Object.keys(avg),
                datasets: [{
                  label: 'Averages',
                  data: Object.values(avg),
                  backgroundColor: 'rgba(75,192,192,0.6)'
                }]
              }}
              options={{ responsive: true, plugins: { legend: { display: false } } }}
            />
          </div>
        )}
        {Object.keys(typeDist).length > 0 && (
          <div style={{ maxWidth: 300, background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px #eee', padding: 16 }}>
            <h5 style={{ textAlign: 'center', margin: 0 }}>Type Distribution</h5>
            <Pie
              data={{
                labels: Object.keys(typeDist),
                datasets: [{
                  label: 'Type Distribution',
                  data: Object.values(typeDist),
                  backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'
                  ]
                }]
              }}
            />
          </div>
        )}
      </div>
    );
  };

  return (
    <div style={{ maxWidth: 800, margin: '2rem auto', fontFamily: 'Inter, sans-serif', background: '#f4f6fa', borderRadius: 12, boxShadow: '0 2px 16px #e0e0e0', padding: 32 }}>
      <h2 style={{ textAlign: 'center', color: '#2d3a4b', marginBottom: 32 }}>Chemical Equipment Visualizer (Web)</h2>
      {!loggedIn && (
        <form onSubmit={handleLogin} style={{ marginBottom: 30, display: 'flex', gap: 12, justifyContent: 'center' }}>
          <input placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} required style={{ padding: 8, borderRadius: 6, border: '1px solid #bbb', minWidth: 120 }} />
          <input placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} required style={{ padding: 8, borderRadius: 6, border: '1px solid #bbb', minWidth: 120 }} />
          <button type="submit" style={{ padding: '8px 18px', borderRadius: 6, background: '#2d3a4b', color: '#fff', border: 'none', fontWeight: 600 }} disabled={loading}>{loading ? 'Logging in...' : 'Login'}</button>
        </form>
      )}
      {loggedIn && (
        <>
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 10 }}>
            <button onClick={handleLogout} style={{ padding: '6px 16px', borderRadius: 6, background: '#e53935', color: '#fff', border: 'none', fontWeight: 600 }}>Logout</button>
          </div>
          <form onSubmit={handleUpload} style={{ marginBottom: 24, display: 'flex', gap: 12, alignItems: 'center', justifyContent: 'center' }}>
            <input type="file" accept=".csv" onChange={handleFileChange} style={{ padding: 6, borderRadius: 6, border: '1px solid #bbb', background: '#fff' }} />
            <button type="submit" style={{ padding: '8px 18px', borderRadius: 6, background: '#4caf50', color: '#fff', border: 'none', fontWeight: 600 }} disabled={loading}>{loading ? 'Uploading...' : 'Upload CSV'}</button>
          </form>
          {error && <div style={{ color: 'red', marginBottom: 16, textAlign: 'center' }}>{error}</div>}
          {summary && (
            <div style={{ marginBottom: 24, background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px #eee', padding: 18 }}>
              <h4 style={{ margin: 0, color: '#2d3a4b' }}>Summary (Latest Upload)</h4>
              {renderSummary(summary)}
              {renderCharts(summary)}
            </div>
          )}
          {selectedSummary && (
            <div style={{ marginBottom: 24, background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px #eee', padding: 18 }}>
              <h4 style={{ margin: 0, color: '#2d3a4b' }}>Summary (From History)</h4>
              {renderSummary(selectedSummary)}
              {renderCharts(selectedSummary)}
              <div style={{ display: 'flex', gap: 10, marginTop: 10 }}>
                <button onClick={() => setSelectedSummary(null)} style={{ padding: '6px 16px', borderRadius: 6, background: '#bbb', color: '#fff', border: 'none' }}>Close</button>
                <button onClick={() => handleDownloadPDF(selectedId)} disabled={downloading} style={{ padding: '6px 16px', borderRadius: 6, background: '#2d3a4b', color: '#fff', border: 'none' }}>
                  {downloading ? 'Downloading...' : 'Download PDF'}
                </button>
              </div>
            </div>
          )}
          <h4 style={{ color: '#2d3a4b', marginBottom: 10 }}>Upload History</h4>
          <div style={{ overflowX: 'auto', background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px #eee', padding: 10 }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 15 }}>
              <thead>
                <tr style={{ background: '#f4f6fa' }}>
                  <th style={{ padding: 8, borderBottom: '1px solid #e0e0e0' }}>ID</th>
                  <th style={{ padding: 8, borderBottom: '1px solid #e0e0e0' }}>File</th>
                  <th style={{ padding: 8, borderBottom: '1px solid #e0e0e0' }}>Date</th>
                  <th style={{ padding: 8, borderBottom: '1px solid #e0e0e0' }}>Summary</th>
                  <th style={{ padding: 8, borderBottom: '1px solid #e0e0e0' }}>PDF</th>
                </tr>
              </thead>
              <tbody>
                {history.map(h => (
                  <tr key={h.id} style={{ borderBottom: '1px solid #f0f0f0' }}>
                    <td style={{ padding: 8 }}>{h.id}</td>
                    <td style={{ padding: 8 }}>{h.filename}</td>
                    <td style={{ padding: 8 }}>{new Date(h.uploaded_at).toLocaleString()}</td>
                    <td style={{ padding: 8 }}><button onClick={() => { setSelectedSummary(h.summary); setSelectedId(h.id); }} style={{ padding: '4px 10px', borderRadius: 5, background: '#1976d2', color: '#fff', border: 'none', fontSize: 14 }}>View</button></td>
                    <td style={{ padding: 8 }}><button onClick={() => handleDownloadPDF(h.id)} disabled={downloading} style={{ padding: '4px 10px', borderRadius: 5, background: '#1976d2', color: '#fff', border: 'none', fontSize: 14 }}>PDF</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

export default App;
