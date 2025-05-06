export class Command {
    /**
     * @param {any} [response]
     * @param {number} runtimeName
     */
    static createResponse(response?: any, runtimeName: number): Command;
    /**
     * @param {any} [response]
     * @param {number} runtimeName
     * @method
     */
    static createReference(response?: any, runtimeName: number): Command;
    /**
     * @param {any} [response]
     * @param {number} runtimeName
     * @returns {Command}
     * @method
     */
    static createArrayResponse(response?: any, runtimeName: number): Command;
    /**
     * Constructs a new Command instance.
     * @param {number} runtimeName - The runtime name associated with the command.
     * @param {number} commandType - The type of the command.
     * @param {any} [payload] - The optional payload of the command.
     * @method
     */
    constructor(runtimeName: number, commandType: number, payload?: any);
    runtimeName: number;
    commandType: number;
    payload: any;
    dropFirstPayloadArg(): Command;
    /**
     * @param {any} arg
     * @returns {Command}
     */
    addArgToPayload(arg: any): Command;
    /**
     * @param {Command|null} current_command
     * @returns {Command}
     */
    prependArgToPayload(current_command: Command | null): Command;
}
