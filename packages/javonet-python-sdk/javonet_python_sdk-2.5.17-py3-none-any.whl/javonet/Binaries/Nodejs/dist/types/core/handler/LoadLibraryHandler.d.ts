export class LoadLibraryHandler extends AbstractHandler {
    static loadedLibraries: any[];
    requiredParametersCount: number;
    process(command: any): number;
    getLoadedLibraries(): any[];
}
import { AbstractHandler } from './AbstractHandler.js';
