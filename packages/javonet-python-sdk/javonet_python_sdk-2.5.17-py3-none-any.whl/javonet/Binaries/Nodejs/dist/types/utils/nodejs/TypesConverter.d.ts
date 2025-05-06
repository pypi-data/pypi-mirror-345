/**
 * ConvertTypeHandler class handles the conversion of JType to Type.
 */
export class ConvertTypeHandler {
    /**
     * Minimum required parameters count for the command.
     * @type {number}
     */
    requiredParametersCount: number;
    /**
     * Processes the given command to convert JType to Type.
     * @param {Object} command - The command to process.
     * @returns {any} The converted type.
     */
    process(command: Object): any;
    /**
     * Validates the command to ensure it has enough parameters.
     * @param {Object} command - The command to validate.
     */
    validateCommand(command: Object): void;
}
/**
 * TypesConverter class provides utilities for converting between types.
 */
export class TypesConverter {
    /**
     * Converts a JavaScript type to a JType equivalent.
     * @param {Function} type - The JavaScript type.
     * @returns {number} The corresponding JType.
     */
    static convertTypeToJType(type: Function): number;
    /**
     * Converts a JType to a JavaScript type equivalent.
     * @param {number} type - The JType to convert.
     * @returns {Function} The corresponding JavaScript type.
     */
    static convertJTypeToType(type: number): Function;
}
/**
 * Enum for JType mappings.
 */
export type JType = number;
export namespace JType {
    let Boolean: number;
    let Float: number;
    let String: number;
    let Null: number;
}
