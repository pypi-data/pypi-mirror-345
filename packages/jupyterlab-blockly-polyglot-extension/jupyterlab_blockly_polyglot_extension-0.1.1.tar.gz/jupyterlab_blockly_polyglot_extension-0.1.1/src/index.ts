import { ILayoutRestorer, JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { Widget } from '@lumino/widgets';
import { INotebookTracker, NotebookPanel } from "@jupyterlab/notebook";
import { Cell } from "@jupyterlab/cells";
import * as Blockly from 'blockly/core';
import { ICommandPalette, MainAreaWidget, IWidgetTracker, ISessionContext, WidgetTracker } from '@jupyterlab/apputils';
import * as cells from "@jupyterlab/cells";
import { ICellModel } from "@jupyterlab/cells";
import { Kernel, Session, KernelMessage } from "@jupyterlab/services";
import { DocumentRegistry } from "@jupyterlab/docregistry";
import { CommandRegistry } from "@lumino/commands";
import { IToolbox } from "./AbstractToolbox";
import { PythonToolbox } from "./PythonToolbox";
import { RToolbox } from "./RToolbox";

// TODO: seems like logging is not wired up throughout

/**
 * BlocklyWidget is a wrapper for Blockly. It does all the integration between Blockly and Jupyter. Language specific issues are handled by respective geneators and toolboxes
 */
export class BlocklyWidget extends Widget {
  /**
   * Notebooks we have open
   */
  notebooks: INotebookTracker;
  /**
   * Blockly workspace (basically Blockly session state)
   */
  workspace: Blockly.WorkspaceSvg | null;
  /**
   * Toolbox defining most blockly behavior, including language specific behavior
   */
  toolbox:IToolbox | null;
  /**
   * Flag for  whether the widget is attached to Jupyter
   */
  notHooked: boolean
  /**
   * Language generator in use
   */
  generator: any;
  /** 
   * last cell for blocks to code state managment
   */
  lastCell: Cell | null;
  /** 
   * blocks rendered flag for state managment. Set to false every time a block is created. Set to true when blocks have been deserialized OR have been serialized
   */
  blocksInSyncWithXML: boolean;


  constructor(notebooks: INotebookTracker) {
    super();

    //--------------------
    // Initialize state
    //--------------------
    //track notebooks
    this.notebooks = notebooks;

    //listen for notebook cell changes
    this.notebooks.activeCellChanged.connect(this.onActiveCellChanged(), this);

    this.lastCell = null;
    this.blocksInSyncWithXML = false;
    this.workspace = null;
    this.toolbox = null;
    this.notHooked = true;

    //---------------------
    // Widget UI in Jupyter
    //---------------------
    //div to hold blockly
    const div: any = document.createElement("div");

    //initial size will be immediately resized
    div.setAttribute("style", "height: 480px; width: 600px;");

    //id for debug and to refer to during injection
    div.id = "blocklyDivPoly";
    this.node.appendChild(div);

    //div for buttons    
    const buttonDiv: any = document.createElement("div");
    buttonDiv.id = "buttonDivPoly";

    //button to trigger code generation
    const blocksToCodeButton: any = document.createElement("button");
    blocksToCodeButton.innerText = "Blocks to Code";
    blocksToCodeButton.addEventListener("click", (_arg: any): void => {
      this.BlocksToCode(this.notebooks.activeCell,true);
    });
    buttonDiv.appendChild(blocksToCodeButton);

    //button to reverse xml to blocks
    const codeToBlocksButton: any = document.createElement("button");
    codeToBlocksButton.innerText = "Code to Blocks";
    codeToBlocksButton.addEventListener("click", (_arg_1: any): void => {
      this.DeserializeBlocksFromXML();
    });
    buttonDiv.appendChild(codeToBlocksButton);

    //button for bug reports
    const bugReportButton: any = document.createElement("button");
    bugReportButton.innerText = "Report Bug";
    bugReportButton.addEventListener("click", (_arg_2: any): void => {
      const win: any = window.open("https://jupyterlab-blockly-polyglot-extension/issues", "_blank");
      win.focus();
    });     
    buttonDiv.appendChild(bugReportButton);

    //checkbox for JLab sync (if cell is selected and has serialized blocks, decode them to workspace; if cell is empty, empty workspace)
    const syncCheckbox: any = document.createElement("input");
    syncCheckbox.setAttribute("type", "checkbox");
    syncCheckbox.checked = true;
    syncCheckbox.id = "syncCheckboxPoly";
    const syncCheckboxLabel: any = document.createElement("label");
    syncCheckboxLabel.innerText = "Notebook Sync";
    syncCheckboxLabel.setAttribute("for", "syncCheckboxPoly");
    buttonDiv.appendChild(syncCheckbox);
    buttonDiv.appendChild(syncCheckboxLabel);

    this.node.appendChild(buttonDiv);
  }

  /**
   * A kind of registry/factory that returns the correct toolbox given the name of the kernel
   * @param kernelName 
   */
  GetToolBox( kernelName : string) {
    if( this.workspace ) {
      switch(true){
        //R kernel
        case kernelName == "ir":
          this.toolbox = new RToolbox(this.notebooks,this.workspace) as IToolbox;
          break;
        // Python kernel
        case kernelName.toLocaleLowerCase().includes("python"):
          this.toolbox = new PythonToolbox(this.notebooks,this.workspace) as IToolbox;
          break;
        default:
          window.alert(`You are attempting to use Blockly Polyglot with unknown kernel ${kernelName}. No blocks are defined for this kernel.`);

      }
      //load the toolbox with blocks
      if( this.toolbox ){
        this.toolbox.UpdateToolbox();

        this.toolbox?.DoFinalInitialization();
        // TODO test; greys out everything
        // this.toolbox.GreyOutBlocks([]);
      }
    }

    console.log("jupyterlab_blockly_polyglot_extension: Attaching toolbox for " + `${kernelName}`);
  }

  /**
   * Remove blocks from workspace without affecting variable map like blockly.getMainWorkspace().clear() would
   */
  clearBlocks(): void {
    const workspace: Blockly.Workspace = Blockly.getMainWorkspace();
    const blocks = workspace.getAllBlocks(false);
    for (let i = 0; i < blocks.length; i++) {
      const block = blocks[i];
      //looks like disposing chains to child blocks, so check block exists b/f disposing
      if(workspace.getBlockById(block.id)) {
        block.dispose(false);
      }
    }
  }

  /**
   * !!!UNUSED Experimental function!!! that could replace 'blocksRendered' flag. Checks if blocks are saved/serialized. Blocks are considered saved if serialization of the current blocks matches xml in the cell. 
   */
  AreBlocksSaved(): boolean {
    const cellSerializedBlocks: string | null = this.GetActiveCellSerializedBlockXML();
    const workspaceSerializedBlocks = this.toolbox?.EncodeWorkspace();
    if( cellSerializedBlocks && cellSerializedBlocks == workspaceSerializedBlocks) {
      return true;
    } else {
      return false;
    }
  }

  /**
   * The kernel has executed. Refresh intellisense and log execution and error if it exists
   * @returns 
   */
  onKernelExecuted(): ((arg0: Kernel.IKernelConnection, arg1: KernelMessage.IIOPubMessage<any>) => boolean) {
    return (sender: Kernel.IKernelConnection, args: KernelMessage.IIOPubMessage<any>): boolean => {
        const messageType: string = args.header.msg_type.toString();
        switch (messageType) {
          case "execute_input": {
              console.log(`jupyterlab_blockly_polyglot_extension: kernel '${sender.name}' executed code, updating intellisense`);
            // LogToServer(JupyterLogEntry082720_Create("execute-code", args.content.code));
            this.toolbox?.UpdateAllIntellisense();
            break;
          }
          case "error": {
            // LogToServer(JupyterLogEntry082720_Create("execute-code-error", JSON.stringify(args.content)));
            break;
          }
          default: 0;
        }
      
      return true;
    };
  };

  /**
   * The active cell in the notebook has changed. Update state, particularly involving the clearing/serialization/deserialization of blocks.
   * @returns 
   */
  onActiveCellChanged(): (arg0: INotebookTracker, arg1: Cell<ICellModel> | null) => boolean {
    return (sender: INotebookTracker, args: Cell<ICellModel> | null): boolean => {
      if (args) {
        // LogToServer(JupyterLogEntry082720_Create("active-cell-change", args.node.outerText));
        const syncCheckbox: HTMLInputElement | null = document.getElementById("syncCheckboxPoly") as HTMLInputElement;
        const autosaveCheckbox: HTMLInputElement | null = document.getElementById("autosaveCheckbox") as HTMLInputElement;

        // if autosave enabled, attempt to save our current blocks to the previous cell we just navigated off (to prevent losing work)
        if (autosaveCheckbox?.checked && this.lastCell) {
          // this.RenderCodeToLastCell(); //refactoring to BlocksToCode
          this.BlocksToCode(this.lastCell)
          // set lastCell to current cell
          this.lastCell = args;
        }

        // if sync enabled, the blocks workspace should:
        // clear itself when encountering a new empty cell
        // replace itself with serialized blocks if they exist
        // however, if we have blocks are not in sync with XML, we don't want to lose them by clearing the workspace
        if (syncCheckbox?.checked && this.notebooks.activeCell) {
          //if blocks are in sync and the active cell has no xml to load, just clear the workspace;
          if (this.blocksInSyncWithXML && this.GetActiveCellSerializedBlockXML() == null) {
            this.clearBlocks();
          }
          //otherwise try to to create blocks from xnl string (fails gracefully)
          else {
            this.DeserializeBlocksFromXML();
          }
          //Update intellisense on blocks we just created
          this.toolbox?.UpdateAllIntellisense();
        }


      }
      return true;
    };
  };

  /**
   * Widget has attached to DOM and is ready for interaction. Inject blockly into div and set up event listeners for blockly events
   */
  onAfterAttach(): void {

    //toolbox can't be null or blockly throws errors
    // let starterToolbox =  { "kind": "categoryToolbox",  "contents": [] };
    // Sneak in a message to users who don't understand interface
    let starterToolbox =  { "kind": "categoryToolbox",  
      "contents": [
        { "kind": "CATEGORY", "contents": [], "colour": 20, "name":"OPEN" },
        { "kind": "CATEGORY", "contents": [], "colour": 70, "name":"A" },
        { "kind": "CATEGORY", "contents": [], "colour": 120, "name":"NOTEBOOK" },
        { "kind": "CATEGORY", "contents": [], "colour": 170, "name":"TO" },
        { "kind": "CATEGORY", "contents": [], "colour": 220, "name":"USE" },
        { "kind": "CATEGORY", "contents": [], "colour": 270, "name":"BLOCKLY" },
      ] 
    };
    this.workspace = Blockly.inject("blocklyDivPoly", {toolbox: starterToolbox});

    // TODO: move toolbox initialization elsewhere; should change with kernel
    // console.log("jupyterlab_blockly_polyglot_extension: blockly palette initialized");

    const logListener = (e: Blockly.Events.Abstract): void => {
      //TODO reconsider how blocksRendered is working
      //this fires when user creates blocks AND when blocks are deserialized
      if (e.type === "create") {
        this.blocksInSyncWithXML = false
      }
      // "finished loading" event seems to only fire when deserializing
      if (e.type === "finished_loading") {
        this.blocksInSyncWithXML = true
      }
      // LogToServer(BlocklyLogEntry082720_Create<Blockly_Events_Abstract__Class>(e.type, e));
    };
    this.workspace.removeChangeListener(logListener);
    this.workspace.addChangeListener(logListener);
  }

  /**
   * Widget has been resized; update UI 
   */
  onResize(msg: Widget.ResizeMessage): void {
    const blocklyDiv: any = document.getElementById("blocklyDivPoly");
    const buttonDiv: any = document.getElementById("buttonDivPoly");
    const adjustedHeight: number = msg.height - 30;
    blocklyDiv.setAttribute("style", "position: absolute; top: 0px; left: 0px; width: " + msg.width.toString() + "px; height: " + adjustedHeight.toString() + "px");
    buttonDiv.setAttribute("style", "position: absolute; top: " + adjustedHeight.toString() + "px; left: " + "0" + "px; width: " + msg.width.toString() + "px; height: " + "30" + "px");
    Blockly.svgResize(this.workspace as Blockly.WorkspaceSvg);
  }

/**
 * Get the XML comment string of the active cell if the string exists
 * @returns 
 */
GetActiveCellSerializedBlockXML(): string | null {
  if (this.notebooks.activeCell) {
    const cellText: string = this.notebooks.activeCell.model.sharedModel.getSource();
    if (cellText.indexOf("xmlns") >= 0) {
      const regex = /(<xml[\s\S]+<\/xml>)/;
      let match = cellText.match(regex);
      //if we match overall and the capture group, return the capture group
      if (match && match[0]) {
        return match[0]
      }
    }
    //No xml to match against
    else {
      return null;
    }
  }
  //No active cell
  return null;
}

/**
 * Render blocks to code and serialize blocks at the same time. Do error checking to prevent user error IF this action was user-initiated (not autosave).
 */
BlocksToCode(cell : Cell | null, userInitated: boolean = false): void {
  const code: string = this.toolbox?.BlocksToCode() ?? "";
  //this.generator.workspaceToCode(this.workspace);
  if (cell != null) {
    // if user called blocks to code on a markdown cell, complain
    if( userInitated && cells.isMarkdownCellModel(cell.model) ) {
      window.alert("You are calling \'Blocks to Code\' on a MARKDOWN cell. Select an empty CODE cell and try again.");
    // if this is a code cell, do blocks to code
    } else if(cells.isCodeCellModel(cell.model)) {
      let cell_contents = code + "\n#" + this.toolbox?.EncodeWorkspace();
      this.notebooks.activeCell?.model.sharedModel.setSource( cell_contents );
      console.log(("jupyterlab_blockly_polyglot_extension: wrote to cell\n" + code) + "\n");
      // LogToServer(JupyterLogEntry082720_Create("blocks-to-code", this$.notebooks.activeCell.model.value.text));
      this.blocksInSyncWithXML = true;
    }
  }
  else {
    console.log(("jupyterlab_blockly_polyglot_extension: cell is null, could not execute blocks to code for\n" + code) + "\n");
  }
};

/**
 * Render blocks in workspace using xml. Defaults to xml present in active cell
 */
DeserializeBlocksFromXML(): void {
  if (this.notebooks.activeCell) {
    const xmlString = this.GetActiveCellSerializedBlockXML();
    if( xmlString != null ){
      try {
        //clear existing blocks so we don't junk up the workspace
        this.clearBlocks();

        this.toolbox?.DecodeWorkspace(xmlString)

        // LogToServer(JupyterLogEntry082720_Create("xml-to-blocks", xmlString));
        } catch (e: any) {
          window.alert("Unable to perform \'Code to Blocks\': XML is either invald or renames existing variables. Specific error message is: " + e.message);
          console.log("jupyterlab_blockly_polyglot_extension: unable to decode blocks, last line is invald xml");
        }
      }
      else {
        console.log("jupyterlab_blockly_polyglot_extension: unable to decode blocks, active cell is null");
      }
    }
  };

} //end BlocklyWidget


/**
 * Return a MainAreaWidget wrapping a BlocklyWidget
 */
export function createMainAreaWidget(bw: BlocklyWidget): MainAreaWidget<BlocklyWidget> {
  const w: MainAreaWidget<BlocklyWidget> = new MainAreaWidget({
    content: bw as any,
  });
  w.id = "blockly-jupyterlab-polyglot";
  w.title.label = "Blockly Polyglot";
  w.title.closable = true;
  return w;
};

/**
 * Attach a MainAreaWidget by splitting the viewing area and placing in the left hand pane, if possible
 */
export function attachWidget(app: JupyterFrontEnd, notebooks: INotebookTracker, widget: MainAreaWidget): void {
  if (!widget.isAttached) {
    if( notebooks.currentWidget != null ) {
      const options: DocumentRegistry.IOpenOptions = {
        ref: notebooks.currentWidget.id,
        mode: "split-left",
      };
      notebooks.currentWidget.context.addSibling(widget, options);
    //Forcing a left split when there is no notebook open results in partially broken behavior, so we must add to the main area
    } else {
      app.shell.add(widget, "main");
    }
  app.shell.activateById(widget.id);
  }
};

/**
 * Catch notebook changed event for enabling extension and attaching to left side when query string command is given
 * @param this 
 * @param sender 
 * @param args 
 * @returns 
 */
export const runCommandOnNotebookChanged = function (this: any, sender: IWidgetTracker<NotebookPanel>, args: NotebookPanel | null): boolean {
  if( sender.currentWidget != null ) {
    console.log("jupyterlab_blockly_polyglot_extension: notebook changed, autorunning blockly polyglot command");
    this.commands.execute("blockly_polyglot:open");
  }
  return true;
};

/**
 * The kernel has changed. Make sure we are logging kernel messages and load the appropriate langauge toolbox
 * @param this
 * @param sender 
 * @param args 
 * @returns 
 */
export function onKernelChanged(this: any, sender: ISessionContext, args: Session.ISessionConnection.IKernelChangedArgs): boolean {
  const widget: BlocklyWidget = this;
  //NOTE: removing "notHooked" logic
  // if (widget.notHooked) {
    if(sender.session?.kernel != null ) {
      //listend for kernel messages
      let connection_status = sender.session.kernel.iopubMessage.connect(widget.onKernelExecuted(), widget);
      console.log(`jupyterlab_blockly_polyglot_extension: onKernelExecuted event is ${connection_status ? "now": "already"} connected for ${sender.session.kernel.name}`);
      // console.log("jupyterlab_blockly_polyglot_extension: Listening for kernel messages");
      //connect appropriate toolbox
      widget.GetToolBox(sender.session.kernel.name);
      // console.log("jupyterlab_blockly_polyglot_extension: Attaching toolbox for " + `${sender.session.kernel.name}`);
      
      // widget.notHooked = false;
    }
    return true;
  // }
  // else {
  //   return false;
  // }
};

/**
 * The notebook has changed
 * @param this 
 * @param sender 
 * @param args 
 * @returns 
 */
export function onNotebookChanged(this: any, sender: IWidgetTracker<NotebookPanel>, args: NotebookPanel | null): boolean {
  const blocklyWidget: BlocklyWidget = this;
  if( sender.currentWidget != null) {
    console.log("jupyterlab_blockly_polyglot_extension: notebook changed to " +  sender.currentWidget.context.path);
    // LogToServer(JupyterLogEntry082720_Create("notebook-changed", notebook.context.path));
    let connection_status = sender.currentWidget.sessionContext.kernelChanged.connect(onKernelChanged, blocklyWidget);
    console.log(`jupyterlab_blockly_polyglot_extension: kernelChanged event is ${connection_status ? "now": "already"} connected`);

    //onKernelChanged will only fire the first time a kernel is loaded
    //so if a user switches back and forth between notebooks with different kernels that are
    //already loaded, we need to catch that here to update the toolbox
    // if the kernel is known, update the toolbox
    if(sender.currentWidget.sessionContext?.session?.kernel?.name){
      blocklyWidget.GetToolBox(sender.currentWidget.sessionContext?.session?.kernel?.name);
    }
  }
  return true;
};

/**
 * Plugin definition for Jupyter; makes use of BlocklyWidget
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab_blockly_polyglot_extension',
  autoStart: true,
  requires: [ICommandPalette, INotebookTracker, ILayoutRestorer],
  activate: (app: JupyterFrontEnd, palette: ICommandPalette, notebooks: INotebookTracker, restorer: ILayoutRestorer) => {
    console.log("jupyterlab_blockly_polyglot_extension: activated");

     //Create a blockly widget and place inside main area widget
    const blocklyWidget: BlocklyWidget = new BlocklyWidget(notebooks);
    let widget: MainAreaWidget<BlocklyWidget> = createMainAreaWidget(blocklyWidget);

    //Set up widget tracking to restore state
    const tracker: WidgetTracker<MainAreaWidget<BlocklyWidget>> = new WidgetTracker({
      namespace: "blockly_polyglot",
    });
    if (restorer) {
      restorer.restore(tracker, {
        command: "blockly_polyglot:open",
        name: (): string => "blockly_polyglot",
      });
    }

    //wait until a notebook is displayed to hook kernel messages
    notebooks.currentChanged.connect(onNotebookChanged, blocklyWidget);

    //Add application command to display
    app.commands.addCommand("blockly_polyglot:open", {
      label: "Blockly Polyglot",
      execute: (): void => {
        //Recreate the widget if the user previously closed it
        if (widget == null || widget.isDisposed) {
          widget = createMainAreaWidget(blocklyWidget);
        }
        //Attach the widget to the UI in a smart way
        attachWidget(app, notebooks, widget);
        //Track the widget to restore its state if the user does a refresh
        if (!tracker.has(widget)) {
          tracker.add(widget);
        }
      },
    } as CommandRegistry.ICommandOptions);

     //Add command to command palette
    palette.addItem({ command: "blockly_polyglot:open", category: 'Blockly' });

    //----------------------
    // Process query string
    //----------------------
    const searchParams: any = new URLSearchParams(window.location.search);

    //If query string has bl=1, trigger the open command once the application is ready
    if( searchParams.get("bl") == "1"){
        console.log("jupyterlab_blockly_polyglot_extension: triggering open command based on query string input");
        //wait until a notebook is displayed so we dock correctly (e.g. nbgitpuller deployment)
        //NOTE: workspaces are stateful, so the notebook must be closed, then openned in the workspace for this to fire
        app.restored.then<void>((): void => {
          notebooks.currentChanged.connect(runCommandOnNotebookChanged, app);
          //If we force blockly to be open, do not allow blockly to be closed; useful for classes and experiments
          widget.title.closable = false;
        });
    }
    
    //If query string has id=, set up logging with this id
    if( searchParams.get("id") == "1"){
      //TODO set up logging with this id
    }

    //If query string has log=, set up logging with this log endpoint url
    if( searchParams.get("log") == "1"){
      //TODO set up logging with this url
    }

  }
};

export default plugin;