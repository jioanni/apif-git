Welcome to the API Fortress Post-Receive Git Hook.

The hook is designed to push any changes to your API Fortress test code to the API Fortress platform. It leverages the same configuration file that the API Fortress Command Line tool uses and will automatically identify the necessary webhook by branch. In the file itself, a user needs to specify the **location of the config file** and the **name of the folder that contains the tests**