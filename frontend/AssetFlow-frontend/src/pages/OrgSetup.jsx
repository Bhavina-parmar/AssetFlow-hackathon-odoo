import { useState } from 'react';
import AppLayout from '../components/AppLayout';
import DepartmentTab from './orgTabs/DepartmentTab';
import CategoryTab from './orgTabs/CategoryTab';
import EmployeeTab from './orgTabs/EmployeeTab';
import './OrgSetup.css';

const TABS = [
  { key: 'departments', label: 'Department Management' },
  { key: 'categories', label: 'Asset Category Management' },
  { key: 'employees', label: 'Employee Directory' },
];

export default function OrgSetup() {
  const [tab, setTab] = useState('departments');

  return (
    <AppLayout
      title="Organization Setup"
      subtitle="Master data everything else in AssetFlow depends on."
    >
      <div className="tabs">
        {TABS.map((t) => (
          <button
            key={t.key}
            className={'tab-btn' + (tab === t.key ? ' is-active' : '')}
            onClick={() => setTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'departments' && <DepartmentTab />}
      {tab === 'categories' && <CategoryTab />}
      {tab === 'employees' && <EmployeeTab />}
    </AppLayout>
  );
}
