import React, { useRef } from 'react';
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { Terminal, Plus, Code, Folder, Settings, User } from 'lucide-react';
import './Sidebar.css';

const MOCK_REPOS = [
  { id: 1, name: 'facebook/react', active: true },
  { id: 2, name: 'vercel/next.js', active: false },
  { id: 3, name: 'vuejs/core', active: false },
  { id: 4, name: 'sveltejs/svelte', active: false },
];

export default function Sidebar({ onHomeClick }) {
  const sidebarRef = useRef(null);

  useGSAP(() => {
    gsap.fromTo(
      sidebarRef.current,
      { x: -50, opacity: 0 },
      { x: 0, opacity: 1, duration: 0.6, ease: 'power3.out' }
    );
    
    gsap.fromTo(
      '.repo-item',
      { x: -20, opacity: 0 },
      { x: 0, opacity: 1, duration: 0.4, stagger: 0.08, ease: 'power2.out', delay: 0.3 }
    );
  }, { scope: sidebarRef });

  return (
    <aside className="sidebar glass-panel" ref={sidebarRef}>
      <div className="sidebar-header">
        <div className="logo" onClick={onHomeClick} style={{cursor: 'pointer'}}>
          <Terminal size={24} color="var(--color-accent-blue)" />
          <span>Repo-Learn</span>
        </div>
        <button className="new-analysis-btn" onClick={onHomeClick}>
          <Plus size={16} />
          <span>New Analysis</span>
        </button>
      </div>

      <div className="sidebar-content">
        <div className="section-title">RECENT REPOSITORIES</div>
        <ul className="repo-list">
          {MOCK_REPOS.map((repo) => (
            <li key={repo.id} className={`repo-item ${repo.active ? 'active' : ''}`}>
              <Code size={16} />
              <span>{repo.name}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="sidebar-footer">
        <button className="footer-btn">
          <Settings size={18} />
          <span>Settings</span>
        </button>
        <button className="footer-btn">
          <User size={18} />
          <span>Profile</span>
        </button>
      </div>
    </aside>
  );
}
