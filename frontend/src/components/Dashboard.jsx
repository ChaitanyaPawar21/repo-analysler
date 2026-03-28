import React, { useRef } from 'react';
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import FolderStructureCard from './cards/FolderStructureCard';
import DependencyGraphCard from './cards/DependencyGraphCard';
import ExecutionFlowCard from './cards/ExecutionFlowCard';
import CriticalFilesCard from './cards/CriticalFilesCard';
import AIExplanationCard from './cards/AIExplanationCard';
import './Dashboard.css';

export default function Dashboard() {
  const dashboardRef = useRef(null);

  useGSAP(() => {
    gsap.fromTo(
      '.dashboard-card',
      { y: 30, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.6, stagger: 0.1, ease: 'power2.out', delay: 0.4 }
    );
  }, { scope: dashboardRef });

  return (
    <div className="dashboard-grid" ref={dashboardRef}>
      {/* Top Row - Folder Structure spans full width */}
      <div className="card-container col-span-12">
        <FolderStructureCard />
      </div>

      {/* Middle Row - Dependencies mapping to reference image */}
      <div className="card-container col-span-12">
        <DependencyGraphCard />
      </div>
      
      {/* Third Row - Execution Flow full width */}
      <div className="card-container col-span-12">
        <ExecutionFlowCard />
      </div>

      {/* Bottom Row - Critical Files and AI Overview side by side */}
      <div className="card-container col-span-6">
        <CriticalFilesCard />
      </div>
      <div className="card-container col-span-6">
        <AIExplanationCard />
      </div>
    </div>
  );
}
