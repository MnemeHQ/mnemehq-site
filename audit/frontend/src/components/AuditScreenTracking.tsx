import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { trackAuditScreen } from '../analytics';

export function AuditScreenTracking() {
  const location = useLocation();

  useEffect(() => {
    trackAuditScreen(location.pathname);
  }, [location.pathname]);

  return null;
}
