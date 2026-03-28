import React, { useRef } from 'react';
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { Star, GitFork, Code2, MessageSquare, Play } from 'lucide-react';
import './Header.css';

export default function Header({ query, onOpenChat }) {
  const headerRef = useRef(null);

  const [org, repo] = query ? query.split('/') : ['facebook', 'react'];

  useGSAP(() => {
    gsap.fromTo(
      headerRef.current,
      { y: -30, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.6, ease: 'power2.out', delay: 0.2 }
    );
  }, { scope: headerRef });

  return (
    <header className="repo-header glass-panel" ref={headerRef}>
      <div className="header-info">
        <h1 className="repo-title">{org} / <span>{repo || org}</span></h1>
        
        <div className="repo-metadata">
          <div className="meta-item">
            <Star size={14} />
            <span>212k</span>
          </div>
          <div className="meta-item">
            <GitFork size={14} />
            <span>44.5k</span>
          </div>
          <div className="meta-item lang-badge">
            <Code2 size={14} />
            <span>JavaScript</span>
          </div>
        </div>
      </div>

      <div className="header-actions">
        <button className="btn-secondary" onClick={onOpenChat}>
          <MessageSquare size={16} />
          <span>Open Chat</span>
        </button>
        <button className="btn-primary">
          <Play size={16} fill="currentColor" />
          <span>Analyze Repo</span>
        </button>
      </div>
    </header>
  );
}
