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
var CommandSerializer_exports = {};
__export(CommandSerializer_exports, {
  CommandSerializer: () => CommandSerializer
});
module.exports = __toCommonJS(CommandSerializer_exports);
var import_TypeSerializer = require("./TypeSerializer.cjs");
var import_Command = require("../../utils/Command.cjs");
var import_RuntimeName = require("../../utils/RuntimeName.cjs");
class CommandSerializer {
  serialize(rootCommand, connectionData) {
    const buffers = [];
    buffers.push(Uint8Array.of(rootCommand.runtimeName, 0));
    if (connectionData) {
      buffers.push(connectionData.serializeConnectionData());
    } else {
      buffers.push(Uint8Array.of(0, 0, 0, 0, 0, 0, 0));
    }
    buffers.push(Uint8Array.of(import_RuntimeName.RuntimeName.Nodejs, rootCommand.commandType));
    this.serializeRecursively(rootCommand, buffers);
    return concatenateUint8Arrays(buffers);
  }
  serializeRecursively(command, buffers) {
    for (const item of command.payload) {
      if (item instanceof import_Command.Command) {
        buffers.push(import_TypeSerializer.TypeSerializer.serializeCommand(item));
        this.serializeRecursively(item, buffers);
      } else {
        buffers.push(import_TypeSerializer.TypeSerializer.serializePrimitive(item));
      }
    }
  }
}
function concatenateUint8Arrays(arrays) {
  let totalLength = arrays.reduce((sum, arr) => sum + arr.length, 0);
  const result = new Uint8Array(totalLength);
  let offset = 0;
  for (const arr of arrays) {
    result.set(arr, offset);
    offset += arr.length;
  }
  return result;
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  CommandSerializer
});
