import React, { useEffect, useRef } from "react";
import "./OsContextMenu.less";
import { forwardDesktopApiMethodCallToPlatform } from "../desktop";
import { Streamlit } from "streamlit-component-lib";

const TRIGGERS = ["hover", "contextMenu"]; // Perhaps expose as params?

interface OsContextMenuProps {
  item: Record<string, any>;
  label?: string;
  height?: number;
  padding?: string;
}

const OsContextMenu: React.FC<{ params: OsContextMenuProps; }> = ({ params: {
  item,
  label,
  height = 30,
  padding = "6px",
}}) => {
  const contextMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => Streamlit.setFrameHeight(), []);

  useEffect(() => {
    const el = contextMenuRef.current;
    if (!el) return;

    const adjustCoordinatesForIframe = (
      windowObj: Window,
      coords: { x: number; y: number, item: Record<string, any> }
    ): { x: number; y: number } => {
      if (windowObj.parent === windowObj || !windowObj.frameElement) {
        return coords;
      } else if (windowObj.frameElement.getAttribute('data-octostar-iframe') === 'true') {
        // Octostar API now auto adjusts context menu coordinates for top iframe
        return coords;
      }

      const rect = windowObj.frameElement.getBoundingClientRect();
      return adjustCoordinatesForIframe(windowObj.parent, {
        ...coords,
        x: coords.x + rect.left,
        y: coords.y + rect.top,
      });
    };

    const handleMouseEvent = (event: MouseEvent) => {
      event.preventDefault();

      const request = adjustCoordinatesForIframe(window, {
        x: event.clientX,
        y: el.getBoundingClientRect().y,
        item,
      });
      forwardDesktopApiMethodCallToPlatform({
        service: "desktop",
        method: 'showContextMenu',
        params: request
      });
    };

    if (TRIGGERS.includes("hover")) {
      el.addEventListener("mouseenter", handleMouseEvent);
    }

    if (TRIGGERS.includes("contextMenu")) {
      el.addEventListener("contextmenu", handleMouseEvent);
    }

    return () => {
      if (TRIGGERS.includes("hover")) {
        el.removeEventListener("mouseenter", handleMouseEvent);
      }

      if (TRIGGERS.includes("contextMenu")) {
        el.removeEventListener("contextmenu", handleMouseEvent);
      }
    };
  }, [item]);

  return (
    <div
      id="osContextMenu"
      ref={contextMenuRef}
      className="context-menu"
      draggable
      style={{
        padding,
        height: `${height}px`,
      }}
    >
      {label || item.entity_label || "missing label"}
    </div>
  );
};

export default OsContextMenu;
