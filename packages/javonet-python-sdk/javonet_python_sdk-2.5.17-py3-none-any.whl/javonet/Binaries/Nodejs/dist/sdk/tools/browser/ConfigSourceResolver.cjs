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
var ConfigSourceResolver_exports = {};
__export(ConfigSourceResolver_exports, {
  ConfigSourceResolver: () => ConfigSourceResolver
});
module.exports = __toCommonJS(ConfigSourceResolver_exports);
function hasOwnProperty(obj, key) {
  return Object.prototype.hasOwnProperty.call(obj, key);
}
class ConfigSourceResolver {
  /**
   *
   * @param {object | string} configSource
   */
  constructor(configSource) {
    if (typeof configSource === "string") {
      try {
        this.jsonObject = JSON.parse(configSource);
      } catch (err) {
        throw new Error(
          `Failed to parse configSource as JSON: ${err instanceof Error ? err.message : "Unknown error"}`
        );
      }
    } else if (configSource && typeof configSource === "object") {
      this.jsonObject = configSource;
    } else {
      throw new Error("configSource must be a JSON object or JSON string");
    }
  }
  getLicenseKey() {
    if (!hasOwnProperty(this.jsonObject, "licenseKey")) {
      throw new Error(
        "License key not found in configuration file. Please check your configuration file."
      );
    }
    return this.jsonObject.licenseKey;
  }
  getRuntimes() {
    return this.jsonObject.runtimes;
  }
  /**
   * @param {string} runtimeName
   * @param {string} configName
   * @returns {any}
   */
  getRuntime(runtimeName, configName) {
    const runtimes = this.getRuntimes();
    if (hasOwnProperty(runtimes, runtimeName)) {
      const runtime = runtimes[runtimeName];
      if (Array.isArray(runtime)) {
        for (let item of runtime) {
          if (item.name === configName) {
            return item;
          }
        }
      } else if (runtime?.name === configName) {
        return runtime;
      }
    }
    throw new Error(
      `Runtime config ${configName} not found in configuration file for runtime ${runtimeName}. Please check your configuration file.`
    );
  }
  /**
   * @param {string} runtimeName
   * @param {string} configName
   * @returns {any}
   */
  getChannel(runtimeName, configName) {
    const runtime = this.getRuntime(runtimeName, configName);
    if (!hasOwnProperty(runtime, "channel")) {
      throw new Error(
        `Channel key not found in configuration file for config ${configName}. Please check your configuration file.`
      );
    }
    return runtime.channel;
  }
  /**
   * @param {string} runtimeName
   * @param {string} configName
   * @returns {any}
   */
  getChannelType(runtimeName, configName) {
    const channel = this.getChannel(runtimeName, configName);
    if (!hasOwnProperty(channel, "type")) {
      throw new Error(
        `Channel type not found in configuration file for config ${configName}. Please check your configuration file.`
      );
    }
    return channel.type;
  }
  /**
   * @param {string} runtimeName
   * @param {string} configName
   * @returns {any}
   */
  getChannelHost(runtimeName, configName) {
    const channel = this.getChannel(runtimeName, configName);
    if (!hasOwnProperty(channel, "host")) {
      throw new Error(
        `Channel host not found in configuration file for config ${configName}. Please check your configuration file.`
      );
    }
    return channel.host;
  }
  /**
   * @param {string} runtimeName
   * @param {string} configName
   * @returns {any}
   */
  getChannelPort(runtimeName, configName) {
    const channel = this.getChannel(runtimeName, configName);
    if (!hasOwnProperty(channel, "port")) {
      throw new Error(
        `Channel port not found in configuration file for config ${configName}. Please check your configuration file.`
      );
    }
    return channel.port;
  }
  /**
   * @param {string} runtimeName
   * @param {string} configName
   * @returns {any}
   */
  getModules(runtimeName, configName) {
    const runtime = this.getRuntime(runtimeName, configName);
    if (hasOwnProperty(runtime, "modules")) {
      return runtime.modules;
    }
    return "";
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  ConfigSourceResolver
});
