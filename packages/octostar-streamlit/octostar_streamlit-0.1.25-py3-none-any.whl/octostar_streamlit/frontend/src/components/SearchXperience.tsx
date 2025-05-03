import React, { useEffect } from "react";
import { Streamlit } from "streamlit-component-lib";
import "./Button.less";
import { forwardDesktopApiMethodCallToPlatform } from "../desktop";

export const SearchXperience = (props: any) => { // TODO: Better typing of props
  useEffect(() => Streamlit.setFrameHeight(100), []);
  const label = props?.params?.title || 'SearchXperience';

  const getResults = React.useCallback(async () => {
    const result = await forwardDesktopApiMethodCallToPlatform(props);
    Streamlit.setComponentValue(result);
  }, []);

  return (
    <button className="octostar-button" onClick={getResults}>{label}</button>
  );
};


