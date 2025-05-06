"use strict";
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);
var ConfigRuntimeFactory_exports = {};
__export(ConfigRuntimeFactory_exports, {
  ConfigRuntimeFactory: () => ConfigRuntimeFactory
});
module.exports = __toCommonJS(ConfigRuntimeFactory_exports);
var import_WsConnectionData = require("../utils/connectionData/WsConnectionData.cjs");
var import_TcpConnectionData = require("../utils/nodejs/connectionData/TcpConnectionData.cjs");
var import_RuntimeName = require("../utils/RuntimeName.cjs");
var import_RuntimeNameHandler = require("../utils/RuntimeNameHandler.cjs");
var import_RuntimeContext = require("./RuntimeContext.cjs");
var import_ConfigSourceResolver = require("./tools/browser/ConfigSourceResolver.cjs");
var import_Runtime = require("../utils/Runtime.cjs");
var import_JsonFileResolver = require("./tools/nodejs/JsonFileResolver.cjs");
var import_InMemoryConnectionData = require("../utils/connectionData/InMemoryConnectionData.cjs");
const import_meta = {};
const requireDynamic = (0, import_Runtime.getRequire)(import_meta.url);
class ConfigRuntimeFactory {
  /** @type {import('../core/transmitter/Transmitter.js') | null} */
  transmitter = null;
  /**
   * @param {object | string} configSource
   * @param {import('../core/transmitter/Transmitter.js') | null} transmitter
   */
  constructor(configSource, transmitter = null) {
    this.configSource = configSource;
    this.transmitter = transmitter;
    if ((0, import_Runtime.isNodejsRuntime)()) {
      this.transmitter?.setConfigSource(configSource);
    }
  }
  /**
   * Creates RuntimeContext instance to interact with the .NET Framework runtime.
   * @param {string} [configName="default"] - The name of the configuration to use (optional).
   * @return {RuntimeContext} a RuntimeContext instance for the .NET Framework runtime
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
   */
  clr(configName = "default") {
    return this.#getRuntimeContext(import_RuntimeName.RuntimeName.Clr, configName);
  }
  /**
   * Creates RuntimeContext instance to interact with the JVM runtime.
   * @param {string} [configName="default"] - The name of the configuration to use (optional).
   * @return {RuntimeContext} a RuntimeContext instance for the JVM runtime
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
   */
  jvm(configName = "default") {
    return this.#getRuntimeContext(import_RuntimeName.RuntimeName.Jvm, configName);
  }
  /**
   * Creates RuntimeContext instance to interact with the .NET runtime.
   * @param {string} [configName="default"] - The name of the configuration to use (optional).
   * @return {RuntimeContext} a RuntimeContext instance for the .NET runtime
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
   */
  netcore(configName = "default") {
    return this.#getRuntimeContext(import_RuntimeName.RuntimeName.Netcore, configName);
  }
  /**
   * Creates RuntimeContext instance to interact with the Perl runtime.
   * @param {string} [configName="default"] - The name of the configuration to use (optional).
   * @return {RuntimeContext} a RuntimeContext instance for the Perl runtime
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
   */
  perl(configName = "default") {
    return this.#getRuntimeContext(import_RuntimeName.RuntimeName.Perl, configName);
  }
  /**
   * Creates RuntimeContext instance to interact with the Python runtime.
   * @param {string} [configName="default"] - The name of the configuration to use (optional).
   * @return {RuntimeContext} a RuntimeContext instance for the Python runtime
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
   */
  python(configName = "default") {
    return this.#getRuntimeContext(import_RuntimeName.RuntimeName.Python, configName);
  }
  /**
   * Creates RuntimeContext instance to interact with the Ruby runtime.
   * @param {string} [configName="default"] - The name of the configuration to use (optional).
   * @return {RuntimeContext} a RuntimeContext instance for the Ruby runtime
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
   */
  ruby(configName = "default") {
    return this.#getRuntimeContext(import_RuntimeName.RuntimeName.Ruby, configName);
  }
  /**
   * Creates RuntimeContext instance to interact with Node.js runtime.
   * @param {string} [configName="default"] - The name of the configuration to use (optional).
   * @return {RuntimeContext} a RuntimeContext instance for the Node.js runtime
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
   */
  nodejs(configName = "default") {
    return this.#getRuntimeContext(import_RuntimeName.RuntimeName.Nodejs, configName);
  }
  /**
   * Creates RuntimeContext instance to interact with the Python 2.7 runtime.
   * @param {string} [configName="default"] - The name of the configuration to use (optional).
   * @return {RuntimeContext} a RuntimeContext instance for the Python 2.7 runtime
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
   */
  python27(configName = "default") {
    return this.#getRuntimeContext(import_RuntimeName.RuntimeName.Python27, configName);
  }
  /**
   * @param {number} runtime
   * @param {string} configName
   * @returns
   */
  #getRuntimeContext(runtime, configName = "default") {
    if ((0, import_Runtime.isBrowserRuntime)()) {
      const jfr = new import_ConfigSourceResolver.ConfigSourceResolver(this.configSource);
      const connType = jfr.getChannelType(import_RuntimeNameHandler.RuntimeNameHandler.getName(runtime), configName);
      let connData = null;
      if (connType === "webSocket") {
        connData = new import_WsConnectionData.WsConnectionData(
          jfr.getChannelHost(import_RuntimeNameHandler.RuntimeNameHandler.getName(runtime), configName)
        );
      } else {
        throw new Error("Unsupported connection type: " + connType);
      }
      const rtmCtx = import_RuntimeContext.RuntimeContext.getInstance(runtime, connData);
      this.#loadModules(runtime, configName, jfr, rtmCtx);
      return rtmCtx;
    }
    if ((0, import_Runtime.isNodejsRuntime)()) {
      let jfr = new import_JsonFileResolver.JsonFileResolver(this.configSource);
      try {
        const licenseKey = jfr.getLicenseKey();
        this.transmitter?.activate(licenseKey);
      } catch (error) {
        throw error;
      }
      let rtmCtx = null;
      let connData = null;
      let connType = jfr.getChannelType(import_RuntimeNameHandler.RuntimeNameHandler.getName(runtime), configName);
      if (connType === "inMemory") {
        connData = new import_InMemoryConnectionData.InMemoryConnectionData();
      } else if (connType === "tcp") {
        connData = new import_TcpConnectionData.TcpConnectionData(
          jfr.getChannelHost(import_RuntimeNameHandler.RuntimeNameHandler.getName(runtime), configName),
          jfr.getChannelPort(import_RuntimeNameHandler.RuntimeNameHandler.getName(runtime), configName)
        );
      } else if (connType === "webSocket") {
        connData = new import_WsConnectionData.WsConnectionData(
          jfr.getChannelHost(import_RuntimeNameHandler.RuntimeNameHandler.getName(runtime), configName)
        );
      } else {
        throw new Error("Unsupported connection type: " + connType);
      }
      rtmCtx = import_RuntimeContext.RuntimeContext.getInstance(runtime, connData);
      this.#loadModules(runtime, configName, jfr, rtmCtx);
      return rtmCtx;
    }
  }
  // @ts-ignore
  #loadModules(runtime, configName, jfr, rtmCtx) {
    try {
      const modules = jfr.getModules(import_RuntimeNameHandler.RuntimeNameHandler.getName(runtime), configName).split(",").filter((module2) => module2.trim() !== "");
      if ((0, import_Runtime.isNodejsRuntime)()) {
        if (typeof this.configSource !== "string") {
          throw new Error("configSource is not a string");
        }
        const path = requireDynamic("path");
        const configDirectoryAbsolutePath = path?.dirname(this.configSource);
        modules.forEach((module2) => {
          if (path?.isAbsolute(module2)) {
            rtmCtx.loadLibrary(module2);
          } else {
            rtmCtx.loadLibrary(path?.join(configDirectoryAbsolutePath, module2));
          }
        });
      }
    } catch (error) {
      throw error;
    }
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  ConfigRuntimeFactory
});
