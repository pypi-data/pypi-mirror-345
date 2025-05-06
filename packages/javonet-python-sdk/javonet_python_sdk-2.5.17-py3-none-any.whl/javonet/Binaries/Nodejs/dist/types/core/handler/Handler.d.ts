export class Handler {
    /**
     * @param {import('../interpreter/Interpreter.js').Interpreter} interpreter
     */
    constructor(interpreter: import("../interpreter/Interpreter.js").Interpreter);
    interpreter: import("../interpreter/Interpreter.js").Interpreter;
    /**
     * @param {{ commandType: number; payload: any[]; runtimeName: number; }} command
     */
    handleCommand(command: {
        commandType: number;
        payload: any[];
        runtimeName: number;
    }): Command;
    /**
     * @param {any} response
     * @param {number} runtimeName
     * @returns {Command}
     */
    parseCommand(response: any, runtimeName: number): Command;
}
/**
 * @type {Record<number, AbstractHandler>}
 */
export const handlers: Record<number, AbstractHandler>;
import { Command } from '../../utils/Command.js';
import { AbstractHandler } from './AbstractHandler.js';
