// Modules to control application life and create native browser window
const { app, BrowserWindow } = require('electron');

// Keep a global reference of the window object, if you don't, the window will
// be closed automatically when the JavaScript object is garbage collected.
let mainWindow;

// Used in configuring path to load html from React
const path = require('path');
const url = require('url');

function createWindow () {
    let browserOptions = {width: 800, height: 600};
    // Create the browser window.
    mainWindow = new BrowserWindow(browserOptions);

    // Configuring locaiton for HTML outputted after React
    const startURL = url.format({
      pathname: path.join(__dirname, '../build/index.html'),
      protocol: 'file:', 
      slashes: true
    });

    // Loads html
    mainWindow.loadURL(startURL);

    // Open the DevTools
    mainWindow.webContents.openDevTools();

    // Emitted when the window is closed.
    mainWindow.on('closed', function () {
    // Dereference the window object, usually you would store windows
    // in an array if your app supports multi windows, this is the time
    // when you should delete the corresponding element.
    mainWindow = null;
    });
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', createWindow);


// Quit when all windows are closed.
app.on('window-all-closed', function () {
    // On OS X it is common for applications and their menu bar
    // to stay active until the user quits explicitly with Cmd + Q
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', function () {
    // On OS X it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (mainWindow === null) {
        createWindow();
    }
});
