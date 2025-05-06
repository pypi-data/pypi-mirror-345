export class ConfigSourceResolver {
    /**
     *
     * @param {object | string} configSource
     */
    constructor(configSource: object | string);
    jsonObject: any;
    getLicenseKey(): any;
    getRuntimes(): any;
    /**
     * @param {string} runtimeName
     * @param {string} configName
     * @returns {any}
     */
    getRuntime(runtimeName: string, configName: string): any;
    /**
     * @param {string} runtimeName
     * @param {string} configName
     * @returns {any}
     */
    getChannel(runtimeName: string, configName: string): any;
    /**
     * @param {string} runtimeName
     * @param {string} configName
     * @returns {any}
     */
    getChannelType(runtimeName: string, configName: string): any;
    /**
     * @param {string} runtimeName
     * @param {string} configName
     * @returns {any}
     */
    getChannelHost(runtimeName: string, configName: string): any;
    /**
     * @param {string} runtimeName
     * @param {string} configName
     * @returns {any}
     */
    getChannelPort(runtimeName: string, configName: string): any;
    /**
     * @param {string} runtimeName
     * @param {string} configName
     * @returns {any}
     */
    getModules(runtimeName: string, configName: string): any;
}
