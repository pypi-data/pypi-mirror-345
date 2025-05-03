import React from 'react';
import ReactDOM from 'react-dom/client';
import { SearchXperience } from './SearchXperience';
import { OsDropzone } from './OsDropzone';
import OsContextMenu from './OsContextMenu';
import { GetSearchResults } from './GetSearchResults';

export const ComponentsMap = {
    'SearchXperience': SearchXperience,
    'OsDropzone': OsDropzone,
    'OsContextMenu': OsContextMenu,
    'GetSearchResults': GetSearchResults
}

export type Components = keyof typeof ComponentsMap;

let rendered = false;
function renderComponent(componentName: Components, props: any) {
    const container = document.getElementById("app");

    if (container && !rendered) {
        rendered = true;
        // console.log("SDK101: rendering component.", props)
        const root = ReactDOM.createRoot(container);
        const Component = ComponentsMap[componentName];
        const streamlitKey = props.key;
        root.render(
        <React.StrictMode>
            <Component {...props} streamlitKey={streamlitKey} />
        </React.StrictMode>
        );
    } else {
      console.error("Root element with id 'app' not found");
    }
}

export default renderComponent;
