import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import SurahListPage from './pages/SurahListPage'
import SurahAyahPage from './pages/SurahAyahPage'
import AyahWorkspacePage from './pages/AyahWorkspacePage'
import RukuListPage from './pages/RukuListPage'
import WordDictionaryPage from './pages/WordDictionaryPage'
import SearchPage from './pages/SearchPage'

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
            path="/surahs/:surahNumber"
            element={
              <ProtectedRoute>
                <SurahAyahPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/surahs/:surahNumber/ayahs/:ayahNumber"
            element={
              <ProtectedRoute>
                <AyahWorkspacePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/rukus"
            element={
              <ProtectedRoute>
                <RukuListPage />
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
                <SearchPage />
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
