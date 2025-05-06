import logging
import os

from textwrap import dedent

logger = logging.getLogger(__name__)


class ShellScriptWriter:
    """This class formats shell scripts (.sh files) to be used in the docker-compose.yml file."""

    @staticmethod
    def write_executable_script(path: str, content: str):
        # Normalize line endings
        content: str = content.replace("\r\n", "\n").replace("\r", "\n")

        # Ensure script starts with proper shebang
        if not content.startswith("#!/bin/bash"):
            content = "#!/bin/bash\n" + content

        try:
            # Write the script file
            with open(path, "w", newline="\n") as f:
                f.write(dedent(content))

            # Set executable permission for user, group, others (chmod 755)
            os.chmod(path, 0o755)

            logger.info(f"✅ Script written and made executable: {path}")

        except Exception as e:
            logger.error(f"❌ Failed to write script to {path}: {str(e)}")
            raise
