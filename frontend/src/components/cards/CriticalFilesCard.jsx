import React from 'react';
import { Flame } from 'lucide-react';
import './Cards.css';

const CRITICAL_FILES = [
  { path: 'packages/react-reconciler/src/ReactFiberWorkLoop.js', score: 98 },
  { path: 'packages/react/src/ReactElement.js', score: 92 },
  { path: 'packages/react-dom/src/client/ReactDOMRoot.js', score: 87 },
  { path: 'packages/scheduler/src/Scheduler.js', score: 85 },
];

export default function CriticalFilesCard() {
  return (
    <div className="dashboard-card glass-panel critical-files-card">
      <div className="card-header">
        <Flame size={18} color="#EF4444" />
        <span>Critical Files</span>
      </div>
      <div className="ranking-list">
        {CRITICAL_FILES.map((file, idx) => (
          <div key={idx} className="rank-item">
            <div className="rank-number">{idx + 1}</div>
            <div className="rank-path">
              <code>{file.path}</code>
            </div>
            <div className="rank-score">
              <span className={`score-badge ${file.score > 90 ? 'high' : 'medium'}`}>
                {file.score}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
