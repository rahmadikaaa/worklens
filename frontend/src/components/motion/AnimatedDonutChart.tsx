import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AnimatedNumber } from './MotionPrimitives';

export interface DonutSegment {
  id: string;
  label: string;
  value: number;
  color: string;
}

interface AnimatedDonutChartProps {
  data: DonutSegment[];
  size?: number;
  strokeWidth?: number;
  centerTitle?: string;
  centerValue?: number;
  centerSuffix?: string;
  onSegmentClick?: (segment: DonutSegment) => void;
}

export const AnimatedDonutChart: React.FC<AnimatedDonutChartProps> = ({
  data,
  size = 220,
  strokeWidth = 26,
  centerTitle = 'Total',
  centerValue,
  centerSuffix = '',
  onSegmentClick,
}) => {
  const [hoveredSegment, setHoveredSegment] = useState<DonutSegment | null>(null);

  const total = data.reduce((acc, curr) => acc + curr.value, 0);
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;

  let accumulatedPercent = 0;

  const currentDisplayValue = hoveredSegment ? hoveredSegment.value : (centerValue ?? total);
  const currentDisplayTitle = hoveredSegment ? hoveredSegment.label : centerTitle;

  return (
    <div className="flex flex-col sm:flex-row items-center gap-6">
      {/* SVG Container */}
      <div className="relative flex items-center justify-center shrink-0" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90 overflow-visible">
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="transparent"
            stroke="#1e293b"
            strokeWidth={strokeWidth}
          />

          {data.map((seg) => {
            const percent = total > 0 ? seg.value / total : 0;
            const strokeDasharray = `${circumference * percent} ${circumference * (1 - percent)}`;
            const strokeDashoffset = -circumference * accumulatedPercent;
            accumulatedPercent += percent;

            const isHovered = hoveredSegment?.id === seg.id;

            return (
              <motion.circle
                key={seg.id}
                cx={size / 2}
                cy={size / 2}
                r={radius}
                fill="transparent"
                stroke={seg.color}
                strokeWidth={isHovered ? strokeWidth + 4 : strokeWidth}
                strokeDasharray={strokeDasharray}
                initial={{ strokeDashoffset: circumference }}
                animate={{
                  strokeDashoffset,
                  transition: { duration: 0.9, ease: 'easeOut' },
                }}
                onMouseEnter={() => setHoveredSegment(seg)}
                onMouseLeave={() => setHoveredSegment(null)}
                onClick={() => onSegmentClick && onSegmentClick(seg)}
                className={`transition-all duration-200 ${onSegmentClick ? 'cursor-pointer' : ''}`}
                style={{
                  filter: isHovered ? `drop-shadow(0 0 6px ${seg.color}88)` : 'none',
                }}
              />
            );
          })}
        </svg>

        {/* Center Text with Smooth Transitions */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center pointer-events-none px-4">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentDisplayTitle}
              initial={{ opacity: 0, y: 3 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -3 }}
              transition={{ duration: 0.15 }}
              className="space-y-0.5"
            >
              <span className="text-[11px] font-medium uppercase tracking-wider text-slate-400 block truncate max-w-[120px]">
                {currentDisplayTitle}
              </span>
              <span className="text-xl sm:text-2xl font-bold tracking-tight text-white block">
                <AnimatedNumber
                  value={currentDisplayValue}
                  durationMs={600}
                  suffix={centerSuffix}
                />
              </span>
              {total > 0 && hoveredSegment && (
                <span className="text-[10px] font-mono text-sky-400 block">
                  {((hoveredSegment.value / total) * 100).toFixed(1)}%
                </span>
              )}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>

      {/* Interactive Legend */}
      <div className="flex-1 w-full space-y-2">
        {data.map((seg) => {
          const isHovered = hoveredSegment?.id === seg.id;
          const pct = total > 0 ? ((seg.value / total) * 100).toFixed(1) : '0';

          return (
            <motion.div
              key={seg.id}
              whileHover={{ x: 3, transition: { duration: 0.15 } }}
              onMouseEnter={() => setHoveredSegment(seg)}
              onMouseLeave={() => setHoveredSegment(null)}
              onClick={() => onSegmentClick && onSegmentClick(seg)}
              className={`flex items-center justify-between p-2 rounded-lg text-xs transition-colors duration-150 ${
                isHovered ? 'bg-slate-800/80' : 'hover:bg-slate-800/40'
              } ${onSegmentClick ? 'cursor-pointer' : ''}`}
            >
              <div className="flex items-center space-x-2.5 truncate pr-2">
                <span
                  className="h-2.5 w-2.5 rounded-full shrink-0"
                  style={{ backgroundColor: seg.color }}
                />
                <span className="text-slate-300 truncate font-medium">{seg.label}</span>
              </div>
              <div className="flex items-center space-x-2 shrink-0">
                <span className="font-mono text-white font-semibold">
                  {seg.value.toLocaleString()}
                </span>
                <span className="font-mono text-slate-400 text-[11px] w-12 text-right">
                  {pct}%
                </span>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

