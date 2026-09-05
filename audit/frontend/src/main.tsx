import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { migrateLegacyHashRoute, ROUTER_BASENAME } from './routing'
import './styles.css'
import { initializeAnalytics } from './analytics'

migrateLegacyHashRoute()
initializeAnalytics()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter basename={ROUTER_BASENAME}>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
