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
var TypesConverter_exports = {};
__export(TypesConverter_exports, {
  ConvertTypeHandler: () => ConvertTypeHandler,
  JType: () => JType,
  TypesConverter: () => TypesConverter
});
module.exports = __toCommonJS(TypesConverter_exports);
class ConvertTypeHandler {
  constructor() {
    this.requiredParametersCount = 1;
  }
  /**
   * Processes the given command to convert JType to Type.
   * @param {Object} command - The command to process.
   * @returns {any} The converted type.
   */
  process(command) {
    this.validateCommand(command);
    return TypesConverter.convertJTypeToType(command.payload[0]);
  }
  /**
   * Validates the command to ensure it has enough parameters.
   * @param {Object} command - The command to validate.
   */
  validateCommand(command) {
    if (command.payload.length < this.requiredParametersCount) {
      throw new Error("ConvertTypeHandler parameters mismatch");
    }
  }
}
class TypesConverter {
  /**
   * Converts a JavaScript type to a JType equivalent.
   * @param {Function} type - The JavaScript type.
   * @returns {number} The corresponding JType.
   */
  static convertTypeToJType(type) {
    switch (type) {
      case Boolean:
        return JType.Boolean;
      case Number:
        return JType.Float;
      // Assuming Number maps to Float
      case String:
        return JType.String;
      case Object:
        return JType.Null;
      // Assuming Object maps to Null
      default:
        return JType.Null;
    }
  }
  /**
   * Converts a JType to a JavaScript type equivalent.
   * @param {number} type - The JType to convert.
   * @returns {Function} The corresponding JavaScript type.
   */
  static convertJTypeToType(type) {
    switch (type) {
      case JType.Boolean:
        return Boolean;
      case JType.Float:
        return Number;
      case JType.String:
        return String;
      case JType.Null:
        return null;
      default:
        return null;
    }
  }
}
const JType = {
  Boolean: 1,
  Float: 2,
  String: 3,
  Null: 4
};
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  ConvertTypeHandler,
  JType,
  TypesConverter
});
