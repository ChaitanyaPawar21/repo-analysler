import React, { useState } from 'react';
import { Folder, FolderOpen, FileJson, FileCode2, ChevronRight, ChevronDown, Sparkles, Binary } from 'lucide-react';
import './FolderStructureCard.css';

// Deep mock tree mimicking a real React project
const MOCK_TREE = [
  { name: '.github', type: 'folder', children: [
    { name: 'workflows', type: 'folder', children: [
      { name: 'ci.yml', type: 'file', icon: 'binary', desc: 'GitHub Actions workflow file that runs test suites and linting on every push and pull request.' }
    ]}
  ]},
  { name: 'packages', type: 'folder', isOpen: true, children: [
    { name: 'react', type: 'folder', isOpen: true, children: [
      { name: 'src', type: 'folder', isOpen: true, children: [
        { name: 'ReactElement.js', type: 'file', icon: 'js', desc: 'Contains the logic for creating and validating React Elements, the building blocks of React views.' },
        { name: 'ReactHooks.js', type: 'file', icon: 'js', desc: 'Defines the foundational Hooks API (useState, useEffect) that components use to hook into React state and lifecycle.' },
        { name: 'ReactSharedInternals.js', type: 'file', icon: 'js', desc: 'Exports internal constants and modules shared between react and the various reconcilers.' }
      ]},
      { name: 'index.js', type: 'file', icon: 'js', desc: 'The main entry point for the React package. Re-exports public APIs.' },
      { name: 'package.json', type: 'file', icon: 'json', desc: 'NPM configuration for the react package, defining version, entry points, and dependencies.' }
    ]},
    { name: 'react-dom', type: 'folder', children: [
      { name: 'client', type: 'folder', children: [
        { name: 'ReactDOMRoot.js', type: 'file', icon: 'js', desc: 'Provides the createRoot API for rendering React elements into the DOM concurrently.' }
      ]},
      { name: 'server', type: 'folder', children: [
        { name: 'ReactDOMServer.js', type: 'file', icon: 'js', desc: 'Handles server-side rendering logic to convert component trees into HTML strings or streams.' }
      ]}
    ]},
    { name: 'react-reconciler', type: 'folder', children: [
      { name: 'src', type: 'folder', children: [
        { name: 'ReactFiberWorkLoop.js', type: 'file', icon: 'js', desc: 'The heart of React\'s concurrent mode. Contains the interruptible work loop that processes Fiber nodes.' },
        { name: 'ReactFiberCommitWork.js', type: 'file', icon: 'js', desc: 'Handles the commit phase, where React writes the final calculated changes to the host environment (like the DOM).' }
      ]}
    ]},
    { name: 'scheduler', type: 'folder', children: [
      { name: 'src', type: 'folder', children: [
        { name: 'Scheduler.js', type: 'file', icon: 'js', desc: 'A cooperative scheduler for scheduling priority-based work loops in the browser.' }
      ]}
    ]}
  ]},
  { name: 'scripts', type: 'folder', children: [
    { name: 'rollup', type: 'folder', children: [
      { name: 'build.js', type: 'file', icon: 'js', desc: 'Build script that uses Rollup to compile all the monorepo packages into their production bundles.' }
    ]}
  ]},
  { name: 'package.json', type: 'file', icon: 'json', desc: 'Main repository package.json managing global devDependencies and workspace declarations.' },
  { name: 'README.md', type: 'file', icon: 'binary', desc: 'Main documentation file explaining how to build and contribute to the repository.' },
];

const FileIcon = ({ icon }) => {
  if (icon === 'json') return <FileJson size={14} color="#FACC15" />;
  if (icon === 'js') return <FileCode2 size={14} color="#F7DF1E" />;
  return <Binary size={14} color="var(--color-text-muted)" />;
};

const TreeNode = ({ node, indentation = 0, selectedNode, onSelectNode }) => {
  const [isOpen, setIsOpen] = useState(node.isOpen || false);
  const isFolder = node.type === 'folder';
  const isSelected = selectedNode === node;

  const handleRowClick = (e) => {
    e.stopPropagation();
    if (isFolder) {
      setIsOpen(!isOpen);
    }
    // Set selected node to display in the right panel
    onSelectNode(node);
  };

  return (
    <div className="fs-tree-node">
      <div 
        className={`fs-tree-row ${isSelected ? 'selected' : ''}`} 
        style={{ paddingLeft: `${indentation * 16}px` }}
        onClick={handleRowClick}
      >
        <span className="fs-collapse-icon">
          {isFolder ? (
            isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />
          ) : <span style={{ width: 14, display: 'inline-block' }} />}
        </span>
        
        <span className="fs-type-icon">
          {isFolder ? (
            isOpen ? <FolderOpen size={16} color="var(--color-accent-blue)" /> : <Folder size={16} color="var(--color-text-muted)" />
          ) : (
            <FileIcon icon={node.icon} />
          )}
        </span>
        
        <span className="fs-node-name">{node.name}</span>
      </div>
      
      {isFolder && isOpen && node.children && (
        <div className="fs-tree-children">
          {node.children.map((child, idx) => (
            <TreeNode 
              key={`${indentation}-${idx}`} 
              node={child} 
              indentation={indentation + 1} 
              selectedNode={selectedNode}
              onSelectNode={onSelectNode}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default function FolderStructureCard() {
  const [selectedNode, setSelectedNode] = useState(null);

  // default placeholder text
  const placeholderText = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam id arcu sed nisl tempor fermentum. Nunc at elit diam. Nullam id dui non diam lacinia sagittis vel ut nulla. Proin in lorem quis lorem fermentum egestas in mattis enim.";

  return (
    <div className="dashboard-card glass-panel fs-card">
      <div className="fs-header">
        <div className="fs-header-title">
          <Folder size={18} color="var(--color-accent-blue)" />
          <span>Repository Architecture</span>
        </div>
        <div className="fs-header-subtitle">
          Interactive deep-dive
        </div>
      </div>

      <div className="fs-body">
        
        {/* Left Side: Folder Tree */}
        <div className="fs-tree-container">
          {MOCK_TREE.map((node, idx) => (
            <TreeNode 
              key={`root-${idx}`} 
              node={node} 
              selectedNode={selectedNode} 
              onSelectNode={setSelectedNode} 
            />
          ))}
        </div>

        {/* Right Side: AI Explanation Details */}
        <div className="fs-detail-container">
          {selectedNode ? (
            <div className={`fs-detail-box ${selectedNode.type === 'folder' ? 'folder-state' : 'file-state'}`}>
              <div className="fs-detail-header">
                {selectedNode.type === 'folder' ? <FolderOpen size={24} color="var(--color-accent-blue)" /> : <FileCode2 size={24} color="#F7DF1E" />}
                <h3>{selectedNode.name}</h3>
              </div>
              <div className="fs-detail-type-badge">
                {selectedNode.type === 'folder' ? 'Directory' : 'File'}
              </div>
              <div className="fs-detail-explanation">
                <div className="fs-detail-ai-tag">
                  <Sparkles size={14} color="#A855F7" />
                  <span>AI Analysis</span>
                </div>
                <p>{selectedNode.desc || placeholderText}</p>
              </div>
            </div>
          ) : (
            <div className="fs-detail-empty">
              <Folder size={48} color="rgba(255,255,255,0.05)" />
              <p>Select any file or directory to view its AI insights</p>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
