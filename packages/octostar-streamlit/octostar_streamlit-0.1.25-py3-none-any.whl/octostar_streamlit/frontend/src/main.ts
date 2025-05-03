import { isEqual } from "lodash";
import { Streamlit, RenderData } from "streamlit-component-lib"
import { forwardDesktopApiMethodCallToPlatform } from "./desktop";
import { forwardOntologyApiMethodCallToPlatform } from "./ontology";
import { forwardExtrasApiMethodCallToPlatform } from "./extras";
import {
  RemoteAppBridge,
  RemoteAppMethodCall,
  forwardRemoteAppApiMethodCallToPlatform,
  methodCallHandler as remoteAppMethodCallHander,
} from "./remoteApp";
import renderComponent from './components/ComponentRenderer'
import { forwardContextApiMethodCallToPlatform } from "./context";
import { forwardSavedSearchApiMethodCallToPlatform } from "./savedSearch";

type Args = {
  service: any; // TODO: Add typing for service names
  key: string;
  method: any; // TODO: Add binding to only allow names from the declared service
  params: any; // TODO: Add binding to only params from the declared method in the said service
  subscribe?: string;
}

let subscribedToFutureResults: false|(() => void) = false;
// let oldArgs: Args | null = null;
/**
 * The component's render function. This will be called immediately after
 * the component is initially loaded, and then again every time the
 * component gets new data from Python.
 */
async function onRender(event: Event): Promise<void> {
  // Get the RenderData from the event
  const data = (event as CustomEvent<RenderData<Args>>).detail;

  // if (oldArgs && oldArgs.key === data.args.key) {
  //   if (isEqual(oldArgs.params, data.args.params)) {
  //     // Skip re-triggering the API if params are the same
  //     return;
  //   }
  // }
  // oldArgs = data.args;

  if (!data.args) {
    throw new Error("No call definition passed to the component!");
  } else {
    console.log(`StreamlitSDK: ${data.args.service}:${data.args.method}:${data.args.key}`)
  }

  const service = data.args["service"];

  // Streamlit.setFrameHeight(0);
  function onValueChanged(value: any) {
    console.log(`StreamlitSDK: ${data.args.subscribe} value changed for ${data.args.service}:${data.args.method}:${data.args.key}`, value);
    Streamlit.setComponentValue(value);
  }

  switch (service) {
    case "component":
      renderComponent(data.args.method, data.args);
      return;
    case "context":
      const result = await forwardContextApiMethodCallToPlatform(data.args);
      Streamlit.setComponentValue(result);
      break;
    case "desktop":
      try {
        if (data.args.method === "searchXperience") {
          renderComponent('SearchXperience', data.args);
          return;
        }
        if (data.args.method === "getSearchResults" && data.args.params.enableSelection) {
          renderComponent('GetSearchResults', data.args);
          return;
        }
        const result = await forwardDesktopApiMethodCallToPlatform(data.args);

        console.log({ result });

        Streamlit.setComponentValue(result);
        Streamlit.setFrameHeight();

        if (data.args.subscribe && !subscribedToFutureResults) {
          subscribedToFutureResults = await forwardDesktopApiMethodCallToPlatform({
            service: "desktop",
            params: onValueChanged,
            method: data.args.subscribe as any
          });
        }
      } catch (error) {
        console.error("Error in octostar-streamlit iframe: ", error);
      }
      break;

    case "ontology":
      Promise.resolve(forwardOntologyApiMethodCallToPlatform(data.args)).then(
        (result) => {
          Streamlit.setComponentValue(result);
          Streamlit.setFrameHeight();
        }
      );
      break;

    case "extras":
      if (data.args.method === "osDropzone") {
        renderComponent('OsDropzone', data.args);
        return;
      }
      Promise.resolve(forwardExtrasApiMethodCallToPlatform(data.args)).then(
        (result) => {
          Streamlit.setComponentValue(result);
          Streamlit.setFrameHeight();
        }
      );
      break;

    case "savedSearch":
      Promise.resolve(forwardSavedSearchApiMethodCallToPlatform(data.args)).then(
        (result) => {
          Streamlit.setComponentValue(result);
          Streamlit.setFrameHeight();
        }
      );
      break;

    case "remoteApp":
      const remoteAppArgs: RemoteAppMethodCall<keyof RemoteAppBridge, unknown> =
        data.args;

      if (remoteAppArgs.method === "subscribeToContext") {
        return remoteAppMethodCallHander.subscribeToContext(
          remoteAppArgs.params,
          async (result: any) => {
            console.log("received context", result);

            console.log("context setting component value");
            Streamlit.setComponentValue(result);
            Streamlit.setFrameHeight();
          }
        );
      }

      Promise.resolve(
        forwardRemoteAppApiMethodCallToPlatform(remoteAppArgs)
      ).then((result) => {
        Streamlit.setComponentValue(result);
        Streamlit.setFrameHeight();
      });
      break;
    default:
      throw new Error(`Call to an unknown service: ${service}`);
  }

  // We tell Streamlit to update our frameHeight after each render event, in
  // case it has changed. (This isn't strictly necessary for the example
  // because our height stays fixed, but this is a low-cost function, so
  // there's no harm in doing it redundantly (except for React component renders)
  Streamlit.setFrameHeight();
}

// Attach our `onRender` handler to Streamlit's render event.
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender)

// Tell Streamlit we're ready to start receiving data. We won't get our
// first RENDER_EVENT until we call this function.
Streamlit.setComponentReady()

// Finally, tell Streamlit to update our initial height. We omit the
// `height` parameter here to have it default to our scrollHeight.
Streamlit.setFrameHeight()

// Attach cleanup when the component is removed
window.addEventListener("unload", () => {
  if (subscribedToFutureResults) {
    subscribedToFutureResults();
    subscribedToFutureResults = false;
  }
});
