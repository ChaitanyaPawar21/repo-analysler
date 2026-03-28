import React, { useRef } from 'react';
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { MoveRight, GitCommit } from 'lucide-react';
import './Cards.css';

export default function ExecutionFlowCard() {
  const flowRef = useRef(null);

  useGSAP(() => {
    const tl = gsap.timeline({ repeat: -1 });
    
    tl.fromTo('.flow-arrow', 
      { x: -10, opacity: 0 },
      { x: 5, opacity: 1, duration: 0.6, stagger: 0.3, ease: 'power2.out' }
    )
    .to('.flow-arrow', { x: 15, opacity: 0, duration: 0.4, stagger: 0.3 }, "+=0.5");
    
  }, { scope: flowRef });

  return (
    <div className="dashboard-card glass-panel flow-card" ref={flowRef}>
      <div className="card-header">
        <GitCommit size={18} color="var(--color-accent-blue)" />
        <span>Execution Flow</span>
      </div>
      <div className="flow-container">
        
        <div className="flow-step">
          <div className="step-box">Entry: index.js</div>
        </div>
        
        <div className="flow-arrow"><MoveRight color="var(--color-accent-blue)" /></div>
        
        <div className="flow-step">
          <div className="step-box">React.createElement</div>
        </div>
        
        <div className="flow-arrow"><MoveRight color="var(--color-accent-blue)" /></div>
        
        <div className="flow-step">
          <div className="step-box">Fiber Reconciler</div>
        </div>
        
        <div className="flow-arrow"><MoveRight color="var(--color-accent-blue)" /></div>
        
        <div className="flow-step">
          <div className="step-box">Commit Phase (DOM)</div>
        </div>

      </div>
    </div>
  );
}
