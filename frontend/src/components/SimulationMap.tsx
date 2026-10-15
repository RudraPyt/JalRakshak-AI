import React, { useState, useMemo } from 'react';
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  Anchor,
  Home,
  AlertCircle,
  Layers,
} from 'lucide-react';
import type {
  ZoneNode,
  NetworkEdge,
  Boat,
  Shelter,
  Incident,
  Assignment,
} from '../types';

interface SimulationMapProps {
  zones: ZoneNode[];
  edges: NetworkEdge[];
  boats: Boat[];
  shelters: Shelter[];
  incidents: Incident[];
  activeAssignments?: Assignment[];
  selectedEntity: { type: 'boat' | 'incident' | 'shelter' | 'edge' | 'zone'; data: any } | null;
  onSelectEntity: (type: 'boat' | 'incident' | 'shelter' | 'edge' | 'zone', data: any) => void;
}

export const SimulationMap: React.FC<SimulationMapProps> = ({
  zones,
  edges,
  boats,
  shelters,
  incidents,
  selectedEntity,
  onSelectEntity,
}) => {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });

  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [filterLayer, setFilterLayer] = useState<'all' | 'incidents' | 'boats' | 'shelters'>('all');

  // Coordinate scaling: Map synthetic X [0.2, 3.2] and Y [0.4, 3.0] to SVG canvas [80, 820] x [80, 560]
  const svgWidth = 900;
  const svgHeight = 620;
  const paddingX = 90;
  const paddingY = 80;

  const minX = 0.2;
  const maxX = 3.2;
  const minY = 0.4;
  const maxY = 3.0;

  const toSvgX = (x: number) => {
    return paddingX + ((x - minX) / (maxX - minX)) * (svgWidth - 2 * paddingX);
  };

  const toSvgY = (y: number) => {
    return paddingY + ((y - minY) / (maxY - minY)) * (svgHeight - 2 * paddingY);
  };

  // Quick lookup map of zone coordinates
  const zoneCoords = useMemo(() => {
    const map = new Map<string, { x: number; y: number }>();
    zones.forEach((z) => {
      map.set(z.zone_id, { x: toSvgX(z.x), y: toSvgY(z.y) });
    });
    return map;
  }, [zones]);

  // Active routes edges lookup
  const activeRouteEdges = useMemo(() => {
    const edgeSet = new Set<string>();
    boats.forEach((b) => {
      if (b.planned_route_zones && b.planned_route_zones.length > 1) {
        for (let i = 0; i < b.planned_route_zones.length - 1; i++) {
          const u = b.planned_route_zones[i];
          const v = b.planned_route_zones[i + 1];
          const match = edges.find(
            (e) => (e.from_zone === u && e.to_zone === v) || (e.from_zone === v && e.to_zone === u)
          );
          if (match) edgeSet.add(match.edge_id);
        }
      }
    });
    return edgeSet;
  }, [boats, edges]);

  // Pan / Zoom handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return;
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    setPan({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y,
    });
  };

  const handleMouseUp = () => setIsDragging(false);

  const handleResetView = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  return (
    <div
      className="glass-panel"
      style={{
        position: 'relative',
        width: '100%',
        height: '620px',
        overflow: 'hidden',
        background: 'var(--map-bg)',
        border: '1px solid var(--border-strong)',
        cursor: isDragging ? 'grabbing' : 'grab',
      }}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      {/* Map Controls Overlay */}
      <div
        style={{
          position: 'absolute',
          top: '12px',
          right: '12px',
          zIndex: 10,
          display: 'flex',
          gap: '0.4rem',
        }}
      >
        <button
          className="btn btn-secondary"
          style={{ padding: '0.4rem 0.6rem' }}
          onClick={(e) => {
            e.stopPropagation();
            setZoom((z) => Math.min(2.0, z + 0.15));
          }}
          title="Zoom In"
        >
          <ZoomIn size={14} />
        </button>
        <button
          className="btn btn-secondary"
          style={{ padding: '0.4rem 0.6rem' }}
          onClick={(e) => {
            e.stopPropagation();
            setZoom((z) => Math.max(0.6, z - 0.15));
          }}
          title="Zoom Out"
        >
          <ZoomOut size={14} />
        </button>
        <button
          className="btn btn-secondary"
          style={{ padding: '0.4rem 0.6rem' }}
          onClick={(e) => {
            e.stopPropagation();
            handleResetView();
          }}
          title="Reset View"
        >
          <Maximize2 size={14} />
        </button>
      </div>

      {/* Layer Visibility Filter */}
      <div
        style={{
          position: 'absolute',
          top: '12px',
          left: '12px',
          zIndex: 10,
          display: 'flex',
          alignItems: 'center',
          gap: '0.35rem',
          background: 'var(--map-overlay-bg)',
          padding: '0.25rem 0.5rem',
          borderRadius: '8px',
          border: '1px solid var(--border-subtle)',
        }}
      >
        <Layers size={13} color="var(--cyan-bright)" />
        <span style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>Layer:</span>
        {(['all', 'incidents', 'boats', 'shelters'] as const).map((layer) => (
          <button
            key={layer}
            onClick={(e) => {
              e.stopPropagation();
              setFilterLayer(layer);
            }}
            style={{
              fontSize: '0.7rem',
              fontWeight: 600,
              textTransform: 'capitalize',
              padding: '0.15rem 0.45rem',
              borderRadius: '4px',
              border: 'none',
              cursor: 'pointer',
              background: filterLayer === layer ? 'var(--cyan-bright)' : 'transparent',
              color: filterLayer === layer ? '#ffffff' : 'var(--text-muted)',
            }}
          >
            {layer}
          </button>
        ))}
      </div>

      {/* Legend Badge */}
      <div
        style={{
          position: 'absolute',
          bottom: '12px',
          left: '12px',
          zIndex: 10,
          background: 'var(--map-overlay-bg)',
          padding: '0.4rem 0.75rem',
          borderRadius: '8px',
          border: '1px solid var(--border-subtle)',
          fontSize: '0.725rem',
          display: 'flex',
          gap: '0.85rem',
          color: 'var(--text-muted)',
        }}
      >
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
          <span style={{ width: '12px', height: '3px', background: 'var(--cyan-bright)', display: 'inline-block' }} /> Open Route
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
          <span style={{ width: '12px', height: '3px', background: 'var(--rose-crit)', borderTop: '2px dashed var(--rose-crit)', display: 'inline-block' }} /> Closed Hazard
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
          <Anchor size={12} color="var(--blue-bright)" /> Boat Fleet
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
          <AlertCircle size={12} color="var(--rose-crit)" /> Incident Pin
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
          <Home size={12} color="var(--emerald-safe)" /> Shelter Facility
        </span>
      </div>

      {/* Main SVG Graph */}
      <svg
        width="100%"
        height="100%"
        viewBox={`0 0 ${svgWidth} ${svgHeight}`}
        style={{
          transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
          transformOrigin: 'center center',
          transition: isDragging ? 'none' : 'transform 0.15s ease-out',
        }}
      >
        <defs>
          {/* Glowing Filters */}
          <filter id="glow-cyan" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
          <filter id="glow-red" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
          {/* Animated Route Marker Gradient */}
          <linearGradient id="active-flow" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#06b6d4" />
            <stop offset="50%" stopColor="#38bdf8" />
            <stop offset="100%" stopColor="#6366f1" />
          </linearGradient>
        </defs>

        {/* 1. EDGES / ROUTES */}
        <g id="edges-group">
          {edges.map((edge) => {
            const u = zoneCoords.get(edge.from_zone);
            const v = zoneCoords.get(edge.to_zone);
            if (!u || !v) return null;

            const isClosed = edge.status === 'closed';
            const isUncertain = edge.status === 'uncertain';
            const isActiveRoute = activeRouteEdges.has(edge.edge_id);
            const isSelected = selectedEntity?.type === 'edge' && selectedEntity?.data.edge_id === edge.edge_id;

            const midX = (u.x + v.x) / 2;
            const midY = (u.y + v.y) / 2;

            return (
              <g
                key={edge.edge_id}
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectEntity('edge', edge);
                }}
                style={{ cursor: 'pointer' }}
              >
                {/* Background Line for hit test */}
                <line
                  x1={u.x}
                  y1={u.y}
                  x2={v.x}
                  y2={v.y}
                  stroke="transparent"
                  strokeWidth="18"
                />

                {/* Visible Edge Line */}
                <line
                  x1={u.x}
                  y1={u.y}
                  x2={v.x}
                  y2={v.y}
                  stroke={
                    isClosed
                      ? 'var(--rose-crit)'
                      : isActiveRoute
                      ? 'url(#active-flow)'
                      : isUncertain
                      ? 'var(--amber-warn)'
                      : 'rgba(6, 182, 212, 0.45)'
                  }
                  strokeWidth={isSelected ? 5 : isActiveRoute ? 4 : isClosed ? 3 : 2}
                  strokeDasharray={isClosed ? '6,6' : isActiveRoute ? '8,4' : undefined}
                  className={isActiveRoute ? 'animated-route-flow' : undefined}
                  filter={isClosed ? 'url(#glow-red)' : isSelected ? 'url(#glow-cyan)' : undefined}
                />

                {/* Closed Hazard Badge / Label on Midpoint */}
                {isClosed && (
                  <g transform={`translate(${midX}, ${midY})`}>
                    <circle r="11" fill="rgba(244, 63, 94, 0.9)" />
                    <text
                      textAnchor="middle"
                      dy="4"
                      fontSize="9"
                      fontWeight="bold"
                      fill="#fff"
                    >
                      ✕
                    </text>
                  </g>
                )}

                {/* Edge ID & travel time badge */}
                {!isClosed && (
                  <g transform={`translate(${midX}, ${midY})`}>
                    <rect
                      x="-18"
                      y="-8"
                      width="36"
                      height="16"
                      rx="4"
                      fill="var(--map-badge-bg)"
                      stroke={isSelected ? 'var(--cyan-bright)' : 'var(--border-subtle)'}
                      strokeWidth="1"
                    />
                    <text
                      textAnchor="middle"
                      dy="3.5"
                      fontSize="8.5"
                      fontFamily="var(--font-mono)"
                      fill="var(--text-muted)"
                    >
                      {edge.edge_id}
                    </text>
                  </g>
                )}
              </g>
            );
          })}
        </g>

        {/* 2. ZONE NODES */}
        <g id="zones-group">
          {zones.map((zone) => {
            const pos = zoneCoords.get(zone.zone_id);
            if (!pos) return null;

            const isSelected = selectedEntity?.type === 'zone' && selectedEntity?.data.zone_id === zone.zone_id;
            const zoneIncidents = incidents.filter((inc) => inc.zone === zone.zone_id && inc.lifecycle_status !== 'fully_served');


            return (
              <g
                key={zone.zone_id}
                transform={`translate(${pos.x}, ${pos.y})`}
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectEntity('zone', zone);
                }}
                style={{ cursor: 'pointer' }}
              >
                {/* Zone Halo */}
                <circle
                  r={isSelected ? 26 : 22}
                  fill="var(--map-node-bg)"
                  stroke={isSelected ? 'var(--cyan-bright)' : 'rgba(6, 182, 212, 0.3)'}
                  strokeWidth={isSelected ? 2.5 : 1.5}
                />

                {/* Inner Ring */}
                <circle
                  r="14"
                  fill="var(--map-node-inner)"
                  stroke="var(--border-subtle)"
                  strokeWidth="1"
                />

                {/* Zone Label */}
                <text
                  textAnchor="middle"
                  dy="-28"
                  fontSize="11"
                  fontWeight="600"
                  fill="var(--text-main)"
                  letterSpacing="0.02em"
                >
                  {zone.zone_id}
                </text>

                {/* Mini counts inside node */}
                <text
                  textAnchor="middle"
                  dy="3.5"
                  fontSize="9.5"
                  fontFamily="var(--font-mono)"
                  fontWeight="700"
                  fill={zoneIncidents.length > 0 ? 'var(--amber-warn)' : 'var(--text-muted)'}
                >
                  {zoneIncidents.length > 0 ? `${zoneIncidents.length} req` : 'ok'}
                </text>
              </g>
            );
          })}
        </g>

        {/* 3. SHELTER FACILITIES */}
        {(filterLayer === 'all' || filterLayer === 'shelters') && (
          <g id="shelters-group">
            {shelters.map((shelter) => {
              const zonePos = zoneCoords.get(shelter.zone_id);
              if (!zonePos) return null;

              // Offset shelter marker slightly northwest of its anchor zone
              const sx = zonePos.x - 38;
              const sy = zonePos.y - 32;

              const remaining = Math.max(0, shelter.capacity_people - shelter.current_occupancy - shelter.reserved_capacity);
              const isFull = shelter.status === 'full' || remaining === 0;
              const isSelected = selectedEntity?.type === 'shelter' && selectedEntity?.data.shelter_id === shelter.shelter_id;


              return (
                <g
                  key={shelter.shelter_id}
                  transform={`translate(${sx}, ${sy})`}
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelectEntity('shelter', shelter);
                  }}
                  style={{ cursor: 'pointer' }}
                >
                  {/* Outer container */}
                  <rect
                    x="-24"
                    y="-16"
                    width="48"
                    height="32"
                    rx="6"
                    fill={isFull ? 'rgba(244, 63, 94, 0.2)' : 'rgba(16, 185, 129, 0.2)'}
                    stroke={isSelected ? 'var(--cyan-bright)' : isFull ? 'var(--rose-crit)' : 'var(--emerald-safe)'}
                    strokeWidth={isSelected ? 2 : 1}
                  />

                  {/* Shelter Icon */}
                  <g transform="translate(-16, -11) scale(0.65)">
                    <Home color={isFull ? '#f87171' : '#34d399'} />
                  </g>

                  {/* Shelter ID */}
                  <text
                    x="2"
                    y="-4"
                    fontSize="8.5"
                    fontWeight="700"
                    fill="#ffffff"
                    fontFamily="var(--font-mono)"
                  >
                    {shelter.shelter_id}
                  </text>

                  {/* Occupancy / Remaining Capacity */}
                  <text
                    x="-18"
                    y="10"
                    fontSize="7.5"
                    fill={isFull ? '#fda4af' : '#a7f3d0'}
                    fontFamily="var(--font-mono)"
                  >
                    {shelter.current_occupancy + shelter.reserved_capacity}/{shelter.capacity_people}
                  </text>
                </g>
              );
            })}
          </g>
        )}

        {/* 4. INCIDENT PINS */}
        {(filterLayer === 'all' || filterLayer === 'incidents') && (
          <g id="incidents-group">
            {incidents.map((inc) => {
              const zonePos = zoneCoords.get(inc.zone);
              if (!zonePos) return null;

              // Offset incident slightly southeast of its zone
              const ix = zonePos.x + 36;
              const iy = zonePos.y - 18;

              const isCritical = inc.reported_urgency === 'critical';
              const isHigh = inc.reported_urgency === 'high';
              const isResolved = inc.lifecycle_status === 'fully_served';
              const isBottleneck = inc.lifecycle_status === 'unmet_shelter_bottleneck';
              const isSelected = selectedEntity?.type === 'incident' && selectedEntity?.data.incident_id === inc.incident_id;

              if (isResolved) return null; // Don't clutter solved incidents on primary pin view

              const pinColor = isCritical
                ? 'var(--rose-crit)'
                : isHigh
                ? 'var(--amber-warn)'
                : isBottleneck
                ? '#f43f5e'
                : 'var(--cyan-bright)';

              return (
                <g
                  key={inc.incident_id}
                  transform={`translate(${ix}, ${iy})`}
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelectEntity('incident', inc);
                  }}
                  style={{ cursor: 'pointer' }}
                >
                  {/* Pulsing ring for critical/high */}
                  {(isCritical || isHigh) && (
                    <circle
                      r="16"
                      fill="none"
                      stroke={pinColor}
                      strokeWidth="1.5"
                      className="pulsing-ring"
                    />
                  )}

                  {/* Pin Circle */}
                  <circle
                    r="10"
                    fill={isBottleneck ? 'rgba(244, 63, 94, 0.4)' : 'var(--map-node-bg)'}
                    stroke={isSelected ? 'var(--cyan-bright)' : pinColor}
                    strokeWidth={isSelected ? 2.5 : 1.5}
                  />

                  {/* Affected Headcount text */}
                  <text
                    textAnchor="middle"
                    dy="3"
                    fontSize="8.5"
                    fontWeight="800"
                    fill="var(--text-main)"
                    fontFamily="var(--font-mono)"
                  >
                    {inc.people_awaiting_pickup !== undefined
                      ? inc.people_awaiting_pickup
                      : Math.max(0, inc.people_affected - inc.people_rescued - inc.people_onboard)}
                  </text>


                  {/* Label tooltip */}
                  <text
                    textAnchor="start"
                    x="13"
                    y="3"
                    fontSize="8"
                    fontWeight="600"
                    fill={pinColor}
                    fontFamily="var(--font-mono)"
                  >
                    {inc.incident_id}
                  </text>
                </g>
              );
            })}
          </g>
        )}

        {/* 5. BOAT FLEET */}
        {(filterLayer === 'all' || filterLayer === 'boats') && (
          <g id="boats-group">
            {boats.map((boat, idx) => {
              const zonePos = zoneCoords.get(boat.current_zone);
              if (!zonePos) return null;

              // Spread boats if multiple in same zone
              const bx = zonePos.x + (idx % 2 === 0 ? -32 : 32);
              const by = zonePos.y + 32;

              const isFailed = boat.status === 'failed';
              const isInTransit = boat.status === 'in_transit' || boat.status === 'servicing';
              const isSelected = selectedEntity?.type === 'boat' && selectedEntity?.data.boat_id === boat.boat_id;

              const boatColor = isFailed
                ? 'var(--rose-crit)'
                : isInTransit
                ? 'var(--cyan-bright)'
                : 'var(--emerald-safe)';

              return (
                <g
                  key={boat.boat_id}
                  transform={`translate(${bx}, ${by})`}
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelectEntity('boat', boat);
                  }}
                  style={{ cursor: 'pointer' }}
                >
                  {/* Boat Container Box */}
                  <rect
                    x="-24"
                    y="-14"
                    width="48"
                    height="28"
                    rx="6"
                    fill="var(--map-node-bg)"
                    stroke={isSelected ? 'var(--cyan-bright)' : boatColor}
                    strokeWidth={isSelected ? 2 : 1.2}
                    filter={isFailed ? 'url(#glow-red)' : isSelected ? 'url(#glow-cyan)' : undefined}
                  />

                  {/* Boat Icon */}
                  <g transform="translate(-19, -9) scale(0.6)">
                    <Anchor color={boatColor} />
                  </g>

                  {/* Boat ID */}
                  <text
                    x="1"
                    y="-2"
                    fontSize="8"
                    fontWeight="700"
                    fill="#ffffff"
                    fontFamily="var(--font-mono)"
                  >
                    {boat.boat_id.replace('BOAT', 'B')}
                  </text>

                  {/* Onboard / Capacity */}
                  <text
                    x="1"
                    y="8"
                    fontSize="7.5"
                    fill={boat.onboard_people > 0 ? 'var(--cyan-bright)' : 'var(--text-muted)'}
                    fontFamily="var(--font-mono)"
                  >
                    {boat.onboard_people}/{boat.capacity_people}
                  </text>
                </g>
              );
            })}
          </g>
        )}
      </svg>
    </div>
  );
};
