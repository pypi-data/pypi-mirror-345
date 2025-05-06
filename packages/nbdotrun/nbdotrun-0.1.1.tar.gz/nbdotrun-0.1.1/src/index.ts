import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';

import { CodeCellModel, CodeCell, ICellModel } from '@jupyterlab/cells';

const PLUGIN_NAME = 'nbdotrun';
const PLUGIN_ID = `${PLUGIN_NAME}:plugin`;

function throttle(fn: () => void, delay: number) {
  let timeout: number | null = null;
  return () => {
    if (timeout) {
      return;
    }
    timeout = window.setTimeout(() => {
      fn();
      timeout = null;
    }, delay);
  };
}

function escapeRegExp(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function shouldAutoExecute(text: string, triggerSymbol: string) {
  const lines = text.trimEnd().split('\n');
  const last = lines[lines.length - 1];
  const regex = new RegExp(`^\\s*${escapeRegExp(triggerSymbol)}\\s*$`);
  return regex.test(last);
}

function attachNotebookListener(panel: NotebookPanel, triggerSymbol: string) {
  // track which cells have been connected
  const connectedCells = new WeakSet<ICellModel>();

  panel.context.ready.then(() => {
    const notebook = panel.content;
    const model = notebook.model;

    if (!model) {
      console.error(`${PLUGIN_NAME} Failed to retrieve notebook model`);
      return;
    }

    const throttledScan = throttle(() => {
      for (let i = 0; i < model.cells.length; i++) {
        const cellWidget = notebook.widgets[i];
        const cellModel = model.cells.get(i);

        if (cellModel?.type === 'code' && cellWidget instanceof CodeCell) {
          const codeModel = cellModel as CodeCellModel;
          const source = codeModel.sharedModel.getSource();

          if (shouldAutoExecute(source, triggerSymbol)) {
            console.log(
              `${PLUGIN_NAME} Executing cell ${i} due to terminal symbol match: "${triggerSymbol}"`
            );

            // remove the trigger line
            const newSource = source
              .trimEnd()
              .split('\n')
              .slice(0, -1)
              .join('\n');

            codeModel.sharedModel.setSource(newSource);

            void CodeCell.execute(cellWidget, panel.sessionContext);
          }
        }
      }
    }, 300); // debounce time in ms

    // Initial hookup for existing cells
    for (let i = 0; i < model.cells.length; i++) {
      const cellModel = model.cells.get(i);
      if (!connectedCells.has(cellModel) && cellModel.type === 'code') {
        const codeModel = cellModel as CodeCellModel;
        codeModel.contentChanged.connect(throttledScan);
        connectedCells.add(codeModel);
      }
    }

    model.cells.changed.connect((_, changes) => {
      throttledScan();

      if (changes.type === 'add') {
        changes.newValues.forEach(cell => {
          if (!connectedCells.has(cell) && cell.type === 'code') {
            const codeModel = cell as CodeCellModel;
            codeModel.contentChanged.connect(throttledScan);
            connectedCells.add(codeModel);
          }
        });
      }
    });
  });
}

function activateNbdotrun(
  app: JupyterFrontEnd,
  notebooks: INotebookTracker,
  settings?: ISettingRegistry
) {
  console.log(`JupyterLab extension ${PLUGIN_NAME} is activated!`);

  let triggerSymbol = '.';

  if (settings) {
    settings
      .load(PLUGIN_ID)
      .then(settings => {
        triggerSymbol = settings.get('triggerSymbol').composite as string;
      })
      .catch(reason => {
        console.error(`${PLUGIN_NAME} Failed to load settings`, reason);
      });
  }

  notebooks.widgetAdded.connect((_, panel) => {
    attachNotebookListener(panel, triggerSymbol);
  });

  notebooks.forEach(panel => attachNotebookListener(panel, triggerSymbol));
}

/**
 * Initialization data for the nbdotrun extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: PLUGIN_ID,
  description:
    'A JupyterLab extension that will listen for code cell changes and run if ending in dot (`.`).',
  autoStart: true,
  requires: [INotebookTracker],
  optional: [ISettingRegistry],
  activate: activateNbdotrun
};

export default plugin;
