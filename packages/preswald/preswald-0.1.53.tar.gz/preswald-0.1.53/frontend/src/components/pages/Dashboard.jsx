import React from 'react';

import { Alert, AlertDescription } from '@/components/ui/alert';

import DynamicComponents from '../DynamicComponents';
import LoadingState from '../LoadingState';

const Dashboard = ({ components, error, handleComponentUpdate }) => {
  console.log('[Dashboard] Rendering with:', { components, error });

  const isValidComponents =
    components &&
    components.rows &&
    Array.isArray(components.rows) &&
    components.rows.every((row) => Array.isArray(row));

  const renderContent = () => {
    if (error) {
      return (
        <Alert variant="destructive" className="dashboard-error">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      );
    }

    if (!isValidComponents) {
      return (
        <div className="dashboard-loading-container">
          <LoadingState
            isConnected={true}
            customText={!components ? 'Loading components' : 'Invalid components data'}
          />
        </div>
      );
    }

    if (components.rows.length === 0) {
      return (
        <div className="dashboard-empty">
          <p className="dashboard-empty-text">No components to display</p>
        </div>
      );
    }

    return <DynamicComponents components={components} onComponentUpdate={handleComponentUpdate} />;
  };

  return <div className="dashboard-container">{renderContent()}</div>;
};

export default Dashboard;
