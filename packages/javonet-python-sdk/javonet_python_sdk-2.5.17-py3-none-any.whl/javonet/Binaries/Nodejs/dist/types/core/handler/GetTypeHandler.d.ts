export class GetTypeHandler extends AbstractHandler {
    /** @type {number} */
    requiredParametersCount: number;
    /** @type {NamespaceCache | null} */
    namespaceCache: NamespaceCache | null;
    /** @type {TypeCache | null} */
    typeCache: TypeCache | null;
    /** @type {LoadLibraryHandler | null} */
    loadLibaryHandler: LoadLibraryHandler | null;
    process(command: any): any;
    getAvailableTypes(): any[];
}
import { AbstractHandler } from './AbstractHandler.js';
import { NamespaceCache } from '../namespaceCache/NamespaceCache.js';
import { TypeCache } from '../typeCache/TypeCache.js';
import { LoadLibraryHandler } from './LoadLibraryHandler.js';
