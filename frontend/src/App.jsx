import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import SurahListPage from './pages/SurahListPage'
import WordDictionaryPage from './pages/WordDictionaryPage'
import ComingSoonPage from './pages/ComingSoonPage'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/surahs"
            element={
              <ProtectedRoute>
                <SurahListPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/rukus"
            element={
              <ProtectedRoute>
                <ComingSoonPage title="রুকুর তালিকা" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dictionary"
            element={
              <ProtectedRoute>
                <WordDictionaryPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/search"
            element={
              <ProtectedRoute>
                <ComingSoonPage title="অনুসন্ধান" />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
