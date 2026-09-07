import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { BuildDetail } from './pages/BuildDetail'
import { Dashboard } from './pages/Dashboard'
import { RepoDetail } from './pages/RepoDetail'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/repos/:repoId" element={<RepoDetail />} />
        <Route path="/runs/:runId" element={<BuildDetail />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
