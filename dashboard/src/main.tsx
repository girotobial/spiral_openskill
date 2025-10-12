import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route } from "react-router";
import { Layout } from './layouts/Layout.tsx';
import App from './components/App.tsx'
import { Matchmaker } from './components/Matchmaker.tsx';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<App/>} />
          <Route path="matchmaker" element={<Matchmaker/>} />
        </Route>
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
