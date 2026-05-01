import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

const SwarmGraph = ({ swarmStatus }) => {
  const svgRef = useRef();
  const wrapperRef = useRef();

  useEffect(() => {
    if (!swarmStatus || Object.keys(swarmStatus).length === 0) return;

    const nodes = Object.entries(swarmStatus).map(([name, data]) => ({
      id: name,
      group: data.running ? 1 : 2,
      tasks: data.tasks || 0,
      lastActive: Date.now(),
      department: (name === 'Dre' || name === 'Ava') ? 'Strategic' : 
                  (name === 'Codesmith') ? 'Engineering' : 
                  (name === 'Fenko') ? 'Marketing' : 'Security'
    }));

    const departments = ['Strategic', 'Engineering', 'Marketing', 'Security'];
    const deptCenters = {
      'Strategic': { x: 300, y: 175 },
      'Engineering': { x: 150, y: 110 },
      'Marketing': { x: 450, y: 110 },
      'Security': { x: 300, y: 270 }
    };

    const links = [];
    if (swarmStatus['Fenko'] && swarmStatus['Codesmith']) {
      links.push({ source: 'Fenko', target: 'Codesmith', value: 3 });
    }
    if (swarmStatus['Dre']) {
      Object.keys(swarmStatus).forEach(name => {
        if (name !== 'Dre') links.push({ source: 'Dre', target: name, value: 1.5 });
      });
    }

    const width = 600;
    const height = 350;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    // --- GRADIENTS & FILTERS ---
    const defs = svg.append("defs");
    
    const nodeGlow = defs.append("filter")
      .attr("id", "nodeGlow")
      .attr("x", "-50%")
      .attr("y", "-50%")
      .attr("width", "200%")
      .attr("height", "200%");
    
    nodeGlow.append("feGaussianBlur")
      .attr("stdDeviation", "4")
      .attr("result", "blur");
    
    const feMerge = nodeGlow.append("feMerge");
    feMerge.append("feMergeNode").attr("in", "blur");
    feMerge.append("feMergeNode").attr("in", "SourceGraphic");

    // Wave group removed for stability

    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id(d => d.id).distance(130))
      .force("charge", d3.forceManyBody().strength(-500))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(50))
      .force("x", d3.forceX(d => deptCenters[d.department]?.x).strength(0.15))
      .force("y", d3.forceY(d => deptCenters[d.department]?.y).strength(0.15));

    // Department Labels
    svg.append("g")
      .selectAll("text")
      .data(departments)
      .join("text")
      .attr("x", d => deptCenters[d].x)
      .attr("y", d => deptCenters[d].y)
      .attr("text-anchor", "middle")
      .attr("fill", "white")
      .attr("opacity", 0.03)
      .attr("font-size", "45px")
      .attr("font-weight", "950")
      .attr("pointer-events", "none")
      .attr("letter-spacing", "0.2em")
      .text(d => d.toUpperCase());

    const link = svg.append("g")
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke", "rgba(14, 165, 233, 0.15)")
      .attr("stroke-width", d => d.value * 1.5)
      .attr("stroke-dasharray", "4, 4")
      .attr("class", "neural-path");

    const node = svg.append("g")
      .selectAll("g")
      .data(nodes)
      .join("g")
      .call(d3.drag()
        .on("start", (e, d) => { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
        .on("drag", (e, d) => { d.fx = e.x; d.fy = e.y; })
        .on("end", (e, d) => { if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }));

    // Node Outer Ring (Load Sensitive)
    node.append("circle")
      .attr("r", d => 22 + (d.tasks * 2))
      .attr("fill", "transparent")
      .attr("stroke", d => d.group === 1 ? "rgba(14, 165, 233, 0.4)" : "rgba(239, 68, 68, 0.2)")
      .attr("stroke-width", "1")
      .attr("stroke-dasharray", "2, 2")
      .attr("class", "node-outer-ring");

    // Core Node
    node.append("circle")
      .attr("r", d => 10 + Math.min(d.tasks, 15))
      .attr("fill", d => d.group === 1 ? "var(--accent-primary)" : "#ef4444")
      .style("filter", "url(#nodeGlow)")
      .attr("class", "node-core");

    node.append("text")
      .text(d => d.id.toUpperCase())
      .attr("y", d => 40 + (d.tasks * 2))
      .attr("text-anchor", "middle")
      .attr("fill", "white")
      .attr("font-size", "9px")
      .attr("font-weight", "900")
      .attr("letter-spacing", "0.15em")
      .attr("class", "opacity-40 uppercase tracking-widest");

    simulation.on("tick", () => {
      link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
          .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
      node.attr("transform", d => `translate(${d.x},${d.y})`);
    });

    return () => simulation.stop();
  }, [swarmStatus]);

  return (
    <div ref={wrapperRef} className="w-full h-full bg-black/40 rounded-[2.5rem] border border-white/5 overflow-hidden flex flex-col relative">
       <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle_at_50%_50%,rgba(14,165,233,0.05),transparent)]" />
       
       <div className="px-8 py-5 border-b border-white/5 flex justify-between items-center bg-white/[0.02] backdrop-blur-xl z-10">
          <div className="flex items-center gap-3">
             <div className="w-2 h-2 bg-blue-500 rounded-full shadow-[0_0_10px_rgba(14,165,233,0.8)] animate-pulse" />
             <span className="text-[10px] font-black uppercase tracking-[0.2em] text-blue-400">Neural Network Topology</span>
          </div>
          <div className="flex gap-6 items-center">
            <span className="text-[8px] font-black uppercase opacity-20 tracking-widest">Global Synaptic Load</span>
            <div className="w-32 h-1 bg-white/5 rounded-full overflow-hidden">
               <div style={{ width: '78%' }} className="h-full bg-gradient-to-r from-blue-600 to-blue-400" />
            </div>
          </div>
       </div>

       <div className="flex-1 relative overflow-hidden flex items-center justify-center">
         <div className="absolute inset-0 grid-war-room opacity-5" />
         <svg ref={svgRef} viewBox="0 0 600 350" className="w-full h-full z-10 cursor-crosshair scale-110" />
       </div>

       <style jsx>{`
         .grid-war-room {
           background-image: 
             linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
             linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px);
           background-size: 40px 40px;
         }
       `}</style>
    </div>
  );
};

export default SwarmGraph;
