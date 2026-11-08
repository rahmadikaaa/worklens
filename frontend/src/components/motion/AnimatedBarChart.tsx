import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export interface BarItem {
  id: string;
  label: string;
  value: number;
  secondaryValue?: number;
  color?: string;
  tooltipText?: string;
}

interface AnimatedBarChartProps {
  data: BarItem[];
  maxValue?: number;
  valueSuffix?: string;
  onBarClick?: (item: BarItem) => void;
  heightClass?: string;
}

export const AnimatedBarChart: React.FC<AnimatedBarChartProps> = ({
  data,
  maxValue,
  valueSuffix = '',
  onBarClick,
}) => {
  const [hoveredItem, setHoveredItem] = useState<BarItem | null>(null);

  const calculatedMax = maxValue ?? Math.max(...data.map((d) => d.value), 1);

  return (
    <div className="space-y-3.5 relative">
      {data.map((item, index) => {
        const percent = Math.min((item.value / calculatedMax) * 100, 100);
        const isHovered = hoveredItem?.id === item.id;
        const barColor = item.color || '#0ea5e9';

        return (
          <div
            key={item.id}
            onMouseEnter={() => setHoveredItem(item)}
            onMouseLeave={() => setHoveredItem(null)}
            onClick={() => onBarClick && onBarClick(item)}
            className={`group p-2 rounded-lg transition-colors duration-150 ${
              isHovered ? 'bg-slate-800/60' : 'hover:bg-slate-800/30'
            } ${onBarClick ? 'cursor-pointer' : ''}`}
          >
            <div className="flex items-center justify-between text-xs mb-1.5">
              <span className="text-slate-300 font-medium truncate max-w-[220px]" title={item.label}>
                {item.label}
              </span>
              <span className="font-mono text-slate-100 font-semibold ml-2 shrink-0">
                {item.value.toLocaleString()} {valueSuffix}
              </span>
            </div>

            {/* Bar Background Track */}
            <div className="h-2.5 w-full bg-slate-800/80 rounded-full overflow-hidden relative">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${percent}%` }}
                transition={{
                  duration: 0.8,
                  delay: index * 0.05,
                  ease: 'easeOut',
                }}
                className="h-full rounded-full transition-all duration-200"
                style={{
                  backgroundColor: barColor,
                  filter: isHovered ? `drop-shadow(0 0 6px ${barColor}99)` : 'none',
                }}
              />
            </div>
          </div>
        );
      })}

      {/* Floating Tooltip */}
      <AnimatePresence>
        {hoveredItem && (
          <motion.div
            initial={{ opacity: 0, y: 4, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 4, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className="absolute top-2 right-2 z-20 pointer-events-none bg-slate-900 border border-slate-700/80 px-3 py-1.5 rounded-lg shadow-xl text-xs backdrop-blur"
          >
            <span className="text-slate-400 font-normal">Active Item: </span>
            <span className="text-sky-400 font-semibold">{hoveredItem.label}</span>
            <div className="text-slate-200 font-mono mt-0.5">
              {hoveredItem.value.toLocaleString()} {valueSuffix}
              {hoveredItem.tooltipText ? ` • ${hoveredItem.tooltipText}` : ''}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

