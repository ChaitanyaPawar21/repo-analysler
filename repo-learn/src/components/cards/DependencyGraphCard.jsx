import React, { useCallback } from 'react';
import { Network, Database, Server, Smartphone, Layout, ShoppingCart, UserCheck } from 'lucide-react';
import { ReactFlow, Controls, Background, addEdge, useNodesState, useEdgesState, MarkerType } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import './DependencyGraph.css';

import CustomGraphNode from './CustomGraphNode';

const nodeTypes = {
  customNode: CustomGraphNode,
};

// Initial setup matching the business logic visual complexity
const initialNodes = [
  // --- PARENT GROUPS ---
  {
    id: 'group-auth',
    type: 'group',
    data: { label: 'Auth & Identity' },
    position: { x: 50, y: 50 },
    style: { width: 280, height: 200, backgroundColor: 'rgba(56, 189, 248, 0.05)', border: '1px solid rgba(56, 189, 248, 0.3)', borderRadius: 16 },
  },
  {
    id: 'group-core',
    type: 'group',
    data: { label: 'Core Discovery' },
    position: { x: 400, y: 0 },
    style: { width: 500, height: 350, backgroundColor: 'rgba(234, 179, 8, 0.05)', border: '1px solid rgba(234, 179, 8, 0.3)', borderRadius: 16 },
  },
  {
    id: 'group-checkout',
    type: 'group',
    data: { label: 'Order & Checkout' },
    position: { x: 950, y: 50 },
    style: { width: 400, height: 250, backgroundColor: 'rgba(168, 85, 247, 0.05)', border: '1px solid rgba(168, 85, 247, 0.3)', borderRadius: 16 },
  },

  // --- CHILD NODES ---
  // Auth
  {
    id: 'node-login',
    type: 'customNode',
    data: { label: 'User Login', icon: <UserCheck size={18} />, description: 'Handles session tokens and OAuth validation against identity providers.', style: { borderLeftColor: '#38bdf8' } },
    position: { x: 40, y: 60 },
    parentId: 'group-auth',
    extent: 'parent',
  },
  
  // Core Discovery
  {
    id: 'node-app',
    type: 'customNode',
    data: { label: 'Mobile App', icon: <Smartphone size={18} />, description: 'Entry point for consumer application.', style: { borderLeftColor: '#eab308' } },
    position: { x: 40, y: 130 },
    parentId: 'group-core',
    extent: 'parent',
  },
  {
    id: 'node-browse',
    type: 'customNode',
    data: { label: 'Catalogue Browse', icon: <Layout size={18} />, description: 'Fetches cached catalog data dynamically as user scrolls.', style: { borderLeftColor: '#eab308' } },
    position: { x: 250, y: 50 },
    parentId: 'group-core',
    extent: 'parent',
  },
  {
    id: 'node-search',
    type: 'customNode',
    data: { label: 'Direct Search', icon: <Database size={18} />, description: 'Hits the Elasticsearch index to return immediate text matches.', style: { borderLeftColor: '#eab308' } },
    position: { x: 250, y: 200 },
    parentId: 'group-core',
    extent: 'parent',
  },

  // Checkout
  {
    id: 'node-cart',
    type: 'customNode',
    data: { label: 'Shopping Cart', icon: <ShoppingCart size={18} />, description: 'Validates stock availability and calculates taxes in real-time.', style: { borderLeftColor: '#a855f7' } },
    position: { x: 40, y: 80 },
    parentId: 'group-checkout',
    extent: 'parent',
  },
  {
    id: 'node-payment',
    type: 'customNode',
    data: { label: 'Payment Gateway', icon: <Server size={18} />, description: 'Processes secure transactions via third-party providers (Stripe/PayPal).', style: { borderLeftColor: '#a855f7' } },
    position: { x: 220, y: 80 },
    parentId: 'group-checkout',
    extent: 'parent',
  }
];

// Edges defined with orthogonal step routing
const initialEdges = [
  { id: 'e-login-app', source: 'node-login', target: 'node-app', type: 'smoothstep', animated: true, markerEnd: { type: MarkerType.ArrowClosed, color: '#94a3b8' }, style: { stroke: '#94a3b8', strokeWidth: 2 } },
  { id: 'e-app-browse', source: 'node-app', target: 'node-browse', type: 'smoothstep', markerEnd: { type: MarkerType.ArrowClosed, color: '#94a3b8' }, style: { stroke: '#94a3b8', strokeWidth: 2 } },
  { id: 'e-app-search', source: 'node-app', target: 'node-search', type: 'smoothstep', markerEnd: { type: MarkerType.ArrowClosed, color: '#94a3b8' }, style: { stroke: '#94a3b8', strokeWidth: 2 } },
  { id: 'e-browse-cart', source: 'node-browse', target: 'node-cart', type: 'smoothstep', markerEnd: { type: MarkerType.ArrowClosed, color: '#a855f7' }, style: { stroke: '#a855f7', strokeWidth: 2 } },
  { id: 'e-search-cart', source: 'node-search', target: 'node-cart', type: 'smoothstep', markerEnd: { type: MarkerType.ArrowClosed, color: '#a855f7' }, style: { stroke: '#a855f7', strokeWidth: 2 } },
  { id: 'e-cart-gateway', source: 'node-cart', target: 'node-payment', type: 'smoothstep', animated: true, markerEnd: { type: MarkerType.ArrowClosed, color: '#a855f7' }, style: { stroke: '#a855f7', strokeWidth: 2 } }
];

export default function DependencyGraphCard() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback((params) => setEdges((eds) => addEdge({ ...params, type: 'smoothstep', markerEnd: { type: MarkerType.ArrowClosed } }, eds)), [setEdges]);

  return (
    <div className="dashboard-card glass-panel dep-flow-card">
      <div className="card-header dep-header">
        <Network size={18} color="var(--color-accent-blue)" />
        <span>System Architecture & Dependency Graph</span>
        <span className="graph-badge">Ctrl + Scroll to Zoom</span>
      </div>
      
      <div className="react-flow-wrapper">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
          panOnScroll={false}
          zoomOnScroll={false}
          zoomOnPinch={true}
          panOnDrag={true}
          preventScrolling={false}
          minZoom={0.2}
          attributionPosition="bottom-right"
          className="dark-theme-flow"
        >
          <Background color="rgba(255,255,255,0.05)" gap={20} size={1} />
          <Controls className="custom-controls" showInteractive={false} />
        </ReactFlow>
      </div>
    </div>
  );
}
