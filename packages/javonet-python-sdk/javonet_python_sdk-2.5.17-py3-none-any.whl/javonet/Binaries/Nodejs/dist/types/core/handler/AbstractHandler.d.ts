export class AbstractHandler {
    handlers: any[];
    process(command: any): void;
    handleCommand(command: any): void;
    iterate(cmd: any): void;
    process_stack_trace(error: any, class_name: any): any;
}
