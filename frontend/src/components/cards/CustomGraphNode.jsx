import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { Info } from 'lucide-react';

const CustomNode = ({ data }) => {
  return (
    <div className="custom-flow-node group" style={{ ...data.style }}>
      <Handle type="target" position={Position.Left} className="flow-handle" />
      
      <div className="node-content">
        <div className="node-icon-wrapper">
          {data.icon}
        </div>
        <div className="node-label">{data.label}</div>
      </div>
      
      {/* Tooltip on hover */}
      <div className="node-tooltip">
        <div className="tooltip-header">
          <Info size={14} color="var(--color-accent-blue)" />
          <span>{data.label} Function</span>
        </div>
        <div className="tooltip-body">
          {data.description || "Processes the data efficiently in this pipeline block."}
        </div>
      </div>

      <Handle type="source" position={Position.Right} className="flow-handle" />
    </div>
  );
};

export default memo(CustomNode);
