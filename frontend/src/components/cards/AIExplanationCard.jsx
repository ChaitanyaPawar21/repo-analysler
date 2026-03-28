import React from 'react';
import { AlignLeft, Bot } from 'lucide-react';
import './Cards.css';

export default function AIExplanationCard() {
  return (
    <div className="dashboard-card glass-panel ai-card">
      <div className="card-header">
        <AlignLeft size={18} color="var(--color-accent-blue)" />
        <span>AI Overview</span>
      </div>
      
      <div className="ai-content-container">
        <div className="ai-bubble">
          <div className="ai-avatar">
            <Bot size={16} color="white" />
          </div>
          <div className="ai-text">
            <p><strong>React</strong> is a JavaScript library for building user interfaces.</p>
            <p>Key points from the repository:</p>
            <ul>
              <li>The codebase works heavily with a <code>Fiber</code> architecture to manage an interruptible work loop.</li>
              <li><code>packages/react-reconciler</code> manages the generic logic for diffing trees.</li>
              <li>Components are internally represented by <code>ReactElement</code> which is ultimately committed to the DOM in <code>react-dom</code>.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
