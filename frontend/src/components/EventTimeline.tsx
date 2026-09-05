import React from 'react';
import { Event } from '../types';
import RiskBadge from './RiskBadge';
import { formatDistanceToNow } from 'date-fns';
import { MapPin, ArrowRight, Video } from 'lucide-react';

interface EventTimelineProps {
  events: Event[];
  onSelectEvent?: (event: Event) => void;
}

export default function EventTimeline({ events = [], onSelectEvent }: EventTimelineProps) {
  if (events.length === 0) {
    return (
      <div className="py-8 text-center text-slate-400 text-sm">
        No recent events recorded.
      </div>
    );
  }

  return (
    <div className="flow-root">
      <ul className="-mb-6">
        {events.map((event, idx) => {
          const isCritical = event.riskLevel === 'CRITICAL';
          const isHigh = event.riskLevel === 'HIGH';

          return (
            <li key={event.id || idx}>
              <div className="relative pb-6">
                {idx !== events.length - 1 && (
                  <span
                    className="absolute top-4 left-3.5 -ml-px h-full w-0.5 bg-slate-200"
                    aria-hidden="true"
                  />
                )}
                <div
                  className="relative flex items-start space-x-3 group cursor-pointer hover:bg-slate-50/80 p-2 rounded-xl transition-colors"
                  onClick={() => onSelectEvent && onSelectEvent(event)}
                >
                  <div className="relative">
                    <span
                      className={`h-7 w-7 rounded-full flex items-center justify-center ring-4 ring-white shadow-xs ${
                        isCritical
                          ? 'bg-red-500 text-white'
                          : isHigh
                          ? 'bg-orange-500 text-white'
                          : event.riskLevel === 'MEDIUM'
                          ? 'bg-amber-500 text-white'
                          : 'bg-emerald-500 text-white'
                      }`}
                    >
                      <Video className="w-3.5 h-3.5" />
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <p className="text-xs font-bold text-slate-900 truncate">
                        {(event.type || event.event_type || 'Safety Observation').replace(/_/g, ' ').toUpperCase()}
                      </p>
                      <time className="text-[11px] text-slate-400 font-mono shrink-0">
                        {event.timestamp
                          ? formatDistanceToNow(new Date(event.timestamp), { addSuffix: true })
                          : 'Just now'}
                      </time>
                    </div>
                    <p className="text-xs text-slate-600 line-clamp-2 mt-0.5">
                      {event.description || event.explanation}
                    </p>
                    <div className="flex items-center justify-between gap-2 mt-2">
                      <div className="flex items-center gap-2">
                        <RiskBadge level={event.riskLevel} />
                        <span className="flex items-center text-[11px] text-slate-500">
                          <MapPin className="w-3 h-3 mr-1 text-slate-400" />
                          {event.location}
                        </span>
                      </div>
                      <span className="text-[11px] font-semibold text-blue-600 opacity-0 group-hover:opacity-100 flex items-center gap-0.5 transition-opacity">
                        Inspect <ArrowRight className="w-3 h-3" />
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
