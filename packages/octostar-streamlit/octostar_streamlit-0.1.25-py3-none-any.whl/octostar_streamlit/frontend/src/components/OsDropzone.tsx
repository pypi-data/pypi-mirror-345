import React, { useEffect, useRef } from "react";
import { Streamlit } from "streamlit-component-lib";

import './OsDropzone.less';
import { forwardDesktopApiMethodCallToPlatform } from "../desktop";
import { desktopApi, remoteAppApi } from "@octostar/platform-api";

type OsDropZoneProps = {
  streamlitKey: string;
  params: { label: string; };
};

const componentId = "osDropZone";

export const OsDropzone: React.FC<OsDropZoneProps> = ({ params: { label }, streamlitKey }) => {
  const uploaderRef = useRef<HTMLDivElement | null>(null);
  const dropzoneTopic = streamlitKey;


  useEffect(() => Streamlit.setFrameHeight(100), []);

  const getResults = React.useCallback(async () => {
    const result = await forwardDesktopApiMethodCallToPlatform({
      method: "searchXperience",
      service: "desktop",
      params: {
        "defaultConcept": null,
        "defaultSearchFields": null,
        "disableConceptSelector": null,
        "taskID": null,
        "title": "Search Big Data"
      },
    });
    Streamlit.setComponentValue(result);
  }, []);

  useEffect(() => {
    const el = uploaderRef.current;
    if (!el) {
      return;
    }
    let visible = false;

    const debounce = (func: (...args: any[]) => void, wait: number) => {
      let timeout: NodeJS.Timeout;
      return function (...args: any[]) {
        clearTimeout(timeout);
        // @ts-ignore
        timeout = setTimeout(() => func.apply(this, args), wait);
      };
    };

    const adjustCoordinatesForIframe = (
      windowObj: Window,
      coords: { x: number; y: number; [key: string]: any }
    ): { x: number; y: number; [key: string]: any } => {
      if (windowObj.parent === windowObj || !windowObj.frameElement) {
        if (windowObj.location.search) {
          // Still inside an iFrame, potentially Cross-Origin
          const urlParams = new URLSearchParams(windowObj.location.search);
          const channelId = urlParams.get('octostarChannelId');
          if (channelId) {
            coords.adjustForIframe = channelId;
          }
        }

        return coords;
      }
      const rect = windowObj.frameElement.getBoundingClientRect();
      return adjustCoordinatesForIframe(windowObj.parent, {
        ...coords,
        x: coords.x + rect.left,
        y: coords.y + rect.top,
      });
    };

    const publishDropZone = () => {
      console.log("publishDropZone");
      const rect = el.getBoundingClientRect();
      const request = adjustCoordinatesForIframe(window, {
        id: dropzoneTopic,
        x: rect.left,
        y: rect.top,
        width: rect.width,
        height: rect.height,
        onDropTopic: dropzoneTopic,
      });

      remoteAppApi().dropZoneRequest([request]).then(dropzoneResult => Streamlit.setComponentValue(dropzoneResult.data));
    };

    const updateHandler = () => {
      const rect = el.getBoundingClientRect();
      const newVisible = rect.width !== 0 && rect.height !== 0;
      if (true || newVisible || newVisible !== visible) {
        visible = newVisible;
        publishDropZone();
      }
    };

    const debouncedUpdateHandler = debounce(updateHandler, 200);

    const observer = new ResizeObserver((entries) => {
      for (let entry of entries) {
        debouncedUpdateHandler();
      }
    });

    observer.observe(el);
    observer.observe(document.body);

    window.addEventListener("scroll", debouncedUpdateHandler, true);

    remoteAppApi().subscribeToDragStart(dropzoneTopic, publishDropZone);

    function handleClick() {
      desktopApi().searchXperience().then(data => {
        console.log("onClick searchXperience", data);
        Streamlit.setComponentValue(data);
      });
    }

    el.addEventListener("click", handleClick);

    return () => {
      observer.disconnect();
      window.removeEventListener("scroll", debouncedUpdateHandler, true);
      remoteAppApi().unsubscribeFromDragStart(dropzoneTopic);
      el.removeEventListener("click", handleClick);
    };
  }, [dropzoneTopic]);

  return (
    <div id={componentId} className="antd-uploader" ref={uploaderRef}>
      <div className="upload-icon">+</div>
      <span className="upload-text" onClick={getResults}>{label}</span>
    </div>
  );
};

