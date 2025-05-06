/**
 * Handles retrieving a static method as a delegate.
 */
export class GetStaticMethodAsDelegateHandler extends AbstractHandler {
    /** @type {Array<*>} */
    args: Array<any>;
    /** @type {Function|null} */
    method: Function | null;
    /** @type {number} */
    requiredParametersCount: number;
    /**
     * Processes a command to retrieve a static method as a delegate.
     * @param {Command} command - The command containing payload data.
     * @param {Array<*>} command.payload - The payload containing type, method name, and arguments.
     * @returns {Function} The delegate for the static method.
     * @throws {Error} If the parameters mismatch or the method cannot be found.
     */
    process(command: Command): Function;
    /**
     * Retrieves the method from the type.
     * @param {Object} type - The class or constructor to search for the method.
     * @param {string} methodName - The name of the method.
     * @param {Array<Function>} argsType - The argument types.
     * @param {Object} modifier - Parameter modifier (not used in JS implementation).
     * @returns {Function|null} The found method or null if not found.
     */
    getMethod(type: Object, methodName: string): Function | null;
    /**
     * Creates an error message when the method is not found.
     * @param {Object} type - The class or constructor.
     * @param {string} methodName - The method name.
     * @returns {Error} The error with detailed message.
     */
    createMethodNotFoundError(type: Object, methodName: string): Error;
}
import { AbstractHandler } from './AbstractHandler.js';
