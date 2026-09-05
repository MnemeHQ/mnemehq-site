import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { reportScreen } from '../analytics';

export function AuditScreenTracking() {
  const { pathname } = useLocation();
  useEffect(() => { reportScreen(pathname); }, [pathname]);
  return null;
}
