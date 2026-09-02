import { useId, useLayoutEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { Info } from 'lucide-react';

interface InfoTooltipProps {
  label: string;
  children: string;
}

const TOOLTIP_WIDTH = 300;
const VIEWPORT_GAP = 16;
const TRIGGER_GAP = 10;

export function InfoTooltip({ label, children }: InfoTooltipProps) {
  const id = useId();
  const triggerRef = useRef<HTMLButtonElement>(null);
  const [open, setOpen] = useState(false);
  const [position, setPosition] = useState({ top: 0, left: 0, below: false, width: TOOLTIP_WIDTH });

  useLayoutEffect(() => {
    if (!open) return;

    const updatePosition = () => {
      const trigger = triggerRef.current;
      if (!trigger) return;

      const rect = trigger.getBoundingClientRect();
      const width = Math.min(TOOLTIP_WIDTH, window.innerWidth - VIEWPORT_GAP * 2);
      const left = Math.min(
        window.innerWidth - VIEWPORT_GAP - width / 2,
        Math.max(VIEWPORT_GAP + width / 2, rect.left + rect.width / 2),
      );
      const below = rect.top < 150;

      setPosition({
        top: below ? rect.bottom + TRIGGER_GAP : rect.top - TRIGGER_GAP,
        left,
        below,
        width,
      });
    };

    updatePosition();
    window.addEventListener('resize', updatePosition);
    window.addEventListener('scroll', updatePosition, true);
    return () => {
      window.removeEventListener('resize', updatePosition);
      window.removeEventListener('scroll', updatePosition, true);
    };
  }, [open]);

  return (
    <span className="info-tooltip-wrap">
      <button
        ref={triggerRef}
        type="button"
        className="info-tooltip-trigger"
        aria-label={`More information: ${label}`}
        aria-describedby={open ? id : undefined}
        aria-expanded={open}
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
        onClick={() => setOpen(true)}
        onKeyDown={(event) => {
          if (event.key === 'Escape') setOpen(false);
        }}
      >
        <Info size={14} aria-hidden="true" />
      </button>
      {open && createPortal(
        <span
          id={id}
          role="tooltip"
          className={`info-tooltip-bubble ${position.below ? 'is-below' : 'is-above'}`}
          style={{ top: position.top, left: position.left, width: position.width }}
        >
          {children}
        </span>,
        document.body,
      )}
    </span>
  );
}
