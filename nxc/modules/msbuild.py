# import sys
# import requests
from requests import ConnectionError

class NXCModule:
    """
    Module by @gerbot_, upload and run MSBuild files on the target.
    """
    
    name = "msbuild"
    description = "Upload and run MSBuild files on the target"
    supported_protocols = ["smb"]
    opsec_safe = False
    multiple_hosts = True

    def __init__(self, job, sock, session, args):
        self.job = job
        self.sock = sock
        self.session = session
        self.args = args

    def options(self, context, module_data):
        """
        Define and handle user-provided options for the module.
        """
        context.register_option("MSBUILD_FILE", "Path to the MSBuild file to upload and execute", required=True)

    def on_admin_login(self, context, connection):
        """
        Called when a successful SMB connection with admin privileges is established.
        """
        msbuild_file = context.options.get("MSBUILD_FILE")
        if not msbuild_file:
            context.log("Please provide the path to the MSBuild file using the 'set MSBUILD_FILE' command")
            return

        try:
            # Upload the MSBuild file to the target
            with open(msbuild_file, "rb") as file:
                file_content = file.read()
            remote_path = f"C:\\Windows\\Temp\\{msbuild_file.split('/')[-1]}"
            connection.put_file(remote_path, file_content)

            # Execute the MSBuild file on the target
            command = f"C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\MSBuild.exe {remote_path}"
            output = connection.exec_cmd(command)

            # Log the output and send it back to the controller
            context.log(output)

            # Clean up the uploaded MSBuild file
            connection.exec_cmd(f"del {remote_path}")

        except (ConnectionError, ValueError) as e:
            context.log(f"Error: {str(e)}")

        except Exception as e:
            context.log(f"Unexpected error: {str(e)}")

    def run(self):
        """
        Main entry point for the module.
        """
        self.job.spawn_smb_client(self.session, self.on_admin_login)
