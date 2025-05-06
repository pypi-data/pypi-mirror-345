/**
 * The ConfigRuntimeFactory class provides methods for creating runtime contexts.
 * Each method corresponds to a specific runtime (CLR, JVM, .NET Core, Perl, Ruby, Node.js, Python) and returns a RuntimeContext instance for that runtime.
 * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
 */
export class ConfigRuntimeFactory {
    /**
     * @param {object | string} configSource
     * @param {import('../core/transmitter/Transmitter.js') | null} transmitter
     */
    constructor(configSource: object | string, transmitter?: typeof import("../core/transmitter/Transmitter.js") | null);
    /** @type {import('../core/transmitter/Transmitter.js') | null} */
    transmitter: typeof import("../core/transmitter/Transmitter.js") | null;
    configSource: string | object;
    /**
     * Creates RuntimeContext instance to interact with the .NET Framework runtime.
     * @param {string} [configName="default"] - The name of the configuration to use (optional).
     * @return {RuntimeContext} a RuntimeContext instance for the .NET Framework runtime
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
     */
    clr(configName?: string): RuntimeContext;
    /**
     * Creates RuntimeContext instance to interact with the JVM runtime.
     * @param {string} [configName="default"] - The name of the configuration to use (optional).
     * @return {RuntimeContext} a RuntimeContext instance for the JVM runtime
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
     */
    jvm(configName?: string): RuntimeContext;
    /**
     * Creates RuntimeContext instance to interact with the .NET runtime.
     * @param {string} [configName="default"] - The name of the configuration to use (optional).
     * @return {RuntimeContext} a RuntimeContext instance for the .NET runtime
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
     */
    netcore(configName?: string): RuntimeContext;
    /**
     * Creates RuntimeContext instance to interact with the Perl runtime.
     * @param {string} [configName="default"] - The name of the configuration to use (optional).
     * @return {RuntimeContext} a RuntimeContext instance for the Perl runtime
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
     */
    perl(configName?: string): RuntimeContext;
    /**
     * Creates RuntimeContext instance to interact with the Python runtime.
     * @param {string} [configName="default"] - The name of the configuration to use (optional).
     * @return {RuntimeContext} a RuntimeContext instance for the Python runtime
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
     */
    python(configName?: string): RuntimeContext;
    /**
     * Creates RuntimeContext instance to interact with the Ruby runtime.
     * @param {string} [configName="default"] - The name of the configuration to use (optional).
     * @return {RuntimeContext} a RuntimeContext instance for the Ruby runtime
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
     */
    ruby(configName?: string): RuntimeContext;
    /**
     * Creates RuntimeContext instance to interact with Node.js runtime.
     * @param {string} [configName="default"] - The name of the configuration to use (optional).
     * @return {RuntimeContext} a RuntimeContext instance for the Node.js runtime
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
     */
    nodejs(configName?: string): RuntimeContext;
    /**
     * Creates RuntimeContext instance to interact with the Python 2.7 runtime.
     * @param {string} [configName="default"] - The name of the configuration to use (optional).
     * @return {RuntimeContext} a RuntimeContext instance for the Python 2.7 runtime
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
     */
    python27(configName?: string): RuntimeContext;
    #private;
}
import { RuntimeContext } from './RuntimeContext.js';
